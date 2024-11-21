import os
import subprocess
import filecmp

def run_baseline_test(input_file, output_dir):
    # Define paths for baseline script using relative path from `a2`
    baseline_script = os.path.join("src", "a2", "baseline.py")
    
    # Run baseline.py with input_file and output_dir as arguments
    result = subprocess.run(
        ["python", baseline_script, input_file, output_dir],
        capture_output=True,
        text=True
    )
    
    # Check if the command ran successfully
    assert result.returncode == 0, f"baseline.py failed with error: {result.stderr}"

    # Define expected output files based on input_file name
    input_name = os.path.basename(input_file).split('.')[0]
    expected_md5 = os.path.join("expected", f"{input_name}-md5.txt")
    expected_wordfreq = os.path.join("expected", f"{input_name}-wordfreq.txt")
    expected_shingle = os.path.join("expected", f"{input_name}-shingle.txt")

    # Define actual output files
    md5_output = os.path.join(output_dir, f"{input_name}-md5.txt")
    wordfreq_output = os.path.join(output_dir, f"{input_name}-wordfreq.txt")
    shingle_output = os.path.join(output_dir, f"{input_name}-shingle.txt")

    # Compare files line by line and display any mismatches for debugging
    def compare_files(file1, file2):
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            for i, (line1, line2) in enumerate(zip(f1, f2), 1):
                if line1.strip() != line2.strip():
                    print(f"Difference at line {i}:\nExpected: '{line2.strip()}'\nActual: '{line1.strip()}'")
                    return False
    return True

    
    assert compare_files(md5_output, expected_md5), f"MD5 output mismatch for {input_file}"
    assert compare_files(wordfreq_output, expected_wordfreq), f"Word frequency output mismatch for {input_file}"
    assert compare_files(shingle_output, expected_shingle), f"Shingle output mismatch for {input_file}"

    print(f"Test passed for {input_file}")



def test_baseline():
    # Set up directories
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    # Run tests for each input file
    test_files = [os.path.join("data", "five.tsv"), os.path.join("data", "thirty.tsv")]
    for test_file in test_files:
        run_baseline_test(test_file, output_dir)

if __name__ == "__main__":
    test_baseline()
