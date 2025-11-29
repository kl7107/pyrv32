#!/usr/bin/env python3
"""Decode NetHack's weird output format."""

with open('/tmp/nethack_raw_output.txt', 'r') as f:
    raw = f.read()

print("="*70)
print("RAW OUTPUT INTERPRETATION")
print("="*70)
print()

# Strip out the escape sequences and just show the characters
import re

# Remove all escape sequences
text_only = re.sub(r'\x1b\[[^a-zA-Z]*[a-zA-Z]', '', raw)
print("Text with escape codes removed:")
print(repr(text_only))
print()
print("Decoded:")
print(text_only)
print()

# Analyze the pattern more carefully
# Pattern seems to be: ESC[B ESC[D <char>
# Which means: down one line, left one column, then print char
# This creates a vertical output!

print("="*70)
print("PATTERN ANALYSIS")
print("="*70)

# Let's extract just characters that follow the ESC[D sequence
matches = re.findall(r'\x1b\[D(.)', raw)
print(f"Characters following ESC[D: {len(matches)}")
print("Text: " + ''.join(matches))
print()

# Or maybe it's trying to write vertically?
# Let's see if we can reconstruct the intended output
print("="*70)
print("RECONSTRUCTION ATTEMPT")
print("="*70)

# Start fresh and parse step by step
pos = 0
row = 0
col = 0
screen = {}  # (row, col) -> char

i = 0
while i < len(raw):
    if raw[i:i+2] == '\x1b[':
        # Escape sequence
        j = i + 2
        while j < len(raw) and raw[j] not in 'ABCDHJKm':
            j += 1
        if j < len(raw):
            cmd = raw[i:j+1]
            if cmd == '\x1b[B':  # Down
                row += 1
            elif cmd == '\x1b[D':  # Left
                col -= 1
            elif cmd == '\x1b[H':  # Home
                row = 0
                col = 0
            elif cmd == '\x1b[2J':  # Clear screen
                screen = {}
                row = 0
                col = 0
            i = j + 1
        else:
            i += 1
    else:
        # Regular character
        screen[(row, col)] = raw[i]
        col += 1
        i += 1

# Display the screen
if screen:
    max_row = max(r for r, c in screen.keys())
    max_col = max(c for r, c in screen.keys())
    print(f"Screen dimensions: {max_row+1} rows x {max_col+1} cols")
    print()
    
    for r in range(max_row + 1):
        line = ''
        for c in range(max_col + 1):
            line += screen.get((r, c), ' ')
        print(line.rstrip())
