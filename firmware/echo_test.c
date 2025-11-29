/*
 * Simple echo test program
 * Reads from console UART RX and echoes back to console UART TX
 */

#define CONSOLE_UART_TX      0x10001000
#define CONSOLE_UART_RX      0x10001004
#define CONSOLE_UART_RX_STATUS 0x10001008

// Console UART functions (different from debug UART in runtime.c)
void console_putc(char c) {
    volatile char *uart_tx = (volatile char *)CONSOLE_UART_TX;
    *uart_tx = c;
}

void console_puts(const char* s) {
    while (*s) {
        console_putc(*s++);
    }
}

int console_has_char() {
    volatile unsigned char *uart_status = (volatile unsigned char *)CONSOLE_UART_RX_STATUS;
    return *uart_status != 0;
}

char console_getc() {
    volatile unsigned char *uart_rx = (volatile unsigned char *)CONSOLE_UART_RX;
    while (!console_has_char());  // Wait for character
    return *uart_rx;
}

int main() {
    console_puts("Echo test ready. Type characters and see them echoed back.\r\n");
    console_puts("Send 'Q' to quit.\r\n");
    
    while (1) {
        // Wait for and read a character
        char c = console_getc();
        
        // Echo it back
        console_putc(c);
        
        // Quit on 'Q'
        if (c == 'Q' || c == 'q') {
            console_puts("\r\nQuitting...\r\n");
            break;
        }
    }
    
    return 0;
}
