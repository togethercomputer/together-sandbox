export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

export function base32Encode(
  input: string,
  lowercase: boolean = true,
  removePadding: boolean = true
): string {
  const buffer = Buffer.from(input, "utf-8");
  let bits = 0;
  let value = 0;
  let output = "";

  for (let i = 0; i < buffer.length; i++) {
    value = (value << 8) | buffer[i]!;
    bits += 8;
    while (bits >= 5) {
      output += BASE32_ALPHABET[(value >>> (bits - 5)) & 31];
      bits -= 5;
    }
  }

  if (bits > 0) {
    output += BASE32_ALPHABET[(value << (5 - bits)) & 31];
  }

  while (output.length % 8 !== 0) {
    output += "=";
  }

  if (removePadding) {
    output = output.replace(/=+$/, "");
  }

  if (lowercase) {
    output = output.toLowerCase();
  }

  return output;
}

/**
 * Exit once stdout and stderr have flushed.
 *
 * On macOS (and anywhere else stdout is an async pipe) `process.exit()` drops
 * whatever is still queued, so piped output is cut off at the pipe buffer
 * size (64 KB). An empty write is queued behind any pending data, so its
 * callback fires once everything before it has been handed to the OS.
 */
export async function exit(code: number): Promise<never> {
  await Promise.all(
    [process.stdout, process.stderr].map(
      (stream) =>
        new Promise<void>((resolve) => {
          if (stream.destroyed || !stream.writable) return resolve();
          // The reader may have gone away (`| head`): an EPIPE here would
          // otherwise surface as an uncaught 'error' event.
          stream.on("error", () => resolve());
          stream.write("", () => resolve());
        }),
    ),
  );
  process.exit(code);
}
