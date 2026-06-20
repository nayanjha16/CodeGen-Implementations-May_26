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