---
description: "Automated multi-agent development workflow with quality gates from idea to production code"
allowed-tools: ["Task", "Read", "Write", "Edit", "MultiEdit", "Grep", "Glob", "TodoWrite", "Bash"]
---

# Spec Workflow - Automated Development Pipeline

Execute complete development workflow using intelligent sub-agent chaining with quality gates.

## Context

- Feature to develop: $ARGUMENTS
- Automated multi-agent workflow with quality gates (95% threshold)
- Sub-agents work in independent contexts with smart chaining
- Maximum 3 iterations to ensure convergence

## Your Role

You are the Workflow Orchestrator managing an automated development pipeline using Claude Code Sub-Agents. You coordinate a quality-gated workflow that ensures 95%+ code quality through intelligent looping.

## Workflow Execution Logic

### Quality Gate Configuration

```yaml
quality-threshold: 95
max-iterations: 3
feedback-loop: enabled
auto-retry: true
```

### Execution Chain

Execute the following agents in sequence, with quality gates:

1. **spec-analyst**: Generate comprehensive requirements
2. **spec-architect**: Design system architecture
3. **spec-developer**: Implement code based on specs
4. **spec-validator**: Evaluate quality (0-100% score)
5. **Decision Point**:
   - Score ≥95%: Continue to spec-tester
   - Score <95%: Loop back to spec-analyst with feedback
6. **spec-tester**: Generate comprehensive test suite

## Implementation Steps

### Step 1: Initialize Workflow

Create workflow tracking structure:

```bash
mkdir -p ./claude/docs/$(date +%Y)/$(date +%m)/$(date +%d)/workflow
mkdir -p ./claude/docs/$(date +%Y)/$(date +%m)/$(date +%d)/specs
mkdir -p ./claude/docs/$(date +%Y)/$(date +%m)/$(date +%d)/architecture
mkdir -p ./claude/docs/$(date +%Y)/$(date +%m)/$(date +%d)/implementation
mkdir -p ./claude/docs/$(date +%Y)/$(date +%m)/$(date +%d)/validation
mkdir -p ./claude/docs/$(date +%Y)/$(date +%m)/$(date +%d)/tests
```

### Step 2: Execute Agent Chain

```claude-code
# Iteration 1
First use the spec-analyst sub agent to:
- Analyze the feature request: [$ARGUMENTS]
- Generate requirements.md with functional/non-functional requirements
- Create user-stories.md with acceptance criteria
- Document assumptions and constraints
- Output location: ./claude/docs/{date}/specs/

Then use the spec-architect sub agent to:
- Design system architecture based on requirements
- Create architecture.md with component diagrams
- Generate api-spec.md with endpoint definitions
- Document technology stack decisions
- Output location: ./claude/docs/{date}/architecture/

Then use the spec-developer sub agent to:
- Implement code following architecture specifications
- Create modular, maintainable components
- Include error handling and logging
- Follow coding best practices
- Output location: ./src/ (or appropriate project structure)

Then use the spec-validator sub agent to:
- Evaluate implementation against requirements
- Check code quality and maintainability
- Verify architecture compliance
- Generate quality-score.md with score (0-100%)
- Include specific feedback for improvements
- Output location: ./claude/docs/{date}/validation/

# Quality Gate Decision
If validation score ≥95%:
  Finally use the spec-tester sub agent to:
  - Generate comprehensive unit tests
  - Create integration test scenarios
  - Develop end-to-end test cases
  - Document test coverage metrics
  - Output location: ./tests/

If validation score <95%:
  First use the spec-analyst sub agent again with:
  - Previous validation feedback
  - Specific areas requiring improvement
  - Updated requirements based on findings
  Then repeat the entire chain (max 3 iterations)
```

### Step 3: Track Iterations

Monitor and document each iteration:

```markdown
## Iteration Tracking

### Iteration 1
- Start Time: [timestamp]
- Requirements Generated: ✅
- Architecture Designed: ✅
- Implementation Complete: ✅
- Validation Score: 88%
- Decision: Loop back with feedback

### Iteration 2
- Start Time: [timestamp]
- Requirements Refined: ✅
- Architecture Updated: ✅
- Implementation Improved: ✅
- Validation Score: 96%
- Decision: Proceed to testing

### Final Results
- Total Iterations: 2
- Final Quality Score: 96%
- Tests Generated: ✅
- Workflow Complete: ✅
```

## Expected Outputs

### Document Structure

```
./claude/docs/{YYYY}/{MM}/{DD}/
├── workflow/
│   ├── iteration-tracking.md
│   └── workflow-summary.md
├── specs/
│   ├── requirements.md
│   ├── user-stories.md
│   └── acceptance-criteria.md
├── architecture/
│   ├── architecture.md
│   ├── api-spec.md
│   └── tech-stack.md
├── implementation/
│   └── implementation-notes.md
├── validation/
│   ├── quality-score.md
│   └── validation-report.md
└── tests/
    ├── test-plan.md
    └── coverage-report.md
```

### Code Structure

```
./src/
├── components/
├── services/
├── utils/
└── types/

./tests/
├── unit/
├── integration/
└── e2e/
```

## Quality Metrics

### Scoring Dimensions

1. **Requirements Coverage** (25%)
   - All functional requirements implemented
   - Non-functional requirements addressed
   - Acceptance criteria met

2. **Code Quality** (25%)
   - Clean, readable code
   - Proper error handling
   - Performance optimized
   - Security best practices

3. **Architecture Compliance** (25%)
   - Follows design patterns
   - Proper separation of concerns
   - Scalable structure
   - Technology stack alignment

4. **Documentation** (25%)
   - Code comments where necessary
   - API documentation complete
   - README updated
   - User guides if applicable

## Workflow Benefits

- **Automated Quality Control**: 95% threshold ensures high standards
- **Intelligent Feedback Loops**: Review feedback guides improvements
- **Independent Agent Contexts**: Clean environment for each agent
- **Single Command Execution**: One command triggers entire workflow
- **Traceable Process**: Full audit trail of decisions and iterations

## Execute Workflow

**Feature Description**: $ARGUMENTS

Starting automated development workflow with quality gates...

Begin by creating the workflow tracking structure and initiating the first agent in the chain.