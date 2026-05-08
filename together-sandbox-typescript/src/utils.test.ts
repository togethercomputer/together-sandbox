import { describe, it, expect, vi, beforeEach } from "vitest";
import { callApi, sleep, RETRYABLE_STATUS_CODES } from "./utils.js";
import { ApiError, SandboxError } from "./errors.js";
import type { RetryContext } from "./types.js";

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

    it("stops and rethrows after maxAttempts on TypeError", async () => {
      const fn = vi.fn().mockRejectedValue(new TypeError("network error"));

      const assertion = expect(
        callApi("testOp", fn, { maxAttempts: 2 }),
      ).rejects.toThrow();
      await vi.runAllTimersAsync();
      await assertion;
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
      expect(ctx).toHaveProperty("error");
      expect(ctx).toHaveProperty("delay");
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

    it("includes operation name, message, and code for ApiError-shaped errors", async () => {
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

    it("re-throws TypeError for network errors with its original message", async () => {
      const fn = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));

      await expect(
        callApi("listFiles", fn, { maxAttempts: 1 }),
      ).rejects.toThrow("Failed to fetch");
    });
  });

  // ─── ApiError and SandboxError classes ───────────────────────────────────────

  describe("ApiError class", () => {
    it("is instanceof Error and instanceof ApiError", () => {
      const err = new ApiError("something failed", "NOT_FOUND", 404, []);
      expect(err).toBeInstanceOf(Error);
      expect(err).toBeInstanceOf(ApiError);
    });

    it("sets name to 'ApiError'", () => {
      const err = new ApiError("msg", "ERR", 400, []);
      expect(err.name).toBe("ApiError");
    });

    it("exposes message, code, status, and errors", () => {
      const errors = [
        { parameter: "id", code: "REQUIRED", message: "id is required" },
      ];
      const err = new ApiError("bad input", "BAD_REQUEST", 400, errors);
      expect(err.message).toBe("bad input");
      expect(err.code).toBe("BAD_REQUEST");
      expect(err.status).toBe(400);
      expect(err.errors).toEqual(errors);
    });
  });

  describe("SandboxError class", () => {
    it("is instanceof Error and instanceof SandboxError", () => {
      const err = new SandboxError("exec failed", 500, 500);
      expect(err).toBeInstanceOf(Error);
      expect(err).toBeInstanceOf(SandboxError);
    });

    it("sets name to 'SandboxError'", () => {
      const err = new SandboxError("msg", 404, 404);
      expect(err.name).toBe("SandboxError");
    });

    it("exposes message, numeric code, and status", () => {
      const err = new SandboxError("file not found", 404, 404);
      expect(err.message).toBe("file not found");
      expect(err.code).toBe(404);
      expect(err.status).toBe(404);
    });

    it("code is a number, not a string", () => {
      const err = new SandboxError("err", 500, 500);
      expect(typeof err.code).toBe("number");
    });
  });

  // ─── callApi typed error detection ───────────────────────────────────────────

  describe("callApi typed error detection", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    it("throws ApiError when result.error has management-API error shape", async () => {
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

      expect(err).toBeInstanceOf(ApiError);
      expect((err as ApiError).code).toBe("NOT_FOUND");
      expect((err as ApiError).status).toBe(404);
      expect((err as ApiError).message).toBe(
        "Failed to getSandbox: sandbox not found (code: NOT_FOUND)",
      );
      expect((err as ApiError).errors).toEqual([]);
    });

    it("throws SandboxError when result.error has sandbox-API error shape (numeric code)", async () => {
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

      expect(err).toBeInstanceOf(SandboxError);
      expect((err as SandboxError).code).toBe(404);
      expect((err as SandboxError).status).toBe(404);
      expect((err as SandboxError).message).toBe(
        "Failed to files.read: file not found (code: 404)",
      );
    });

    it("ApiError at a retryable status still retries, final throw is ApiError", async () => {
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
      ).rejects.toBeInstanceOf(ApiError);
      await vi.runAllTimersAsync();
      await assertion;
      expect(fn).toHaveBeenCalledTimes(3);
    });

    it("re-throws TypeError as TypeError (not wrapped in ApiError or SandboxError)", async () => {
      const fn = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));

      const err = await callApi("testOp", fn, { maxAttempts: 1 }).catch(
        (e) => e,
      );

      expect(err).toBeInstanceOf(TypeError);
      expect(err.message).toBe("Failed to fetch");
    });
  });

  // ─── context parameter ─────────────────────────────────────────────────────────

  describe("context parameter", () => {
    it("appends context to ApiError message when provided", async () => {
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

      expect((err as ApiError).message).toBe(
        "Failed to files.read for sandbox 'abc123': not found (code: NOT_FOUND)",
      );
    });

    it("appends context to SandboxError message when provided", async () => {
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

      expect((err as SandboxError).message).toBe(
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

      expect((err as ApiError).message).toBe(
        "Failed to createSandbox: invalid body (code: BAD_REQUEST)",
      );
      expect((err as ApiError).message).not.toContain("for sandbox");
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
