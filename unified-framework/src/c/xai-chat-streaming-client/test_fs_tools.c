/**
 * @file test_fs_tools.c
 * @brief Comprehensive tests for filesystem tools
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <sys/stat.h>
#include "fs_tools.h"

#define TEST_DIR "test_fs_temp"
#define TEST_FILE "test_fs_temp/test_file.txt"
#define TEST_SUBDIR "test_fs_temp/subdir"

int tests_passed = 0;
int tests_failed = 0;

#define TEST(name) \
    printf("\n[TEST] %s\n", name); \
    if (1)

#define ASSERT(condition, message) \
    do { \
        if (!(condition)) { \
            printf("  ❌ FAIL: %s\n", message); \
            tests_failed++; \
            return; \
        } else { \
            printf("  ✓ PASS: %s\n", message); \
            tests_passed++; \
        } \
    } while (0)

// Test fixtures
void setup() {
    // Create test directory
    mkdir(TEST_DIR, 0755);
}

void teardown() {
    // Clean up test directory
    system("rm -rf " TEST_DIR);
}

// ========================================
// State Management Tests
// ========================================

void test_state_create() {
    TEST("State Create") {
        fs_session_state_t *state = fs_state_create();
        ASSERT(state != NULL, "State creation succeeds");
        ASSERT(state->working_directory != NULL, "Working directory initialized");
        ASSERT(state->initialized == 1, "State marked as initialized");
        fs_state_destroy(state);
    }
}

void test_state_change_directory() {
    TEST("State Change Directory") {
        fs_session_state_t *state = fs_state_create();

        // Change to /tmp
        int result = fs_state_change_directory(state, "/tmp");
        ASSERT(result == 0, "Change to /tmp succeeds");
        ASSERT(strcmp(state->working_directory, "/tmp") == 0 ||
               strcmp(state->working_directory, "/private/tmp") == 0, // macOS alias
               "Working directory updated to /tmp");

        // Change to invalid directory
        result = fs_state_change_directory(state, "/nonexistent_dir_12345");
        ASSERT(result == -1, "Change to nonexistent directory fails");

        fs_state_destroy(state);
    }
}

// ========================================
// PWD Tests
// ========================================

void test_pwd() {
    TEST("PWD") {
        fs_session_state_t *state = fs_state_create();

        char *cwd = fs_pwd(state);
        ASSERT(cwd != NULL, "PWD returns non-null");
        ASSERT(strlen(cwd) > 0, "PWD returns non-empty string");
        ASSERT(cwd[0] == '/', "PWD returns absolute path");

        free(cwd);
        fs_state_destroy(state);
    }
}

// ========================================
// CD Tests
// ========================================

void test_cd_success() {
    TEST("CD Success") {
        fs_session_state_t *state = fs_state_create();

        fs_cd_result_t *result = fs_cd(state, "/tmp");
        ASSERT(result != NULL, "CD result not null");
        ASSERT(result->success == 1, "CD to /tmp succeeds");
        ASSERT(result->current_directory != NULL, "Current directory returned");

        fs_cd_result_destroy(result);
        fs_state_destroy(state);
    }
}

void test_cd_failure() {
    TEST("CD Failure") {
        fs_session_state_t *state = fs_state_create();

        fs_cd_result_t *result = fs_cd(state, "/nonexistent_dir_xyz");
        ASSERT(result != NULL, "CD result not null");
        ASSERT(result->success == 0, "CD to nonexistent dir fails");
        ASSERT(result->error_message != NULL, "Error message provided");

        fs_cd_result_destroy(result);
        fs_state_destroy(state);
    }
}

// ========================================
// LS Tests
// ========================================

void test_ls() {
    TEST("LS") {
        fs_session_state_t *state = fs_state_create();

        fs_list_result_t *result = fs_ls(state, ".", 0, 1);
        ASSERT(result != NULL, "LS result not null");
        ASSERT(result->success == 1, "LS succeeds");
        ASSERT(result->entries != NULL, "Entries array returned");

        size_t num_entries = json_object_array_length(result->entries);
        ASSERT(num_entries > 0, "LS returns at least one entry");

        fs_list_result_destroy(result);
        fs_state_destroy(state);
    }
}

void test_ls_hidden() {
    TEST("LS with Hidden Files") {
        fs_session_state_t *state = fs_state_create();

        fs_list_result_t *result_no_hidden = fs_ls(state, ".", 0, 0);
        fs_list_result_t *result_with_hidden = fs_ls(state, ".", 1, 0);

        size_t count_no_hidden = json_object_array_length(result_no_hidden->entries);
        size_t count_with_hidden = json_object_array_length(result_with_hidden->entries);

        ASSERT(count_with_hidden >= count_no_hidden,
               "LS with hidden shows equal or more entries");

        fs_list_result_destroy(result_no_hidden);
        fs_list_result_destroy(result_with_hidden);
        fs_state_destroy(state);
    }
}

// ========================================
// Read File Tests
// ========================================

void test_read_file() {
    TEST("Read File") {
        fs_session_state_t *state = fs_state_create();

        // Create a test file
        FILE *f = fopen(TEST_FILE, "w");
        fprintf(f, "Hello World\nLine 2\nLine 3\n");
        fclose(f);

        fs_read_result_t *result = fs_read(state, TEST_FILE, 100);
        ASSERT(result != NULL, "Read result not null");
        ASSERT(result->success == 1, "Read succeeds");
        ASSERT(result->content != NULL, "Content returned");
        ASSERT(strstr(result->content, "Hello World") != NULL, "Content matches");
        ASSERT(result->truncated == 0, "File not truncated");

        fs_read_result_destroy(result);
        fs_state_destroy(state);
    }
}

void test_read_file_truncation() {
    TEST("Read File with Truncation") {
        fs_session_state_t *state = fs_state_create();

        // Create a test file with many lines
        FILE *f = fopen(TEST_FILE, "w");
        for (int i = 0; i < 100; i++) {
            fprintf(f, "Line %d\n", i);
        }
        fclose(f);

        fs_read_result_t *result = fs_read(state, TEST_FILE, 10);
        ASSERT(result != NULL, "Read result not null");
        ASSERT(result->success == 1, "Read succeeds");
        ASSERT(result->truncated == 1, "File truncated");

        fs_read_result_destroy(result);
        fs_state_destroy(state);
    }
}

void test_read_nonexistent() {
    TEST("Read Nonexistent File") {
        fs_session_state_t *state = fs_state_create();

        fs_read_result_t *result = fs_read(state, "nonexistent_file.txt", 100);
        ASSERT(result != NULL, "Read result not null");
        ASSERT(result->success == 0, "Read fails");
        ASSERT(result->error_message != NULL, "Error message provided");

        fs_read_result_destroy(result);
        fs_state_destroy(state);
    }
}

// ========================================
// Write File Tests
// ========================================

void test_write_file() {
    TEST("Write File") {
        fs_session_state_t *state = fs_state_create();

        const char *content = "Test content\n";
        fs_write_result_t *result = fs_write(state, TEST_FILE, content, 0);

        ASSERT(result != NULL, "Write result not null");
        ASSERT(result->success == 1, "Write succeeds");
        ASSERT(result->bytes_written == strlen(content), "Correct bytes written");

        // Verify file content
        FILE *f = fopen(TEST_FILE, "r");
        char buffer[256];
        fgets(buffer, sizeof(buffer), f);
        fclose(f);

        ASSERT(strcmp(buffer, content) == 0, "File content matches");

        fs_write_result_destroy(result);
        fs_state_destroy(state);
    }
}

void test_write_file_append() {
    TEST("Write File Append") {
        fs_session_state_t *state = fs_state_create();

        // Write initial content
        fs_write_result_t *result1 = fs_write(state, TEST_FILE, "Line 1\n", 0);
        ASSERT(result1->success == 1, "Initial write succeeds");
        fs_write_result_destroy(result1);

        // Append content
        fs_write_result_t *result2 = fs_write(state, TEST_FILE, "Line 2\n", 1);
        ASSERT(result2->success == 1, "Append write succeeds");
        fs_write_result_destroy(result2);

        // Verify both lines
        FILE *f = fopen(TEST_FILE, "r");
        char buffer[256];
        fgets(buffer, sizeof(buffer), f);
        ASSERT(strcmp(buffer, "Line 1\n") == 0, "First line correct");
        fgets(buffer, sizeof(buffer), f);
        ASSERT(strcmp(buffer, "Line 2\n") == 0, "Second line correct");
        fclose(f);

        fs_state_destroy(state);
    }
}

// ========================================
// File Info Tests
// ========================================

void test_file_info() {
    TEST("File Info") {
        fs_session_state_t *state = fs_state_create();

        // Create a test file
        FILE *f = fopen(TEST_FILE, "w");
        fprintf(f, "Test\n");
        fclose(f);

        fs_info_result_t *result = fs_info(state, TEST_FILE);
        ASSERT(result != NULL, "Info result not null");
        ASSERT(result->success == 1, "Info succeeds");
        ASSERT(result->info != NULL, "Info object returned");

        // Check for expected fields
        json_object *type_obj, *size_obj;
        ASSERT(json_object_object_get_ex(result->info, "type", &type_obj), "Type field exists");
        ASSERT(json_object_object_get_ex(result->info, "size", &size_obj), "Size field exists");

        const char *type = json_object_get_string(type_obj);
        ASSERT(strcmp(type, "file") == 0, "Type is 'file'");

        fs_info_result_destroy(result);
        fs_state_destroy(state);
    }
}

// ========================================
// Mkdir Tests
// ========================================

void test_mkdir() {
    TEST("Mkdir") {
        fs_session_state_t *state = fs_state_create();

        fs_op_result_t *result = fs_mkdir(state, TEST_SUBDIR, 0);
        ASSERT(result != NULL, "Mkdir result not null");
        ASSERT(result->success == 1, "Mkdir succeeds");

        // Verify directory exists
        struct stat st;
        ASSERT(stat(TEST_SUBDIR, &st) == 0, "Directory exists");
        ASSERT(S_ISDIR(st.st_mode), "Path is a directory");

        fs_op_result_destroy(result);
        fs_state_destroy(state);
    }
}

void test_mkdir_recursive() {
    TEST("Mkdir Recursive") {
        fs_session_state_t *state = fs_state_create();

        const char *deep_path = TEST_DIR "/a/b/c";
        fs_op_result_t *result = fs_mkdir(state, deep_path, 1);

        ASSERT(result != NULL, "Mkdir result not null");
        ASSERT(result->success == 1, "Recursive mkdir succeeds");

        // Verify directory exists
        struct stat st;
        ASSERT(stat(deep_path, &st) == 0, "Deep directory exists");

        fs_op_result_destroy(result);
        fs_state_destroy(state);
    }
}

// ========================================
// Rm Tests
// ========================================

void test_rm_file() {
    TEST("Rm File") {
        fs_session_state_t *state = fs_state_create();

        // Create a test file
        FILE *f = fopen(TEST_FILE, "w");
        fprintf(f, "Test\n");
        fclose(f);

        fs_op_result_t *result = fs_rm(state, TEST_FILE, 0);
        ASSERT(result != NULL, "Rm result not null");
        ASSERT(result->success == 1, "Rm succeeds");

        // Verify file deleted
        struct stat st;
        ASSERT(stat(TEST_FILE, &st) != 0, "File deleted");

        fs_op_result_destroy(result);
        fs_state_destroy(state);
    }
}

void test_rm_directory_recursive() {
    TEST("Rm Directory Recursive") {
        fs_session_state_t *state = fs_state_create();

        // Create directory with content
        mkdir(TEST_SUBDIR, 0755);
        FILE *f = fopen(TEST_SUBDIR "/file.txt", "w");
        fprintf(f, "Test\n");
        fclose(f);

        fs_op_result_t *result = fs_rm(state, TEST_SUBDIR, 1);
        ASSERT(result != NULL, "Rm result not null");
        ASSERT(result->success == 1, "Recursive rm succeeds");

        // Verify directory deleted
        struct stat st;
        ASSERT(stat(TEST_SUBDIR, &st) != 0, "Directory deleted");

        fs_op_result_destroy(result);
        fs_state_destroy(state);
    }
}

// ========================================
// JSON Conversion Tests
// ========================================

void test_json_conversion() {
    TEST("JSON Conversion") {
        fs_session_state_t *state = fs_state_create();

        // Test CD result
        fs_cd_result_t *cd_result = fs_cd(state, "/tmp");
        char *cd_json = fs_cd_result_to_json(cd_result);
        ASSERT(cd_json != NULL, "CD result converts to JSON");
        ASSERT(strstr(cd_json, "success") != NULL, "JSON contains success field");
        free(cd_json);
        fs_cd_result_destroy(cd_result);

        // Test LS result
        fs_list_result_t *ls_result = fs_ls(state, ".", 0, 0);
        char *ls_json = fs_list_result_to_json(ls_result);
        ASSERT(ls_json != NULL, "LS result converts to JSON");
        ASSERT(strstr(ls_json, "entries") != NULL, "JSON contains entries field");
        free(ls_json);
        fs_list_result_destroy(ls_result);

        fs_state_destroy(state);
    }
}

// ========================================
// Main Test Runner
// ========================================

int main() {
    printf("========================================\n");
    printf("Filesystem Tools Test Suite\n");
    printf("========================================\n");

    setup();

    // Run all tests
    test_state_create();
    test_state_change_directory();
    test_pwd();
    test_cd_success();
    test_cd_failure();
    test_ls();
    test_ls_hidden();
    test_read_file();
    test_read_file_truncation();
    test_read_nonexistent();
    test_write_file();
    test_write_file_append();
    test_file_info();
    test_mkdir();
    test_mkdir_recursive();
    test_rm_file();
    test_rm_directory_recursive();
    test_json_conversion();

    teardown();

    printf("\n========================================\n");
    printf("Test Results\n");
    printf("========================================\n");
    printf("✓ Passed: %d\n", tests_passed);
    printf("❌ Failed: %d\n", tests_failed);
    printf("========================================\n");

    return tests_failed > 0 ? 1 : 0;
}
