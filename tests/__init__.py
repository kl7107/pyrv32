"""
Test package for pyrv32.

Auto-discovers and runs all test_*.py modules and test_*() functions.
All test functions receive a 'runner' object with log() and test_fail() methods.
"""

import os
import sys
import importlib
import tempfile


class TestRunner:
    """Simple test runner with auto-discovery"""
    
    def __init__(self):
        self.log_file = None
        self.log_path = None
        self.tests_run = 0
        self.tests_passed = 0
        
    def setup_logging(self, module_name):
        """Create temp log file for a test module"""
        self.log_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False,
            prefix=f'pyrv32_{module_name}_',
            suffix='.log'
        )
        self.log_path = self.log_file.name
        
    def log(self, msg):
        """Write to log file"""
        if self.log_file:
            self.log_file.write(msg + '\n')
            self.log_file.flush()
    
    def test_fail(self, test_name, expected, actual, context=""):
        """Handle test failure - log and exit immediately"""
        self.log(f"\n{'=' * 60}")
        self.log(f"TEST FAILED: {test_name}")
        self.log(f"Expected: {expected}")
        self.log(f"Actual:   {actual}")
        if context:
            self.log(f"Context:  {context}")
        self.log(f"Log file: {self.log_path}")
        self.log(f"{'=' * 60}\n")
        
        if self.log_file:
            self.log_file.close()
        
        print(f"\n{'=' * 60}")
        print(f"TEST FAILED: {test_name}")
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        if context:
            print(f"Context:  {context}")
        print(f"Log file: {self.log_path}")
        print(f"{'=' * 60}\n")
        sys.exit(1)
    
    def run_test_function(self, module_name, func_name, func):
        """Run a single test function"""
        import inspect
        
        test_name = f"{module_name}.{func_name}"
        self.log(f"\nRunning: {test_name}")
        
        try:
            # Check if function expects runner parameter (new style vs old style)
            sig = inspect.signature(func)
            if len(sig.parameters) > 0:
                # New style: pass runner to test function
                func(self)
            else:
                # Old style: call without parameters (backward compatibility)
                func()
            
            self.tests_passed += 1
            self.log(f"  ✓ PASS")
            print(f"✓ {func_name}")
        except Exception as e:
            self.test_fail(test_name, "no exception", str(e), 
                          f"Exception during test: {type(e).__name__}")


def run_all_tests():
    """
    Auto-discover and run all test_*() functions in all test_*.py modules.
    
    Returns:
        List of log file paths.
    """
    log_paths = []
    tests_dir = os.path.dirname(__file__)
    
    # Find all test_*.py files
    test_files = sorted([
        f[:-3]  # Remove .py extension
        for f in os.listdir(tests_dir)
        if f.startswith('test_') and f.endswith('.py')
    ])
    
    if not test_files:
        print("No test files found")
        return log_paths
    
    for test_module_name in test_files:
        # Import the test module
        module = importlib.import_module(f'tests.{test_module_name}')
        
        # Find all test_*() functions
        test_functions = [
            (name, getattr(module, name))
            for name in dir(module)
            if name.startswith('test_') and callable(getattr(module, name))
        ]
        
        if not test_functions:
            print(f"Warning: No test_*() functions found in {test_module_name}")
            continue
        
        # Create test runner for this module
        runner = TestRunner()
        runner.setup_logging(test_module_name)
        
        # Log header
        runner.log("=" * 60)
        runner.log(f"Running tests from {test_module_name}.py")
        runner.log(f"Log file: {runner.log_path}")
        runner.log("=" * 60)
        
        print(f"Running {test_module_name}...")
        
        # Run all test functions
        for func_name, func in test_functions:
            runner.run_test_function(test_module_name, func_name, func)
        
        # Log summary
        runner.log(f"\n{'=' * 60}")
        runner.log(f"✓ All {test_module_name} tests passed ({len(test_functions)}/{len(test_functions)})")
        runner.log(f"Log file: {runner.log_path}")
        runner.log(f"{'=' * 60}\n")
        
        print(f"✓ All {test_module_name} tests passed ({len(test_functions)}/{len(test_functions)})")
        
        if runner.log_file:
            runner.log_file.close()
        log_paths.append(runner.log_path)
    
    return log_paths
