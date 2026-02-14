### 003 Temporal Workflow Patterns

#### Workflow Design

- **Deterministic Workflows**: Workflows must be deterministic - no random, time, or I/O operations
- **Activities for Side Effects**: All non-deterministic operations go in Activities
- **Entity Workflows**: Use entity workflows for long-lived business entities (infrastructure, projects)
- **Idempotent Activities**: Design activities to be safely retried

#### Workflow Structure

```python
# GOOD - Clear separation of concerns
@workflow.defn
class CoreInfraWorkflow:
    @workflow.run
    async def run(self, request: CoreInfraRequest) -> CoreInfraResult:
        # 1. Validate input
        validated_request = await self._validate_request(request)

        # 2. Get human approval if needed
        if request.requires_approval:
            approved_request = await self._get_approval(validated_request)

        # 3. Execute activities
        result = await self._provision_infrastructure(approved_request)

        # 4. Return result
        return result
```

#### Activity Design

- **Single Responsibility**: Each activity should do one thing
- **Timeout Configuration**: Always set appropriate timeouts
- **Retry Policies**: Configure retry policies for transient failures
- **Heartbeats**: Use heartbeats for long-running activities
- **Activity Context**: Use activity context for cancellation and heartbeats

#### Signal and Query Handlers

- **Signals for Updates**: Use signals to update workflow state
- **Queries for State**: Use queries to read workflow state without side effects
- **Signal Validation**: Validate signal inputs before processing
- **Query Performance**: Keep queries fast and simple

#### Error Handling

- **Application Errors**: Use ApplicationError for business logic failures
- **Temporal Errors**: Let Temporal handle retries for transient failures
- **Compensation Logic**: Implement saga pattern for complex rollbacks
- **Dead Letter Queue**: Handle permanently failed workflows appropriately
