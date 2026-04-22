import sys
from types import ModuleType

# Mock the broken plugin module
try:
    import google.generativeai.plugins
except ImportError:
    m = ModuleType("google.generativeai.plugins")
    m.get_plugins = lambda: []
    sys.modules["google.generativeai.plugins"] = m
    print("Mocked google.generativeai.plugins to bypass ImportError")

# Now run the original benchmark
import os
import subprocess

if __name__ == "__main__":
    # We'll just run the benchmark_runner.py in the same process
    # to maintain the mock
    import benchmark_runner
    benchmark_runner.main()
