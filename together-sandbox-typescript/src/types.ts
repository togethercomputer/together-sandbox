import type {
  Sandbox as SandboxModel,
  CreateSandboxData,
} from "./api-clients/api/types.gen.js";

/**
 * Converts snake_case property names to camelCase.
 * Guards against leading underscores (e.g., `_type`, `_id`) to preserve them as-is.
 */
type SnakeToCamelCase<S extends string> =
  S extends `${infer Head}_${infer Tail}`
    ? Head extends ""
      ? S // preserve "_type", "_id", etc.
      : `${Head}${Capitalize<SnakeToCamelCase<Tail>>}`
    : S;

/**
 * Converts all top-level property keys from snake_case to camelCase.
 * Shallow transformation — only affects direct keys, not nested objects.
 */
type CamelCasedProperties<T extends object> = {
  [K in keyof T as SnakeToCamelCase<K & string>]: T[K];
};

/**
 * Public camelCase version of the management API Sandbox response type.
 */
export type SandboxInfo = CamelCasedProperties<SandboxModel>;

/**
 * Public camelCase version of the create sandbox request parameters.
 */
export type CreateSandboxParams = CamelCasedProperties<
  CreateSandboxData["body"]
>;

/**
 * Runtime mapper that converts snake_case object keys to camelCase.
 * Guards against leading underscores to preserve special fields like `_type`.
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
