# CSR v1.0 — System Architecture

## 1. Overview

CSR (Canonical Semantic Representation) is a language-agnostic intermediate representation (IR) designed to represent programs as a semantic graph rather than syntax.

It enables:
- Code understanding
- Cross-language translation
- Program analysis
- AI reasoning over software

---

## 2. High-Level Architecture

CSR is structured into 4 major layers:

---

## 3. Core Components

### 3.1 Core IR (`codespec/core`)

Responsible for:
- Identity system (UUID + labels)
- Canonical enums (NodeKind, StatementKind, etc.)
- Base graph object model
- Global CSR graph container

---

### 3.2 Model Layer (`codespec/model`)

Defines semantic constructs:

#### Entities
- Module
- Class
- Routine
- Variable

#### Statements
- Assignment
- Decision
- Return
- Block

#### Expressions
- Literal
- VariableReference
- BinaryOperation
- Call

---

### 3.3 Graph System

CSR is simultaneously:
- A tree (ownership hierarchy)
- A graph (semantic relationships)

Edges include:
- CALLS
- READS
- WRITES
- INHERITS

---

### 3.4 Execution Model

CSR represents execution as:


---

## 4. Data Flow

### Step 1: Parsing
Source code → AST (Tree-sitter)

### Step 2: Translation
AST → CSR nodes

### Step 3: Normalization
- Operator normalization
- Control-flow simplification
- Type mapping

### Step 4: Graph Construction
- Nodes registered in CSRGraph
- Relationships linked

### Step 5: Analysis
- CFG generation
- Call graph extraction
- Dependency analysis

---

## 5. Design Goals

- Language independence
- Deterministic representation
- Graph-first structure
- AI-friendly abstraction
- No syntax leakage

---

## 6. Output Forms

CSR can be serialized into:

- JSON (default)
- Graph formats (future: Neo4j, RDF)
- Visualization formats (future)

---

## 7. Extensibility

CSR is designed to evolve via:
- new NodeKinds
- new RelationshipKinds
- extended expression types
- new analysis passes

Without breaking existing structure.

---

## 8. Summary

CSR is not an AST.

It is a semantic execution graph designed for reasoning, translation, and analysis.
