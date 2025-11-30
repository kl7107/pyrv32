/*
 * Test fopen with relative paths
 */

void uart_puts(const char *s);
void uart_putln(const char *s);

// Minimal FILE structure
typedef struct {
    int fd;
} FILE;

extern FILE *fopen(const char *filename, const char *mode);
extern int fclose(FILE *fp);

int main(void) {
    uart_putln("Testing fopen with ../dat/data.base");
    
    FILE *fp = fopen("../dat/data.base", "r");
    if (fp) {
        uart_putln("SUCCESS: File opened!");
        fclose(fp);
    } else {
        uart_putln("FAILED: Could not open file");
    }
    
    uart_putln("Testing fopen with dat/data.base");
    fp = fopen("dat/data.base", "r");
    if (fp) {
        uart_putln("SUCCESS: File opened!");
        fclose(fp);
    } else {
        uart_putln("FAILED: Could not open file");
    }
    
    uart_putln("Testing fopen with /dat/data.base");
    fp = fopen("/dat/data.base", "r");
    if (fp) {
        uart_putln("SUCCESS: File opened!");
        fclose(fp);
    } else {
        uart_putln("FAILED: Could not open file");
    }
    
    return 0;
}
