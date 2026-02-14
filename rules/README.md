# eHub Development Rules

This directory contains the development rules and standards for the eHub project. These rules help maintain code quality, consistency, and best practices across the codebase.

## Rule Files

- **000-core.md**: Core principles (KISS, DRY, git workflow, architecture)
- **001-code-quality.md**: Code quality standards (functions, errors, organization, testing)
- **002-cli-standards.md**: CLI design patterns (arguments, secrets, UX)
- **003-temporal-patterns.md**: Temporal workflow and activity patterns
- **004-infrastructure-code.md**: Infrastructure as Code standards (Terraform, security)
- **005-taskfile-standards.md**: Taskfile patterns (compose/cascade, task design, workflows)
- **006-python-local-dev.md**: Python (conda) and local development (Docker/Compose)
- **007-agent-logging.md**: Agent interaction recording and log structure

## How to Use

1. **Read First**: Review all rules before starting development
2. **Reference Often**: Keep these rules in mind during code reviews
3. **Update as Needed**: Propose updates when patterns emerge or rules become outdated
4. **Enforce Consistently**: Apply rules uniformly across all components

## Philosophy

These rules exist to:

- **Reduce Cognitive Load**: Consistent patterns make code easier to understand
- **Prevent Mistakes**: Learn from past errors and avoid repeating them
- **Improve Quality**: Maintain high standards across the codebase
- **Speed Up Development**: Clear guidelines reduce decision fatigue

## Contributing

When adding new rules:

1. Ensure they align with core principles
2. Provide concrete examples (good and bad)
3. Explain the "why" behind the rule
4. Keep rules concise and actionable
