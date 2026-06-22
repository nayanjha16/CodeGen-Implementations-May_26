# src/processor.py

def clean_generated_sql(raw_text):
    """
    Takes raw text from the model, strips out structural comment boundaries,
    and returns a clean executable SQL statement.
    """
    lines = raw_text.split("\n")
    valid_sql_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Halt processing if the model restarts prompt generation loops
        if (stripped.startswith("```") or 
            stripped.startswith("#") or 
            stripped.startswith("###") or
            "Explanation:" in line or 
            "Question:" in line or
            "SQL Query:" in line):
            break
            
        valid_sql_lines.append(line)
        
    generated_sql_clean = " ".join(valid_sql_lines).strip()
    final_sql = f"SELECT {generated_sql_clean}".strip()
    
    if final_sql.endswith(";"):
        final_sql = final_sql[:-1].strip()
        
    return final_sql
    
def clean_generated_nosql(raw_text):
    """
    Takes raw text from the Module 2 translator model, strips out structural 
    prompt markers, and isolates the functional MongoDB query string.
    """
    lines = raw_text.split("\n")
    valid_nosql_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Halt processing if the model leaks template blocks or wraps it in markdown blocks
        if (stripped.startswith("```") or 
            stripped.startswith("#") or 
            stripped.startswith("###") or
            "SQL:" in line or
            "Instruction:" in line or
            "Response:" in line):
            break
            
        valid_nosql_lines.append(line)
        
    generated_nosql_clean = " ".join(valid_nosql_lines).strip()
    
    # Clean up double spacing caused by multi-line squashing
    final_mql = " ".join(generated_nosql_clean.split())
    
    return final_mql