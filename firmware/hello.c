/*
 * Hello World - Minimal bare-metal C program for RV32IM
 */

/* Runtime functions (UART output) */
void uart_putc(char c);
void uart_puts(const char *s);
void uart_putln(const char *s);
void uart_puthex(unsigned int value);
void uart_putdec(int value);

int main(void) {
    uart_putln("Hello, World from RV32IM!");
    uart_puts("This is a C program running on PyRV32.");
    uart_putc('\n');
    
    /* Test some arithmetic */
    int a = 42;
    int b = 13;
    int sum = a + b;
    
    uart_puts("Testing arithmetic: ");
    uart_putdec(a);
    uart_puts(" + ");
    uart_putdec(b);
    uart_puts(" = ");
    uart_putdec(sum);
    uart_putc('\n');
    
    /* Test hex output */
    uart_puts("Hex value: ");
    uart_puthex(0xDEADBEEF);
    uart_putc('\n');
    
    uart_putln("Program complete!");
    
    return 0;
}
