/*
 * Test argc/argv/envp setup
 */

#include <stdio.h>
#include <string.h>

// External variables set by crt0
extern char **environ;

int main(int argc, char **argv, char **envp) {
    printf("=== Test argc/argv/envp ===\n\n");
    
    // Test 1: argc
    printf("[1] argc = %d\n", argc);
    if (argc < 1) {
        printf("    FAIL: argc should be at least 1\n");
        return 1;
    }
    printf("    PASS\n");
    
    // Test 2: argv
    printf("\n[2] argv contents:\n");
    for (int i = 0; i < argc; i++) {
        if (argv[i] == NULL) {
            printf("    FAIL: argv[%d] is NULL\n", i);
            return 1;
        }
        printf("    argv[%d] = \"%s\"\n", i, argv[i]);
    }
    if (argv[argc] != NULL) {
        printf("    FAIL: argv[%d] should be NULL\n", argc);
        return 1;
    }
    printf("    argv[%d] = NULL (correct)\n", argc);
    printf("    PASS\n");
    
    // Test 3: envp via function parameter
    printf("\n[3] envp via parameter:\n");
    if (envp == NULL) {
        printf("    envp is NULL\n");
    } else {
        int env_count = 0;
        while (envp[env_count] != NULL) {
            printf("    envp[%d] = \"%s\"\n", env_count, envp[env_count]);
            env_count++;
        }
        printf("    Found %d environment variables\n", env_count);
        printf("    PASS\n");
    }
    
    // Test 4: environ global variable
    printf("\n[4] environ global variable:\n");
    if (environ == NULL) {
        printf("    environ is NULL\n");
    } else {
        int env_count = 0;
        while (environ[env_count] != NULL) {
            printf("    environ[%d] = \"%s\"\n", env_count, environ[env_count]);
            env_count++;
        }
        printf("    Found %d environment variables\n", env_count);
        printf("    PASS\n");
    }
    
    // Test 5: getenv() function
    printf("\n[5] getenv() function:\n");
    char *path = getenv("PATH");
    if (path) {
        printf("    PATH = \"%s\"\n", path);
        printf("    PASS\n");
    } else {
        printf("    PATH not found (may be expected if no env set)\n");
        printf("    PASS\n");
    }
    
    char *test_var = getenv("TEST");
    if (test_var) {
        printf("    TEST = \"%s\"\n", test_var);
        printf("    PASS\n");
    } else {
        printf("    TEST not found\n");
    }
    
    printf("\n=== All tests passed! ===\n");
    return 0;
}
