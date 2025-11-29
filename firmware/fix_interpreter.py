#!/usr/bin/env python3
"""Replace uart_ with console_ in interpreter_test.c"""

with open('/home/dev/git/zesarux/pyrv32/firmware/interpreter_test.c', 'r') as f:
    content = f.read()

# Replace function calls
replacements = {
    'uart_getc()': 'console_getc()',
    'uart_putc(': 'console_putc(',
    'uart_puts(': 'console_puts(',
    'uart_put_hex(': 'console_put_hex(',
    'uart_put_dec(': 'console_put_dec(',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('/home/dev/git/zesarux/pyrv32/firmware/interpreter_test.c', 'w') as f:
    f.write(content)

print("✓ Updated function calls in interpreter_test.c")
