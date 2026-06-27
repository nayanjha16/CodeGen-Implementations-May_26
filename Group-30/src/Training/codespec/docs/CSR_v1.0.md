# CSR v1.0 — Canonical Semantic Representation

## 1. Overview

CSR (Canonical Semantic Representation) is a language-independent semantic model for representing software.

It is designed for:

- Code understanding
- Cross-language translation
- Program analysis
- AI-assisted code generation
- Graph-based reasoning over software systems

CSR does NOT represent syntax.

CSR represents meaning.

---

## 2. Core Principle

> CSR describes what a program *means*, not how it is written.

All programming languages (Python, C++, Java, etc.) are converted into CSR before any further processing.

---

## 3. Top-Level Structure

A CSR program consists of:

- Entities
- Statements
- Expressions
- Relationships

---

## 4. Entities

Entities represent *things that exist* in a program.

### 4.1 Entity Types

- Program
- Module
- Namespace
- Class
- Interface
- Routine
- Parameter
- Variable
- Field
- Property
- Enumeration
- EnumerationValue
- Type
- Package

---

### 4.2 Entity Rules

- Every entity has a unique identifier (UUID)
- Every entity has a name (if applicable)
- Entities may contain other entities (ownership)
- Entities may participate in relationships

---

## 5. Statements

Statements represent *actions or control flow constructs*.

### 5.1 Statement Types

- Assignment
- Return
- Loop
- Decision
- Switch
- Break
- Continue
- Throw
- Try
- Catch
- ExpressionStatement
- Block

---

### 5.2 Statement Rules

- Statements operate on expressions
- Statements may contain nested statements
- Control flow is represented structurally, not syntactically

---

## 6. Expressions

Expressions represent *computable values*.

### 6.1 Expression Types

- Literal
- VariableReference
- FieldReference
- ArrayAccess
- MemberAccess
- Call
- ObjectCreation
- BinaryOperation
- UnaryOperation
- ConditionalExpression
- Lambda
- Cast

---

### 6.2 Expression Rules

- Expressions always produce a value
- Expressions may be nested arbitrarily
- All operators are normalized into semantic forms

---

## 7. Relationships

Relationships represent semantic connections between entities.

### 7.1 Relationship Types

- OWNS
- CONTAINS
- CALLS
- USES
- RETURNS
- THROWS
- INHERITS
- IMPLEMENTS
- CREATES
- READS
- WRITES
- DEPENDS_ON

---

### 7.2 Relationship Rules

- Relationships are directed edges in a graph
- Relationships connect two CSR objects
- Relationships do NOT represent ownership unless explicitly OWNS or CONTAINS

---

## 8. Normalization Rules

CSR enforces semantic normalization:

### 8.1 Assignments

All assignment operations are normalized:

- `x = x + 1`
- `x += 1`
- `x++`

All become:

Assignment(
    target = VariableReference(x),
    value = BinaryOperation(ADD, x, 1)
)

---

### 8.2 Control Flow

All loops are normalized into:

Loop(
    initializer,
    condition,
    update,
    body
)

All conditionals become:

Decision(
    condition,
    true_branch,
    false_branch
)

---

## 9. Type System

CSR uses a unified type system:

- Integer
- Float
- Boolean
- String
- Void
- Custom types (user-defined classes)

All language-specific types are mapped into canonical types.

---

## 10. Identity Model

Each CSR object has:

- UUID (global unique identity)
- Kind (semantic type)
- Label (human-readable identifier)

Example:

Routine:
    uuid  -> 550e8400-e29b-41d4-a716-446655440000
    kind  -> ROUTINE
    label -> ROUTINE_000001

---

## 11. Design Constraints

- CSR MUST NOT contain syntax-specific constructs
- CSR MUST NOT reference source language constructs
- CSR MUST be language-agnostic
- CSR MUST be graph-representable
- CSR MUST be deterministic when required

---

## 12. Intended Usage

CSR is intended to be used for:

- Code translation (Python ↔ C++ ↔ Java)
- Code analysis
- AI-based reasoning over programs
- Code generation
- Program understanding
- Graph-based retrieval (RAG systems)

---

## 13. Versioning

This document defines CSR v1.0.

Future versions may extend:

- new entity types
- new relationships
- improved normalization rules

but MUST preserve backward compatibility where possible.