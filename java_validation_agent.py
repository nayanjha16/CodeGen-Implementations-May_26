from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, SecretStr
from state import AgentState
from config import QWEN_BASE_MODEL, GROQ_API_KEY
import json
import subprocess
import tempfile
import os
import re
    
validation_llm = ChatGroq(
    model=QWEN_BASE_MODEL,
    api_key=SecretStr(GROQ_API_KEY),
    temperature=0.2,
    max_retries=2,
    reasoning_effort="none",
    max_tokens=4000  # Increased to allow complete test case generation
)

validation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert Software Validation Agent responsible for generating comprehensive functional test cases for AI-generated JAVA programs.

Your responsibility is ONLY to generate high-quality test cases based on the user's programming problem.

You are NOT allowed to:
- explain the solution
- generate source code
- modify or repair code
- optimize code
- judge code quality
- provide implementation hints
- include thinking tags or explanations

Your objective is to generate test cases that thoroughly validate the correctness of the generated Java program.

IMPORTANT: Generate 5-8 concise test cases that cover the most important scenarios. Quality over quantity - focus on edge cases and boundary conditions.

Instructions:

1. Carefully analyze the programming problem.
2. Refer the provided reference Java code to get the method signature and class name.
3. Determine:
   - expected input format
   - expected output format
   - input constraints
   - edge cases
4. Generate test cases covering (prioritize in this order):
   - Normal/typical cases (1-2 cases)
   - Boundary conditions (1-2 cases)
   - Edge cases specific to the problem (1-2 cases)
   - Error or special cases if applicable (1 case)
   
KEEP IT CONCISE: Aim for 5-8 test cases maximum. Each test case description should be 2-5 words.

Each test case must contain:
- description: Description of the test case
- function: The method name to test (e.g., "add")
- className: The class name containing the method (e.g., "Solution")
- input: Array of input parameters (MUST be actual numeric values, NOT Java constants)
- expected_output: The expected return value (MUST be an actual numeric value, NOT Java constants like Integer.MAX_VALUE)
- inputTypes: Array of Java input type names (e.g., ["int", "int"])
- For methods having a single List parameter,
    the input field MUST contain one element,
    which is the entire list.

    Correct

    "input":[
        [1,2,3]
    ]

    Wrong

    "input":[1,2,3]


Rules:

- Expected outputs must be logically correct.
- Do not make unsupported assumptions.
- Do not invent new requirements.
- Keep descriptions concise.
- Return ONLY valid JSON with "test_cases" as the root key.
- Do not include markdown.
- Do not include explanations.
- Do not wrap the JSON in code fences.
- Do NOT use thinking tags (<think></think>) - respond with ONLY JSON.
- CRITICAL: ALL input values and expected_output MUST be actual literals (numbers, strings), NEVER Java constants or expressions
- CRITICAL: Do not use Integer.MAX_VALUE, Integer.MIN_VALUE, or any other Java constants - use actual numeric values instead
- IMPORTANT: The JSON response MUST have this exact structure with "test_cases" as the main key containing an array of test cases.
- Input types must be valid Java types (int, long, double, boolean, String, etc.)

Return ONLY this JSON format - no other text:

{{
  "test_cases": [
    {{
      "description": "Normal Case",
      "function": "methodName",
      "className": "ClassName",
      "input": [10, 5],
      "inputTypes": ["int", "int"],
      "expected_output": 15
    }},
    {{
      "description": "Edge Case",
      "function": "methodName",
      "className": "ClassName",
      "input": [100],
      "inputTypes": ["int"],
      "expected_output": 200
    }}
  ]
}}
"""
        ),
        (
            "human",            
            '''
            Generate test cases for the following programming problem: {user_query} 
            and the code for reference: {generated_code}  
            
            IMPORTANT: Return ONLY a valid JSON object with "test_cases" as the root key. Do not include any other text, explanations, thinking, or markdown.            
            Include className and inputTypes for each test case.
            '''            
            
        )
    ]
)

def generate_test_cases(user_query: str, generated_code: str) -> str:
    """
    Generate test cases for the given programming problem.

    Args:
        user_query (str): The programming problem description.
        generated_code (str): The generated Java code to be tested.

    Returns:
        str: The generated test cases in JSON format.
    """
    
    response = validation_llm.invoke(validation_prompt.format_messages(user_query=user_query, generated_code=generated_code))
    content = response.content if response else ""
    
    if not content or not content.strip():
        print(f"ERROR: Empty LLM response. Raw response: {response}")
        raise ValueError("LLM returned empty response for test case generation")
    
    print(f"DEBUG: Raw LLM response length: {len(content)}")
    print(f"DEBUG: First 300 chars: {content[:300]}")
    
    # Remove think tags
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    
    # Strip whitespace after removing think tags
    content = content.strip()
    
    if not content:
        print(f"ERROR: Response contained only think tags, no JSON found")
        raise ValueError("LLM response contained only think tags without any JSON")
    
    print(f"DEBUG: After removing think tags - length: {len(content)}")
    print(f"DEBUG: First 300 chars: {content[:300]}")
    
    # Clean Java constants from JSON
    # Replace Integer.MAX_VALUE, Integer.MIN_VALUE, etc. with actual values
    content = re.sub(r'Integer\.MAX_VALUE', '2147483647', content)
    content = re.sub(r'Integer\.MIN_VALUE', '-2147483648', content)
    content = re.sub(r'Long\.MAX_VALUE', '9223372036854775807', content)
    content = re.sub(r'Long\.MIN_VALUE', '-9223372036854775808', content)
    
    # Handle expressions like "Integer.MAX_VALUE - 1"
    content = re.sub(r'2147483647\s*-\s*1', '2147483646', content)
    content = re.sub(r'-2147483648\s*\+\s*1', '-2147483647', content)
    
    # Detect and remove incomplete test cases at the end (truncated response)
    # Look for incomplete JSON at the end (unclosed strings, incomplete fields)
    if content.rstrip().endswith('"') and content.rstrip()[-2] != ',':
        # Ends with a quote that's not properly closed - likely truncated
        print(f"DEBUG: Detected truncated response - removing incomplete test case")
        # Find the last complete test object
        last_complete_idx = content.rfind('},')
        if last_complete_idx != -1:
            # Find the position after the last complete object
            end_pos = last_complete_idx + 2
            # Trim to this position and close the JSON properly
            content = content[:end_pos].rstrip()
            # Remove trailing comma if present
            if content.endswith(','):
                content = content[:-1]
    
    # Check for incomplete strings in JSON (like 'inputTypes": ["')
    if re.search(r':\s*\[$', content) or re.search(r':\s*"[^"]*$', content):
        print(f"DEBUG: Detected incomplete field at end of response - truncating")
        # Find the last complete comma+closing brace
        last_complete_idx = content.rfind('},')
        if last_complete_idx != -1:
            content = content[:last_complete_idx+1]  # Keep up to and including the }
        else:
            # Try to find last complete closing brace
            last_brace_idx = content.rfind('}')
            if last_brace_idx != -1:
                content = content[:last_brace_idx+1]
    
    print(f"DEBUG: Attempting to parse JSON from response")
    
    # Try to close incomplete JSON by counting braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    
    print(f"DEBUG: Brace count - open: {open_braces}, close: {close_braces}")
    print(f"DEBUG: Bracket count - open: {open_brackets}, close: {close_brackets}")
    
    # If JSON is incomplete, try to fix it
    if close_braces < open_braces or close_brackets < open_brackets:
        print(f"DEBUG: JSON appears incomplete, attempting to fix")
        # Add missing closing brackets and braces
        missing_brackets = open_brackets - close_brackets
        missing_braces = open_braces - close_braces
        content = content + (']' * missing_brackets) + ('}' * missing_braces)
        print(f"DEBUG: Added {missing_brackets} closing brackets and {missing_braces} closing braces")
    
    # Try to find and parse test_cases in the JSON
    try:
        # First attempt: direct parse
        parsed = json.loads(content)
        if "test_cases" in parsed:
            return content
        # If no test_cases key, wrap it
        if isinstance(parsed, list):
            content = json.dumps({"test_cases": parsed})
            return content
    except json.JSONDecodeError as e:
        print(f"DEBUG: Direct JSON parse failed: {e}, attempting extraction")
    
    # Second attempt: extract individual test case objects
    if '"test_cases"' in content:
        # Try to extract all test case objects within the test_cases array
        test_cases_start = content.find('"test_cases"')
        if test_cases_start != -1:
            # Find the opening bracket after test_cases
            bracket_start = content.find('[', test_cases_start)
            if bracket_start != -1:
                # Extract from [ to the end, try to build valid JSON
                bracket_content = content[bracket_start:]
                # Count and close if needed
                open_br = bracket_content.count('[')
                close_br = bracket_content.count(']')
                if close_br < open_br:
                    bracket_content = bracket_content + (']' * (open_br - close_br))
                
                # Rebuild the structure
                reconstructed = content[:test_cases_start] + '"test_cases": ' + bracket_content
                open_obj = reconstructed.count('{')
                close_obj = reconstructed.count('}')
                if close_obj < open_obj:
                    reconstructed = reconstructed + ('}' * (open_obj - close_obj))
                
                print(f"DEBUG: Attempting to parse reconstructed JSON")
                try:
                    parsed = json.loads(reconstructed)
                    content = reconstructed
                    print(f"DEBUG: Successfully parsed reconstructed JSON")
                except json.JSONDecodeError as e2:
                    print(f"DEBUG: Reconstructed JSON still invalid: {e2}")
    
    # Third attempt: extract individual test objects and rebuild
    print(f"DEBUG: Attempting to extract individual test case objects")
    # Find all complete test case objects
    test_obj_pattern = r'\{\s*"description"[^{}]*(?:"input"\s*:\s*\[[^\]]*\]|"inputTypes"\s*:\s*\[[^\]]*\]|"function"\s*:\s*"[^"]*"|"className"\s*:\s*"[^"]*"|"expected_output"\s*:\s*[^,\}])*\s*\}'
    test_objects = re.findall(test_obj_pattern, content)
    
    if test_objects:
        print(f"DEBUG: Found {len(test_objects)} test objects")
        try:
            test_cases = []
            for obj_str in test_objects:
                try:
                    # Clean up and parse each object
                    obj = json.loads(obj_str)
                    test_cases.append(obj)
                except json.JSONDecodeError as obj_err:
                    print(f"DEBUG: Could not parse individual object: {obj_err}")
                    continue
            
            if test_cases:
                content = json.dumps({"test_cases": test_cases})
                print(f"DEBUG: Successfully rebuilt JSON from {len(test_cases)} test objects")
                return content
        except Exception as e:
            print(f"DEBUG: Failed to extract test objects: {e}")
    
    return content

def execute_java_tests(code: str, test_cases: list[dict]) -> list[dict]:
    """
    Execute test harnesses against Java source code.
    
    Compiles the provided Java source code and test harnesses together,
    then executes the test harnesses.

    Args:
        code (str): The Java source code to test.
        test_cases (list[dict]): A list of test cases with input and expected_output.

    Returns:
        list[dict]: A list of results for each test case, indicating pass/fail and any error messages.
    """
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Extract class name from first test case (className field is required from LLM)
            if not test_cases or "className" not in test_cases[0]:
                # Fallback: try to extract from code
                class_match = re.search(r'(?:public\s+)?class\s+(\w+)', code)
                if not class_match:
                    raise ValueError("Could not find class definition in Java code. Test cases must include 'className' field.")
                class_name = class_match.group(1)
            else:
                class_name = test_cases[0]["className"]
            
            # Write source code to temp directory
            source_file_path = os.path.join(temp_dir, f"{class_name}.java")
            with open(source_file_path, 'w') as f:
                f.write(code)
            
            # Compile source code first
            compile_source = subprocess.run(
                ['javac', source_file_path],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if compile_source.returncode != 0:
                for test_case in test_cases:
                    results.append({
                        "description": test_case["description"],
                        "input": test_case["input"],
                        "expected_output": test_case["expected_output"],
                        "actual_output": None,
                        "passed": False,
                        "error": f"Source compilation error: {compile_source.stderr}"
                    })
                return results
            
            # Execute each test case
            for test_case in test_cases:
                try:
                    function_name = test_case["function"]
                    input_data = test_case["input"]
                    expected_output = test_case["expected_output"]
                    input_types = test_case.get("inputTypes", ["int"] * len(input_data))
                    
                    # Build method call parameters
                    params = []
                    args = []
                    # for i, (val, typ) in enumerate(zip(input_data, input_types)):
                    #     param_name = f"param{i}"
                    #     params.append(f'{typ} {param_name} = {val};')
                    #     args.append(param_name)
                    for i, (val, typ) in enumerate(zip(input_data, input_types)):
                        param_name = f"param{i}"

                        declaration = typ
                        if typ == "List":
                            declaration = "java.util.List"
                        elif typ.startswith("List<"):
                            declaration = typ.replace("List", "java.util.List")

                        params.append(
                            f"{declaration} {param_name} = {java_literal(val, typ)};"
                        )

                        args.append(param_name)
                     
                    # # Create test harness - sanitize test name for Windows filenames
                    # test_name = test_case.get('description', 'test')
                    # # Remove illegal Windows filename characters: < > : " / \ | ? *
                    # test_name = re.sub(r'[<>:"/\\|?*]', '', test_name)
                    # # Replace spaces and dashes with underscores
                    # test_name = re.sub(r'[\s\-]+', '_', test_name)
                    # # Limit length to avoid path too long issues
                    # test_name = test_name[:50]
                    
                    test_name = test_case.get("description", "test")

                    # Replace every non-alphanumeric character with _
                    test_name = re.sub(r'[^A-Za-z0-9_]', '_', test_name)

                    # Collapse multiple underscores
                    test_name = re.sub(r'_+', '_', test_name)

                    # Cannot start with a digit
                    if test_name and test_name[0].isdigit():
                        test_name = "_" + test_name

                    test_name = test_name[:50]
                    
                    test_harness = f"""
public class Test_{test_name} {{
    public static void main(String[] args) {{
        try {{
            {class_name} obj = new {class_name}();
            {chr(10).join(params) if params else ''}
            Object result = obj.{function_name}({', '.join(args)});
            System.out.println("RESULT:" + result);
        }} catch (Exception e) {{
            System.out.println("ERROR:" + e.getMessage());            
        }}
    }}
}}
"""
                    
                    # Write test harness
                    test_file_path = os.path.join(temp_dir, f"Test_{test_name}.java")
                    with open(test_file_path, 'w') as f:
                        f.write(test_harness)
                    
                    # Compile test harness
                    compile_test = subprocess.run(
                        ['javac', '-cp', temp_dir, test_file_path],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if compile_test.returncode != 0:
                        results.append({
                            "description": test_case["description"],
                            "input": input_data,
                            "expected_output": expected_output,
                            "actual_output": None,
                            "passed": False,
                            "error": f"Test compilation error: {compile_test.stderr}"
                        })
                        continue
                    
                    # Run test
                    test_class_name = f"Test_{test_name}"
                    run_result = subprocess.run(
                        ['java', '-cp', temp_dir, test_class_name],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    output = run_result.stdout.strip()
                    
                    if "ERROR:" in output:
                        results.append({
                            "description": test_case["description"],
                            "input": input_data,
                            "expected_output": expected_output,
                            "actual_output": None,
                            "passed": False,
                            "error": output
                        })
                    else:
                        # Extract result
                        result_value = None
                        for line in output.split('\n'):
                            if line.startswith("RESULT:"):
                                result_value = line.replace("RESULT:", "").strip()
                                break
                        
                        # Compare with expected output
                        passed = str(result_value) == str(expected_output)
                        results.append({
                            "description": test_case["description"],
                            "input": input_data,
                            "expected_output": expected_output,
                            "actual_output": result_value,
                            "passed": passed,
                            "error": None
                        })
                        
                except Exception as e:
                    results.append({
                        "description": test_case["description"],
                        "input": test_case["input"],
                        "expected_output": test_case["expected_output"],
                        "actual_output": None,
                        "passed": False,
                        "error": str(e)
                    })
        
        except Exception as e:
            for test_case in test_cases:
                results.append({
                    "description": test_case["description"],
                    "input": test_case["input"],
                    "expected_output": test_case["expected_output"],
                    "actual_output": None,
                    "passed": False,
                    "error": f"Setup error: {str(e)}"
                })
    
    return results

def validate_java_code(user_query: str, code: str) -> float:
    """
    Validate the generated Java code against the programming problem by generating and executing test cases.

    Args:
        user_query (str): The programming problem description.
        code (str): The generated Java code to be tested.

    Returns:
        float: The percentage of test cases that passed.
    """
    test_cases_json = ""
    try:
        test_cases_json = generate_test_cases(user_query, code)
        
        print(f"DEBUG: Generated test cases JSON length: {len(test_cases_json)}")
        print(f"DEBUG: First 300 chars: {test_cases_json[:300]}")
        
        if not test_cases_json or not test_cases_json.strip():
            print(f"ERROR: Empty test cases JSON")
            return 0.0
            
        test_cases = json.loads(test_cases_json)["test_cases"]  # Convert JSON string to Python object
        results = execute_java_tests(code, test_cases)
        
        # Print test results
        print("\n=== Test Results ===")
        for result in results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"[{status}] {result['description']}")
            if result["error"]:
                print(f"  Error: {result['error']}")
        
        total = len(results)
        passed_count = sum(1 for r in results if r.get("passed"))
        pass_percentage = (passed_count / total * 100) if total > 0 else 0.0
        print(f"\nPass Rate: {passed_count}/{total} ({pass_percentage:.1f}%)")
        return pass_percentage
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON response: {e}")
        print(f"DEBUG: Raw response length: {len(test_cases_json)}")
        print(f"DEBUG: Raw response (first 500 chars): {test_cases_json[:500]}")
        print(f"DEBUG: Raw response (last 200 chars): {test_cases_json[-200:]}")
        return 0.0
    except Exception as e:
        print(f"ERROR in validate_java_code: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

def java_literal(value, java_type):
    """
    Convert a Python value into a valid Java literal.

    Supports:
    - int, long, double, float
    - boolean
    - char
    - String
    - int[], long[], double[], float[], char[], String[]
    - java.util.List / List
    """

    java_type = java_type.strip()

    # ---------- Primitive ----------
    if java_type in ("int", "Integer"):
        return str(int(value))

    elif java_type == "long":
        return f"{int(value)}L"

    elif java_type == "double":
        return str(float(value))

    elif java_type == "float":
        return f"{float(value)}f"

    elif java_type == "boolean":
        return str(value).lower()

    elif java_type == "char":
        return f"'{value}'"

    elif java_type == "String":
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    # ---------- Primitive Arrays ----------
    elif java_type == "int[]":
        return "new int[]{" + ", ".join(map(str, value)) + "}"

    elif java_type == "long[]":
        return "new long[]{" + ", ".join(f"{v}L" for v in value) + "}"

    elif java_type == "double[]":
        return "new double[]{" + ", ".join(map(str, value)) + "}"

    elif java_type == "float[]":
        return "new float[]{" + ", ".join(f"{v}f" for v in value) + "}"

    elif java_type == "char[]":
        return "new char[]{" + ", ".join(f"'{c}'" for c in value) + "}"

    elif java_type == "String[]":
        vals = [f'"{str(v)}"' for v in value]
        return "new String[]{" + ", ".join(vals) + "}"

    # ---------- Lists ----------
    elif "List" in java_type:

        if len(value) == 0:
            return "java.util.Arrays.asList()"

        first = value[0]

        if isinstance(first, bool):
            vals = ", ".join(str(v).lower() for v in value)

        elif isinstance(first, int):
            vals = ", ".join(map(str, value))

        elif isinstance(first, float):
            vals = ", ".join(map(str, value))

        else:
            vals = ", ".join(f'"{str(v)}"' for v in value)

        return f"java.util.Arrays.asList({vals})"

    # ---------- Nested int[][] ----------
    elif java_type == "int[][]":
        rows = []
        for row in value:
            rows.append("{" + ", ".join(map(str, row)) + "}")
        return "new int[][]{" + ", ".join(rows) + "}"

    elif java_type == "long[][]":
        rows = []
        for row in value:
            rows.append("{" + ", ".join(f"{v}L" for v in row) + "}")
        return "new long[][]{" + ", ".join(rows) + "}"

    elif java_type == "double[][]":
        rows = []
        for row in value:
            rows.append("{" + ", ".join(map(str, row)) + "}")
        return "new double[][]{" + ", ".join(rows) + "}"

    elif java_type == "String[][]":
        rows = []
        for row in value:
            rows.append("{" + ", ".join(f'"{v}"' for v in row) + "}")
        return "new String[][]{" + ", ".join(rows) + "}"

    # ---------- Generic fallback ----------
    elif isinstance(value, str):
        return json.dumps(value)

    elif isinstance(value, bool):
        return str(value).lower()

    elif isinstance(value, list):
        return str(value)

    else:
        return str(value)    