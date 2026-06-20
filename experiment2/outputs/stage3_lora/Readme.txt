"Stage 3 demonstrated that while Low-Rank Adaptation (LoRA) fine-tuning successfully optimizes the model’s internal grammar 
engine—achieving a 94.8% SELECT syntax precision—the parameter capacity of a 350M Small Language Model is insufficient for zero-knowledge cross-domain generalization. 
Without inline DDL schema context, the model suffers from severe entity hallucination when evaluated on unseen database environments."


"In Stage 4, we evaluated the impact of adding explicit negative-constraint system instructions (e.g., anti-join rules) to the prompt. 
While this successfully resolved aggregation token errors (fixing metric selection errors like duplicate AVG vs MAX clauses), 
it introduced attention fragmentation in the 350M parameter architecture.Because of the model's constrained parameter capacity, 
processing multi-layered operational rules alongside direct DDL schemas caused alias mapping degradation (e.g., generating non-existent $T_3$ table bindings).
This demonstrates that while Small Language Models (SLMs) excel at schema grounding, complex instruction-following constraints degrade syntax coherence compared to larger Scale Foundations."

