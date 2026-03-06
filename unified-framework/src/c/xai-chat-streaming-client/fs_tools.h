/**
 * @file fs_tools.h
 * @brief Filesystem Tools for XAI Chat Client
 *
 * Provides structured filesystem operations as individual tools with
 * type-safe parameters, state management, and better safety than raw bash.
 */

#ifndef FS_TOOLS_H
#define FS_TOOLS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <json-c/json.h>

// Session state for maintaining working directory across tool calls
typedef struct {
    char *working_directory;
    char *home_directory;
    int initialized;
} fs_session_state_t;

// Result structures for different operations
typedef struct {
    char *current_directory;
    char *error_message;
    int success;
} fs_cd_result_t;

typedef struct {
    json_object *entries;  // Array of file entries
    char *error_message;
    int success;
} fs_list_result_t;

typedef struct {
    char *content;
    size_t size;
    int truncated;
    char *error_message;
    int success;
} fs_read_result_t;

typedef struct {
    size_t bytes_written;
    char *error_message;
    int success;
} fs_write_result_t;

typedef struct {
    json_object *info;  // File metadata
    char *error_message;
    int success;
} fs_info_result_t;

typedef struct {
    char *error_message;
    int success;
} fs_op_result_t;

// Session state management
fs_session_state_t* fs_state_create(void);
void fs_state_destroy(fs_session_state_t *state);
int fs_state_change_directory(fs_session_state_t *state, const char *path);
const char* fs_state_get_directory(fs_session_state_t *state);

// Tool definitions for registration with XAI API
json_object* fs_tool_pwd_definition(void);
json_object* fs_tool_cd_definition(void);
json_object* fs_tool_ls_definition(void);
json_object* fs_tool_read_definition(void);
json_object* fs_tool_write_definition(void);
json_object* fs_tool_info_definition(void);
json_object* fs_tool_mkdir_definition(void);
json_object* fs_tool_rm_definition(void);

// Tool implementations
char* fs_pwd(fs_session_state_t *state);
fs_cd_result_t* fs_cd(fs_session_state_t *state, const char *path);
fs_list_result_t* fs_ls(fs_session_state_t *state, const char *path, int show_hidden, int long_format);
fs_read_result_t* fs_read(fs_session_state_t *state, const char *path, int max_lines);
fs_write_result_t* fs_write(fs_session_state_t *state, const char *path, const char *content, int append);
fs_info_result_t* fs_info(fs_session_state_t *state, const char *path);
fs_op_result_t* fs_mkdir(fs_session_state_t *state, const char *path, int recursive);
fs_op_result_t* fs_rm(fs_session_state_t *state, const char *path, int recursive);

// Result cleanup
void fs_cd_result_destroy(fs_cd_result_t *result);
void fs_list_result_destroy(fs_list_result_t *result);
void fs_read_result_destroy(fs_read_result_t *result);
void fs_write_result_destroy(fs_write_result_t *result);
void fs_info_result_destroy(fs_info_result_t *result);
void fs_op_result_destroy(fs_op_result_t *result);

// Convert results to JSON strings
char* fs_cd_result_to_json(fs_cd_result_t *result);
char* fs_list_result_to_json(fs_list_result_t *result);
char* fs_read_result_to_json(fs_read_result_t *result);
char* fs_write_result_to_json(fs_write_result_t *result);
char* fs_info_result_to_json(fs_info_result_t *result);
char* fs_op_result_to_json(fs_op_result_t *result);

#endif // FS_TOOLS_H
