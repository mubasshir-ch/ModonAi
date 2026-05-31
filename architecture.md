# Feature-Modular Discord Architecture (FMDA)

This document outlines the architectural standards for the Modonai project. All new features and refactors must adhere to this structure to ensure maintainability, scalability, and clarity for both human developers and AI agents.

## Core Principle

Features are encapsulated within self-contained modules located in `bot/features/<feature_name>/`. Logic is strictly separated into **Interaction (Cog)**, **Business Logic (Service)**, and **Presentation (UI)** layers.

## Directory Structure

Each feature folder follows this layout:

```text
bot/features/<feature_name>/
├── <feature_name>_cog.py      # Controller: Commands, listeners, and routing.
├── <feature_name>_service.py  # Logic: Data processing and business rules.
├── <feature_name>_ui.py       # View: Embeds, Views, Buttons, and Modals.
├── [component]/               # Supporting logic (e.g., models/, utils/, api/)
└── [component].py             # Supporting files (e.g., constants.py, schemas.py)
```

### Naming & Organization Rules

1.  **The Primary Trio:** The `_cog.py`, `_service.py`, and `_ui.py` files **must** be prefixed with the feature name (e.g., `moderation_cog.py`).
2.  **Supporting Components:** Any additional logic (APIs, models, utilities, configurations) resides inside the feature folder. These can be **individual files** or **subdirectories**.
3.  **No Prefix for Support:** Supporting files or folders **do not** use the `<feature_name>_` prefix. Use generic, descriptive names (e.g., `api.py` or `models/`).
4.  **Common Logic:** Logic shared across multiple features (e.g., core database wrappers, global helpers) must be placed in a top-level `bot/common/` or `bot/core/` directory.

## Component Responsibilities

### 1. Cog (The Controller)
*   **Role:** The entry point for all Discord interactions.
*   **Responsibilities:**
    *   Registers `commands.Cog`, Slash Commands, and Event Listeners.
    *   Handles user input validation and permissions.
    *   Orchestrates the flow by calling the **Service** for logic and the **UI** for responses.

### 2. Service (Business Logic)
*   **Role:** The "brain" of the feature.
*   **Responsibilities:**
    *   Contains pure business logic and data processing.
    *   Handles database queries and external API calls (via supporting files).
    *   Remains "Discord-agnostic" where possible (avoiding UI-specific code).

### 3. UI (The View)
*   **Role:** The visual interface.
*   **Responsibilities:**
    *   Defines `discord.Embed`, `discord.ui.View`, `Buttons`, and `Modals`.
    *   Handles visual formatting and simple UI-level state changes.

## Interaction Flow

Standard execution follows this path:
`User Action` → **Cog** (Validate/Route) → **Service** (Process/Logic) → **UI** (Format/Render) → `User Response`.
