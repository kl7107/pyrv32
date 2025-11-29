/*
 * Test program for file-related syscalls
 * Tests: chdir, getcwd, link, unlink, rename, access
 */

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>

void test_getcwd_chdir() {
    char cwd[256];
    
    printf("\n=== Testing getcwd/chdir ===\n");
    
    // Get initial cwd
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        printf("Initial CWD: %s\n", cwd);
    } else {
        printf("ERROR: getcwd failed: %s\n", strerror(errno));
    }
    
    // Test chdir to /tmp
    if (chdir("/tmp") == 0) {
        printf("chdir /tmp: OK\n");
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            printf("New CWD: %s\n", cwd);
        }
    } else {
        printf("ERROR: chdir /tmp failed: %s\n", strerror(errno));
    }
    
    // Test chdir back to root
    if (chdir("/") == 0) {
        printf("chdir /: OK\n");
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            printf("New CWD: %s\n", cwd);
        }
    } else {
        printf("ERROR: chdir / failed: %s\n", strerror(errno));
    }
}

void test_link_unlink() {
    int fd;
    char buf[32];
    
    printf("\n=== Testing link/unlink ===\n");
    
    // Create original file
    fd = open("/tmp/original.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("ERROR: open /tmp/original.txt failed: %s\n", strerror(errno));
        return;
    }
    write(fd, "test data", 9);
    close(fd);
    printf("Created /tmp/original.txt\n");
    
    // Create hard link
    if (link("/tmp/original.txt", "/tmp/linked.txt") == 0) {
        printf("link /tmp/original.txt -> /tmp/linked.txt: OK\n");
        
        // Verify link exists and has same content
        fd = open("/tmp/linked.txt", O_RDONLY);
        if (fd >= 0) {
            int n = read(fd, buf, sizeof(buf));
            buf[n] = '\0';
            printf("Read from link: '%s'\n", buf);
            close(fd);
        } else {
            printf("ERROR: open /tmp/linked.txt failed: %s\n", strerror(errno));
        }
    } else {
        printf("ERROR: link failed: %s\n", strerror(errno));
    }
    
    // Test unlink original
    if (unlink("/tmp/original.txt") == 0) {
        printf("unlink /tmp/original.txt: OK\n");
        
        // Verify link still exists
        fd = open("/tmp/linked.txt", O_RDONLY);
        if (fd >= 0) {
            printf("Link still accessible after unlinking original: OK\n");
            close(fd);
        } else {
            printf("ERROR: link disappeared after unlink: %s\n", strerror(errno));
        }
    } else {
        printf("ERROR: unlink failed: %s\n", strerror(errno));
    }
    
    // Clean up
    unlink("/tmp/linked.txt");
}

void test_rename() {
    int fd;
    
    printf("\n=== Testing rename ===\n");
    
    // Create file to rename
    fd = open("/tmp/oldname.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("ERROR: open /tmp/oldname.txt failed: %s\n", strerror(errno));
        return;
    }
    write(fd, "rename test", 11);
    close(fd);
    printf("Created /tmp/oldname.txt\n");
    
    // Rename it
    if (rename("/tmp/oldname.txt", "/tmp/newname.txt") == 0) {
        printf("rename /tmp/oldname.txt -> /tmp/newname.txt: OK\n");
        
        // Verify old name doesn't exist
        if (access("/tmp/oldname.txt", F_OK) < 0) {
            printf("Old name no longer exists: OK\n");
        } else {
            printf("ERROR: Old name still exists after rename\n");
        }
        
        // Verify new name exists
        if (access("/tmp/newname.txt", F_OK) == 0) {
            printf("New name exists: OK\n");
        } else {
            printf("ERROR: New name doesn't exist: %s\n", strerror(errno));
        }
    } else {
        printf("ERROR: rename failed: %s\n", strerror(errno));
    }
    
    // Clean up
    unlink("/tmp/newname.txt");
}

void test_access() {
    int fd;
    
    printf("\n=== Testing access ===\n");
    
    // Create test file with specific permissions
    fd = open("/tmp/access_test.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("ERROR: open /tmp/access_test.txt failed: %s\n", strerror(errno));
        return;
    }
    close(fd);
    printf("Created /tmp/access_test.txt (mode 0644)\n");
    
    // Test F_OK (existence)
    if (access("/tmp/access_test.txt", F_OK) == 0) {
        printf("access F_OK: OK (file exists)\n");
    } else {
        printf("ERROR: access F_OK failed: %s\n", strerror(errno));
    }
    
    // Test R_OK (read permission)
    if (access("/tmp/access_test.txt", R_OK) == 0) {
        printf("access R_OK: OK (readable)\n");
    } else {
        printf("ERROR: access R_OK failed: %s\n", strerror(errno));
    }
    
    // Test W_OK (write permission)
    if (access("/tmp/access_test.txt", W_OK) == 0) {
        printf("access W_OK: OK (writable)\n");
    } else {
        printf("ERROR: access W_OK failed: %s\n", strerror(errno));
    }
    
    // Test non-existent file
    if (access("/tmp/nonexistent.txt", F_OK) < 0) {
        printf("access F_OK on nonexistent: correctly failed (%s)\n", strerror(errno));
    } else {
        printf("ERROR: access F_OK on nonexistent should have failed\n");
    }
    
    // Clean up
    unlink("/tmp/access_test.txt");
}

void test_stat() {
    int fd;
    struct stat st;
    
    printf("\n=== Testing stat/fstat ===\n");
    
    // Create test file
    fd = open("/tmp/stat_test.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("ERROR: open /tmp/stat_test.txt failed: %s\n", strerror(errno));
        return;
    }
    write(fd, "0123456789", 10);
    printf("Created /tmp/stat_test.txt (10 bytes)\n");
    
    // Test fstat on open fd
    if (fstat(fd, &st) == 0) {
        printf("fstat: OK\n");
        printf("  st_size: %lld\n", (long long)st.st_size);
        printf("  st_mode: 0%o\n", st.st_mode & 0777);
        printf("  st_nlink: %d\n", (int)st.st_nlink);
    } else {
        printf("ERROR: fstat failed: %s\n", strerror(errno));
    }
    
    close(fd);
    
    // Test stat by path
    if (stat("/tmp/stat_test.txt", &st) == 0) {
        printf("stat: OK\n");
        printf("  st_size: %lld\n", (long long)st.st_size);
        printf("  st_mode: 0%o\n", st.st_mode & 0777);
    } else {
        printf("ERROR: stat failed: %s\n", strerror(errno));
    }
    
    // Clean up
    unlink("/tmp/stat_test.txt");
}

int main() {
    printf("=== File Syscall Tests ===\n");
    
    test_getcwd_chdir();
    test_link_unlink();
    test_rename();
    test_access();
    test_stat();
    
    printf("\n=== All tests complete ===\n");
    return 0;
}
