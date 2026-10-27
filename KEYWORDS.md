# Keywords — Anthropic's vocabulary for agentic systems

One line per term. Grouped the way Anthropic talks about them. **Where** points to the concept (`NN`) or project (`P0N`) in this repo; `—` = not covered here yet.

## Architecture: workflows vs agents

| Term | Meaning | Where |
|---|---|---|
| **Augmented LLM** | The building block: a model plus retrieval, tools and memory. | [04](concepts/04_workflows_and_multi_agent/) |
| **Workflow** | LLM calls orchestrated by *predefined code paths*. Predictable, testable. | [04](concepts/04_workflows_and_multi_agent/) |
| **Agent** | LLM *dynamically directs its own process* and tool use in a loop until done. | [02](concepts/02_agentic_loop/) |
| **"Start simple"** | Single call → workflow → agent → multi-agent; add complexity only when it measurably helps. | [04](concepts/04_workflows_and_multi_agent/) |
| **Prompt chaining** | Fixed sequence of calls, each consuming the previous output, optional gates between. | [04](concepts/04_workflows_and_multi_agent/) |
| **Routing** | Classify the input, dispatch to a specialised prompt/model/queue. | [P01](projects/01_ticket_routing/) |
| **Parallelization** | *Sectioning* (independent subtasks at once) or *voting* (same task several times). | [P03](projects/03_research_multi_agent/) |
| **Orchestrator–workers** | Lead LLM decides subtasks at runtime, delegates to workers, merges results. | [P03](projects/03_research_multi_agent/) |
| **Evaluator–optimizer** | One call generates, another critiques against criteria, loop until good. | [04](concepts/04_workflows_and_multi_agent/) |
| **Hub-and-spoke** | One coordinator (hub) talks to all subagents (spokes); spokes never talk to each other. | [04/01](concepts/04_workflows_and_multi_agent/01_hub_and_spoke/) |
| **Coordinator / lead agent** | The hub: decomposes, dispatches, detects gaps, aggregates. Does no work itself. | [04/01](concepts/04_workflows_and_multi_agent/01_hub_and_spoke/) |
| **Subagent** | Worker with its **own fresh context**; knows only what the coordinator passes it. | [04/02](concepts/04_workflows_and_multi_agent/02_subagents_sdk/) |
| **Decomposition breadth** | Split broadly with non-overlapping scopes; narrow splits silently drop coverage. | [04/01](concepts/04_workflows_and_multi_agent/01_hub_and_spoke/) |
| **Fixed pipeline vs dynamic decomposition** | Steps known upfront vs plan emerges during the work. Choose by shape, not size. | [04/03](concepts/04_workflows_and_multi_agent/03_task_decomposition/) |
| **Attention dilution** | Too many items in one context → shallow, inconsistent treatment. Fix: per-item passes + one integration pass. | [04/03](concepts/04_workflows_and_multi_agent/03_task_decomposition/) |

## The loop & build surfaces

| Term | Meaning | Where |
|---|---|---|
| **Agentic loop** | `while stop_reason == "tool_use"`: run tools, append results, call again. | [02](concepts/02_agentic_loop/) |
| **`stop_reason`** | `end_turn`, `tool_use`, `max_tokens`, `pause_turn`, `refusal`: check it every turn. | [02](concepts/02_agentic_loop/) |
| **`tool_use` / `tool_result`** | Model's call block / your answer block, paired by `tool_use_id`. | [02](concepts/02_agentic_loop/) |
| **Parallel tool use** | Several `tool_use` blocks in one turn; return all results in one user message. | [02](concepts/02_agentic_loop/) |
| **Messages API** | `POST /v1/messages`, stateless; you resend the full history. | [02](concepts/02_agentic_loop/) |
| **Tool Runner** | SDK helper (`client.beta.messages.tool_runner` + `@beta_tool`) that runs the loop for your tools. | [02](concepts/02_agentic_loop/) |
| **Claude Agent SDK** | Claude Code's harness as a library: built-in tools, subagents, hooks, sessions. You host it. | [05/00](concepts/05_guardrails_and_hooks/00_agent_sdk_basics/) |
| **Claude Managed Agents** | Anthropic hosts the loop *and* a per-session sandbox; versioned agent configs. | [02](concepts/02_agentic_loop/) |
| **Harness** | Everything around the model: loop, tools, context management, permissions. | [02](concepts/02_agentic_loop/) |

## Tools (Agent–Computer Interface)

| Term | Meaning | Where |
|---|---|---|
| **ACI (agent–computer interface)** | Tools are the agent's UI; design them as carefully as a human UI. | [03](concepts/03_tool_design/) |
| **Tool description** | The routing signal: purpose, inputs, examples, limits, boundaries to sibling tools. | [03/01](concepts/03_tool_design/01_schema_design/) |
| **Misrouting** | Model picks the wrong tool because descriptions overlap or are vague. | [03/01](concepts/03_tool_design/01_schema_design/) |
| **Structured error response** | `errorCategory` (transient/validation/business/permission) + `isRetryable` + description. | [03/02](concepts/03_tool_design/02_structured_errors/) |
| **`is_error`** | Flag on a `tool_result` that tells the model the call failed, so it can recover. | [02](concepts/02_agentic_loop/) |
| **`tool_choice`** | `auto` / `any` / `tool` / `none`: how strongly to force tool use. | [03/03](concepts/03_tool_design/03_tool_choice/) |
| **Strict tool use** | `strict: true`: tool inputs are guaranteed to match the schema. | [03](concepts/03_tool_design/) |
| **Structured outputs** | `output_config.format` JSON schema: the response is guaranteed to match it. | [03](concepts/03_tool_design/) |
| **Least privilege / scoped tools** | Each role gets only the 4–5 tools it needs; constrained tools over generic ones. | [03/03](concepts/03_tool_design/03_tool_choice/) |
| **MCP (Model Context Protocol)** | Open protocol to expose tools/resources to any agent. | [03](concepts/03_tool_design/) |
| **MCP connector** | Call remote MCP servers directly from the Messages API (`mcp_servers` + `mcp_toolset`). | [03](concepts/03_tool_design/) |
| **Server tools** | Run on Anthropic's side: web search, web fetch, code execution. | — |
| **Tool search** | Load tool definitions on demand (`defer_loading`) to scale to many tools. | — |
| **Programmatic tool calling** | Claude calls your tools from inside code execution, saving round trips and tokens. | — |
| **Agent Skills** | Folders of instructions/scripts loaded via *progressive disclosure*. | — |

## Guardrails & control

| Term | Meaning | Where |
|---|---|---|
| **"Prompts are probabilistic, code is deterministic"** | Central rule: costly failures get code-level enforcement. | [05](concepts/05_guardrails_and_hooks/) |
| **Determinism ladder** | Prompt → schema → gate → hook → human: pick the rung by cost of failure. | [05](concepts/05_guardrails_and_hooks/) |
| **Prerequisite gate** | Early-return check in a tool handler ("BLOCKED: verify first"). | [05/01](concepts/05_guardrails_and_hooks/01_prerequisite_gates_and_handoff/), [P02](projects/02_support_agent/) |
| **Hooks (`PreToolUse` / `PostToolUse`)** | Deterministic callbacks: policy *before* a tool runs, data shaping *after*. | [05/02](concepts/05_guardrails_and_hooks/02_sdk_hooks/) |
| **Structured handoff** | Validated object for a human (customer, summary, root cause, amount, action). | [P02](projects/02_support_agent/) |
| **Human in the loop** | Human approval for irreversible or high-value actions. | [05](concepts/05_guardrails_and_hooks/) |
| **Prompt injection** | Instructions hidden in tool results/data; treat them as data, gate the actions. | [P02](projects/02_support_agent/) |
| **`permission_mode`** | Agent SDK setting for which tool calls auto-approve. | [05/00](concepts/05_guardrails_and_hooks/00_agent_sdk_basics/) |

## Context engineering

| Term | Meaning | Where |
|---|---|---|
| **Context engineering** | Curating the *smallest set of high-signal tokens* at every turn, not only the first prompt. | [06](concepts/06_context_engineering/) |
| **Context window** | Everything the model sees: system, tools, history, tool results, documents. | [06](concepts/06_context_engineering/) |
| **Context rot** | Recall and focus degrade as the context grows. Context is a finite "attention budget". | [06](concepts/06_context_engineering/) |
| **Right altitude (system prompt)** | Between brittle if/else rules and vague guidance. | [06](concepts/06_context_engineering/) |
| **Just-in-time retrieval** | Keep references (IDs, paths), load details via tools when needed. | [P03](projects/03_research_multi_agent/) |
| **Compaction** | Summarise old history near the limit and continue with the summary. | [06](concepts/06_context_engineering/) |
| **Context editing** | Clear stale tool results / thinking blocks from the history. | [06](concepts/06_context_engineering/) |
| **Memory tool / structured note-taking** | Agent writes state to files outside the window and reloads it later. | [06](concepts/06_context_engineering/) |
| **Progressive disclosure** | Show the model a short summary first, details only on demand. | — |
| **Resume / fork / fresh start** | Continue a session, branch from it, or restart with a curated summary. | [06/01](concepts/06_context_engineering/01_session_state/) |
| **Stale context** | Old tool results that no longer match reality; they silently bias reasoning. | [06/01](concepts/06_context_engineering/01_session_state/) |

## Evals

| Term | Meaning | Where |
|---|---|---|
| **Success criteria** | Specific, measurable targets (accuracy, latency, cost, safety) defined *before* building. | [07](concepts/07_evals/) |
| **Eval dataset** | Fixed inputs from real traffic plus edge and adversarial cases. | [P01](projects/01_ticket_routing/) |
| **Code-based grader** | Exact match, regex, schema or state check: cheap and deterministic. | [07](concepts/07_evals/) |
| **LLM-as-judge** | Model grades against a rubric; reason first, then verdict. | [07](concepts/07_evals/) |
| **Outcome vs trajectory** | Grade the final state *and* the path (right tools, right order). | [P02](projects/02_support_agent/) |
| **Transcript** | Full record of a run; read it to understand *why* a case failed. | [07](concepts/07_evals/) |
| **pass@k / pass^k** | At least one of k tries succeeds / all k tries succeed (consistency). | — |
| **Discriminating eval** | A set hard enough to tell two versions apart; 100 % for both tells you nothing. | [P01](projects/01_ticket_routing/) |
| **Faithfulness / grounding** | Claims backed by the provided sources (citations, verbatim quotes). | [P03](projects/03_research_multi_agent/) |

## Inference optimization

| Term | Meaning | Where |
|---|---|---|
| **Prompt caching** | Reuse a stable prefix (`tools → system → messages`); cache reads cost ~10 % of input. | [08](concepts/08_inference_optimization/) |
| **`cache_control` breakpoint** | Marks where the cached prefix ends (max 4); a minimum prefix size applies. | [08](concepts/08_inference_optimization/) |
| **Silent cache invalidator** | A timestamp, UUID or unsorted JSON in the prefix, so every request misses the cache. | [08](concepts/08_inference_optimization/) |
| **Batch API** | Async processing at −50 % cost, results within 24 h. | [08](concepts/08_inference_optimization/) |
| **Effort** | `output_config.effort` (`low` … `max`): trades thoroughness against tokens. | [08](concepts/08_inference_optimization/) |
| **Adaptive thinking** | Model decides when and how much to think (`thinking: {type: "adaptive"}`). | [08](concepts/08_inference_optimization/) |
| **Model tiers** | Opus (hardest reasoning) · Sonnet (most production) · Haiku (high-volume, simple, subagents). | [08](concepts/08_inference_optimization/) |
| **TTFT** | Time to first token; improved by streaming, shorter prefixes, caching. | [08](concepts/08_inference_optimization/) |
| **Token counting** | `messages.count_tokens`: know the cost before sending. | [08](concepts/08_inference_optimization/) |
| **Cost per completed task** | The real metric: a cheaper call that needs more retries isn't cheaper. | [08](concepts/08_inference_optimization/) |

## AI Fluency (4D framework)

| Term | Meaning | Where |
|---|---|---|
| **4D Framework / AI Fluency** | Four competencies for working with AI (Dakan & Feller): Delegation, Description, Discernment, Diligence. | [4D](projects/4D_framework/) |
| **Automation / Augmentation / Agency** | The three modes: AI executes, you and AI co-create, or AI acts on its own within boundaries you set. | [4D](projects/4D_framework/) |
| **Delegation** | Decide what AI should do at all and in which mode; delegate implementation, keep judgement. | [4D/1](projects/4D_framework/1_delegation/) |
| **Description** | Tell AI what you want: product, process and performance. Tests are the most precise form. | [4D/2](projects/4D_framework/2_description/) |
| **Discernment** | Judge whether the output is *good*, not just working: product, process, performance. | [4D/3](projects/4D_framework/3_discernment/) |
| **Diligence** | Vouch for what you ship: creation, transparency and deployment diligence. | [4D/4](projects/4D_framework/4_diligence/) |
| **Description–Discernment loop** | Inner loop: describe → AI produces → judge → refine the description. | [4D](projects/4D_framework/) |

## Sources

- Building effective agents — <https://www.anthropic.com/engineering/building-effective-agents>
- Writing tools for agents — <https://www.anthropic.com/engineering/writing-tools-for-agents>
- Effective context engineering for AI agents — <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- How we built our multi-agent research system — <https://www.anthropic.com/engineering/multi-agent-research-system>
- Demystifying evals for AI agents — <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- Build with Claude — <https://platform.claude.com/docs/en/build-with-claude/overview>
- AI Fluency framework (Dakan & Feller) — <https://ringling.libguides.com/ai/framework>
- AI Fluency: Framework and foundations — <https://academy.claude.com/courses/ai-fluency-framework-foundations>
