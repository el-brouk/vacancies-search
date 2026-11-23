---
name: simplify
description: >-
  Simplify and shorten code using KISS and YAGNI while following Codex coding
  rules. Use when the user asks to simplify, reduce complexity, trim code,
  remove over-engineering, or invokes @simplify.
disable-model-invocation: true
---

# Simplify

Simplify and shorten existing code. Prefer deletion and flattening over new
abstractions. Preserve behavior unless the user explicitly allows otherwise.

## Principles

### KISS

- Prefer the most straightforward solution that works.
- Flatten nested conditionals, ternaries, and callbacks when clearer.
- Prefer clear names and linear control flow over clever tricks.
- Do not add helpers, wrappers, or layers that do not earn their complexity.

### YAGNI

- Remove unused code, dead branches, unreachable paths, and speculative APIs.
- Do not add features, options, configs, or generalizations "for later".
- Do not introduce abstractions until there are real repeated use cases.
- Prefer deleting an unused abstraction to polishing it.

### Cursor coding rules

- Change only what is required for the simplification. Minimal diff.
- Match existing project style, naming, and patterns.
- Do not add comments, docstrings, or markdown docs unless they are necessary
  to preserve non-obvious intent or the user asks for them.
- Do not create extra files, drive-by refactors, or unrelated cleanups.
- Do not expand scope into new features, renames across the codebase, or
  architectural rewrites unless the user asks.
- Keep answers and change summaries concise.

## Workflow

1. Identify the target scope (selection, file, or paths the user named).
2. Understand current behavior before editing. Skim callers and tests if needed.
3. Simplify in this order:
   - Delete dead / unused / duplicate code
   - Inline trivial one-off helpers
   - Collapse redundant branches and temporary variables
   - Replace over-abstracted code with direct logic
   - Shorten verbose code without harming readability
4. Preserve public APIs and observable behavior unless told otherwise.
5. Summarize what became simpler and what was removed. Do not restate the whole diff.

## Checklist

Before finishing:

- [ ] Behavior is unchanged (or intentional changes are explicitly called out)
- [ ] No speculative flexibility or unused parameters remain
- [ ] No new abstraction was added unless it removed more complexity than it added
- [ ] Diff is minimal and scoped to the request
- [ ] No leftover comments like `// removed` or no-op shims

## Anti-patterns

- Rewriting working code in a new style without reducing complexity
- "Cleaning up" unrelated files
- Replacing simple logic with a pattern/framework
- Adding fallbacks, options, or configurability that nothing needs yet
- Shortening code until it becomes cryptic
