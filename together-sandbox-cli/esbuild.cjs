const esbuild = require("esbuild");
const path = require("path");
const fs = require("fs");

const devtoolsStubPlugin = {
  name: "stub-react-devtools",
  setup(build) {
    build.onResolve({ filter: /^react-devtools-core$/ }, () => ({
      path: path.join(__dirname, "build/fakeReactDevtoolsCore.js"),
      namespace: "file",
    }));
  },
};

const isWatch = process.argv.includes("--watch");

// External modules that should NOT be bundled
const externalModules = [
  "node:*",
  "fs",
  "path",
  "os",
  "crypto",
  "readline",
  "child_process",
  "stream",
  "util",
  "events",
  "buffer",
  "url",
  "http",
  "https",
  "net",
  "tls",
  "zlib",
  "string_decoder",
  "@sentry/node",
];

const buildOptions = {
  entryPoints: ["src/main.ts"],
  outfile: "dist/together-sandbox.mjs",
  bundle: true,
  format: "esm",
  platform: "node",
  banner: {
    js: `#!/usr/bin/env node\nimport { createRequire as __createRequire } from "module";\nconst require = __createRequire(import.meta.url);`,
  },
  external: externalModules,
  // Resolve @together-sandbox/sdk to the SDK TypeScript source directly,
  // so it gets inlined into the bundle rather than installed as an npm package.
  alias: {
    "@together-sandbox/sdk": path.resolve(
      __dirname,
      "../together-sandbox-typescript/src/index.ts",
    ),
  },
  plugins: [devtoolsStubPlugin],
};

if (isWatch) {
  const watcher = require("@parcel/watcher");

  async function build() {
    try {
      await esbuild.build(buildOptions);
      console.log("Build succeeded");
    } catch (err) {
      console.error("Build failed:", err.message);
    }
  }

  build();

  watcher.subscribe("src", () => {
    build();
  });
} else {
  esbuild
    .build(buildOptions)
    .then(() => fs.chmodSync(buildOptions.outfile, 0o755))
    .catch(() => process.exit(1));
}
