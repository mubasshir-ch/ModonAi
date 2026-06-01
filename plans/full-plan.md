# ModonAi: Natural Language Moderation Feature Plan

## 1. Overview
The core feature of ModonAi is the `/prompt` slash command. This allows server administrators to describe complex server modifications in natural language. The bot will parse the request, draft a high-level goal list, and then enter a dynamic **Agentic Execution Loop** to fulfill the request using both autonomous retrieval and user-verified mutation tools.

## 2. Architecture & Tech Stack Choices
To address the key technical requirements outlined for the project:

*   **Model Agnosticism (Switching Models Easily):**
    *   **Recommendation:** Use **LiteLLM**. It provides a unified, drop-in replacement for the OpenAI API that supports OpenAI, Gemini, Claude, DeepSeek, and local models (via Ollama).
*   **Guaranteed Structured Format:**
    *   **Recommendation:** Use the **Instructor** library alongside LiteLLM. It patches the LLM client to guarantee responses adhere strictly to predefined **Pydantic** models.
*   **True MCP Server Architecture:**
    *   Each tool is a self-contained module in `mcp/tools/` containing its own schema, metadata, and `pycord` execution logic.
*   **Anti-Hallucination Guardrails:**
    *   The system prompt explicitly restricts the LLM to *only* use the tools explicitly provided in the registry. If a user requests an unsupported action, the LLM must inform the user rather than hallucinating.
*   **Continuous Agentic Loop:**
    *   **Core Logic:** Instead of a static sequence of tool calls, the AI manages a dynamic **Task Checklist**. It executes retrieval tools autonomously to gather data and presents mutation tools to the user for verification. The AI can reason between steps, update its checklist (add/remove/complete tasks), and adapt to real-time feedback or errors.
*   **Context Window Management (Token Limits):**
    *   **Challenge:** Some API providers (like GitHub Models' free tier) impose strict input limits (e.g., 8,000 tokens). The accumulated history of tool calls and JSON responses can quickly exceed this limit, causing the agentic loop to crash.
    *   **Strategy:**
        1.  **Strict Output Truncation:** Enforce hard limits on the size of data returned by retrieval tools (e.g., truncating JSON strings to ~2000 characters) before appending them to the AI's history.
        2.  **History Pruning/Rolling Window:** Implement a mechanism to prune older, less relevant "thoughts" or read-only tool results from the context array, retaining only the initial prompt, the current checklist, and the most recent actions.
        3.  **Optimized Tool Returns:** Redesign retrieval tools to return only essential fields (e.g., returning only `id` and `name` of roles, dropping verbose metadata unless explicitly requested).

## 3. Interaction Flow

### Phase 1: High-Level Planning
1.  **Trigger:** Admin executes `/prompt <instructions>`.
2.  **Drafting Goals:** The AI generates a `BroadPlan` which is simply a list of high-level objectives (e.g., "1. Create 'Staff' Category", "2. Set up Moderator role"). It does *not* decide on specific tool parameters yet.
3.  **Review:** The bot sends an Embed titled **[Plan-Mode]** showing the high-level objectives.
4.  **User Actions:**
    *   **Proceed:** Transitions the bot into the Agentic Loop.
    *   **Suggest Changes:** AI refines the objectives and provides an `explanation` for the changes.
    *   **Cancel:** Aborts the process.

### Phase 2: Agentic Execution Loop
*Once approved, the bot enters a loop with the following steps:*

1.  **Reasoning & Action Selection:**
    *   The AI analyzes the current `Task Checklist` and its internal context.
    *   It decides on the **Next Action**: This could be an internal thought, a retrieval tool call, or a mutation tool call.
2.  **Tool Execution & Permission Gate:**
    *   **Read-Only Tools:** Executed **autonomously** in the background to gather context (e.g., fetching IDs). The results are fed back into the AI's memory.
    *   **Mutation Tools:** The bot pauses and presents a **Task Verification UI** (Embed + Buttons) to the admin.
        *   **Accept:** AI executes the mutation and proceeds.
        *   **Accept-All:** AI auto-executes all remaining mutation tools without further confirmation.
        *   **Reject:** AI reasons why the task was rejected and updates its plan/checklist accordingly.
3.  **Dynamic Task Management:**
    *   After each tool result, the AI updates its checklist: marking tasks as `done`, adding new sub-tasks discovered during investigation, or removing irrelevant ones.
    *   The bot provides regular status updates to the user (e.g., "🔍 Found Moderator role ID: 123... Now drafting channel permissions.")
4.  **Completion:** The loop ends when the AI determines all objectives are met. It then provides a final summary of all actions taken.

## 4. Documentation Strategy
*   **Storage:** Plans are stored in `plans/` at the project root.
*   **Cross-Referencing:** Use relative Markdown links for inter-document navigation.
