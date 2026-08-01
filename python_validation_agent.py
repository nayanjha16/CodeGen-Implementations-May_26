from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, SecretStr
from state import AgentState
from config import QWEN_BASE_MODEL, GROQ_API_KEY
import json
    
validation_llm = ChatGroq(
    model=QWEN_BASE_MODEL,
    api_key=SecretStr(GROQ_API_KEY),
    temperature=0.2,
    max_retries=2,
    reasoning_effort="none"    
)

validation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert Software Validation Agent responsible for generating comprehensive functional test cases for AI-generated programs.

Your responsibility is ONLY to generate high-quality test cases based on the user's programming problem.

You are NOT allowed to:
- explain the solution
- generate source code
- modify or repair code
- optimize code
- judge code quality
- provide implementation hints

Your objective is to generate test cases that thoroughly validate the correctness of the generated program.

IMPORTANT: Generate 5-8 concise test cases that cover the most important scenarios. Quality over quantity - focus on edge cases and boundary conditions.

Instructions:

1. Carefully analyze the programming problem.
2. Refer the provided reference code to get the function signature.
3. Determine:
   - expected input format
   - expected output format
   - input constraints
   - edge cases
4. Generate diverse test cases covering:
   - Normal cases
   - Boundary conditions
   - Empty inputs (if applicable)
   - Single element inputs
   - Duplicate values
   - Negative values (if applicable)
   - Zero values
   - Maximum/minimum values
   - Large inputs
   - Invalid inputs (only if meaningful)
   - Special corner cases

Each test case must contain:
- description: Brief description of the test case
- function: The function name to test
- input: Dictionary with parameter names as keys (e.g., {{"numbrs": [1, 2, 3]}} for a function like def foo(numbrs))
         OR a list if the function takes multiple positional parameters (e.g., [5, 3] for def foo(a, b))
         OR a single value if the function takes one parameter
- expected_output: The expected return value

Rules:

- Expected outputs must be logically correct.
- Do not make unsupported assumptions.
- Do not invent new requirements.
- Keep descriptions concise.
- Return ONLY valid JSON with "test_cases" as the root key.
- Do not include markdown.
- Do not include explanations.
- Do not wrap the JSON in code fences.
- CRITICAL: For inputs, use DICTIONARY format with parameter names as keys: {{"parameter_name": value}}
- IMPORTANT: The JSON response MUST have this exact structure with "test_cases" as the main key containing an array of test cases.

Return ONLY this JSON format - no other text:

{{
  "test_cases": [
    {{
      "description": "Normal Case",
      "function": "biggest_num",
      "input": {{"numbrs": [1, 5, 3, 9, 2]}},
      "expected_output": 9
    }},
    {{
      "description": "Edge Case with Single Element",
      "function": "biggest_num",
      "input": {{"numbrs": [42]}},
      "expected_output": 42
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
            
            IMPORTANT: Return ONLY a valid JSON object with "test_cases" as the root key. Do not include any other text, explanations, or thinking.
            '''            
            
        )
    ]
)

def generate_test_cases(user_query: str, generated_code: str) -> str:
    """
    Generate test cases for the given programming problem.

    Args:
        user_query (str): The programming problem description.
        generated_code (str): The generated Python code to be tested.

    Returns:
        str: The generated test cases in JSON format.
    """
    import re
    
    response = validation_llm.invoke(validation_prompt.format_messages(user_query=user_query, generated_code=generated_code))
    content = response.content if response else ""
    
    if not content or not content.strip():
        print(f"ERROR: Empty LLM response. Raw response: {response}")
        raise ValueError("LLM returned empty response for test case generation")
    
    # print(f"DEBUG: Raw LLM response length: {len(content)}")
    # print(f"DEBUG: First 400 chars: {content[:400]}")
    
    
    # Remove think tags
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    content = content.strip()
    
    # Extract function name from generated code
    func_name_match = re.search(r'def\s+(\w+)\s*\(', generated_code)
    default_func_name = func_name_match.group(1) if func_name_match else "unknown"
    
    # print(f"DEBUG: Detected function name: {default_func_name}")
    
    # Extract JSON from the response (in case there's other text)
    json_match = re.search(r'\{[\s\S]*\}', content)
    if json_match:
        content = json_match.group(0)
    
    # print(f"DEBUG: Extracted JSON length: {len(content)}")
    
    # Try to parse and validate
    try:
        parsed = json.loads(content)
        
        # Ensure test_cases exists
        if "test_cases" not in parsed:
            if isinstance(parsed, list):
                parsed = {"test_cases": parsed}
            elif "description" in parsed:
                # Single test case, wrap it
                parsed = {"test_cases": [parsed]}
        
        # Validate and fix test cases
        if "test_cases" in parsed:
            for i, tc in enumerate(parsed["test_cases"]):
                # Ensure function field exists
                if "function" not in tc:
                    tc["function"] = default_func_name
                    #print(f"DEBUG: Added missing function name to test case {i}")
                
                # Ensure description exists
                if "description" not in tc:
                    tc["description"] = f"Test Case {i+1}"
                
                # Ensure input and expected_output exist
                if "input" not in tc or "expected_output" not in tc:
                    print(f"WARNING: Test case {i} missing required fields")
        
        content = json.dumps(parsed)
        print(f"DEBUG: Validated testcases JSON: {content}")
        
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse error in generation: {e}")
        # Return as-is and let the validation handle it
    
    return content

def execute_python_tests(code: str, test_cases: list[dict]) -> list[dict]:
    """
    Execute the provided Python code against the given test cases.

    Args:
        code (str): The Python code to be tested.
        test_cases (list[dict]): A list of test cases, each containing 'input' and 'expected_output'.

    Returns:
        list[dict]: A list of results for each test case, indicating pass/fail and any error messages.
    """
    results = []
    for test_case in test_cases:
        input_data = test_case.get("input")
        expected_output = test_case.get("expected_output")
        function_name = test_case.get("function")
        
        if not function_name:
            results.append({
                "description": test_case.get("description", "Unknown"),
                "input": input_data,
                "expected_output": expected_output,
                "actual_output": None,
                "passed": False,
                "error": "Missing 'function' field in test case"
            })
            continue
            
        try:
            # Prepare the execution environment
            local_vars = {}
            exec(code, {}, local_vars)
            
            # Call the function with appropriate argument unpacking
            function = local_vars[function_name]
            
            # Debug print
            print(f"DEBUG: Calling {function_name} with input: {input_data}")
            
            if isinstance(input_data, dict):
                # Input is a dictionary - unpack as keyword arguments
                actual_output = function(**input_data)
            elif isinstance(input_data, (list, tuple)):
                # Input is a list or tuple - unpack as positional arguments
                actual_output = function(*input_data)
            else:
                # Input is a scalar - pass directly
                actual_output = function(input_data)
            
            passed = actual_output == expected_output
            results.append({
                "description": test_case.get("description", "Test"),
                "input": input_data,
                "expected_output": expected_output,
                "actual_output": actual_output,
                "passed": passed,
                "error": None
            })
        except KeyError as ke:
            results.append({
                "description": test_case.get("description", "Test"),
                "input": input_data,
                "expected_output": expected_output,
                "actual_output": None,
                "passed": False,
                "error": f"KeyError: {ke} - Function '{function_name}' not found in code"
            })
        except TypeError as te:
            results.append({
                "description": test_case.get("description", "Test"),
                "input": input_data,
                "expected_output": expected_output,
                "actual_output": None,
                "passed": False,
                "error": f"TypeError: {te} - Check if input format matches function signature"
            })
        except Exception as e:
            results.append({
                "description": test_case.get("description", "Test"),
                "input": input_data,
                "expected_output": expected_output,
                "actual_output": None,
                "passed": False,
                "error": f"{type(e).__name__}: {str(e)}"
            })
    return results

def validate_python_code(user_query: str, code: str) -> float:
    """
    Validate the generated code against the programming problem by generating and executing test cases.

    Args:
        user_query (str): The programming problem description.
        generated_code (str): The generated Python code to be tested.

    Returns:
        float: The percentage of test cases that passed.
    """
    test_cases_json = ""
    try:
        test_cases_json = generate_test_cases(user_query, code)
        # print(f"DEBUG: Generated test cases JSON length: {len(test_cases_json)}")
        
        if not test_cases_json:
            print(f"ERROR: No test cases generated")
            return 0.0
            
        # print(f"DEBUG: First 300 chars: {test_cases_json[:300]}")
        
        test_cases = json.loads(test_cases_json)["test_cases"]  # Convert JSON string to Python object
        
        print(f"DEBUG: Parsed {len(test_cases)} test cases")
        
        # Validate and fix test cases format
        for i, tc in enumerate(test_cases):
            print(f"DEBUG: Test case {i}:")
            print(f"  Description: {tc.get('description', 'N/A')}")
            print(f"  Function: {tc.get('function', 'N/A')}")
            print(f"  Input type: {type(tc.get('input'))}, Value: {tc.get('input')}")
            print(f"  Expected output: {tc.get('expected_output')}")
            
            if "input" not in tc:
                print(f"WARNING: Test case {i} missing 'input' field")
        
        results = execute_python_tests(code, test_cases)
        
        # Print results
        print("\n=== Test Results ===")
        for result in results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"[{status}] {result['description']}")
            if result["error"]:
                print(f"  Error: {result['error']}")
            print(f"  Input: {result['input']}")
            print(f"  Expected: {result['expected_output']}, Got: {result['actual_output']}")
        
        total = len(results)
        passed_count = sum(1 for r in results if r.get("passed"))
        pass_percentage = (passed_count / total * 100) if total > 0 else 0.0
        print(f"\nPass Rate: {passed_count}/{total} ({pass_percentage:.1f}%)")
        return pass_percentage
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON response: {e}")
        print(f"DEBUG: Raw response length: {len(test_cases_json)}")
        if test_cases_json:
            print(f"DEBUG: Raw response (first 500 chars): {test_cases_json[:500]}")
            print(f"DEBUG: Raw response (last 200 chars): {test_cases_json[-200:]}")
        else:
            print(f"DEBUG: test_cases_json is empty")
        return 0.0
    except KeyError as e:
        print(f"ERROR in validate_code: Key not found: {e}")
        print(f"DEBUG: Check if test case format is correct")
        print(f"DEBUG: Response length: {len(test_cases_json) if test_cases_json else 0}")
        if test_cases_json:
            print(f"DEBUG: First 500 chars: {test_cases_json[:500]}")
        import traceback
        traceback.print_exc()
        return 0.0
    except Exception as e:
        print(f"ERROR in validate_code: {e}")
        print(f"DEBUG: Response length: {len(test_cases_json) if test_cases_json else 0}")
        if test_cases_json:
            print(f"DEBUG: First 500 chars: {test_cases_json[:500]}")
        import traceback
        traceback.print_exc()
        return 0.0