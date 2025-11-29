#!/usr/bin/env python3
"""
Fix NetHack's broken vertical output by converting ESC[B ESC[D <char> pattern
to just <char>.

NetHack is outputting: ESC[B (down) ESC[D (left) <char>
This creates vertical text instead of horizontal.

We'll filter the output to remove this pattern.
"""

import re

def fix_nethack_output(raw_output):
    """
    Convert NetHack's vertical output pattern to normal horizontal text.
    
    Pattern: ESC[B ESC[D <char> means "down, left, print char"
    This should just be: <char>
    """
    # Remove the ESC[B ESC[D pattern before each character
    # Pattern: \x1b[B\x1b[D followed by a printable character
    fixed = re.sub(r'\x1b\[B\x1b\[D(.)', r'\1', raw_output)
    
    # Also handle the case where there's just ESC[B before newline
    fixed = re.sub(r'\x1b\[B\s+\x1b\[B', '\n', fixed)
    
    return fixed

# Test with sample NetHack output
test_input = '\x1b[0m\x1b[2J\x1b[H\x1b[B\x1b[BN\x1b[B\x1b[De\x1b[B\x1b[Dt\x1b[B\x1b[DH\x1b[B\x1b[Da\x1b[B\x1b[Dc\x1b[B\x1b[Dk'

print("Original:")
print(repr(test_input))
print("\nFixed:")
fixed = fix_nethack_output(test_input)
print(repr(fixed))
print("\nDecoded:")
print(fixed)
