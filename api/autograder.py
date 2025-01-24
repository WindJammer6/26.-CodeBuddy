class AutoGrader:
    def run_test_cases(self, test_cases, student_function):
        """
        Run all test cases on the student function, accommodating flat dictionaries.
        """
        score = 0
        total = len(test_cases)

        print(test_cases)

        result_feedback = ""

        # Create a namespace to safely execute the student's function
        namespace = {}
        try:
            exec(student_function, namespace)
            # Extract the function from the namespace
            student_function = namespace["factorial"]
        except Exception as e:
            return f"Error in student code: {e}"

        for i, test in enumerate(test_cases, start=1):
            input_data = int(test["input"])  # Convert input to integer
            expected = int(test["expected_output"])  # Convert expected output to integer

            try:
                result = student_function(input_data)
                
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
    student_submission = """
def factorial(n):
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
    """

    test_cases = [
        {'expected_output': '1', 'input': '0'},
        {'expected_output': '1', 'input': '1'},
        {'expected_output': '120', 'input': '5'},
        {'expected_output': '5040', 'input': '7'},
        {'expected_output': '3628800', 'input': '10'},
    ]

    # Initialize the autograder
    grader = AutoGrader()

    # Test the student's function
    print("Running tests on student submission...\n")
    
    print(grader.run_test_cases(test_cases, student_submission))
