import path from "path";
import ora from "ora";
import type * as yargs from "yargs";
import { instrumentedFetch } from "../utils/sentry";
import {
  VMTier,
  CodeSandbox,
  SandboxClient,
} from "@codesandbox/sdk";
import {
  API,
  api,
  getDefaultTemplateId,
  getInferredApiKey,
  getInferredRegistryUrl,
  isLocalEnvironment,
  sleep,
  base32Encode,
} from "@together-sandbox/sdk";
import {
  buildDockerImage,
  prepareDockerBuild,
  pushDockerImage,
  dockerLogin,
} from "../utils/docker";
import { randomUUID } from "crypto";

export type BuildCommandArgs = {
  directory: string;
  name?: string;
  path?: string;
  alias?: string;
  ports?: number[];
  ci: boolean;
  fromSandbox?: string;
  vmTier?: api.VmUpdateSpecsRequest["tier"];
  logPath?: string;
};

function stripAnsiCodes(str: string) {
  // Matches ESC [ params … finalChar
  //   \x1B       = ESC
  //   \[         = literal “[”
  //   [0-?]*     = any parameter bytes (digits, ;, ?)
  //   [ -/]*     = any intermediate bytes (space through /)
  //   [@-~]      = final byte ( @ A–Z [ \ ] ^ _ ` a–z { | } ~ )
  const CSI_REGEX = /\x1B\[[0-?]*[ -/]*[@-~]/g;
  return str.replace(CSI_REGEX, "");
}

export const buildCommand: yargs.CommandModule<
  Record<string, never>,
  BuildCommandArgs
> = {
  command: "build <directory>",
  describe:
    "Build an efficient memory snapshot from a directory. This snapshot can be used to create sandboxes quickly.",
  builder: (yargs: yargs.Argv) =>
    yargs
      .option("from-sandbox", {
        describe: "Use and update an existing sandbox as a template",
        type: "string",
      })
      .option("name", {
        describe: "Name for the resulting sandbox that will serve as snapshot",
        type: "string",
      })
      .option("ports", {
        describe: "Ports to wait for to open before creating snapshot",
        type: "number",
        array: true,
      })
      .option("vm-tier", {
        describe: "Base specs to use for the template sandbox",
        type: "string",
        choices: VMTier.All.map((t) => t.name),
      })
      .option("vm-build-tier", {
        describe: "Specs to use for building the template sandbox.",
        type: "string",
        choices: VMTier.All.map((t) => t.name),
      })
      .option("alias", {
        describe:
          "Alias that should point to the created template. Alias namespace defaults to template directory, but you can explicitly pass `namespace@alias`",
        type: "string",
      })
      .option("ci", {
        describe: "CI mode, will exit process if any error occurs",
        default: false,
        type: "boolean",
      })
      .option("log-path", {
        describe: "Relative path to log file, if any",
        type: "string",
      })
      .positional("directory", {
        describe: "Path to the project that we'll create a snapshot from",
        type: "string",
        demandOption: "Path to the project is required",
      })
      .check((argv) => {
        // Validate ports parameter - ensure all values are valid numbers
        if (argv.ports && argv.ports.length > 0) {
          const invalidPortsWithOriginal: string[] = [];

          // Get the original arguments to show what the user actually typed
          const originalArgs = process.argv;
          const portArgIndices: number[] = [];

          // Find all --ports arguments in the original command
          originalArgs.forEach((arg, i) => {
            if (arg === "--ports" && i + 1 < originalArgs.length) {
              portArgIndices.push(i + 1);
            }
          });

          argv.ports.forEach((port, i) => {
            const isInvalid =
              !Number.isInteger(port) ||
              port <= 0 ||
              port > 65535 ||
              !Number.isFinite(port);

            if (isInvalid) {
              // Try to get the original input, fallback to the parsed value
              const originalInput = portArgIndices[i]
                ? originalArgs[portArgIndices[i]]
                : String(port);
              invalidPortsWithOriginal.push(originalInput);
            }
          });

          if (invalidPortsWithOriginal.length > 0) {
            throw new Error(
              `Invalid port value(s): ${invalidPortsWithOriginal.join(
                ", "
              )}. Ports must be integers between 1 and 65535.`
            );
          }
        }
        return true;
      }),

  handler: async (argv) => {
    return betaCodeSandboxBuild(argv);
  },
};


function createAlias(directory: string, alias: string) {
  const aliasParts = alias.split("@");

  if (aliasParts.length > 2) {
    throw new Error(
      `Alias name "${alias}" is invalid, must be in the format of name@tag`
    );
  }

  const namespace =
    aliasParts.length === 2 ? aliasParts[0] : path.basename(directory);
  alias = aliasParts.length === 2 ? aliasParts[1] : alias;

  if (namespace.length > 64 || alias.length > 64) {
    throw new Error(
      `Alias name "${namespace}" or tag "${alias}" is too long, must be 64 characters or less`
    );
  }

  if (!/^[a-zA-Z0-9-_]+$/.test(namespace) || !/^[a-zA-Z0-9-_]+$/.test(alias)) {
    throw new Error(
      `Alias name "${namespace}" or tag "${alias}" is invalid, must only contain upper/lower case letters, numbers, dashes and underscores`
    );
  }

  return {
    namespace,
    alias,
  };
}

/**
 * Build a CodeSandbox Template using Docker for use in gvisor-based sandboxes.
 * @param argv arguments to csb build command
 */
export async function betaCodeSandboxBuild(
  argv: yargs.ArgumentsCamelCase<BuildCommandArgs>
): Promise<void> {
  let dockerFileCleanupFn: (() => Promise<void>) | undefined;
  let client: SandboxClient | undefined;

  try {
    const apiKey = getInferredApiKey();
    const api = new API({ apiKey, instrumentation: instrumentedFetch });
    const sdk = new CodeSandbox(apiKey);
    const sandboxTier = argv.vmTier
      ? VMTier.fromName(argv.vmTier)
      : VMTier.Micro;

    const resolvedDirectory = path.resolve(argv.directory);

    const metaInfo = await api.getMetaInfo();
    const teamId = metaInfo.data?.auth?.team;

    if (!teamId) {
      throw new Error(
        "Failed to fetch team information for the provided CSB_API_KEY. Please ensure your API key is correct and has access to a team."
      );
    }

    const base32EncodedTeamId = base32Encode(teamId);

    const registry = getInferredRegistryUrl();
    const repository = base32EncodedTeamId;
    const imageName = `image-${randomUUID().toLowerCase()}`;
    const tag = "latest";
    const fullImageName = `${registry}/${repository}/${imageName}:${tag}`;

    let architecture = "amd64";
    // For dev environments with arm64 (Apple Silicon), use arm64 architecture
    if (process.arch === "arm64" && isLocalEnvironment()) {
      console.log("Using arm64 architecture for Docker build");
      architecture = "arm64";
    }

    // Prepare Docker Build
    const dockerBuildPrepareSpinner = ora({ stream: process.stdout });
    dockerBuildPrepareSpinner.start("Preparing build environment...");

    let dockerfilePath: string;

    try {
      const result = await prepareDockerBuild(
        resolvedDirectory,
        (output: string) => {
          dockerBuildPrepareSpinner.text = `Preparing build environment: (${output})`;
        }
      );
      dockerFileCleanupFn = result.cleanupFn;
      dockerfilePath = result.dockerfilePath;

      dockerBuildPrepareSpinner.succeed("Build environment ready.");
    } catch (error) {
      dockerBuildPrepareSpinner.fail(
        `Failed to prepare build environment: ${(error as Error).message}`
      );
      throw error;
    }

    // Docker Build
    const dockerBuildSpinner = ora({ stream: process.stdout });
    dockerBuildSpinner.start("Building template docker image...");
    try {
      await buildDockerImage({
        dockerfilePath,
        imageName: fullImageName,
        context: resolvedDirectory,
        architecture,
        onOutput: (output: string) => {
          const cleanOutput = stripAnsiCodes(output);
          dockerBuildSpinner.text = `Building template Docker image: (${cleanOutput})`;
        },
      });
    } catch (error) {
      dockerBuildSpinner.fail(
        `Failed to build template Docker image: ${(error as Error).message}`
      );
      throw error;
    }
    dockerBuildSpinner.succeed("Template Docker image built successfully.");

    // Docker Login
    const dockerLoginSpinner = ora({ stream: process.stdout });
    dockerLoginSpinner.start(
      "Authenticating with CodeSandbox Docker registry..."
    );
    try {
      await dockerLogin({
        registry: registry,
        username: "_token",
        password: apiKey,
        onOutput: (output: string) => {
          const cleanOutput = stripAnsiCodes(output);
          dockerLoginSpinner.text = `Authenticating with Docker registry: (${cleanOutput})`;
        },
      });
      dockerLoginSpinner.succeed("Docker registry authentication successful.");
    } catch (error) {
      dockerLoginSpinner.fail(
        `Failed to authenticate with Docker registry: ${
          (error as Error).message
        }`
      );
      throw error;
    }

    // Push Docker Image
    const imagePushSpinner = ora({ stream: process.stdout });
    imagePushSpinner.start("Pushing template Docker image to CodeSandbox...");
    try {
      await pushDockerImage(fullImageName, (output: string) => {
        const cleanOutput = stripAnsiCodes(output);
        imagePushSpinner.text = `Pushing template Docker image to CodeSandbox: (${cleanOutput})`;
      });
    } catch (error) {
      imagePushSpinner.fail(
        `Failed to push template Docker image: ${(error as Error).message}`
      );
      throw error;
    }
    imagePushSpinner.succeed("Template Docker image pushed to CodeSandbox.");

    const templateCreateSpinner = ora({ stream: process.stdout });
    templateCreateSpinner.start("Creating template with Docker image...");
    // Create Template with Docker Image
    const templateData = await api.createTemplate({
      forkOf: argv.fromSandbox || getDefaultTemplateId(api.getClient()),
      title: argv.name,
      // We filter out sdk-templates on the dashboard
      tags: ["sdk-template"],
      // @ts-ignore
      image: {
        registry: registry,
        repository: repository,
        name: imageName,
        tag: "latest",
        architecture: architecture,
      },
    });
    templateCreateSpinner.succeed("Template created with Docker image.");

    // Create a memory snapshot from the template sandboxes
    const templateBuildSpinner = ora({ stream: process.stdout });
    templateBuildSpinner.start("Preparing template snapshot...");

    const sandboxId = templateData.sandboxes[0].id;
    try {
      templateBuildSpinner.text =
        "Preparing template snapshot: Starting sandbox to create snapshot...";
      const sandbox = await sdk.sandboxes.resume(sandboxId);

      templateBuildSpinner.text =
        "Preparing template snapshot: Connecting to sandbox...";
      client = await sandbox.connect();

      if (argv.ports && argv.ports.length > 0) {
        templateBuildSpinner.text = `Preparing template snapshot: Waiting for ports ${argv.ports.join(
          ", "
        )} to be ready...`;
        await Promise.all(
          argv.ports.map(async (port) => {
            if (!client)
              throw new Error("Failed to connect to sandbox to wait for ports");
            const portInfo = await client.ports.waitForPort(port, {
              timeoutMs: 30_000,
            });
          })
        );
      } else {
        templateBuildSpinner.text = `Preparing template snapshot: No ports specified, waiting 0 seconds for tasks to run...`;
        await sleep(10000);
      }

      templateBuildSpinner.text =
        "Preparing template snapshot: Sandbox is ready. Creating snapshot...";
      // TODO: Change back to hibernate once we fix hibernate resume with nydus
      // await sdk.sandboxes.hibernate(sandboxId);
      await sdk.sandboxes.shutdown(sandboxId);

      templateBuildSpinner.succeed("Template snapshot created.");
    } catch (error) {
      templateBuildSpinner.text =
        "Preparing template snapshot: Failed to create snapshot. Cleaning up...";
      await sdk.sandboxes.shutdown(sandboxId);
      templateBuildSpinner.fail(
        `Failed to create template reference and example: ${
          (error as Error).message
        }`
      );
      throw error;
    }

    // Create alias if needed and output final instructions
    const templateFinaliseSpinner = ora({ stream: process.stdout });
    templateFinaliseSpinner.start(
      `\n\nCreating template reference and example...`
    );
    let referenceString;
    let id;

    // Create alias if needed
    if (argv.alias) {
      const alias = createAlias(resolvedDirectory, argv.alias);
      await api.assignVmTagAlias(alias.namespace, alias.alias, {
        tag_id: templateData.tag,
      });

      id = `${alias.namespace}@${alias.alias}`;
      referenceString = `Alias ${id} now referencing: ${templateData.tag}`;
    } else {
      id = templateData.tag;
      referenceString = `Template created with tag: ${templateData.tag}`;
    }

    templateFinaliseSpinner.succeed(`${referenceString}\n\n
  Create sandbox from template using

  SDK:

    sdk.sandboxes.create({
      id: "${id}"
    })

  CLI:

    csb sandboxes fork ${id}\n`);

    process.exit(0);
  } catch (error) {
    console.error(error);
    process.exit(1);
  } finally {
    // Cleanup temporary Dockerfile if created
    if (dockerFileCleanupFn) {
      await dockerFileCleanupFn();
    }
    if (client) {
      await client.disconnect();
      client.dispose();
      client = undefined;
    }
  }
}
