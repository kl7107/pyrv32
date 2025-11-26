/*
 * Fibonacci Calculator - Demonstrates recursion and arithmetic
 */

void uart_putc(char c);
void uart_puts(const char *s);
void uart_putln(const char *s);
void uart_puthex(unsigned int value);
void uart_putdec(int value);

/* Recursive Fibonacci */
int fib(int n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

/* Iterative Fibonacci (more efficient) */
int fib_iter(int n) {
    if (n <= 1) {
        return n;
    }
    
    int a = 0;
    int b = 1;
    
    for (int i = 2; i <= n; i++) {
        int temp = a + b;
        a = b;
        b = temp;
    }
    
    return b;
}

int main(void) {
    uart_putln("Fibonacci Calculator");
    uart_putln("====================");
    uart_putc('\n');
    
    /* Calculate first 15 Fibonacci numbers */
    uart_putln("First 15 Fibonacci numbers:");
    for (int i = 0; i < 15; i++) {
        uart_puts("fib(");
        uart_putdec(i);
        uart_puts(") = ");
        uart_putdec(fib_iter(i));
        uart_putc('\n');
    }
    
    uart_putc('\n');
    uart_putln("Testing recursive vs iterative:");
    
    int n = 10;
    int rec_result = fib(n);
    int iter_result = fib_iter(n);
    
    uart_puts("Recursive fib(");
    uart_putdec(n);
    uart_puts(") = ");
    uart_putdec(rec_result);
    uart_putc('\n');
    
    uart_puts("Iterative fib(");
    uart_putdec(n);
    uart_puts(") = ");
    uart_putdec(iter_result);
    uart_putc('\n');
    
    if (rec_result == iter_result) {
        uart_putln("\n✓ Results match!");
    } else {
        uart_putln("\n✗ Results don't match!");
    }
    
    uart_putln("\nDone!");
    
    return 0;
}
