# STAGE 1: ZERO-SHOT BASELINE EVALUATION REPORT
======================================================================
Project: IIITH M.Tech CS/AI Capstone Project
Dataset: Spider 1.0 Validation Set (1,034 Core Samples)
Model Evaluation Target: Salesforce/codegen-350M-multi
Execution Date: June 2026
Status: COMPLETE & FROZEN
======================================================================

1. EXPERIMENTAL ARCHITECTURE & ENVIRONMENT
----------------------------------------------------------------------
* Computing Runtime: Google Colab Hosted Instance
* Hardware Accelerator: NVIDIA T4 Tensor Core GPU (16GB GDDR6 VRAM)
* Active Storage Mode: Local Drive State Extraction
* Base Frameworks: PyTorch (CUDA-Staged Enabled), Hugging Face Transformers
* Execution Driver: run_all_experiments.py
* Inference Pipeline Throughput: ~1.5 - 1.8 seconds per task
* Overall Pipeline Execution Time: ~0.34 minutes for test loop initialization;
  ~25-30 minutes for full-scale inference over 1,034 records.

2. INFERENCE CONFIGURATION PARAMS
----------------------------------------------------------------------
* limit_samples: None (Full Validation Array Evaluation)
* max_new_tokens: 150
* temperature: 0.0 (Greedy Decoding for Structural Rigidity)
* device: "cuda"
* Input Prompt Context: Zero-Shot (Question string injected natively with zero 
  database relational mapping, table schemas, or syntax structural hints).

3. OFFICIAL EVALUATION RESULTS (EXACT MATCH METRICS)
----------------------------------------------------------------------
The baseline dataset was graded locally using the official Spider evaluation suite 
(`evaluation.py` + `process_sql.py`) with tokenization patterns backed by NLTK (`punkt_tab`).

Execution Command:
python evaluation.py --gold outputs/tmp_gold.txt --pred outputs/tmp_pred.txt --db data/spider/database --table data/spider/tables.json --etype match

Score Summary Matrix:
                     easy                 medium                hard                 extra                all                 
count                248                  446                  174                  166                  1034                

====================== EXACT MATCHING ACCURACY =====================
exact match          0.173                0.011                0.000                0.000                0.046                

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.610                0.311                0.554                0.487                0.467                
select(no AGG)       0.616                0.311                0.585                0.487                0.473                
where                0.209                0.148                0.000                0.000                0.102                
where(no OP)         0.233                0.185                0.025                0.019                0.131                
group(no Having)     0.000                0.182                0.000                0.000                0.167                
group                0.000                0.182                0.000                0.000                0.167                
order                0.000                0.043                0.000                0.000                0.023                
and/or               1.000                0.906                0.899                0.872                0.922                
IUEN                 0.000                0.000                0.000                0.000                0.000                
keywords             0.571                0.297                0.182                0.036                0.274                

---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.391                0.132                0.207                0.223                0.221                
select(no AGG)       0.395                0.132                0.218                0.223                0.224                
where                0.083                0.088                0.000                0.000                0.052                
where(no OP)         0.093                0.110                0.011                0.011                0.067                
group(no Having)     0.000                0.015                0.000                0.000                0.007                
group                0.000                0.015                0.000                0.000                0.007                
order                0.000                0.013                0.000                0.000                0.004                
and/or               0.960                0.973                0.962                0.932                0.961                
IUEN                 0.000                0.000                0.000                0.000                0.000                
keywords             0.187                0.093                0.046                0.012                0.084                

---------------------- PARTIAL MATCHING F1 --------------------------
select               0.477                0.186                0.301                0.306                0.301                
select(no AGG)       0.482                0.186                0.318                0.306                0.304                
where                0.119                0.110                1.000                1.000                0.069                
where(no OP)         0.132                0.138                0.015                0.014                0.089                
group(no Having)     1.000                0.028                1.000                1.000                0.014                
group                1.000                0.028                1.000                1.000                0.014                
order                1.000                0.020                1.000                1.000                0.007                
and/or               0.979                0.938                0.929                0.901                0.9