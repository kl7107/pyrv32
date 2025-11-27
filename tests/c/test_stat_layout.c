/*
 * Test to print stat structure layout
 */

#include <stdio.h>
#include <sys/stat.h>
#include <stddef.h>

int main(void) {
    printf("sizeof(struct stat) = %zu\n", sizeof(struct stat));
    printf("offsetof(st_dev) = %zu\n", offsetof(struct stat, st_dev));
    printf("offsetof(st_ino) = %zu\n", offsetof(struct stat, st_ino));
    printf("offsetof(st_mode) = %zu\n", offsetof(struct stat, st_mode));
    printf("offsetof(st_nlink) = %zu\n", offsetof(struct stat, st_nlink));
    printf("offsetof(st_uid) = %zu\n", offsetof(struct stat, st_uid));
    printf("offsetof(st_gid) = %zu\n", offsetof(struct stat, st_gid));
    printf("offsetof(st_rdev) = %zu\n", offsetof(struct stat, st_rdev));
    printf("offsetof(st_size) = %zu\n", offsetof(struct stat, st_size));
    
    printf("PASS\n");
    return 0;
}
