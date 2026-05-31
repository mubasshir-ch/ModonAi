# ModonAi: Natural Language Moderation Feature Plan

## 1. Overview
The core feature of ModonAi is the `/prompt` slash command. This allows server administrators to describe complex server modifications in natural language. The bot will parse the request, generate a structured execution plan using an LLM, seek user approval, and execute the changes step-by-step with interactive verification.

## 2. Architecture & Tech Stack Choices
To address the key technical requirements outlined for the project:

*   **Model Agnosticism (Switching Models Easily):**
    *   **Recommendation:** Use **LiteLLM**. It provides a unified, drop-in replacement for the OpenAI API that supports OpenAI, Gemini, Claude, DeepSeek, and local models (via Ollama). You can change the underlying provider simply by updating environment variables and the model string.
*   **Guaranteed Structured Format:**
    *   **Recommendation:** Use the **Instructor** library alongside LiteLLM (or LiteLLM's built-in structured output support). Instructor patches the LLM client to guarantee responses adhere strictly to a predefined **Pydantic** model. This ensures the generated plan and tasks are always valid JSON matching our exact schema.
*   **True MCP Server Architecture:**
    *   **Refactoring Need:** The current implementation has fragmented tool logic (schemas in models, instructions in system prompts, execution in services). This will be refactored into a proper Model Context Protocol (MCP) server structure. Each tool will be a self-contained class/module containing its own Pydantic parameters, descriptive metadata (for the LLM), and execution logic.
*   **Anti-Hallucination Guardrails:**
    *   **Requirement:** Since only a subset of Discord actions are currently implemented, the system prompt must explicitly restrict the LLM to *only* use the tools explicitly provided in the schema. If a user requests an unsupported action, the LLM must be instructed to clearly inform the user that the tool is unavailable, rather than hallucinating a fake action.
*   **Robust Task Execution & Failure Handling:**
    *   **Recommendation:** Implement an **Agentic Execution Loop**. If a task fails (e.g., a Discord API error due to missing permissions or rate limits), the error is caught and fed back into the LLM along with the remaining unexecuted plan. The LLM generates a "Correction Plan" (modifying, appending, or removing tasks). The bot then presents this new sub-plan to the user for approval before resuming execution.

## 3. Interaction Flow

### Phase 1: Investigation (Read-Only Autonomy)
*To solve the "Data Dependency Problem" where the AI needs to fetch data (e.g., list roles) before it can use that data in a mutation task (e.g., sending a message with those roles), the interaction flow begins with an autonomous investigation phase.*
1.  **Trigger:** Admin executes `/prompt <instructions>`.
2.  **Autonomous Retrieval:** The bot enters a ReAct (Reasoning and Acting) loop where it is **only** allowed to use "Retrieval/Read-Only" MCP tools (e.g., `list_roles`, `get_channel_info`). 
3.  **Context Gathering:** It silently executes these retrieval tasks in the background, feeding the results back to itself until it has accumulated enough context to fulfill the user's prompt. *No user approval is required for read-only actions.*

### Phase 2: Plan-Mode (Drafting Mutations)
1.  **Drafting:** Once the AI has the necessary context from Phase 1, it generates the structured `ExecutionPlan` containing only "Mutation" (e.g., `create_channel`) and "Messaging" (e.g., `send_message`) tools. Because it already fetched the data in Phase 1, it can successfully inject IDs, role names, or specific data into the parameters of these subsequent tasks.
2.  **Review:** The bot sends an Embed explicitly titled **[Plan-Mode]**. It details the overarching plan and lists the sequence of tasks.
3.  **User Actions (Buttons):**
    *   **Proceed:** Transitions the bot into Execution-Mode.
    *   **Suggest Changes:** Opens a Discord Modal for the admin to type adjustments. 
        *   *UX Improvement:** The bot will use a **`RevisedPlan`** Pydantic model. This model will include the updated plan *and* an `explanation` field where the AI directly answers the user's questions or explains how the suggestions were incorporated. This provides crucial context before the user accepts the new plan.
    *   **Cancel:** Aborts the operation and deletes the message.

### Phase 3: Execution-Mode
1.  **Initialization:** The bot enters an execution loop, processing tasks sequentially based on their `order` index.
2.  **Task Verification (Per Task):**
    *   The bot prepares a task-specific embed detailing the current task, the tool being called, and its parameters.
    *   **Contextual UI:** Raw Discord IDs are dynamically resolved into human-readable mentions (e.g., `<#1234>` for channels, `<@&5678>` for roles) to ensure the admin fully understands the context.
    *   **User Actions (Buttons):**
        *   **Accept:** Executes the task and queues the next one.
        *   **Accept-All:** Executes the current task and auto-executes all remaining tasks without asking for individual confirmations.
        *   **Reject:** Halts execution and opens a modal to suggest changes to the *remaining* plan.
        *   **Cancel:** Aborts the entire remaining process.
3.  **Completion:** Once all tasks are successfully executed, the bot sends a final summary message detailing all changes made to the server.

## 4. Documentation Strategy
*   **Storage:** Plans should be stored in a central `plans/` or `docs/` directory at the project root.
*   **Cross-Referencing (Symlinks vs. Markdown Links):** 
    *   **Recommendation:** Avoid using symlinks across subfolders, as they can cause issues with Git on different operating systems (e.g., Windows vs. Linux) and complicate IDE file indexing. 
    *   Instead, use standard relative Markdown links. For example, in a feature's local readme (`bot/features/prompt/README.md`), you can link to the main plan: `[View Architecture Plan](../../../plans/full-plan.md)`. This keeps documentation organized and universally compatible.
