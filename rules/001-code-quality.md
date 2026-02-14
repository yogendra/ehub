### 001 Code Quality Rules

#### Function Design

- **Single Responsibility**: Each function should do one thing well
- **Same Level of Abstraction**: All statements in a function body should be at the same level

  ```python
  # BAD - mixing abstraction levels
  def process_user(user_id):
      user = db.query("SELECT * FROM users WHERE id = ?", user_id)  # Low level
      validate_user(user)  # High level
      user['email'] = user['email'].lower()  # Low level

  # GOOD - consistent abstraction level
  def process_user(user_id):
      user = fetch_user(user_id)
      validate_user(user)
      normalize_user_data(user)
  ```

- **Small Functions**: Aim for functions under 20 lines; extract if longer
- **Clear Names**: Use descriptive names that reveal intent (e.g., `calculate_total_price` not `calc`)

#### Error Handling

- **Fail Fast**: Validate inputs early and raise clear errors
- **Specific Exceptions**: Use or create specific exception types, not generic `Exception`
- **Context in Errors**: Include relevant context in error messages
- **No Silent Failures**: Never catch exceptions without logging or handling them

#### Code Organization

- **Logical Grouping**: Group related functions and classes together
- **Minimal Dependencies**: Reduce coupling between modules
- **Clear Imports**: Use explicit imports, avoid `import *`
- **Separate Concerns**: Keep business logic separate from infrastructure code

#### Testing

- **Test Coverage**: Write tests for all business logic and edge cases
- **Test Names**: Use descriptive test names that explain the scenario
- **Arrange-Act-Assert**: Structure tests clearly with setup, execution, and verification
- **Mock External Dependencies**: Isolate units under test from external services
