#!/usr/bin/env python3
"""Compile and run portable motion tests; requires a C++ compiler, not ESP32 tools."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="drivedot-tests-") as folder:
    binary = Path(folder) / "motion_test"
    subprocess.run([
        os.environ.get("CXX", "g++"), "-std=c++11", "-Wall", "-Wextra",
        "-Werror", "-I", str(root / "firmware/include"),
        str(root / "firmware/test/motion_test.cpp"), "-o", str(binary),
    ], check=True)
    subprocess.run([str(binary)], check=True)
