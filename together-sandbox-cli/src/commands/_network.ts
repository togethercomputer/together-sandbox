import { readFileSync } from "node:fs";
import type {
  EgressRuleParams,
  IngressRuleParams,
  NetworkPolicyParams,
  SandboxInfo,
} from "together-sandbox";

/** The network policy flags shared by `create` and `run`. */
export interface NetworkPolicyOptions {
  networkPolicy?: string;
  allowIngress?: string[];
  denyIngress?: string[];
  tokenIngress?: string[];
  allowEgress?: string[];
  denyEgress?: string[];
}

const PORT_SPEC = /^(\*|\d+(-\d+)?)$/;

/**
 * Split `TARGET[,PORT]` into its two halves: `api.openai.com,443`,
 * `10.0.0.0/8,8000-9000`, `*,*`. A bare target covers every port.
 *
 * A comma rather than a colon, because `HOST:PORT` reads as an address -- and for
 * an ingress rule that is wrong twice over: the target is the *client*, and the
 * port is the sandbox's, not the client's. It also leaves IPv6 addresses, colons
 * and all, unambiguous.
 */
export function parseTarget(
  value: string,
  flag: string,
): { target: string; toPort?: string } {
  const parts = value.split(",").map((p) => p.trim());
  const [target, port] = parts;
  if (parts.length > 2 || !target || (parts.length === 2 && !PORT_SPEC.test(port)))
    throw new Error(
      `invalid ${flag} "${value}" (expected TARGET or TARGET,PORT, PORT being a port, a range low-high, or *)`,
    );
  // One colon is never an IPv6 address, which has at least two: it is the old
  // HOST:PORT form, which would otherwise be sent on as a host named "host:443".
  if (target.split(":").length === 2) {
    const [host, p] = target.split(":");
    throw new Error(
      `invalid ${flag} "${value}": separate the port with a comma, not a colon (${host},${p})`,
    );
  }
  return { target, toPort: port };
}

/**
 * Read `--network-policy`: inline JSON, or `@path` to a JSON file. Rules may use
 * the SDK's `toPort` or the API's `to_port`, and ports may be numbers.
 */
function readPolicyArg(value: string): NetworkPolicyParams {
  let raw: string;
  try {
    raw = value.startsWith("@") ? readFileSync(value.slice(1), "utf8") : value;
  } catch (error) {
    throw new Error(
      `--network-policy: cannot read ${value.slice(1)}: ${(error as Error).message}`,
    );
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    throw new Error(`--network-policy: invalid JSON: ${(error as Error).message}`);
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed))
    throw new Error(`--network-policy: expected an object with "ingress" and/or "egress"`);

  const { ingress, egress } = parsed as Record<string, unknown>;
  const rules = (key: string, list: unknown) => {
    if (list === undefined) return undefined;
    if (!Array.isArray(list)) throw new Error(`--network-policy: "${key}" must be an array`);
    return list.map((rule: Record<string, unknown>) => {
      const { to_port, toPort, ...rest } = rule ?? {};
      const port = toPort ?? to_port;
      return { ...rest, ...(port !== undefined ? { toPort: String(port) } : {}) };
    });
  };

  return {
    ingress: rules("ingress", ingress) as IngressRuleParams[] | undefined,
    egress: rules("egress", egress) as EgressRuleParams[] | undefined,
  };
}

/**
 * Build the network policy from `--network-policy` and the per-rule flags, which
 * add to it. Undefined when none was given: the sandbox is unrestricted.
 */
export function buildNetworkPolicy(
  argv: NetworkPolicyOptions,
): NetworkPolicyParams | undefined {
  const base = argv.networkPolicy ? readPolicyArg(argv.networkPolicy) : {};
  const ingress: IngressRuleParams[] = [...(base.ingress ?? [])];
  const egress: EgressRuleParams[] = [...(base.egress ?? [])];

  const addIngress = (values: string[] | undefined, flag: string, access: IngressRuleParams["access"]) => {
    for (const value of values ?? []) {
      const { target, toPort } = parseTarget(value, flag);
      ingress.push({ from: target, toPort, access });
    }
  };
  const addEgress = (values: string[] | undefined, flag: string, access: EgressRuleParams["access"]) => {
    for (const value of values ?? []) {
      const { target, toPort } = parseTarget(value, flag);
      egress.push({ to: target, toPort, access });
    }
  };

  addIngress(argv.allowIngress, "--allow-ingress", "allow");
  addIngress(argv.denyIngress, "--deny-ingress", "deny");
  addIngress(argv.tokenIngress, "--token-ingress", "allow_with_token");
  addEgress(argv.allowEgress, "--allow-egress", "allow");
  addEgress(argv.denyEgress, "--deny-egress", "deny");

  if (ingress.length === 0 && egress.length === 0 && !argv.networkPolicy) return undefined;
  return {
    ingress: ingress.length ? ingress : undefined,
    egress: egress.length ? egress : undefined,
  };
}

/**
 * One line per rule, `access target,port` -- the form the flags take -- for
 * `sandboxes get`.
 */
export function formatNetworkPolicy(
  policy: SandboxInfo["networkPolicy"],
  direction: "ingress" | "egress",
): string {
  const rules = policy?.[direction];
  if (!rules?.length) return "<none>";
  return rules
    .map((rule) => {
      const target = "from" in rule ? rule.from : rule.to;
      return `${rule.access} ${target},${rule.to_port ?? "*"}`;
    })
    .join("\n");
}
