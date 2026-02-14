### 007 Agent Logging Standards

#### Conversation Recording

- **Record Chat History**: Every significant interaction or task session must be recorded in the `agent-logs/` directory.
- **File Naming Convention**: Use the format `agent-logs/<YYYY-MM-dd>-<Title>-<Counter>.md`.
  - `YYYY-MM-dd`: Current date.
  - `Title`: Short descriptive title of the session (kebab-case).
  - `Counter`: Incremental number starting from 01 if multiple logs exist for the same day/title.
- **Log Content**:
  - Always include the **full chat transcript** including user requests and agent responses.
  - Include summaries of significant tool calls or technical decisions.
  - Place the full log **before** any high-level summaries or conclusions.

#### Project Hygiene

- **Git Ignore**: The `agent-logs/` directory must be ignored by git to avoid bloating the repository with conversation metadata.
- **Storage**: Only keep relevant documentation in the `rules/` or `docs/` folders; transient chat history stays in `agent-logs/`.
