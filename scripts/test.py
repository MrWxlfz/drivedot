#!/usr/bin/env python3
"""Compile and run portable firmware tests; requires a C++ compiler, not ESP32 tools."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="drivedot-tests-") as folder:
    for source in sorted((root / "firmware/test").glob("*_test.cpp")):
        binary = Path(folder) / source.stem
        subprocess.run([
            os.environ.get("CXX", "g++"), "-std=c++11", "-Wall", "-Wextra",
            "-Werror", "-I", str(root / "firmware/include"),
            str(source), "-o", str(binary),
        ], check=True)
        subprocess.run([str(binary)], check=True)
