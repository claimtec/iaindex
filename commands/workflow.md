---
description: "Execute the automated spec workflow with quality gates"
allowed-tools: ["Task"]
---

# Workflow Execution Command

Quick command to execute the complete spec workflow with quality gates.

## Usage

Simply provide your feature description and the workflow will automatically:
1. Generate requirements (spec-analyst)
2. Design architecture (spec-architect)
3. Implement code (spec-developer)
4. Validate quality (spec-validator)
5. Generate tests if quality ≥95% (spec-tester)
6. Loop with feedback if quality <95% (max 3 iterations)

## Execution

Use the spec-workflow-orchestrator agent to execute the complete workflow:

```
First use the spec-workflow-orchestrator sub agent to execute a complete development workflow for: $ARGUMENTS

The orchestrator will:
- Manage the entire agent chain automatically
- Enforce quality gates (95% threshold)
- Handle feedback loops intelligently
- Track iterations and progress
- Generate comprehensive documentation
- Organize all artifacts in dated folders
```

The workflow will create organized outputs in:
- `./claude/docs/{date}/` - All documentation
- `./src/` - Implementation code
- `./tests/` - Test suites

## Quality Standards

- **Target Score**: 95%
- **Max Iterations**: 3
- **Auto-retry**: Enabled
- **Feedback Integration**: Automatic

## Example

```
/workflow "Build a user authentication system with JWT tokens"
```

This will trigger the complete automated pipeline, managing all agents and quality gates automatically.