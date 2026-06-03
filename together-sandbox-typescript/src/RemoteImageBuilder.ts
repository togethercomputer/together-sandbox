import * as fs from "fs";
import * as path from "path";
import * as tar from "tar";
import ignore from "@balena/dockerignore";
import { EventSource } from "eventsource";

import { withRetry, sleep, RETRYABLE_STATUS_CODES } from "./utils.js";

/**
 * Status codes that should trigger a retry of the SSE log stream. Combines
 * the shared retryable set with 404 (the build pod hasn't materialised yet).
 */
const STREAM_RETRYABLE_STATUS_CODES = new Set<number>([...RETRYABLE_STATUS_CODES, 404]);

/**
 * Minimal logger contract used by {@link RemoteImageBuilderClient} to surface
 * streamed build output to the caller. Mirrors the duck-typed
 * `_BuildLogger` used by the Python SDK.
 */
export interface BuildLogger {
  debug(msg: string): void;
  warning(msg: string): void;
}

/**
 * Options for the remote image builder client.
 */
export interface RemoteImageBuilderOptions {
  apiUrl: string;
  token: string;
  logger?: BuildLogger;
}

/**
 * Options for a single remote build invocation.
 */
export interface RemoteBuildOptions {
  /** Local directory to use as the Docker build context. */
  contextDir: string;
  /**
   * Image name in `"name"` or `"name:tag"` format. The namespace is derived
   * server-side from the auth token. If no tag is included the server
   * defaults to `"latest"`.
   */
  imageName: string;
  /** Dockerfile path relative to {@link contextDir}. Defaults to `"Dockerfile"`. */
  dockerfile?: string;
  /** Optional build arguments. */
  buildArgs?: Record<string, string>;
  /** Produce a nydus-compressed image (default `true`). */
  nydus?: boolean;
}

interface SubmitResponse {
  build_id?: string;
}

interface StatusResponse {
  image_ref?: string;
  [key: string]: unknown;
}

/**
 * Client for the image-builder remote build service.
 *
 * Submits a build context to the service, streams build logs via SSE,
 * and returns the final image reference on success.
 *
 * Mirrors the Python SDK's `RemoteImageBuilderClient` so behaviour stays
 * consistent across both implementations.
 */
export class RemoteImageBuilderClient {
  private readonly _apiUrl: string;
  private readonly _token: string;
  private readonly _logger?: BuildLogger;

  constructor(opts: RemoteImageBuilderOptions) {
    this._apiUrl = opts.apiUrl.replace(/\/+$/, "");
    this._token = opts.token;
    this._logger = opts.logger;
  }

  /**
   * Build and push a container image.
   *
   * Tar-gzips {@link RemoteBuildOptions.contextDir} (honouring `.dockerignore`),
   * POSTs it to `${apiUrl}/builds`, then streams build logs over SSE until
   * the build completes or fails.
   *
   * @returns Full image reference returned by the service
   *   (e.g. `"registry/namespace/name:tag"`).
   * @throws If the build fails or the API rejects the request.
   */
  async build(opts: RemoteBuildOptions): Promise<string> {
    const dockerfile = opts.dockerfile ?? "Dockerfile";
    const nydus = opts.nydus ?? true;

    // ── Collect .dockerignore exclusions ────────────────────────────────────
    const dockerignorePath = path.join(opts.contextDir, ".dockerignore");
    let ig: ReturnType<typeof ignore> | null = null;
    if (fs.existsSync(dockerignorePath)) {
      const content = await fs.promises.readFile(dockerignorePath, "utf-8");
      ig = ignore().add(content.split(/\r?\n/));
    }

    // ── Walk context dir and collect files (non-recursive add, matching the
    //    Python implementation that uses `tarfile.add(..., recursive=False)`).
    const allFiles: string[] = [];
    await this._walkDir(opts.contextDir, "", allFiles);
    allFiles.sort();

    const files = allFiles.filter((rel) => !ig || !ig.ignores(rel));

    // ── Build tar.gz of the context in memory ───────────────────────────────
    const tarStream = tar.c(
      {
        gzip: true,
        cwd: opts.contextDir,
        portable: true,
        // Each path is a file (we walked the tree manually) so there is no
        // directory recursion to worry about; tar will add them as-is.
        noDirRecurse: true,
      },
      files,
    ) as unknown as NodeJS.ReadableStream;
    const tarBuffer = await this._streamToBuffer(tarStream);

    // ── Submit build (retries on transient transport failures) ──────────────
    const buildData = await withRetry<SubmitResponse>("imageBuilder.submit", async () => {
      const form = new FormData();
      form.append("image_name", opts.imageName);
      form.append("dockerfile", dockerfile);
      form.append("build_args", JSON.stringify(opts.buildArgs ?? {}));
      form.append("nydus_convert", nydus ? "true" : "false");
      form.append(
        "context",
        new Blob([new Uint8Array(tarBuffer)], { type: "application/gzip" }),
        "context.tar.gz",
      );

      const response = await fetch(`${this._apiUrl}/builds`, {
        method: "POST",
        headers: { Authorization: `Bearer ${this._token}` },
        body: form,
      });
      if (!response.ok) {
        const text = await response.text().catch(() => "");
        throw new Error(`imageBuilder.submit: HTTP ${response.status}${text ? ` — ${text}` : ""}`);
      }
      return (await response.json()) as SubmitResponse;
    });

    const buildId = buildData.build_id;
    if (!buildId) {
      throw new Error(`No build_id in response: ${JSON.stringify(buildData)}`);
    }

    // Handle Ctrl+C from the user: Node does not propagate SIGINT into
    // pending async code, so without this listener the process would die
    // and leave the build running server-side. The handler issues the
    // DELETE and then exits with the conventional 130 status. We use
    // `once` + `removeListener` so repeat invocations in the same process
    // (e.g. tests, daemons) don't accumulate stale handlers.
    const onSigint = async () => {
      try {
        await this.cancel(buildId);
      } finally {
        process.exit(130);
      }
    };
    process.once("SIGINT", onSigint);

    try {
      return await this._streamUntilDone(buildId);
    } finally {
      process.removeListener("SIGINT", onSigint);
    }
  }

  /**
   * Cancel a running build by deleting its job.
   */
  async cancel(buildId: string): Promise<void> {
    try {
      await fetch(`${this._apiUrl}/builds/${buildId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${this._token}` },
      });
    } catch (e) {
      this._logger?.warning(
        `Failed to cancel build ${buildId}: ${e instanceof Error ? e.message : String(e)}`,
      );
    }
  }

  // ─── Private helpers ──────────────────────────────────────────────────────

  /**
   * Stream build logs via SSE until the build completes or fails.
   *
   * Retries on transient connection errors (e.g. while the build pod is
   * still scheduling). Returns the `image_ref` on success.
   */
  private async _streamUntilDone(buildId: string): Promise<string> {
    const url = `${this._apiUrl}/builds/${buildId}/logs`;
    const maxAttempts = 5;
    const wait = 1000;

    let attempt = 1;
    while (true) {
      let sawDone = false;
      let fatalError: Error | undefined;

      try {
        sawDone = await this._consumeStream(url, (errMsg) => {
          fatalError = new Error(`Build ${buildId} failed: ${errMsg}`);
        });
      } catch (err) {
        const e = err instanceof Error ? err : new Error(String(err));
        // Parse the HTTP status from the `_consumeStream` error message
        // (formatted as `SSE HTTP <code>...`) so we can branch on the
        // shared retryable set plus 404 (build pod isn't ready yet).
        const match = e.message.match(/^SSE HTTP (\d+)/);
        const status = match ? Number(match[1]) : undefined;
        const isRetryable = status !== undefined && STREAM_RETRYABLE_STATUS_CODES.has(status);
        if (!isRetryable || attempt >= maxAttempts) throw e;
        attempt++;
        await sleep(wait);
        continue;
      }

      // An `error` event inside the stream is fatal — don't retry.
      if (fatalError) throw fatalError;

      if (sawDone) {
        const status = await this._getStatus(buildId);
        const imageRef = status.image_ref;
        if (!imageRef) {
          throw new Error(`Build succeeded but no image_ref in status: ${JSON.stringify(status)}`);
        }
        return imageRef;
      }

      // The stream closed, but we are not done, so we just reset retry attempts and continue. It can take a long time with big builds
      attempt = 1;
      await sleep(wait);
    }
  }

  /**
   * Open one SSE connection and consume events until it ends. Returns true
   * iff a JSON `{ "done": true }` sentinel was seen.
   *
   * Invokes {@link onError} with the message when a `{ "error": ... }`
   * sentinel arrives. The caller is responsible for turning that into a
   * thrown error so retry-vs-fatal classification stays in one place.
   */
  private _consumeStream(url: string, onError: (msg: string) => void): Promise<boolean> {
    return new Promise<boolean>((resolve, reject) => {
      const token = this._token;
      const logger = this._logger;
      const es = new EventSource(url, {
        fetch: (input, init) =>
          fetch(input, {
            ...init,
            headers: {
              ...(init?.headers ?? {}),
              Authorization: `Bearer ${token}`,
              Accept: "text/event-stream",
            },
          }),
      });

      let sawDone = false;
      let settled = false;

      const settle = (fn: () => void) => {
        if (settled) return;
        settled = true;
        es.close();
        fn();
      };

      es.onmessage = (event: MessageEvent) => {
        const data = typeof event.data === "string" ? event.data : "";
        // JSON control events contain "done" or "error" keys.
        if (data.startsWith("{") && (data.includes('"done"') || data.includes('"error"'))) {
          try {
            const obj = JSON.parse(data) as {
              done?: boolean;
              error?: string;
            };
            if (obj.done) {
              sawDone = true;
              settle(() => resolve(true));
              return;
            }
            if (obj.error) {
              onError(obj.error);
              settle(() => resolve(false));
              return;
            }
          } catch {
            // Not valid JSON — fall through to logger.
          }
        }
        logger?.debug(`[image-builder] ${data}`);
      };

      es.onerror = (event) => {
        // The `eventsource` package surfaces HTTP errors with a `code`
        // property. Network-level closes (server end of stream) have no
        // `code` and should be treated as "stream ended".
        const evt = event as { code?: number; message?: string };
        if (typeof evt.code === "number") {
          settle(() =>
            reject(new Error(`SSE HTTP ${evt.code}${evt.message ? `: ${evt.message}` : ""}`)),
          );
          return;
        }
        // Stream closed without seeing `done` — let the caller retry.
        settle(() => resolve(sawDone));
      };
    });
  }

  /**
   * Fetch build status JSON.
   */
  private async _getStatus(buildId: string): Promise<StatusResponse> {
    return withRetry<StatusResponse>("imageBuilder.getStatus", async () => {
      const response = await fetch(`${this._apiUrl}/builds/${buildId}`, {
        headers: { Authorization: `Bearer ${this._token}` },
      });
      if (!response.ok) {
        throw new Error(`imageBuilder.getStatus: HTTP ${response.status}`);
      }
      return (await response.json()) as StatusResponse;
    });
  }

  /**
   * Recursive walk that pushes file-or-symlink paths relative to {@link root}
   * into {@link out}. Mirrors `Path.rglob("*")` + `is_file() or is_symlink()`
   * from the Python implementation.
   */
  private async _walkDir(root: string, rel: string, out: string[]): Promise<void> {
    const here = rel ? path.join(root, rel) : root;
    const entries = await fs.promises.readdir(here, { withFileTypes: true });
    for (const entry of entries) {
      const childRel = rel ? path.join(rel, entry.name) : entry.name;
      if (entry.isDirectory()) {
        await this._walkDir(root, childRel, out);
      } else if (entry.isFile() || entry.isSymbolicLink()) {
        out.push(childRel);
      }
    }
  }

  /**
   * Collect a Readable stream's chunks into a single Buffer.
   */
  private async _streamToBuffer(stream: NodeJS.ReadableStream): Promise<Buffer> {
    const chunks: Buffer[] = [];
    for await (const chunk of stream) {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    }
    return Buffer.concat(chunks);
  }
}
