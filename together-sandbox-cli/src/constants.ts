/**
 * Tag stamped on every sandbox and snapshot this CLI creates, so resources can
 * be attributed to it rather than to a direct SDK caller.
 */
export const CLIENT_TAG_KEY = "client";
export const CLIENT_TAG_VALUE = "together-sandbox-cli";

/**
 * Merge the client tag into caller-supplied tags.
 *
 * A tag the user set explicitly wins — they may be re-tagging deliberately, and
 * silently overriding their input would be worse than losing the attribution.
 */
export function withClientTag(
  tags?: Record<string, string>,
): Record<string, string> {
  return { [CLIENT_TAG_KEY]: CLIENT_TAG_VALUE, ...tags };
}
