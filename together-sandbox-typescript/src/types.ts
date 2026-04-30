import type {
  Sandbox as SandboxModel,
  CreateSandboxData,
} from "./api-clients/api/types.gen.js";

/**
 * Converts snake_case property names to camelCase.
 */
type SnakeToCamelCase<S extends string> =
  S extends `${infer Head}_${infer Tail}`
    ? `${Head}${Capitalize<SnakeToCamelCase<Tail>>}`
    : S;

/**
 * Converts all top-level property keys from snake_case to camelCase.
 * Shallow transformation — only affects direct keys, not nested objects.
 */
export type CamelCasedProperties<T extends object> = {
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
