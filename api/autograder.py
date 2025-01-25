import ast
import inspect

class AutoGrader:
    def run_test_cases(self, test_cases, student_function_code):
        """
        Run all test cases on the student function, accommodating any function name and multiple parameters.
        """
        score = 0
        total = len(test_cases)

        result_feedback = ""

        # Parse the student's code to extract the function name
        try:
            parsed_code = ast.parse(student_function_code)
            function_name = None
            for node in ast.walk(parsed_code):
                if isinstance(node, ast.FunctionDef):
                    function_name = node.name
                    break
            
            if not function_name:
                return "Error: No function definition found in the submitted code."
        except Exception as e:
            return f"Error parsing student code: {e}"

        # Create a namespace to safely execute the student's code
        namespace = {}
        try:
            exec(student_function_code, namespace)
            student_function = namespace[function_name]
        except Exception as e:
            return f"Error in student code: {e}"

        # Get the function signature to handle multiple parameters
        try:
            signature = inspect.signature(student_function)
            parameter_names = list(signature.parameters.keys())
        except Exception as e:
            return f"Error retrieving function signature: {e}"

        # Run test cases
        for i, test in enumerate(test_cases, start=1):
            # Extract input arguments and expected output
            input_data = test["input"]  # Expected to be a list or tuple
            expected = test["expected_output"]

            try:
                # Ensure input_data is passed as a tuple to match the function's parameter list
                if not isinstance(input_data, (list, tuple)):
                    input_data = [input_data]  # Wrap single input in a list
                result = student_function(*input_data)  # Pass unpacked arguments
                
                if result == expected:
                    result_feedback += f"- Test {i}: Passed ✅ (Input: {input_data}, Expected: {expected}, Got: {result})\n"
                    score += 1
                else:
                    result_feedback += f"- Test {i}: Failed ❌ (Input: {input_data}, Expected: {expected}, Got: {result})\n"
            except Exception as e:
                result_feedback += f"- Test {i}: Error ❌ (Input: {input_data}, Expected: {expected}, Got: {e})\n"

        result_feedback += f"\nFinal Score: {score}/{total}"

        return result_feedback


if __name__ == '__main__':
    # Example student submission: Function with multiple parameters
    student_submission = """
def add_numbers(a, b, c):
    return a + b + c
    """

    # Test cases for the function
    test_cases = [
        {'input': [1, 2, 3], 'expected_output': 3},
        {'input': [10, 20, 0], 'expected_output': 30},
        {'input': [-1, 1, 0], 'expected_output': 0},
        {'input': [0, 0, 0], 'expected_output': 0},
    ]

    # Initialize the autograder
    grader = AutoGrader()

    # Test the student's function
    print("Running tests on student submission...\n")
    
    print(grader.run_test_cases(test_cases, student_submission))
