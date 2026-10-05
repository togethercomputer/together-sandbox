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

/** One line per inbound rule, e.g. `80 allow from 10.0.0.0/8`. */
export function formatInboundRules(s: SandboxInfo): string {
  const inbound = s.experimental?.network?.inbound;
  if (!inbound || inbound.length === 0) return "<none>";
  return inbound
    .map((rule) => `${rule.to_port ?? "*"} ${rule.access} from ${rule.from.join(", ")}`)
    .join("\n");
}
