# ModonAi: Natural Language Moderation Feature Plan

## 1. Overview
The core feature of ModonAi is the `/prompt` slash command. This allows server administrators to describe complex server modifications in natural language. The bot will parse the request, generate a structured execution plan using an LLM, seek user approval, and execute the changes step-by-step with interactive verification.

## 2. Architecture & Tech Stack Choices
To address the key technical requirements outlined for the project:

*   **Model Agnosticism (Switching Models Easily):**
    *   **Recommendation:** Use **LiteLLM**. It provides a unified, drop-in replacement for the OpenAI API that supports OpenAI, Gemini, Claude, DeepSeek, and local models (via Ollama). You can change the underlying provider simply by updating environment variables and the model string.
*   **Guaranteed Structured Format:**
    *   **Recommendation:** Use the **Instructor** library alongside LiteLLM (or LiteLLM's built-in structured output support). Instructor patches the LLM client to guarantee responses adhere strictly to a predefined **Pydantic** model. This ensures the generated plan and tasks are always valid JSON matching our exact schema.
*   **Robust Task Execution & Failure Handling:**
    *   **Recommendation:** Implement an **Agentic Execution Loop**. If a task fails (e.g., a Discord API error due to missing permissions or rate limits), the error is caught and fed back into the LLM along with the remaining unexecuted plan. The LLM generates a "Correction Plan" (modifying, appending, or removing tasks). The bot then presents this new sub-plan to the user for approval before resuming execution.

## 3. Interaction Flow

### Phase 1: Plan-Mode
1.  **Trigger:** Admin executes `/prompt <instructions>`.
2.  **Processing:** The bot displays a "thinking" state. The prompt is sent to the LLM to generate a structured plan of Discord MCP actions. The LLM is strictly instructed via system prompt to order tasks logically (e.g., roles must be created before channels that assign permissions to those roles).
3.  **Review:** The bot sends an Embed explicitly titled **[Plan-Mode]**. It details the overarching plan and lists the sequence of tasks.
4.  **User Actions (Buttons):**
    *   **Proceed:** Transitions the bot into Execution-Mode.
    *   **Suggest Changes:** Opens a Discord Modal for the admin to type adjustments. The new input, along with the original plan, is sent back to the LLM to generate an updated plan.
    *   **Cancel:** Aborts the operation and deletes the message.

### Phase 2: Execution-Mode
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
