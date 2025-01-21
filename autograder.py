# Assumes the student's code submission is wrapped in a function and is complete (dosen't cause any syntax errors) 

class AutoGrader:
    def run_test_cases(self, test_cases, student_function):
        """
        Run all test cases on the student function, accommodating nested dictionaries.
        """
        score = 0
        total = len(test_cases)

        for i, test in enumerate(test_cases, start=1):
            # Extract the single key-value pair from the dictionary
            test_id, test_data = list(test.items())[0]

            input_data = test_data["input"]
            expected = test_data["expected output"]

            try:
                result = student_function(input_data)
                if result == expected:
                    print(f"Test {test_id}: Passed ✅ (Input: {input_data}, Expected: {expected}, Got: {result})")
                    score += 1
                else:
                    print(f"Test {test_id}: Failed ❌ (Input: {input_data}, Expected: {expected}, Got: {result})")
            except Exception as e:
                print(f"Test {test_id}: Error ❌ (Input: {input_data}, Expected: {expected}, Got: {e})")

        print(f"\nFinal Score: {score}/{total}")
        return score


if __name__ == '__main__':
    def student_submission(n):
        """
        Example of a student submission.
        This function has a deliberate bug for demonstration purposes.
        """
        if n == 0:
            return 1
        return n * n  # Bug: Incorrect factorial logic

    test_cases = [
        {0: {"input": 0, "expected output": 1}},
        {1: {"input": 1, "expected output": 1}},
        {2: {"input": 5, "expected output": 120}},
        {3: {"input": 10, "expected output": 3628800}},
    ]

    # Initialize the autograder
    grader = AutoGrader()

    # Test the student's function
    print("Running tests on student submission...\n")
    grader.run_test_cases(test_cases, student_submission)
