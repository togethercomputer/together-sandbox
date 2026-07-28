// Help-text helpers.
//
// yargs' built-in `.example()` renders a two-column table and hard-wraps the
// command to fit its half of the terminal, which breaks long commands
// mid-token and makes them impossible to copy-paste. These helpers emit the
// examples through `.epilogue()` instead — one comment line, one command line —
// so every command stays intact on a single line.

export interface Example {
  /** What the command does, rendered as a `#` comment above it. */
  describe: string;
  /** The command itself. Use `$0` for the script name, as yargs does. */
  command: string;
}

/**
 * Build an epilogue containing an `Examples:` block, optionally followed by
 * free-form notes.
 */
export function examples(items: Example[], ...notes: string[]): string {
  const block = items
    .map(({ describe, command }) => `  # ${describe}\n  ${command}`)
    .join("\n\n");
  return ["Examples:", block, ...notes].join("\n\n");
}
