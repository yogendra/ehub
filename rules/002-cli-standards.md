### 002 CLI Standards

#### Argument Design

- **Short and Long Forms**: Always provide both short (`-v`) and long (`--verbose`) argument forms
  ```python
  # GOOD
  parser.add_argument('-e', '--environment', help='Target environment')
  parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
  parser.add_argument('-c', '--config', help='Config file path')
  ```
- **Consistent Naming**: Use kebab-case for long arguments (`--dry-run`, not `--dryRun`)
- **Required vs Optional**: Make required arguments positional or clearly marked
- **Sensible Defaults**: Provide reasonable defaults for optional arguments

#### Configuration & Secrets

- **Environment Variables**: Read all secrets and sensitive config from environment variables

  ```python
  # GOOD
  import os

  TEMPORAL_HOST = os.getenv('TEMPORAL_HOST', 'localhost:7233')
  AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')  # No default for secrets

  if not AWS_ACCESS_KEY:
      raise ValueError("AWS_ACCESS_KEY_ID environment variable is required")
  ```

- **Never Hardcode Secrets**: No API keys, passwords, or tokens in code
- **Config File Support**: Support config files for non-sensitive settings (`.ehubrc`, `ehub.yaml`)
- **Environment Precedence**: ENV vars > Config file > Defaults

#### User Experience

- **Help Text**: Provide clear, concise help text for all commands and arguments
- **Examples**: Include usage examples in help output
- **Progress Feedback**: Show progress for long-running operations
- **Error Messages**: Display actionable error messages with suggestions
- **Exit Codes**: Use standard exit codes (0 = success, 1 = error, 2 = usage error)

#### Command Structure

- **Verb-Noun Pattern**: Use clear command structure (e.g., `ehub create project`, `ehub deploy app`)
- **Subcommands**: Group related operations under subcommands
- **Idempotency**: Make commands idempotent where possible
- **Confirmation Prompts**: Require confirmation for destructive operations (with `--force` flag to skip)
