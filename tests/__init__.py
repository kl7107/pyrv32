"""
Test package for pyrv32.

Auto-discovers and runs all test_*.py modules.
"""

import os
import importlib


def run_all_tests():
    """
    Auto-discover and run all test modules in tests/ directory.
    
    Discovers modules matching pattern: test_*.py
    Each module should have a main() or run_*_tests() function.
    
    Returns:
        List of log file paths from tests that create them.
    """
    log_paths = []
    tests_dir = os.path.dirname(__file__)
    
    # Find all test_*.py files
    test_files = sorted([
        f[:-3]  # Remove .py extension
        for f in os.listdir(tests_dir)
        if f.startswith('test_') and f.endswith('.py')
    ])
    
    for test_module_name in test_files:
        # Import the test module
        module = importlib.import_module(f'tests.{test_module_name}')
        
        # Try to find and call the test runner function
        # Convention: main() or run_*_tests()
        if hasattr(module, 'main'):
            result = module.main()
        elif hasattr(module, 'run_all_tests'):
            result = module.run_all_tests()
        else:
            # Try to find run_*_tests pattern
            for attr_name in dir(module):
                if attr_name.startswith('run_') and attr_name.endswith('_tests'):
                    result = getattr(module, attr_name)()
                    break
            else:
                print(f"Warning: No test runner found in {test_module_name}")
                continue
        
        # Collect log path if returned
        if result and isinstance(result, str):
            log_paths.append(result)
    
    return log_paths
