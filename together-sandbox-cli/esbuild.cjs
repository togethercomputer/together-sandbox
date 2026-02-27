const esbuild = require("esbuild");
const path = require("path");
const fs = require("fs");

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
  entryPoints: ["src/main.tsx"],
  outfile: "dist/together-sandbox.mjs",
  bundle: true,
  format: "esm",
  platform: "node",
  banner: {
    js: `#!/usr/bin/env node\n\nimport { createRequire } from "module";\nconst require = createRequire(import.meta.url);\n`,
  },
  // React, Ink, and react-query are bundled to avoid version conflicts
  external: [
    ...externalModules.filter(
      (mod) =>
        mod !== "react" &&
        mod !== "ink" &&
        mod !== "@tanstack/react-query"
    ),
    "@together-sandbox/sdk",
    "react-devtools-core",
  ],
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
  esbuild.build(buildOptions).catch(() => process.exit(1));
}
