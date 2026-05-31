# Future Tasks & Interactive Features

This document outlines planned features that go beyond standard Discord server configuration actions. These features focus on rich, interactive communication between the bot and the users.

## 1. Interactive Messaging Tools
The bot should be able to send complex, interactive messages as part of its execution plan.

*   **`send_embed_message`**: Allow the LLM to design and send beautiful Discord embeds (custom colors, fields, thumbnails, footers) to specific channels (e.g., sending a formatted rules list to the `#rules` channel).
*   **`send_paginated_message`**: Implement a tool for the LLM to send long lists of information that users can click through using "Next/Previous" buttons.

## 2. Conversational & Questionnaire Tools
The bot should be able to pause its execution to gather more information or choices from users.

*   **`ask_user_question`**: A tool where the bot sends a message with specific options (using Discord UI Buttons or Select Menus). The bot waits for the user's interaction before continuing the execution plan based on the selected answer.
*   **`request_user_input`**: A tool where the bot opens a Discord Modal to ask for free-form text input from a user, feeding that input back into the LLM's context.

## 3. Scheduled Tasks
*   **`schedule_action`**: Allow the AI to schedule a message or moderation action to happen at a specific time in the future (e.g., "Post this announcement tomorrow at 9 AM").

## Architectural Considerations for Future Tasks
These tools will require the `Execution-Mode` loop to support **asynchronous waiting states**. Currently, the loop executes tasks sequentially. For interactive tools (like `ask_user_question`), the execution engine must pause, wait for the Discord Interaction event (button click), and then resume the plan with the new context.
