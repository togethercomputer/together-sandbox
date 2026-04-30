import type { CamelCasedProperties } from "./types";

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Runtime mapper that converts snake_case object keys to camelCase.
 */
export function camelCaseKeys<T extends Record<string, unknown>>(
  obj: T,
): CamelCasedProperties<T> {
  return Object.fromEntries(
    Object.entries(obj).map(([key, value]) => [
      key.replace(/_+([a-z])/g, (match, char, offset: number) =>
        offset === 0 ? match : char.toUpperCase(),
      ),
      value,
    ]),
  ) as CamelCasedProperties<T>;
}
