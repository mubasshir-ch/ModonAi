# Testing Plan for ModonAi

## Objective
Establish a robust, future-proof testing strategy for ModonAi that covers unit tests for individual components, comprehensive tests for the Model Context Protocol (MCP) tools, integration tests for the mocked agentic loop, and end-to-end tests involving a real Discord test environment.

## 1. Testing Framework Recommendation

The recommended testing stack for modern asynchronous Python applications, especially Discord bots, is:
- **`pytest`**: The industry standard testing framework for Python. Highly extensible and easy to use.
- **`pytest-asyncio`**: An extension for `pytest` that allows testing asynchronous code, which is essential for a Discord bot built with `py-cord`.
- **`pytest-mock`**: Provides a convenient `mocker` fixture around `unittest.mock`, which is critical for stubbing out Discord API calls and LLM API requests in unit/integration tests.
- **`dpytest` (optional consideration)**: Can be used for more complex Discord state mocking, though standard `AsyncMock` is often sufficient for unit testing tool logic.

### Why this stack?
- It natively supports `async`/`await`.
- It isolates concerns, allowing rapid local testing without hitting rate limits.
- It seamlessly integrates with CI/CD pipelines (e.g., GitHub Actions).

## 2. Testing Strategy

### A. Unit Testing: Individual Functions and Core Logic
Core utility functions and config parsing should be tested in isolation.
- **Configuration & Setup**: Ensure config variables are correctly loaded and validated.
- **Utility Functions**: Test any generic helper functions (like `resolve_member` in `bot/features/prompt/mcp/utils.py`) with various mocked inputs to ensure they behave predictably.

### B. Unit Testing: MCP Tools
Since the bot relies heavily on MCP tools (e.g., `ban_member`, `create_channel`), these must be exhaustively tested locally.
- **Mocking Discord Objects**: Instead of a real `discord.Guild`, pass a mock object constructed via `unittest.mock.MagicMock` or `AsyncMock`. 
- **Testing Execution**: Instantiate the tool, pass the required Pydantic schema parameters and the mock Guild.
- **Assertions**: 
  1. Verify the tool returns the correct success/error dictionary.
  2. Verify that the correct underlying `py-cord` methods (e.g., `member.ban()`, `guild.create_text_channel()`) were called with the expected arguments.
- **Edge Cases**: Mock Pycord exceptions (like `discord.Forbidden` or `discord.HTTPException`) to test that the MCP tools catch and return friendly error messages instead of crashing the bot.

### C. Integration Testing: The Agentic Loop (Mocked LLM)
Integration testing ensures that the prompt parsing, LLM generation, and Discord interactions work cohesively without incurring LLM costs or dealing with non-deterministic outputs.
- **Mocking the LLM**: We will entirely bypass real API calls to OpenAI/Anthropic/Gemini during integration tests. 
- **Testing the Agentic Loop**:
  1. We will mock the `litellm` or `instructor` client to return deterministic, predefined Pydantic models representing the LLM's chosen tool calls.
  2. We inject a mock `discord.Message` containing a test prompt (e.g., "Create a text channel called general").
  3. We verify the agentic loop processes this intent, successfully calls the `create_channel` MCP tool (which is also mocked or acting on mocked Discord objects), and formulates the correct follow-up response back to the user without hallucinating.

### D. End-to-End (E2E) Testing (Live Discord Interaction)
A separate test suite will run tests that actually interact with Discord to ensure the underlying `py-cord` library, the bot's intents, and the Discord API are functioning together as expected.
- **Dedicated Test Server**: These tests will run against a dedicated test Discord server/guild using a test bot token.
- **E2E Workflow**: 
  1. A script (acting as a user or via another bot instance) sends a real message to a designated test channel.
  2. The bot processes the message (potentially using a very cheap LLM model or a mocked LLM layer just for routing, depending on the test scope).
  3. The test asserts that the expected action *actually occurred* on the server (e.g., a channel was actually created, a role was actually assigned).
- **Cleanup**: The E2E framework must clean up after itself (e.g., deleting channels or removing roles it created during the test).

### E. Future Work: Database Testing
*TODO: Add database-related tests when database functionality is implemented.*
Once the MongoDB (`motor`) integration is fully active, we will need to:
- Test database insertions, updates, and retrievals.
- Use `mongomock-motor` or a local Dockerized MongoDB instance to test DB logic without affecting production data.

## 3. Implementation Steps

### Phase 1: Setup
1. Add core testing dependencies to `pyproject.toml` (`pytest`, `pytest-asyncio`, `pytest-mock`).
2. Create a `tests/` directory at the root of the project.
3. Structure the directory into `tests/unit`, `tests/integration`, and `tests/e2e`.
4. Configure `pytest.ini` for `asyncio`.

### Phase 2: Unit Tests (Local, Fast)
1. Write tests for `bot.config`.
2. Create fixtures for mock `discord.Guild`, `discord.Member`, `discord.Role`.
3. Implement unit tests for utility functions and core MCP tools (e.g., `ban_member`, `create_channel`).

### Phase 3: Integration Tests (Agentic Loop)
1. Create a mocking strategy for the LLM client in `prompt_service.py` to return predefined responses.
2. Simulate a discord command/message trigger.
3. Assert the complete workflow: message ingestion -> agent parsing (mocked LLM) -> tool execution -> response generation.

### Phase 4: E2E Tests (Live Discord)
1. Set up a separate configuration file (e.g., `.env.test`) with a test bot token and a test guild ID.
2. Write scripts that trigger bot commands and verify the state changes via the Discord API.
3. Implement teardown fixtures to clean up the test guild after each run.

## 4. Verification
- Run unit and integration tests via `pytest tests/unit tests/integration` to ensure fast, local validation.
- Run E2E tests specifically via `pytest tests/e2e` when full system validation against Discord is required.