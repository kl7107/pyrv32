/*
 * Test program for argc/argv
 * Verifies command-line argument passing works correctly
 */

/* Runtime functions (UART output) */
void uart_putc(char c);
void uart_puts(const char *s);
void uart_putln(const char *s);
void uart_puthex(unsigned int value);
void uart_putdec(int value);

int my_strlen(const char *s) {
    int len = 0;
    while (s[len]) len++;
    return len;
}

int main(int argc, char **argv) {
    uart_putln("=== Testing argc/argv ===");
    
    uart_puts("argc = ");
    uart_putdec(argc);
    uart_putc('\n');
    
    for (int i = 0; i < argc; i++) {
        uart_puts("argv[");
        uart_putdec(i);
        uart_puts("] = \"");
        uart_puts(argv[i]);
        uart_puts("\" (ptr: 0x");
        uart_puthex((unsigned int)argv[i]);
        uart_puts(")\n");
    }
    
    uart_puts("argv[argc] = 0x");
    uart_puthex((unsigned int)argv[argc]);
    uart_puts(" (should be NULL)\n");
    
    // Verify argv[argc] is NULL
    if (argv[argc] != (char*)0) {
        uart_putln("ERROR: argv[argc] should be NULL!");
        return 1;
    }
    
    // Print total argument lengths
    int total_len = 0;
    for (int i = 0; i < argc; i++) {
        total_len += my_strlen(argv[i]);
    }
    uart_puts("Total argument length: ");
    uart_putdec(total_len);
    uart_puts(" bytes\n");
    
    uart_putln("=== Test Complete ===");
    return 0;
}
