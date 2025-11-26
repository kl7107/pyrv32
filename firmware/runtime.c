/*
 * Minimal runtime library for bare-metal RV32IM
 * Provides basic UART output functions
 */

#define UART_TX_ADDR 0x10000000

/* Write a single character to UART */
void uart_putc(char c) {
    volatile char *uart = (volatile char *)UART_TX_ADDR;
    *uart = c;
}

/* Write a null-terminated string to UART */
void uart_puts(const char *s) {
    while (*s) {
        uart_putc(*s);
        s++;
    }
}

/* Write a string with newline */
void uart_putln(const char *s) {
    uart_puts(s);
    uart_putc('\n');
}

/* Write a 32-bit hex value */
void uart_puthex(unsigned int value) {
    const char hex[] = "0123456789ABCDEF";
    uart_puts("0x");
    for (int i = 28; i >= 0; i -= 4) {
        uart_putc(hex[(value >> i) & 0xF]);
    }
}

/* Write a decimal value (simple, no division needed for small values) */
void uart_putdec(int value) {
    if (value < 0) {
        uart_putc('-');
        value = -value;
    }
    
    if (value == 0) {
        uart_putc('0');
        return;
    }
    
    char buf[12];  /* Max 10 digits + sign + null */
    int i = 0;
    
    while (value > 0) {
        buf[i++] = '0' + (value % 10);
        value /= 10;
    }
    
    /* Print in reverse (most significant first) */
    while (i > 0) {
        uart_putc(buf[--i]);
    }
}
