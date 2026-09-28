export function getInferredApiKey() {
  return process.env?.TOGETHER_API_KEY;
}

export function getInferredBaseUrl() {
  if (process.env.TOGETHER_BASE_URL) {
    return process.env.TOGETHER_BASE_URL;
  }

  return "https://api.bartender.codesandbox.io";
}

/**
 * Derives the image-builder service URL from the management API base URL: the
 * `builder` subdomain of the same registrable domain, so any API hostname on a
 * given domain resolves to that domain's single builder host.
 *
 *   https://api.bartender.codesandbox.io   -> https://builder.codesandbox.io
 *   https://api2.bartender.codesandbox.dev -> https://builder.codesandbox.dev
 *   https://api.codesandbox.dev            -> https://builder.codesandbox.dev
 *
 * Hosts with no domain to attach a subdomain to (`localhost`, IP literals) are
 * returned unchanged, so local setups keep talking to what they configured.
 */
export function getBuilderUrl(apiBaseUrl: string): string {
  const url = new URL(apiBaseUrl);
  const labels = url.hostname.split(".");

  // IPv6 literals keep their brackets in `hostname`; IPv4 is all-numeric labels.
  const isIpLiteral =
    url.hostname.startsWith("[") ||
    labels.every((label) => /^\d+$/.test(label));
  if (isIpLiteral || labels.length < 2) {
    return apiBaseUrl;
  }

  url.hostname = ["builder", ...labels.slice(-2)].join(".");
  return url.toString().replace(/\/+$/, "");
}

/**
 * True when the API base URL points at the local `codesandbox.dev` environment
 * (any hostname on that domain, e.g. `api.codesandbox.dev` or
 * `api2.bartender.codesandbox.dev`), where the services — including the image
 * builder — run on this machine.
 */
export function isLocalEnvironment(apiBaseUrl: string): boolean {
  const apiHostName = new URL(apiBaseUrl).hostname;

  return (
    apiHostName === "codesandbox.dev" ||
    apiHostName.endsWith(".codesandbox.dev")
  );
}

/**
 * Whether a build should convert its image to EROFS, so a node mounts it
 * lazily from object storage instead of pulling and unpacking it.
 *
 * Two ways in. `TOGETHER_EROFS_ENABLED=true` opts a caller in explicitly, and
 * a v2 control plane is opted in by where it points: EROFS is what v2 serves,
 * so a base URL on an `api.bartender-v2…` host implies it.
 *
 *   https://api.bartender-v2.codesandbox.io -> true
 *   https://api.bartender.codesandbox.io    -> false, unless the env var is set
 */
/**
 * Whether a build should produce a nydus-compressed image, which a nydus
 * snapshotter mounts lazily.
 *
 * Read the same way as {@link isErofsEnabled}: `TOGETHER_NYDUS_ENABLED=true`
 * opts a caller in explicitly, and the older control plane is opted in by where
 * it points — nydus is what it has always consumed.
 *
 *   https://api.bartender.codesandbox.io    -> true
 *   https://api.bartender-v2.codesandbox.io -> false (that one serves EROFS)
 *   https://api.codesandbox.dev             -> false (devbox nodes unpack OCI
 *                                              layers and reject nydus blobs)
 */
export function isNydusEnabled(apiBaseUrl: string): boolean {
  if (process.env.TOGETHER_NYDUS_ENABLED === "true") {
    return true;
  }

  try {
    // The trailing dot is what keeps `api.bartender-v2…` out.
    return new URL(apiBaseUrl).hostname.startsWith("api.bartender.");
  } catch {
    return false;
  }
}

export function isErofsEnabled(apiBaseUrl: string): boolean {
  if (process.env.TOGETHER_EROFS_ENABLED === "true") {
    return true;
  }

  try {
    return new URL(apiBaseUrl).hostname.startsWith("api.bartender-v2");
  } catch {
    // An unparseable base URL is someone else's error to report; it is not a
    // reason to convert.
    return false;
  }
}

/** Architecture of the machine running the SDK. */
export function getHostArchitecture(): "amd64" | "arm64" {
  return process.arch === "arm64" ? "arm64" : "amd64";
}
