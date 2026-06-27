# CSR v1.0 — Design Decisions

This document explains the reasoning behind key architectural choices in CSR.

---

## 1. Why CSR is NOT an AST

### Decision
CSR is a semantic graph, not a syntax tree.

### Reason
ASTs:
- are language-specific
- encode syntax noise
- are not stable across languages

CSR instead:
- represents meaning
- is language-agnostic
- supports cross-language translation

---

## 2. Why UUID-based Identity

### Decision
Every CSR node uses a UUID + label.

### Reason
- Enables merging multiple files safely
- Avoids name collisions
- Supports distributed parsing
- Ensures graph consistency

---

## 3. Why dual structure (Tree + Graph)

### Decision
CSR uses both:
- ownership tree
- semantic graph

### Reason
Programs naturally have:
- lexical structure (tree)
- semantic relationships (graph)

Both are required for accurate modeling.

---

## 4. Why enums instead of strings

### Decision
All semantic categories are enums.

### Reason
- Prevents inconsistent labeling
- Enables static validation
- Improves performance
- Ensures deterministic behavior

---

## 5. Why expressions are separate from statements

### Decision
CSR strictly separates:
- Statements (actions)
- Expressions (values)

### Reason
This mirrors compiler theory:
- enables optimization
- simplifies translation
- prevents semantic ambiguity

---

## 6. Why normalization is required

### Decision
All constructs are normalized:
- x += 1 → x = x + 1
- if/else unified structure
- calls standardized

### Reason
- simplifies downstream analysis
- removes language-specific variations
- ensures deterministic CSR output

---

## 7. Why CALLS / READS / WRITES are explicit

### Decision
All data/control flow is explicitly represented.

### Reason
- enables static analysis
- supports dependency graphs
- enables AI reasoning
- avoids hidden side effects

---

## 8. Why CSR is graph-first

### Decision
CSR is fundamentally a graph system.

### Reason
Modern program analysis requires:
- call graphs
- dependency graphs
- CFGs
- data-flow graphs

Tree structures alone are insufficient.

---

## 9. Why no source spans in CSR v1

### Decision
CSR does not store source code locations.

### Reason
- irrelevant for cross-language translation
- reduces complexity
- avoids coupling to original syntax

Can be added later as an optional overlay.

---

## 10. Why deterministic design is important

### Decision
CSR aims for deterministic construction where possible.

### Reason
- reproducibility
- diffing between programs
- stable AI pipelines
- caching and indexing

---

## 11. Why modular layering is strict

### Decision
CSR is split into:
- core
- model
- analysis
- builders

### Reason
- separation of concerns
- scalability
- maintainability
- easier extension

---

## 12. Summary

CSR design is guided by one principle:

> Represent meaning, not syntax.

Everything else follows from this.