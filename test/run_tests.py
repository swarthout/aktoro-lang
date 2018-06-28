from pathlib import Path
from aktoro.compiler import compile_ak
import os
import subprocess
import glob
import unittest


class TestAktoro(unittest.TestCase):
    @staticmethod
    def run_file(filename):
        with open(filename) as ak:
            program = ak.read()

        generated = compile_ak(program)
        input_filename_no_extension = filename.split(".ak", 1)[0]
        temp_go_filename = f"{input_filename_no_extension}_aktoro_generated.go"
        with open(temp_go_filename, "w") as go_file:
            go_file.write(generated)
        output = subprocess.check_output(f"go run {temp_go_filename}", shell=True)
        output = output.decode("utf-8")
        os.remove(temp_go_filename)
        return output

    def test(self):
        self.assertEqual('foo'.upper(), 'FOO')
        test_ak_files = glob.glob("test_*/*.ak")
        for filename in test_ak_files:
            result = self.run_file(filename)
            test_path = Path(filename)
            expected_file = test_path.parent / "correct_output.txt"
            with open(expected_file, "r") as e:
                expected = e.read()
            self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
