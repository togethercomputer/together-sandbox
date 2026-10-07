import type { CreateSandboxExperimental, SandboxInfo } from "together-sandbox";

/**
 * Read `--experimental`: the API's `experimental` object as JSON. It is sent
 * as is; the API validates it.
 */
export function parseExperimental(
  value: string | undefined,
): CreateSandboxExperimental | undefined {
  if (value === undefined) return undefined;

  let parsed: unknown;
  try {
    parsed = JSON.parse(value);
  } catch (error) {
    throw new Error(
      `invalid --experimental: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed))
    throw new Error("invalid --experimental: expected a JSON object");

  return parsed as CreateSandboxExperimental;
}

/**
 * One line per inbound allowlist rule, e.g. `80, 8000-8100 from 10.0.0.0/8
 * (token required)`. Without a policy every port is open; with an empty
 * allowlist none is.
 */
export function formatInboundAllowlist(s: SandboxInfo): string {
  const policy = s.experimental?.network_policy;
  if (!policy) return "<no policy: every port is open>";
  const rules = policy.inbound_allowlist ?? [];
  if (rules.length === 0) return "<empty: every port is closed>";
  return rules
    .map((rule) => {
      const from = rule.from?.length ? rule.from.join(", ") : "*";
      const token = rule.requires_token ? " (token required)" : "";
      return `${rule.ports.join(", ")} from ${from}${token}`;
    })
    .join("\n");
}
