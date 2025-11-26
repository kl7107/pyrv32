#!/usr/bin/env python3
"""
Find the NetHack binary in the build directory
"""

import os
import subprocess

# Search for NetHack binary
for root, dirs, files in os.walk('nethack-3.4.3'):
    for f in files:
        if f == 'nethack' or f.endswith('.elf'):
            full_path = os.path.join(root, f)
            print(f"Found: {full_path}")
            # Check if it's executable
            if os.access(full_path, os.X_OK):
                print(f"  Executable: YES")
            else:
                print(f"  Executable: NO")
