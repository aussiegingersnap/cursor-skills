# Orchestration Patterns for Multi-Agent Skills

This reference documents patterns for composing skills in multi-agent systems, based on research into what actually scales.

> **Source**: Derived from "Multi-Agent Systems: What Actually Scales" - synthesis of Google/MIT multi-agent research (Dec 2025), Cursor's production learnings, and Yaggi's Gas Town architecture.

## Core Insight

> **Simplicity scales because complexity creates serial dependencies, and serial dependencies block the conversion of compute into capability.**

Studies show that adding more agents can make systems perform *worse* - past certain thresholds, 20 agents produce less than 3 would have. The difference is architecture.

## Two-Tier Architecture

### The Pattern

Scalable multi-agent systems use strict two-tier hierarchy:

1. **Planners/Orchestrators** - Create tasks, assign to workers, evaluate results
2. **Workers/Atomic Skills** - Execute in isolation, don't know other workers exist
3. **Judge** - Evaluates results against criteria

### Why It Works

Peer coordination creates serial dependencies. Two-tier eliminates them.

**Bad Pattern** (flat coordination):
```
Skill A ←→ Skill B ←→ Skill C
    ↘   shared state   ↙
```
Workers hold locks, forget to release them, become risk-averse.

**Good Pattern** (two-tier):
```
        Orchestrator
       /     |     \
   Skill A  Skill B  Skill C
      ↓        ↓        ↓
   output   output   output
      \        |        /
         Merge/Judge
```
Workers are ephemeral, isolated, stateless.

## Minimum Viable Context

### The Principle

Workers receive exactly enough context to complete their task, no more.

### Why It Matters

When workers understand broader project context:
- **Scope creep** - Agents decide adjacent tasks need doing
- **Reinterpretation** - Agents modify assignments based on their understanding
- **Conflicts** - Every decision potentially conflicts with other workers

### Application to Skills

**Bad**: Pass entire project structure to every skill
```
Skill receives: Full codebase context, all related files, project history
Result: Skill makes "helpful" changes outside its scope
```

**Good**: Pass only task-specific information
```
Skill receives: Specific file to modify, exact criteria to meet
Result: Skill completes focused task, nothing more
```

## Stateless Execution

### The Pattern

Short-lived agents that:
1. Receive task
2. Execute
3. Capture results to external storage
4. Terminate

### Why Continuous Agents Fail

Context accumulation creates serial dependency with the agent's own past:
- **Context pollution** - Signal dilutes in noise
- **Lost in the middle** - Models lose track of information in long contexts
- **Drift** - Quality degrades within hours regardless of context window

### Application to Skills

**Bad**: Long-running skill session that accumulates state
```
Skill starts → builds component → tests → adds analytics → commits
All in one continuous session with growing context
```

**Good**: Episodic skill invocations with external state
```
Orchestrator → task-select skill → writes to TASKS.md → terminates
           → component-design skill → reads TASKS.md, writes component → terminates
           → build-test skill → reads component, tests → terminates
           → commit skill → reads all outputs, commits → terminates
```

Each skill is fresh, external files carry state between invocations.

## External Coordination Mechanisms

### Principle

Workers operate in total isolation. Coordination happens through external systems designed for concurrent access.

### Mechanisms

| Mechanism | Use Case |
|-----------|----------|
| Git | Code changes, version control |
| Files (TASKS.md, etc.) | Task state, progress tracking |
| Task queues | Assignment distribution |
| Merge queues | Output integration |

### Why Internal Coordination Fails

- **Tool contention** - Multiple agents accessing same tools = coordination overhead
- **Message serialization** - Queues serialize tool access
- **State sync** - Agreement required before proceeding

## Prompts as Contracts

### The Principle

79% of multi-agent failures originate from spec/coordination issues, not technical bugs.

Good prompts + isolation reduces coordination infrastructure needed.

### Application to Skills

SKILL.md is the API contract. It should specify:

1. **Inputs** - Exactly what the skill needs
2. **Outputs** - Exactly what the skill produces
3. **Success Criteria** - How to verify completion
4. **Boundaries** - What the skill does NOT do

Clear contracts enable:
- Independent skill development
- Predictable composition
- Easy debugging (check contract compliance)

## Composition Patterns

### Sequential Composition

Orchestrator invokes skills in sequence, each building on previous output.

```
Orchestrator
    ↓
Skill A (inputs: X) → outputs: Y
    ↓
Skill B (inputs: Y) → outputs: Z
    ↓
Skill C (inputs: Z) → outputs: Final
```

### Parallel Composition

Orchestrator invokes independent skills simultaneously.

```
Orchestrator
    ↓
┌───────────────────┐
↓         ↓         ↓
Skill A   Skill B   Skill C
↓         ↓         ↓
└───────────────────┘
    ↓
Merge/Aggregate
```

### Conditional Composition

Orchestrator routes based on results.

```
Orchestrator
    ↓
Skill A → success? 
    ↓ yes      ↓ no
Skill B    Skill C (retry/alternative)
```

## Anti-Patterns

### 1. Skills That Reference Other Skills

**Bad**: Skill A imports or invokes Skill B directly
**Good**: Orchestrator invokes both, manages dependencies

### 2. Skills That Share State

**Bad**: Skills read/write shared in-memory state
**Good**: Skills read/write external files, orchestrator manages sequence

### 3. Skills That Need Project-Wide Context

**Bad**: Skill needs to understand entire codebase to function
**Good**: Skill receives specific files and criteria, operates locally

### 4. Long-Running Skills

**Bad**: Skill runs for extended period, accumulating context
**Good**: Skill completes task quickly, terminates, next skill picks up

## When to Use Orchestrators vs Atomic Skills

| Situation | Use |
|-----------|-----|
| Single focused task | Atomic skill |
| 3+ distinct phases | Orchestrator |
| Tasks that can run in parallel | Orchestrator composing atomic skills |
| Complex conditional logic | Orchestrator |
| Reusable across contexts | Atomic skill |
| Project-specific workflow | Orchestrator |

## Summary

1. **Keep skills atomic** - Resist multi-purpose skills
2. **Context is liability** - Pass minimum viable information
3. **Design for failure** - Skills should be restartable
4. **Prompts are the interface** - SKILL.md clarity matters most
5. **Orchestration is the investment** - Build good task decomposition

> The job is not one brilliant agent running for a week. It's 10,000 dumb agents well-coordinated, running for an hour at a time, progressively getting work done against tight goal definitions.
