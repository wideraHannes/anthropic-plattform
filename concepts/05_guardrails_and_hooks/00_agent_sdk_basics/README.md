# Agent SDK Basics

The Claude Agent SDK is Claude Code packaged as a library: the same agent loop, built-in tools (Read, Edit, Bash, Glob, WebSearch …), context management, subagents, hooks and sessions — programmable from Python or TypeScript. You still host it yourself.

- [`simple_claude_code.py`](simple_claude_code.py) — `query()` with `allowed_tools`, `permission_mode="acceptEdits"`, a system prompt, and streamed `AssistantMessage` / `ResultMessage` events. It edits `utils.py` / `test_utils.py` in this folder.

Note: the SDK talks to the local `claude` CLI and uses its auth and model aliases, not `config.client`.

Docs: <https://code.claude.com/docs/en/agent-sdk/overview>
