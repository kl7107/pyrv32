/*
 * Simple command interpreter test program
 * Accepts commands and returns results on console UART
 */

#define CONSOLE_UART_TX      0x10001000
#define CONSOLE_UART_RX      0x10001004
#define CONSOLE_UART_RX_STATUS 0x10001008

// Console UART functions
void console_putc(char c) {
    volatile char *uart_tx = (volatile char *)CONSOLE_UART_TX;
    *uart_tx = c;
}

void console_puts(const char* s) {
    while (*s) {
        console_putc(*s++);
    }
}

void console_put_hex(unsigned int val) {
    const char* hex = "0123456789ABCDEF";
    console_putc(hex[(val >> 28) & 0xF]);
    console_putc(hex[(val >> 24) & 0xF]);
    console_putc(hex[(val >> 20) & 0xF]);
    console_putc(hex[(val >> 16) & 0xF]);
    console_putc(hex[(val >> 12) & 0xF]);
    console_putc(hex[(val >> 8) & 0xF]);
    console_putc(hex[(val >> 4) & 0xF]);
    console_putc(hex[val & 0xF]);
}

void console_put_dec(int val) {
    if (val < 0) {
        console_putc('-');
        val = -val;
    }
    
    char buf[12];
    int i = 0;
    
    if (val == 0) {
        console_putc('0');
        return;
    }
    
    while (val > 0) {
        buf[i++] = '0' + (val % 10);
        val /= 10;
    }
    
    while (i > 0) {
        console_putc(buf[--i]);
    }
}

int console_has_char() {
    volatile unsigned char *uart_status = (volatile unsigned char *)CONSOLE_UART_RX_STATUS;
    return *uart_status != 0;
}

char console_getc() {
    volatile unsigned char *uart_rx = (volatile unsigned char *)CONSOLE_UART_RX;
    while (!console_has_char());
    return *uart_rx;
}

// Simple string comparison
int str_eq(const char* a, const char* b) {
    while (*a && *b) {
        if (*a != *b) return 0;
        a++;
        b++;
    }
    return *a == *b;
}

// Parse a decimal number
int parse_num(const char* s) {
    int val = 0;
    int neg = 0;
    
    if (*s == '-') {
        neg = 1;
        s++;
    }
    
    while (*s >= '0' && *s <= '9') {
        val = val * 10 + (*s - '0');
        s++;
    }
    
    return neg ? -val : val;
}

// Read a line from UART into buffer
void read_line(char* buf, int max_len) {
    int i = 0;
    
    while (i < max_len - 1) {
        char c = console_getc();
        
        // Echo character
        console_putc(c);
        
        if (c == '\r' || c == '\n') {
            console_puts("\r\n");
            break;
        }
        
        if (c == '\b' || c == 127) {  // Backspace
            if (i > 0) {
                i--;
                console_puts(" \b");  // Erase character
            }
        } else {
            buf[i++] = c;
        }
    }
    
    buf[i] = '\0';
}

// Tokenize command line
void tokenize(char* line, char** tokens, int* count, int max_tokens) {
    *count = 0;
    char* p = line;
    
    while (*p && *count < max_tokens) {
        // Skip whitespace
        while (*p == ' ' || *p == '\t') p++;
        
        if (*p == '\0') break;
        
        tokens[(*count)++] = p;
        
        // Find end of token
        while (*p && *p != ' ' && *p != '\t') p++;
        
        if (*p) {
            *p = '\0';
            p++;
        }
    }
}

int main() {
    char line_buf[128];
    char* tokens[10];
    int token_count;
    
    console_puts("\r\n=== Simple Command Interpreter ===\r\n");
    console_puts("Commands:\r\n");
    console_puts("  ADD <a> <b>   - Add two numbers\r\n");
    console_puts("  SUB <a> <b>   - Subtract b from a\r\n");
    console_puts("  MUL <a> <b>   - Multiply two numbers\r\n");
    console_puts("  HEX <n>       - Show number in hex\r\n");
    console_puts("  ECHO <text>   - Echo back text\r\n");
    console_puts("  QUIT          - Exit interpreter\r\n");
    console_puts("==================================\r\n\r\n");
    
    while (1) {
        console_puts("> ");
        read_line(line_buf, sizeof(line_buf));
        
        tokenize(line_buf, tokens, &token_count, 10);
        
        if (token_count == 0) {
            continue;
        }
        
        const char* cmd = tokens[0];
        
        if (str_eq(cmd, "QUIT") || str_eq(cmd, "quit")) {
            console_puts("Goodbye!\r\n");
            break;
        }
        else if (str_eq(cmd, "ADD") || str_eq(cmd, "add")) {
            if (token_count < 3) {
                console_puts("ERROR: ADD requires 2 arguments\r\n");
            } else {
                int a = parse_num(tokens[1]);
                int b = parse_num(tokens[2]);
                int result = a + b;
                console_put_dec(result);
                console_puts("\r\n");
            }
        }
        else if (str_eq(cmd, "SUB") || str_eq(cmd, "sub")) {
            if (token_count < 3) {
                console_puts("ERROR: SUB requires 2 arguments\r\n");
            } else {
                int a = parse_num(tokens[1]);
                int b = parse_num(tokens[2]);
                int result = a - b;
                console_put_dec(result);
                console_puts("\r\n");
            }
        }
        else if (str_eq(cmd, "MUL") || str_eq(cmd, "mul")) {
            if (token_count < 3) {
                console_puts("ERROR: MUL requires 2 arguments\r\n");
            } else {
                int a = parse_num(tokens[1]);
                int b = parse_num(tokens[2]);
                int result = a * b;
                console_put_dec(result);
                console_puts("\r\n");
            }
        }
        else if (str_eq(cmd, "HEX") || str_eq(cmd, "hex")) {
            if (token_count < 2) {
                console_puts("ERROR: HEX requires 1 argument\r\n");
            } else {
                int val = parse_num(tokens[1]);
                console_puts("0x");
                console_put_hex(val);
                console_puts("\r\n");
            }
        }
        else if (str_eq(cmd, "ECHO") || str_eq(cmd, "echo")) {
            for (int i = 1; i < token_count; i++) {
                console_puts(tokens[i]);
                if (i < token_count - 1) console_putc(' ');
            }
            console_puts("\r\n");
        }
        else {
            console_puts("ERROR: Unknown command '");
            console_puts(cmd);
            console_puts("'\r\n");
        }
    }
    
    return 0;
}
