import os
import subprocess
import sys
import threading

from qtpy.QtCore import QObject, Signal


class TestRunner(QObject):
    """On-demand test executor for the latest modified Python file."""

    sig_log = Signal(str)
    sig_summary = Signal(dict)
    sig_status = Signal(str)

    def __init__(self, watch_dir, input_file="input.txt", expected_file="expected.txt", time_limit=5):
        super().__init__()
        self.watch_dir = watch_dir
        self.input_file = input_file
        self.expected_file = expected_file
        self.time_limit = time_limit
        self._thread = None
        self._lock = threading.Lock()

    def set_watch_dir(self, folder):
        """Update target folder for test execution."""
        self.watch_dir = folder

    def run_latest_file(self):
        """Run tests for the latest modified Python file in the folder."""
        with self._lock:
            if self._thread and self._thread.is_alive():
                self.sig_log.emit("A run is already in progress. Please wait.")
                return

            self._thread = threading.Thread(target=self._run_once, daemon=True)
            self._thread.start()

    def _run_once(self):
        self.sig_status.emit("running")

        try:
            self.sig_log.emit("")
            target_file = self._find_latest_python_file()
            if target_file is None:
                self.sig_log.emit("No Python files found in selected folder.")
                return

            input_path = os.path.join(self.watch_dir, self.input_file)
            expected_path = os.path.join(self.watch_dir, self.expected_file)

            if not os.path.exists(input_path) or not os.path.exists(expected_path):
                self.sig_log.emit("input.txt or expected.txt is missing.")
                return

            try:
                inputs = self._read_test_cases(input_path)
                expected_outputs = self._read_test_cases(expected_path)
            except Exception as error:
                self.sig_log.emit(f"Failed to load test cases: {error}")
                return

            if len(inputs) != len(expected_outputs):
                self.sig_log.emit("ERROR: Number of test cases mismatch.")
                return

            if not self._is_code_file(target_file):
                self.sig_log.emit(f"Skipping {os.path.basename(target_file)} (no executable code).")
                return

            self.sig_log.emit("🚀 Starting run for latest modified Python file...")
            self.sig_log.emit(f"Running latest modified file: {os.path.basename(target_file)}")
            summary = self._test_file(target_file, inputs, expected_outputs)
            self.sig_summary.emit(summary)
        finally:
            self.sig_status.emit("idle")

    def _find_latest_python_file(self):
        try:
            files = os.listdir(self.watch_dir)
        except Exception as error:
            self.sig_log.emit(f"Cannot read folder: {error}")
            return None

        candidates = []
        for file_name in files:
            if not file_name.endswith(".py"):
                continue
            abs_path = os.path.join(self.watch_dir, file_name)
            try:
                mod_time = os.path.getmtime(abs_path)
            except Exception:
                continue
            candidates.append((mod_time, abs_path))

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    def _read_test_cases(self, file_path):
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()
        cases = content.strip().split("\n\n") if content.strip() else []
        return [case.strip() for case in cases]

    def _is_code_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                content = handle.read()

            i = 0
            n = len(content)
            cleaned = ""

            while i < n:
                token = content[i : i + 3]
                if token in ('"""', "'''"):
                    quote = token
                    i += 3
                    while i < n and content[i : i + 3] != quote:
                        i += 1
                    i += 3
                else:
                    cleaned += content[i]
                    i += 1

            for line in cleaned.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                return True

            return False
        except Exception:
            return True

    def _run_test(self, file_path, input_data):
        try:
            result = subprocess.run(
                [sys.executable, file_path],
                input=input_data,
                text=True,
                capture_output=True,
                timeout=self.time_limit,
                cwd=self.watch_dir,
            )

            if result.returncode != 0:
                return None, result.stderr.strip() or "Runtime Error"

            return result.stdout.strip(), None
        except subprocess.TimeoutExpired:
            return None, "TLE"
        except Exception as error:
            return None, str(error)

    def _test_file(self, filename, inputs, expected_outputs):
        base_name = os.path.basename(filename)
        self.sig_log.emit("=" * 40)
        self.sig_log.emit(f"Testing: {base_name}")
        self.sig_log.emit("=" * 40)

        success = 0
        wrong = 0
        error = 0

        for index, (inp, exp) in enumerate(zip(inputs, expected_outputs), 1):
            self.sig_log.emit("")
            output, err = self._run_test(filename, inp)

            if err:
                self.sig_log.emit(f"Test Case {index} : ERROR")
                self.sig_log.emit("❌ ERROR:")
                self.sig_log.emit(f"{err}")
                error += 1
                continue

            if output.strip() == exp.strip():
                self.sig_log.emit(f"Test Case {index} : SUCCESS")
                self.sig_log.emit("📤 OUTPUT:")
                self.sig_log.emit(f"{output}")
                success += 1
            else:
                self.sig_log.emit(f"Test Case {index} : WRONG OUTPUT")
                self.sig_log.emit("📥 EXPECTED:")
                self.sig_log.emit(f"{exp}")
                self.sig_log.emit("📤 GOT:")
                self.sig_log.emit(f"{output}")
                wrong += 1

        total = len(inputs)
        self.sig_log.emit("-" * 40)
        self.sig_log.emit(f"Summary: total={total}")
        self.sig_log.emit(f"success={success},")
        self.sig_log.emit(f"wrong={wrong}")
        self.sig_log.emit(f"error={error}")
        self.sig_log.emit("-" * 40)
        self.sig_log.emit("")

        return {
            "total": total,
            "success": success,
            "wrong": wrong,
            "error": error,
            "file": base_name,
        }
