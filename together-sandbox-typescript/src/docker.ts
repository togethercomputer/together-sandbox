import { promises as fs } from "fs";
import path from "path";
import { writeFile, mkdtemp, rm } from "fs/promises";
import { spawn } from "child_process";
import { tmpdir } from "os";

export async function isDockerAvailable(): Promise<boolean> {
  return new Promise((resolve) => {
    const process = spawn("docker", ["--version"]);
    process.on("close", (code) => {
      resolve(code === 0);
    });
    process.on("error", () => {
      resolve(false);
    });
  });
}

export async function findDockerfile(
  templateDirectory: string,
): Promise<{ exists: boolean; path: string | null }> {
  const dockerfilePath = path.join(templateDirectory, "Dockerfile");
  try {
    await fs.access(dockerfilePath);
    return { exists: true, path: dockerfilePath };
  } catch {
    return { exists: false, path: null };
  }
}

export async function createImageDockerfile(
  image: string,
): Promise<{ dockerfilePath: string; tmpDir: string }> {
  // Create a temporary directory for the Dockerfile
  const tmpDir = await mkdtemp(path.join(tmpdir(), "csb-docker-"));
  const tmpDockerfilePath = path.join(tmpDir, "Dockerfile");

  const dockerfileContent = `FROM ${image}\n`;

  await writeFile(tmpDockerfilePath, dockerfileContent);

  return { dockerfilePath: tmpDockerfilePath, tmpDir };
}

export async function createTemporaryDockerfile(): Promise<string> {
  // Create a temporary directory for the Dockerfile
  const result = await createImageDockerfile("node:24");
  return result.dockerfilePath;
}

export type DockerBuildOptions = {
  dockerfilePath: string;
  imageName: string;
  context: string;
  architecture?: string;
  onOutput?: (output: string) => void;
};

export async function buildDockerImage(
  options: DockerBuildOptions,
): Promise<void> {
  const {
    dockerfilePath,
    imageName,
    context,
    architecture = "amd64",
    onOutput = () => {},
  } = options;

  await new Promise<void>((resolve, reject) => {
    const dockerProcess = spawn(
      "docker",
      [
        "build",
        "--platform",
        `linux/${architecture}`,
        "--progress=plain",
        "-f",
        dockerfilePath,
        "-t",
        imageName,
        context,
      ],
      {
        stdio: ["inherit", "pipe", "pipe"],
      },
    );

    let outputBuffer = "";

    dockerProcess.stdout?.on("data", (data) => {
      const output = data.toString();
      outputBuffer += output;
      // Update spinner with latest output line
      const lines = output.trim().split("\n");
      const lastLine = lines[lines.length - 1];
      if (lastLine) {
        onOutput(lastLine);
      }
    });

    dockerProcess.stderr?.on("data", (data) => {
      const output = data.toString();
      outputBuffer += output;
      // Print stderr to console as well
      const lines = output.trim().split("\n");
      const lastLine = lines[lines.length - 1];
      if (lastLine) {
        onOutput(lastLine);
      }
    });

    dockerProcess.on("close", (code) => {
      if (code === 0) {
        onOutput(`Docker image built successfully: ${imageName}`);
        resolve();
      } else {
        reject(
          new Error(
            `Docker build failed with exit code ${code}\n${outputBuffer}`,
          ),
        );
      }
    });

    dockerProcess.on("error", (error) => {
      reject(`Docker build failed: ${error.message}`);
    });
  });
}

export type DockerLoginOptions = {
  registry?: string;
  username: string;
  password: string;
  onOutput?: (output: string) => void;
};

export async function dockerLogin(options: DockerLoginOptions): Promise<void> {
  const { registry, username, password, onOutput = () => {} } = options;

  await new Promise<void>((resolve, reject) => {
    const args = ["login"];

    if (registry) {
      args.push(registry);
    }

    args.push("--username", username, "--password-stdin");

    const loginProcess = spawn("docker", args, {
      stdio: ["pipe", "pipe", "pipe"],
    });

    // Write password to stdin
    loginProcess.stdin?.write(password);
    loginProcess.stdin?.end();

    let outputBuffer = "";

    loginProcess.stdout?.on("data", (data) => {
      const output = data.toString();
      outputBuffer += output;
      const lines = output.trim().split("\n");
      const lastLine = lines[lines.length - 1];
      if (lastLine) {
        onOutput(lastLine);
      }
    });

    loginProcess.stderr?.on("data", (data) => {
      const output = data.toString();
      outputBuffer += output;
      const lines = output.trim().split("\n");
      const lastLine = lines[lines.length - 1];
      if (lastLine) {
        onOutput(lastLine);
      }
    });

    loginProcess.on("close", (code) => {
      if (code === 0) {
        onOutput(`Docker login successful${registry ? ` to ${registry}` : ""}`);
        resolve();
      } else {
        reject(
          new Error(
            `Docker login failed with exit code ${code}\n${outputBuffer}`,
          ),
        );
      }
    });

    loginProcess.on("error", (error) => {
      reject(new Error(`Docker login failed: ${error.message}`));
    });
  });
}

export async function pushDockerImage(
  imageName: string,
  onOutput?: (output: string) => void,
): Promise<void> {
  onOutput = onOutput || (() => {});

  await new Promise<void>((resolve, reject) => {
    const pushProcess = spawn("docker", ["push", imageName], {
      stdio: ["inherit", "pipe", "pipe"],
    });

    let outputBuffer = "";

    pushProcess.stdout?.on("data", (data) => {
      const output = data.toString();
      outputBuffer += output;
      // Update spinner with latest output line
      const lines = output.trim().split("\n");
      const lastLine = lines[lines.length - 1];
      if (lastLine) {
        onOutput(lastLine);
      }
    });

    pushProcess.stderr?.on("data", (data) => {
      const output = data.toString();
      outputBuffer += output;
      // Print stderr to console as well
      const lines = output.trim().split("\n");
      const lastLine = lines[lines.length - 1];
      if (lastLine) {
        onOutput(lastLine);
      }
    });

    pushProcess.on("close", (code) => {
      if (code === 0) {
        onOutput(`Docker image pushed successfully: ${imageName}`);
        resolve();
      } else {
        reject(
          new Error(
            `Docker push failed with exit code ${code}\n${outputBuffer}`,
          ),
        );
      }
    });

    pushProcess.on("error", (error) => {
      reject(`Docker push failed: ${error.message}`);
    });
  });
}

/**
 * Prepares the Docker build environment for building a Docker image for a Together Sandbox snapshot.
 *
 * @param directory Directory where together-sandbox build is called on
 * @param onOutput Optional output callback for logging
 * @returns A cleanup function to remove temporary Dockerfile if created
 */
export async function prepareDockerBuild(
  directory: string,
  onOutput?: (output: string) => void,
): Promise<{ dockerfilePath: string; cleanupFn: () => Promise<void> }> {
  onOutput = onOutput || (() => {});

  const dockerAvailable = await isDockerAvailable();
  if (!dockerAvailable) {
    console.error(
      "Docker is not available. Please install Docker to use beta build mode.",
    );
    process.exit(1);
  }

  onOutput("Checking for Dockerfile...");

  const dockerfileInfo = await findDockerfile(directory);
  let dockerfilePath: string;
  let needsCleanup = false;
  let tmpDockerfilePath: string | null = null;

  if (!dockerfileInfo.exists) {
    onOutput("Creating temporary Dockerfile...");
    tmpDockerfilePath = await createTemporaryDockerfile();
    dockerfilePath = tmpDockerfilePath;
    needsCleanup = true;
  } else {
    dockerfilePath = dockerfileInfo.path!;
  }

  return {
    dockerfilePath,
    cleanupFn: async () => {
      if (needsCleanup && tmpDockerfilePath) {
        const tmpDir = path.dirname(tmpDockerfilePath);
        await rm(tmpDir, { recursive: true, force: true });
      }
    },
  };
}
