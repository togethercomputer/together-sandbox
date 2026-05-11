import { describe, it, expect, vi, beforeEach } from "vitest";
import { callApi, withRetry } from "./utils.js";
import type { RetryContext } from "./types.js";
import { HttpError } from "./errors.js";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function createMockResponse(status: number): Response {
  return {
    status,
    statusText: `Status ${status}`,
  } as unknown as Response;
}

function createApiResult<T>(
  data?: T,
  error?: unknown,
  status = 200,
): {
  data?: T;
  error?: unknown;
  response: Response;
} {
  return {
    data,
    error,
    response: createMockResponse(status),
  };
}

// ─── Success Path ────────────────────────────────────────────────────────────

describe("callApi", () => {
  describe("success path", () => {
    it("returns result.data when fn succeeds on first attempt", async () => {
      const fn = vi.fn(async () => createApiResult({ foo: "bar" }));

      const result = await callApi("testOp", fn);

      expect(result).toEqual({ foo: "bar" });
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("does not call onRetry when fn succeeds", async () => {
      const onRetry = vi.fn();
      const fn = vi.fn(async () => createApiResult({ foo: "bar" }));
      await callApi("testOp", fn, { onRetry });

      expect(onRetry).not.toHaveBeenCalled();
    });
  });

  // ─── Default Retry on HTTP Status ────────────────────────────────────────

  describe("default retry on HTTP status", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("retries on status 429 (Too Many Requests)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("429"), 429),
        )
        .mockResolvedValueOnce(
          createApiResult({ success: true }, undefined, 200),
        );

      const promise = callApi("testOp", fn);
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toEqual({ success: true });
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it("retries on status 500 (Internal Server Error)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("500"), 500),
        )
        .mockResolvedValueOnce(
          createApiResult({ fixed: true }, undefined, 200),
        );

      const promise = callApi("testOp", fn);
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toEqual({ fixed: true });
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it("retries on status 502 (Bad Gateway)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("502"), 502),
        )
        .mockResolvedValueOnce(createApiResult({ ok: true }, undefined, 200));

      const promise = callApi("testOp", fn);
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toEqual({ ok: true });
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it("retries on status 503 (Service Unavailable)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("503"), 503),
        )
        .mockResolvedValueOnce(
          createApiResult({ ready: true }, undefined, 200),
        );

      const promise = callApi("testOp", fn);
      await vi.runOnlyPendingTimersAsync();
      const result = await promise;

      expect(result).toEqual({ ready: true });
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it("retries on status 504 (Gateway Timeout)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("504"), 504),
        )
        .mockResolvedValueOnce(
          createApiResult({ timeout: false }, undefined, 200),
        );

      const promise = callApi("testOp", fn);
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toEqual({ timeout: false });
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it("retries on status 408 (Request Timeout)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("408"), 408),
        )
        .mockResolvedValueOnce(
          createApiResult({ alive: true }, undefined, 200),
        );

      const promise = callApi("testOp", fn);
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toEqual({ alive: true });
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it("does NOT retry on status 400 (Bad Request)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("Bad Request"), 400),
        );

      const assertion = expect(callApi("testOp", fn)).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("does NOT retry on status 401 (Unauthorized)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("Unauthorized"), 401),
        );

      const assertion = expect(callApi("testOp", fn)).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("does NOT retry on status 403 (Forbidden)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("Forbidden"), 403),
        );

      const assertion = expect(callApi("testOp", fn)).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("does NOT retry on status 404 (Not Found)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("Not Found"), 404),
        );

      const assertion = expect(callApi("testOp", fn)).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("exhausts maxAttempts (default 3) and then throws", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("500"), 500));

      const assertion = expect(callApi("testOp", fn)).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;
      expect(fn).toHaveBeenCalledTimes(3);
    });

    it("fn is called exactly N times where N = maxAttempts", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("500"), 500));

      const assertion = expect(
        callApi("testOp", fn, { maxAttempts: 2 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;
      expect(fn).toHaveBeenCalledTimes(2);
    });
  });

  // ─── Default Retry on Network Error ──────────────────────────────────────

  describe("default retry on network error", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("retries when fn throws TypeError (fetch network failure)", async () => {
      const fn = vi
        .fn()
        .mockRejectedValueOnce(new TypeError("network error"))
        .mockResolvedValueOnce(createApiResult({ success: true }));

      const promise = callApi("testOp", fn);
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toEqual({ success: true });
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it("wraps fetch TypeError into HttpError with status 0 after maxAttempts", async () => {
      const fn = vi.fn().mockRejectedValue(new TypeError("network error"));

      const errPromise = callApi("testOp", fn, { maxAttempts: 2 }).catch(
        (e) => e,
      );
      await vi.runAllTimersAsync();
      const err = await errPromise;

      expect(err).toBeInstanceOf(HttpError);
      expect((err as HttpError).status).toBe(0);
      expect((err as HttpError).message).toContain("network error");
      expect(fn).toHaveBeenCalledTimes(2);
    });
  });

  // ─── shouldRetry Override ────────────────────────────────────────────────

  describe("shouldRetry override", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("returning false stops immediately, even for a retryable status", async () => {
      const shouldRetry = vi.fn().mockReturnValue(false);
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("500"), 500));

      await expect(callApi("testOp", fn, { shouldRetry })).rejects.toThrow();
      expect(fn).toHaveBeenCalledTimes(1);
      expect(shouldRetry).toHaveBeenCalledTimes(1);
    });

    it("returning true retries with default delay", async () => {
      const shouldRetry = vi.fn().mockReturnValue(true);
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("400"), 400),
        )
        .mockResolvedValueOnce(createApiResult({ ok: true }));

      const promise = callApi("testOp", fn, { shouldRetry });
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toEqual({ ok: true });
      expect(fn).toHaveBeenCalledTimes(2);
      expect(shouldRetry).toHaveBeenCalledTimes(1);
    });

    it("returning a number retries with that custom delay", async () => {
      const shouldRetry = vi.fn().mockReturnValue(1000);
      const onRetry = vi.fn();
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("500"), 500),
        )
        .mockResolvedValueOnce(createApiResult({ ok: true }));

      const promise = callApi("testOp", fn, { shouldRetry, onRetry });
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toEqual({ ok: true });
      expect(onRetry).toHaveBeenCalledWith(
        expect.objectContaining({ delay: 1000 }),
      );
    });

    it("is called with correct RetryContext shape: operation, attempt, status, error, delay", async () => {
      const shouldRetry = vi.fn().mockReturnValue(false);
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("503"), 503));

      await expect(callApi("myOp", fn, { shouldRetry })).rejects.toThrow();

      const ctx = shouldRetry.mock.calls[0][0] as RetryContext;
      expect(ctx).toHaveProperty("operation", "myOp");
      expect(ctx).toHaveProperty("attempt", 1);
      expect(ctx).toHaveProperty("status", 503);
      expect(ctx.error).toBeInstanceOf(HttpError);
      expect((ctx.error as HttpError).status).toBe(503);
      expect(typeof ctx.delay).toBe("number");
    });

    it("is called with correct attempt number (1-based)", async () => {
      const shouldRetry = vi
        .fn()
        .mockReturnValueOnce(true)
        .mockReturnValueOnce(true)
        .mockReturnValueOnce(false);
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("500"), 500));

      const assertion = expect(
        callApi("testOp", fn, { shouldRetry, maxAttempts: 4 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;

      expect(shouldRetry).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({ attempt: 1 }),
      );
      expect(shouldRetry).toHaveBeenNthCalledWith(
        2,
        expect.objectContaining({ attempt: 2 }),
      );
      expect(shouldRetry).toHaveBeenNthCalledWith(
        3,
        expect.objectContaining({ attempt: 3 }),
      );
    });
  });

  // ─── onRetry Callback ─────────────────────────────────────────────────────

  describe("onRetry callback", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("is called once per failed attempt (not on the final rethrow)", async () => {
      const onRetry = vi.fn();
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("500"), 500));

      const assertion = expect(
        callApi("testOp", fn, { onRetry, maxAttempts: 3 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;

      // maxAttempts=3 means 3 calls to fn, 2 calls to onRetry (not on the last failure)
      expect(onRetry).toHaveBeenCalledTimes(2);
    });

    it("is called with correct attempt number (1-based)", async () => {
      const onRetry = vi.fn();
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("500"), 500));

      const assertion = expect(
        callApi("testOp", fn, { onRetry, maxAttempts: 3 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;

      expect(onRetry).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({ attempt: 1 }),
      );
      expect(onRetry).toHaveBeenNthCalledWith(
        2,
        expect.objectContaining({ attempt: 2 }),
      );
    });

    it("is called with the computed delay (exponential backoff)", async () => {
      const onRetry = vi.fn();
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("500"), 500));

      vi.spyOn(Math, "random").mockReturnValue(0); // Deterministic jitter

      const assertion = expect(
        callApi("testOp", fn, { onRetry, maxAttempts: 3 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;

      // BASE_DELAY = 500, JITTER = 250, random = 0
      // Attempt 1: 500 * 2^0 + 0 = 500
      // Attempt 2: 500 * 2^1 + 0 = 1000
      expect(onRetry).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({ delay: 500 }),
      );
      expect(onRetry).toHaveBeenNthCalledWith(
        2,
        expect.objectContaining({ delay: 1000 }),
      );
    });

    it("receives updated delay when shouldRetry returns a number", async () => {
      const shouldRetry = vi.fn().mockReturnValue(777);
      const onRetry = vi.fn();
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("500"), 500));

      const assertion = expect(
        callApi("testOp", fn, { shouldRetry, onRetry, maxAttempts: 2 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;

      expect(onRetry).toHaveBeenCalledWith(
        expect.objectContaining({ delay: 777 }),
      );
    });
  });

  // ─── Custom maxAttempts ──────────────────────────────────────────────────

  describe("custom maxAttempts", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("maxAttempts: 1 means no retries — throws on first failure", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, new Error("500"), 500));

      const assertion = expect(
        callApi("testOp", fn, { maxAttempts: 1 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("maxAttempts: 5 retries up to 5 times", async () => {
      const fn = vi
        .fn()
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("500"), 500),
        )
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("500"), 500),
        )
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("500"), 500),
        )
        .mockResolvedValueOnce(
          createApiResult(undefined, new Error("500"), 500),
        )
        .mockResolvedValueOnce(createApiResult({ success: true }));

      const promise = callApi("testOp", fn, { maxAttempts: 5 });
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toEqual({ success: true });
      expect(fn).toHaveBeenCalledTimes(5);
    });
  });

  // ─── Error Messages ──────────────────────────────────────────────────────

  describe("error messages", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("includes operation name, message, and code for management-API-shaped errors", async () => {
      const fn = vi.fn().mockResolvedValue(
        createApiResult(
          undefined,
          {
            code: "INTERNAL_ERROR",
            message: "something went wrong",
            errors: [],
          },
          500,
        ),
      );

      const assertion = expect(callApi("startSandbox", fn)).rejects.toThrow(
        "Failed to startSandbox: something went wrong (code: INTERNAL_ERROR)",
      );
      await vi.runAllTimersAsync();
      await assertion;
    });

    it("preserves the original cause message when wrapping a network TypeError", async () => {
      const fn = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));

      const err = await callApi("listFiles", fn, { maxAttempts: 1 }).catch(
        (e) => e,
      );

      expect(err).toBeInstanceOf(HttpError);
      expect((err as HttpError).message).toContain("Failed to fetch");
    });
  });

  // ─── callApi typed error detection ───────────────────────────────────────────

  describe("callApi typed error detection", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("throws HttpError when result.error has management-API error shape", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(
          createApiResult(
            undefined,
            { code: "NOT_FOUND", message: "sandbox not found", errors: [] },
            404,
          ),
        );

      const err = await callApi("getSandbox", fn, { maxAttempts: 1 }).catch(
        (e) => e,
      );

      expect(err).toBeInstanceOf(HttpError);
      expect((err as HttpError).status).toBe(404);
      expect((err as HttpError).message).toBe(
        "Failed to getSandbox: sandbox not found (code: NOT_FOUND)",
      );
    });

    it("throws HttpError when result.error has sandbox-API error shape (numeric code)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(
          createApiResult(
            undefined,
            { code: 404, message: "file not found" },
            404,
          ),
        );

      const err = await callApi("files.read", fn, { maxAttempts: 1 }).catch(
        (e) => e,
      );

      expect(err).toBeInstanceOf(HttpError);
      expect((err as HttpError).status).toBe(404);
      expect((err as HttpError).message).toBe(
        "Failed to files.read: file not found (code: 404)",
      );
    });

    it("HttpError at a retryable status still retries, final throw is HttpError", async () => {
      const apiErrorShape = {
        code: "INTERNAL_ERROR",
        message: "server fault",
        errors: [],
      };
      const fn = vi
        .fn()
        .mockResolvedValueOnce(createApiResult(undefined, apiErrorShape, 500))
        .mockResolvedValueOnce(createApiResult(undefined, apiErrorShape, 500))
        .mockResolvedValueOnce(createApiResult(undefined, apiErrorShape, 500));

      const assertion = expect(
        callApi("startSandbox", fn),
      ).rejects.toBeInstanceOf(HttpError);
      await vi.runAllTimersAsync();
      await assertion;
      expect(fn).toHaveBeenCalledTimes(3);
    });

    it("wraps fetch TypeError into HttpError on the first attempt", async () => {
      const fn = vi.fn().mockRejectedValue(new TypeError("network error"));

      const err = await callApi("testOp", fn, { maxAttempts: 1 }).catch(
        (e) => e,
      );

      expect(err).toBeInstanceOf(HttpError);
      expect((err as HttpError).status).toBe(0);
      expect((err as HttpError).message).toContain("network error");
      expect(fn).toHaveBeenCalledTimes(1);
    });
  });

  // ─── context parameter ─────────────────────────────────────────────────────────

  describe("context parameter", () => {
    it("appends context to formatted message for management-API shape", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(
          createApiResult(
            undefined,
            { code: "NOT_FOUND", message: "not found", errors: [] },
            404,
          ),
        );

      const err = await callApi(
        "files.read",
        fn,
        { maxAttempts: 1 },
        "for sandbox 'abc123'",
      ).catch((e) => e);

      expect((err as HttpError).message).toBe(
        "Failed to files.read for sandbox 'abc123': not found (code: NOT_FOUND)",
      );
    });

    it("appends context to formatted message for sandbox-API shape", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(
          createApiResult(
            undefined,
            { code: 500, message: "exec failed" },
            500,
          ),
        );

      const err = await callApi(
        "execs.create",
        fn,
        { maxAttempts: 1 },
        "for sandbox 'abc123'",
      ).catch((e) => e);

      expect((err as HttpError).message).toBe(
        "Failed to execs.create for sandbox 'abc123': exec failed (code: 500)",
      );
    });

    it("does not include context in message when context is omitted", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(
          createApiResult(
            undefined,
            { code: "BAD_REQUEST", message: "invalid body", errors: [] },
            400,
          ),
        );

      const err = await callApi("createSandbox", fn, {
        maxAttempts: 1,
      }).catch((e) => e);

      expect((err as HttpError).message).toBe(
        "Failed to createSandbox: invalid body (code: BAD_REQUEST)",
      );
      expect((err as HttpError).message).not.toContain("for sandbox");
    });
  });

  // ─── 204 / no-body path ────────────────────────────────────────────────────────────

  describe("204 / no-body path", () => {
    it("returns undefined when data and error are both absent (204 No Content)", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, undefined, 204));

      const result = await callApi("deleteFile", fn);

      expect(result).toBeUndefined();
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("returns undefined when data is absent on a 200 response", async () => {
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, undefined, 200));

      const result = await callApi("deleteFile", fn);

      expect(result).toBeUndefined();
    });

    it("does not call onRetry for a no-body success", async () => {
      const onRetry = vi.fn();
      const fn = vi
        .fn()
        .mockResolvedValue(createApiResult(undefined, undefined, 204));

      await callApi("deleteFile", fn, { onRetry });

      expect(onRetry).not.toHaveBeenCalled();
    });
  });
});

// ─── withRetry ──────────────────────────────────────────────────────────────

describe("withRetry", () => {
  describe("success path", () => {
    it("returns fn's resolved value on first attempt", async () => {
      const fn = vi.fn(async () => "ok");

      const result = await withRetry("op", fn);

      expect(result).toBe("ok");
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("does not call onRetry when fn succeeds", async () => {
      const onRetry = vi.fn();
      const fn = vi.fn(async () => 42);

      await withRetry("op", fn, { onRetry });

      expect(onRetry).not.toHaveBeenCalled();
    });

    it("passes the 1-based attempt number to fn", async () => {
      const seen: number[] = [];
      const fn = vi.fn(async (attempt: number) => {
        seen.push(attempt);
        if (attempt < 3) throw new Error("boom");
        return "ok";
      });

      vi.useFakeTimers();
      const promise = withRetry("op", fn);
      await vi.runAllTimersAsync();
      const result = await promise;
      vi.useRealTimers();

      expect(result).toBe("ok");
      expect(seen).toEqual([1, 2, 3]);
    });
  });

  describe("retry behavior", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("retries on thrown error and returns on first success", async () => {
      const fn = vi
        .fn()
        .mockRejectedValueOnce(new Error("transient"))
        .mockResolvedValueOnce("ok");

      const promise = withRetry("op", fn);
      await vi.runAllTimersAsync();
      const result = await promise;

      expect(result).toBe("ok");
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it("exhausts maxAttempts (default 3) and rethrows the last error", async () => {
      const lastErr = new Error("final failure");
      const fn = vi
        .fn()
        .mockRejectedValueOnce(new Error("first"))
        .mockRejectedValueOnce(new Error("second"))
        .mockRejectedValueOnce(lastErr);

      const assertion = expect(withRetry("op", fn)).rejects.toBe(lastErr);
      await vi.runAllTimersAsync();
      await assertion;

      expect(fn).toHaveBeenCalledTimes(3);
    });

    it("maxAttempts: 1 makes no retries — throws on first failure", async () => {
      const err = new Error("nope");
      const fn = vi.fn().mockRejectedValue(err);

      await expect(withRetry("op", fn, { maxAttempts: 1 })).rejects.toBe(err);
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("calls onRetry once per failed attempt (not on the final rethrow)", async () => {
      const onRetry = vi.fn();
      const fn = vi.fn().mockRejectedValue(new Error("boom"));

      const assertion = expect(
        withRetry("op", fn, { onRetry, maxAttempts: 3 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;

      expect(onRetry).toHaveBeenCalledTimes(2);
    });

    it("default isRetryable returns true so any thrown error retries", async () => {
      // This is the default — what `pushDockerImage` relies on.
      const fn = vi
        .fn()
        .mockRejectedValueOnce(new Error("docker push failed"))
        .mockResolvedValueOnce(undefined);

      const promise = withRetry("snapshots.pushDockerImage", fn);
      await vi.runAllTimersAsync();
      await promise;

      expect(fn).toHaveBeenCalledTimes(2);
    });
  });

  describe("isRetryable option", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("stops retrying when isRetryable returns false", async () => {
      const err = new Error("fatal");
      const fn = vi.fn().mockRejectedValue(err);
      const isRetryable = vi.fn().mockReturnValue(false);

      await expect(
        withRetry("op", fn, undefined, { isRetryable }),
      ).rejects.toBe(err);

      expect(fn).toHaveBeenCalledTimes(1);
      expect(isRetryable).toHaveBeenCalledTimes(1);
      expect(isRetryable).toHaveBeenCalledWith(err);
    });

    it("retries when isRetryable returns true", async () => {
      const fn = vi
        .fn()
        .mockRejectedValueOnce(new Error("transient"))
        .mockResolvedValueOnce("ok");

      const promise = withRetry("op", fn, undefined, {
        isRetryable: () => true,
      });
      await vi.runAllTimersAsync();

      expect(await promise).toBe("ok");
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it("is ignored when shouldRetry is also provided (shouldRetry wins)", async () => {
      const isRetryable = vi.fn().mockReturnValue(false);
      const shouldRetry = vi.fn().mockReturnValue(true);
      const fn = vi
        .fn()
        .mockRejectedValueOnce(new Error("boom"))
        .mockResolvedValueOnce("ok");

      const promise = withRetry("op", fn, { shouldRetry }, { isRetryable });
      await vi.runAllTimersAsync();

      expect(await promise).toBe("ok");
      expect(shouldRetry).toHaveBeenCalledTimes(1);
      expect(isRetryable).not.toHaveBeenCalled();
    });
  });

  describe("shouldRetry override", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("returning false short-circuits the loop", async () => {
      const shouldRetry = vi.fn().mockReturnValue(false);
      const err = new Error("boom");
      const fn = vi.fn().mockRejectedValue(err);

      await expect(
        withRetry("op", fn, { shouldRetry, maxAttempts: 5 }),
      ).rejects.toBe(err);

      expect(fn).toHaveBeenCalledTimes(1);
      expect(shouldRetry).toHaveBeenCalledTimes(1);
    });

    it("returning a number uses it as the custom delay", async () => {
      const shouldRetry = vi.fn().mockReturnValue(2222);
      const onRetry = vi.fn();
      const fn = vi
        .fn()
        .mockRejectedValueOnce(new Error("transient"))
        .mockResolvedValueOnce("ok");

      const promise = withRetry("op", fn, { shouldRetry, onRetry });
      await vi.runAllTimersAsync();
      await promise;

      expect(onRetry).toHaveBeenCalledWith(
        expect.objectContaining({ delay: 2222 }),
      );
    });

    it("receives a RetryContext with undefined status for non-HTTP errors", async () => {
      const shouldRetry = vi.fn().mockReturnValue(false);
      const fn = vi.fn().mockRejectedValue(new Error("plain"));

      await expect(withRetry("myOp", fn, { shouldRetry })).rejects.toThrow();

      const ctx = shouldRetry.mock.calls[0][0] as RetryContext;
      expect(ctx.operation).toBe("myOp");
      expect(ctx.attempt).toBe(1);
      expect(ctx.status).toBeUndefined();
      expect(ctx.error).toBeInstanceOf(Error);
      expect(typeof ctx.delay).toBe("number");
    });

    it("returning true uses the default exponential-backoff delay", async () => {
      const shouldRetry = vi.fn().mockReturnValue(true);
      const onRetry = vi.fn();
      const fn = vi.fn().mockRejectedValue(new Error("boom"));

      vi.spyOn(Math, "random").mockReturnValue(0); // Deterministic jitter

      const assertion = expect(
        withRetry("op", fn, { shouldRetry, onRetry, maxAttempts: 3 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;

      // BASE_DELAY = 500, JITTER = 250, random = 0
      // Attempt 1 → 500, Attempt 2 → 1000
      expect(onRetry).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({ delay: 500 }),
      );
      expect(onRetry).toHaveBeenNthCalledWith(
        2,
        expect.objectContaining({ delay: 1000 }),
      );
    });
  });
});
