/**
 * @file fs_tools.c
 * @brief Filesystem Tools Implementation
 */

#include "fs_tools.h"
#include <unistd.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include <time.h>
#include <pwd.h>
#include <grp.h>
#include <libgen.h>
#include <limits.h>

// =============================================================================
// Session State Management
// =============================================================================

fs_session_state_t* fs_state_create(void) {
    fs_session_state_t *state = calloc(1, sizeof(fs_session_state_t));
    if (!state) {
        return NULL;
    }

    char cwd[PATH_MAX];
    if (getcwd(cwd, sizeof(cwd))) {
        state->working_directory = strdup(cwd);
        state->home_directory = strdup(cwd);
        state->initialized = 1;
    } else {
        free(state);
        return NULL;
    }

    return state;
}

void fs_state_destroy(fs_session_state_t *state) {
    if (!state) return;

    free(state->working_directory);
    free(state->home_directory);
    free(state);
}

int fs_state_change_directory(fs_session_state_t *state, const char *path) {
    if (!state || !path) return -1;

    char resolved_path[PATH_MAX];

    // Handle relative paths
    if (path[0] != '/') {
        snprintf(resolved_path, sizeof(resolved_path), "%s/%s", state->working_directory, path);
    } else {
        strncpy(resolved_path, path, sizeof(resolved_path) - 1);
        resolved_path[sizeof(resolved_path) - 1] = '\0';
    }

    // Canonicalize path
    char *canonical = realpath(resolved_path, NULL);
    if (!canonical) {
        return -1;
    }

    // Verify it's a directory
    struct stat st;
    if (stat(canonical, &st) != 0 || !S_ISDIR(st.st_mode)) {
        free(canonical);
        return -1;
    }

    // Update state
    free(state->working_directory);
    state->working_directory = canonical;

    return 0;
}

const char* fs_state_get_directory(fs_session_state_t *state) {
    if (!state) return NULL;
    return state->working_directory;
}

// =============================================================================
// Tool Definitions
// =============================================================================

json_object* fs_tool_pwd_definition(void) {
    json_object *tool = json_object_new_object();
    json_object_object_add(tool, "type", json_object_new_string("function"));

    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("pwd"));
    json_object_object_add(function, "description",
        json_object_new_string("Get current working directory"));

    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));
    json_object_object_add(parameters, "properties", json_object_new_object());

    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(tool, "function", function);

    return tool;
}

json_object* fs_tool_cd_definition(void) {
    json_object *tool = json_object_new_object();
    json_object_object_add(tool, "type", json_object_new_string("function"));

    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("cd"));
    json_object_object_add(function, "description",
        json_object_new_string("Change current working directory"));

    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));

    json_object *properties = json_object_new_object();
    json_object *path_prop = json_object_new_object();
    json_object_object_add(path_prop, "type", json_object_new_string("string"));
    json_object_object_add(path_prop, "description",
        json_object_new_string("Target directory path"));
    json_object_object_add(properties, "path", path_prop);
    json_object_object_add(parameters, "properties", properties);

    json_object *required = json_object_new_array();
    json_object_array_add(required, json_object_new_string("path"));
    json_object_object_add(parameters, "required", required);

    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(tool, "function", function);

    return tool;
}

json_object* fs_tool_ls_definition(void) {
    json_object *tool = json_object_new_object();
    json_object_object_add(tool, "type", json_object_new_string("function"));

    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("ls"));
    json_object_object_add(function, "description",
        json_object_new_string("List directory contents with metadata"));

    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));

    json_object *properties = json_object_new_object();

    json_object *path_prop = json_object_new_object();
    json_object_object_add(path_prop, "type", json_object_new_string("string"));
    json_object_object_add(path_prop, "description",
        json_object_new_string("Directory path (default: current directory)"));
    json_object_object_add(properties, "path", path_prop);

    json_object *hidden_prop = json_object_new_object();
    json_object_object_add(hidden_prop, "type", json_object_new_string("boolean"));
    json_object_object_add(hidden_prop, "description",
        json_object_new_string("Show hidden files (default: false)"));
    json_object_object_add(properties, "show_hidden", hidden_prop);

    json_object *long_prop = json_object_new_object();
    json_object_object_add(long_prop, "type", json_object_new_string("boolean"));
    json_object_object_add(long_prop, "description",
        json_object_new_string("Show detailed file information (default: true)"));
    json_object_object_add(properties, "long_format", long_prop);

    json_object_object_add(parameters, "properties", properties);

    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(tool, "function", function);

    return tool;
}

json_object* fs_tool_read_definition(void) {
    json_object *tool = json_object_new_object();
    json_object_object_add(tool, "type", json_object_new_string("function"));

    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("read_file"));
    json_object_object_add(function, "description",
        json_object_new_string("Read file contents with optional line limit"));

    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));

    json_object *properties = json_object_new_object();

    json_object *path_prop = json_object_new_object();
    json_object_object_add(path_prop, "type", json_object_new_string("string"));
    json_object_object_add(path_prop, "description", json_object_new_string("File path to read"));
    json_object_object_add(properties, "path", path_prop);

    json_object *lines_prop = json_object_new_object();
    json_object_object_add(lines_prop, "type", json_object_new_string("integer"));
    json_object_object_add(lines_prop, "description",
        json_object_new_string("Maximum number of lines to read (default: 1000)"));
    json_object_object_add(properties, "max_lines", lines_prop);

    json_object_object_add(parameters, "properties", properties);

    json_object *required = json_object_new_array();
    json_object_array_add(required, json_object_new_string("path"));
    json_object_object_add(parameters, "required", required);

    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(tool, "function", function);

    return tool;
}

json_object* fs_tool_write_definition(void) {
    json_object *tool = json_object_new_object();
    json_object_object_add(tool, "type", json_object_new_string("function"));

    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("write_file"));
    json_object_object_add(function, "description",
        json_object_new_string("Write content to a file"));

    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));

    json_object *properties = json_object_new_object();

    json_object *path_prop = json_object_new_object();
    json_object_object_add(path_prop, "type", json_object_new_string("string"));
    json_object_object_add(path_prop, "description", json_object_new_string("File path to write"));
    json_object_object_add(properties, "path", path_prop);

    json_object *content_prop = json_object_new_object();
    json_object_object_add(content_prop, "type", json_object_new_string("string"));
    json_object_object_add(content_prop, "description", json_object_new_string("Content to write"));
    json_object_object_add(properties, "content", content_prop);

    json_object *append_prop = json_object_new_object();
    json_object_object_add(append_prop, "type", json_object_new_string("boolean"));
    json_object_object_add(append_prop, "description",
        json_object_new_string("Append to file instead of overwriting (default: false)"));
    json_object_object_add(properties, "append", append_prop);

    json_object_object_add(parameters, "properties", properties);

    json_object *required = json_object_new_array();
    json_object_array_add(required, json_object_new_string("path"));
    json_object_array_add(required, json_object_new_string("content"));
    json_object_object_add(parameters, "required", required);

    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(tool, "function", function);

    return tool;
}

json_object* fs_tool_info_definition(void) {
    json_object *tool = json_object_new_object();
    json_object_object_add(tool, "type", json_object_new_string("function"));

    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("file_info"));
    json_object_object_add(function, "description",
        json_object_new_string("Get detailed file or directory metadata"));

    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));

    json_object *properties = json_object_new_object();

    json_object *path_prop = json_object_new_object();
    json_object_object_add(path_prop, "type", json_object_new_string("string"));
    json_object_object_add(path_prop, "description", json_object_new_string("Path to inspect"));
    json_object_object_add(properties, "path", path_prop);

    json_object_object_add(parameters, "properties", properties);

    json_object *required = json_object_new_array();
    json_object_array_add(required, json_object_new_string("path"));
    json_object_object_add(parameters, "required", required);

    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(tool, "function", function);

    return tool;
}

json_object* fs_tool_mkdir_definition(void) {
    json_object *tool = json_object_new_object();
    json_object_object_add(tool, "type", json_object_new_string("function"));

    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("mkdir"));
    json_object_object_add(function, "description",
        json_object_new_string("Create a new directory"));

    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));

    json_object *properties = json_object_new_object();

    json_object *path_prop = json_object_new_object();
    json_object_object_add(path_prop, "type", json_object_new_string("string"));
    json_object_object_add(path_prop, "description", json_object_new_string("Directory path to create"));
    json_object_object_add(properties, "path", path_prop);

    json_object *recursive_prop = json_object_new_object();
    json_object_object_add(recursive_prop, "type", json_object_new_string("boolean"));
    json_object_object_add(recursive_prop, "description",
        json_object_new_string("Create parent directories if needed (default: false)"));
    json_object_object_add(properties, "recursive", recursive_prop);

    json_object_object_add(parameters, "properties", properties);

    json_object *required = json_object_new_array();
    json_object_array_add(required, json_object_new_string("path"));
    json_object_object_add(parameters, "required", required);

    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(tool, "function", function);

    return tool;
}

json_object* fs_tool_rm_definition(void) {
    json_object *tool = json_object_new_object();
    json_object_object_add(tool, "type", json_object_new_string("function"));

    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("rm"));
    json_object_object_add(function, "description",
        json_object_new_string("Remove a file or directory"));

    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));

    json_object *properties = json_object_new_object();

    json_object *path_prop = json_object_new_object();
    json_object_object_add(path_prop, "type", json_object_new_string("string"));
    json_object_object_add(path_prop, "description", json_object_new_string("Path to remove"));
    json_object_object_add(properties, "path", path_prop);

    json_object *recursive_prop = json_object_new_object();
    json_object_object_add(recursive_prop, "type", json_object_new_string("boolean"));
    json_object_object_add(recursive_prop, "description",
        json_object_new_string("Remove directories recursively (default: false)"));
    json_object_object_add(properties, "recursive", recursive_prop);

    json_object_object_add(parameters, "properties", properties);

    json_object *required = json_object_new_array();
    json_object_array_add(required, json_object_new_string("path"));
    json_object_object_add(parameters, "required", required);

    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(tool, "function", function);

    return tool;
}

// =============================================================================
// Helper Functions
// =============================================================================

static char* resolve_path(fs_session_state_t *state, const char *path) {
    if (!path) return NULL;

    char resolved[PATH_MAX];

    // Handle relative paths
    if (path[0] != '/') {
        snprintf(resolved, sizeof(resolved), "%s/%s", state->working_directory, path);
    } else {
        strncpy(resolved, path, sizeof(resolved) - 1);
        resolved[sizeof(resolved) - 1] = '\0';
    }

    // Canonicalize
    char *canonical = realpath(resolved, NULL);
    return canonical;
}

static const char* get_file_type_string(mode_t mode) {
    if (S_ISREG(mode)) return "file";
    if (S_ISDIR(mode)) return "directory";
    if (S_ISLNK(mode)) return "symlink";
    if (S_ISCHR(mode)) return "char_device";
    if (S_ISBLK(mode)) return "block_device";
    if (S_ISFIFO(mode)) return "fifo";
    if (S_ISSOCK(mode)) return "socket";
    return "unknown";
}

static void format_permissions(mode_t mode, char *buf, size_t size) {
    snprintf(buf, size, "%c%c%c%c%c%c%c%c%c",
        (mode & S_IRUSR) ? 'r' : '-',
        (mode & S_IWUSR) ? 'w' : '-',
        (mode & S_IXUSR) ? 'x' : '-',
        (mode & S_IRGRP) ? 'r' : '-',
        (mode & S_IWGRP) ? 'w' : '-',
        (mode & S_IXGRP) ? 'x' : '-',
        (mode & S_IROTH) ? 'r' : '-',
        (mode & S_IWOTH) ? 'w' : '-',
        (mode & S_IXOTH) ? 'x' : '-');
}

// =============================================================================
// Tool Implementations
// =============================================================================

char* fs_pwd(fs_session_state_t *state) {
    if (!state) return NULL;
    return strdup(state->working_directory);
}

fs_cd_result_t* fs_cd(fs_session_state_t *state, const char *path) {
    fs_cd_result_t *result = calloc(1, sizeof(fs_cd_result_t));
    if (!result) return NULL;

    if (!state || !path) {
        result->error_message = strdup("Invalid parameters");
        result->success = 0;
        return result;
    }

    if (fs_state_change_directory(state, path) == 0) {
        result->current_directory = strdup(state->working_directory);
        result->success = 1;
    } else {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to change directory to '%s': %s",
                 path, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
    }

    return result;
}

fs_list_result_t* fs_ls(fs_session_state_t *state, const char *path, int show_hidden, int long_format) {
    fs_list_result_t *result = calloc(1, sizeof(fs_list_result_t));
    if (!result) return NULL;

    const char *target_path = path ? path : ".";
    char *resolved = resolve_path(state, target_path);

    if (!resolved) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to resolve path '%s': %s",
                 target_path, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        return result;
    }

    DIR *dir = opendir(resolved);
    if (!dir) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to open directory '%s': %s",
                 resolved, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        free(resolved);
        return result;
    }

    json_object *entries = json_object_new_array();
    struct dirent *entry;

    while ((entry = readdir(dir)) != NULL) {
        // Skip hidden files if not requested
        if (!show_hidden && entry->d_name[0] == '.') {
            continue;
        }

        json_object *file_entry = json_object_new_object();
        json_object_object_add(file_entry, "name", json_object_new_string(entry->d_name));

        if (long_format) {
            char full_path[PATH_MAX];
            snprintf(full_path, sizeof(full_path), "%s/%s", resolved, entry->d_name);

            struct stat st;
            if (stat(full_path, &st) == 0) {
                json_object_object_add(file_entry, "size", json_object_new_int64(st.st_size));
                json_object_object_add(file_entry, "type",
                    json_object_new_string(get_file_type_string(st.st_mode)));

                char perms[10];
                format_permissions(st.st_mode, perms, sizeof(perms));
                json_object_object_add(file_entry, "permissions", json_object_new_string(perms));

                char time_buf[64];
                struct tm *tm_info = localtime(&st.st_mtime);
                strftime(time_buf, sizeof(time_buf), "%Y-%m-%d %H:%M:%S", tm_info);
                json_object_object_add(file_entry, "modified", json_object_new_string(time_buf));
            }
        }

        json_object_array_add(entries, file_entry);
    }

    closedir(dir);
    free(resolved);

    result->entries = entries;
    result->success = 1;

    return result;
}

fs_read_result_t* fs_read(fs_session_state_t *state, const char *path, int max_lines) {
    fs_read_result_t *result = calloc(1, sizeof(fs_read_result_t));
    if (!result) return NULL;

    if (max_lines <= 0) max_lines = 1000;

    char *resolved = resolve_path(state, path);
    if (!resolved) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to resolve path '%s': %s",
                 path, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        return result;
    }

    FILE *file = fopen(resolved, "r");
    if (!file) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to open file '%s': %s",
                 resolved, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        free(resolved);
        return result;
    }

    // Read file content
    size_t capacity = 4096;
    char *content = malloc(capacity);
    size_t content_size = 0;
    char line_buf[4096];
    int line_count = 0;

    while (fgets(line_buf, sizeof(line_buf), file) && line_count < max_lines) {
        size_t line_len = strlen(line_buf);

        // Grow buffer if needed
        while (content_size + line_len + 1 >= capacity) {
            capacity *= 2;
            char *new_content = realloc(content, capacity);
            if (!new_content) {
                fclose(file);
                free(resolved);
                free(content);
                result->error_message = strdup("Memory allocation failed");
                result->success = 0;
                return result;
            }
            content = new_content;
        }

        memcpy(content + content_size, line_buf, line_len);
        content_size += line_len;
        line_count++;
    }

    content[content_size] = '\0';

    // Check if there's more content
    result->truncated = !feof(file);

    fclose(file);
    free(resolved);

    result->content = content;
    result->size = content_size;
    result->success = 1;

    return result;
}

fs_write_result_t* fs_write(fs_session_state_t *state, const char *path, const char *content, int append) {
    fs_write_result_t *result = calloc(1, sizeof(fs_write_result_t));
    if (!result) return NULL;

    if (!content) {
        result->error_message = strdup("No content provided");
        result->success = 0;
        return result;
    }

    char *resolved = resolve_path(state, path);
    if (!resolved) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to resolve path '%s': %s",
                 path, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        return result;
    }

    const char *mode = append ? "a" : "w";
    FILE *file = fopen(resolved, mode);
    if (!file) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to open file '%s': %s",
                 resolved, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        free(resolved);
        return result;
    }

    size_t content_len = strlen(content);
    size_t written = fwrite(content, 1, content_len, file);

    fclose(file);
    free(resolved);

    if (written != content_len) {
        result->error_message = strdup("Failed to write all content");
        result->success = 0;
    } else {
        result->bytes_written = written;
        result->success = 1;
    }

    return result;
}

fs_info_result_t* fs_info(fs_session_state_t *state, const char *path) {
    fs_info_result_t *result = calloc(1, sizeof(fs_info_result_t));
    if (!result) return NULL;

    char *resolved = resolve_path(state, path);
    if (!resolved) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to resolve path '%s': %s",
                 path, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        return result;
    }

    struct stat st;
    if (stat(resolved, &st) != 0) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to stat '%s': %s",
                 resolved, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        free(resolved);
        return result;
    }

    json_object *info = json_object_new_object();

    json_object_object_add(info, "path", json_object_new_string(resolved));
    json_object_object_add(info, "size", json_object_new_int64(st.st_size));
    json_object_object_add(info, "type", json_object_new_string(get_file_type_string(st.st_mode)));

    char perms[10];
    format_permissions(st.st_mode, perms, sizeof(perms));
    json_object_object_add(info, "permissions", json_object_new_string(perms));

    char time_buf[64];
    struct tm *tm_info = localtime(&st.st_mtime);
    strftime(time_buf, sizeof(time_buf), "%Y-%m-%d %H:%M:%S", tm_info);
    json_object_object_add(info, "modified", json_object_new_string(time_buf));

    tm_info = localtime(&st.st_atime);
    strftime(time_buf, sizeof(time_buf), "%Y-%m-%d %H:%M:%S", tm_info);
    json_object_object_add(info, "accessed", json_object_new_string(time_buf));

    json_object_object_add(info, "inode", json_object_new_int64(st.st_ino));
    json_object_object_add(info, "links", json_object_new_int64(st.st_nlink));

    free(resolved);

    result->info = info;
    result->success = 1;

    return result;
}

static int mkdir_recursive(const char *path) {
    char tmp[PATH_MAX];
    char *p = NULL;
    size_t len;

    snprintf(tmp, sizeof(tmp), "%s", path);
    len = strlen(tmp);
    if (tmp[len - 1] == '/') {
        tmp[len - 1] = 0;
    }

    for (p = tmp + 1; *p; p++) {
        if (*p == '/') {
            *p = 0;
            if (mkdir(tmp, 0755) != 0 && errno != EEXIST) {
                return -1;
            }
            *p = '/';
        }
    }

    if (mkdir(tmp, 0755) != 0 && errno != EEXIST) {
        return -1;
    }

    return 0;
}

fs_op_result_t* fs_mkdir(fs_session_state_t *state, const char *path, int recursive) {
    fs_op_result_t *result = calloc(1, sizeof(fs_op_result_t));
    if (!result) return NULL;

    char *resolved = resolve_path(state, path);
    if (!resolved) {
        // For mkdir, we may need to resolve parent directory
        char parent_buf[PATH_MAX];
        strncpy(parent_buf, path, sizeof(parent_buf) - 1);
        char *parent_path = dirname(parent_buf);

        char *parent_resolved = resolve_path(state, parent_path);
        if (!parent_resolved && !recursive) {
            char error_buf[512];
            snprintf(error_buf, sizeof(error_buf), "Parent directory does not exist: %s", parent_path);
            result->error_message = strdup(error_buf);
            result->success = 0;
            return result;
        }

        char full_path[PATH_MAX];
        if (parent_resolved) {
            char name_buf[PATH_MAX];
            strncpy(name_buf, path, sizeof(name_buf) - 1);
            snprintf(full_path, sizeof(full_path), "%s/%s", parent_resolved, basename(name_buf));
            free(parent_resolved);
        } else {
            // Resolve relative to working directory
            snprintf(full_path, sizeof(full_path), "%s/%s", state->working_directory, path);
        }

        int ret;
        if (recursive) {
            ret = mkdir_recursive(full_path);
        } else {
            ret = mkdir(full_path, 0755);
        }

        if (ret != 0 && errno != EEXIST) {
            char error_buf[512];
            snprintf(error_buf, sizeof(error_buf), "Failed to create directory '%s': %s",
                     full_path, strerror(errno));
            result->error_message = strdup(error_buf);
            result->success = 0;
            return result;
        }

        result->success = 1;
        return result;
    }

    // Path already exists
    struct stat st;
    if (stat(resolved, &st) == 0 && S_ISDIR(st.st_mode)) {
        result->success = 1;
        free(resolved);
        return result;
    }

    char error_buf[512];
    snprintf(error_buf, sizeof(error_buf), "Path already exists and is not a directory: %s", resolved);
    result->error_message = strdup(error_buf);
    result->success = 0;
    free(resolved);

    return result;
}

static int rm_recursive(const char *path) {
    DIR *dir = opendir(path);
    if (!dir) {
        return unlink(path);
    }

    struct dirent *entry;
    int ret = 0;

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        char full_path[PATH_MAX];
        snprintf(full_path, sizeof(full_path), "%s/%s", path, entry->d_name);

        struct stat st;
        if (stat(full_path, &st) == 0) {
            if (S_ISDIR(st.st_mode)) {
                ret = rm_recursive(full_path);
            } else {
                ret = unlink(full_path);
            }

            if (ret != 0) {
                break;
            }
        }
    }

    closedir(dir);

    if (ret == 0) {
        ret = rmdir(path);
    }

    return ret;
}

fs_op_result_t* fs_rm(fs_session_state_t *state, const char *path, int recursive) {
    fs_op_result_t *result = calloc(1, sizeof(fs_op_result_t));
    if (!result) return NULL;

    char *resolved = resolve_path(state, path);
    if (!resolved) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to resolve path '%s': %s",
                 path, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        return result;
    }

    struct stat st;
    if (stat(resolved, &st) != 0) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Path does not exist: %s", resolved);
        result->error_message = strdup(error_buf);
        result->success = 0;
        free(resolved);
        return result;
    }

    int ret;
    if (S_ISDIR(st.st_mode)) {
        if (recursive) {
            ret = rm_recursive(resolved);
        } else {
            ret = rmdir(resolved);
        }
    } else {
        ret = unlink(resolved);
    }

    if (ret != 0) {
        char error_buf[512];
        snprintf(error_buf, sizeof(error_buf), "Failed to remove '%s': %s",
                 resolved, strerror(errno));
        result->error_message = strdup(error_buf);
        result->success = 0;
        free(resolved);
        return result;
    }

    free(resolved);
    result->success = 1;

    return result;
}

// =============================================================================
// Result Cleanup Functions
// =============================================================================

void fs_cd_result_destroy(fs_cd_result_t *result) {
    if (!result) return;
    free(result->current_directory);
    free(result->error_message);
    free(result);
}

void fs_list_result_destroy(fs_list_result_t *result) {
    if (!result) return;
    if (result->entries) {
        json_object_put(result->entries);
    }
    free(result->error_message);
    free(result);
}

void fs_read_result_destroy(fs_read_result_t *result) {
    if (!result) return;
    free(result->content);
    free(result->error_message);
    free(result);
}

void fs_write_result_destroy(fs_write_result_t *result) {
    if (!result) return;
    free(result->error_message);
    free(result);
}

void fs_info_result_destroy(fs_info_result_t *result) {
    if (!result) return;
    if (result->info) {
        json_object_put(result->info);
    }
    free(result->error_message);
    free(result);
}

void fs_op_result_destroy(fs_op_result_t *result) {
    if (!result) return;
    free(result->error_message);
    free(result);
}

// =============================================================================
// JSON Conversion Functions
// =============================================================================

char* fs_cd_result_to_json(fs_cd_result_t *result) {
    if (!result) return NULL;

    json_object *json = json_object_new_object();
    json_object_object_add(json, "success", json_object_new_boolean(result->success));

    if (result->current_directory) {
        json_object_object_add(json, "current_directory",
            json_object_new_string(result->current_directory));
    }

    if (result->error_message) {
        json_object_object_add(json, "error", json_object_new_string(result->error_message));
    }

    const char *json_str = json_object_to_json_string(json);
    char *result_str = strdup(json_str);
    json_object_put(json);

    return result_str;
}

char* fs_list_result_to_json(fs_list_result_t *result) {
    if (!result) return NULL;

    json_object *json = json_object_new_object();
    json_object_object_add(json, "success", json_object_new_boolean(result->success));

    if (result->entries) {
        json_object_object_add(json, "entries", json_object_get(result->entries));
    }

    if (result->error_message) {
        json_object_object_add(json, "error", json_object_new_string(result->error_message));
    }

    const char *json_str = json_object_to_json_string(json);
    char *result_str = strdup(json_str);
    json_object_put(json);

    return result_str;
}

char* fs_read_result_to_json(fs_read_result_t *result) {
    if (!result) return NULL;

    json_object *json = json_object_new_object();
    json_object_object_add(json, "success", json_object_new_boolean(result->success));

    if (result->content) {
        json_object_object_add(json, "content", json_object_new_string(result->content));
        json_object_object_add(json, "size", json_object_new_int64(result->size));
        json_object_object_add(json, "truncated", json_object_new_boolean(result->truncated));
    }

    if (result->error_message) {
        json_object_object_add(json, "error", json_object_new_string(result->error_message));
    }

    const char *json_str = json_object_to_json_string(json);
    char *result_str = strdup(json_str);
    json_object_put(json);

    return result_str;
}

char* fs_write_result_to_json(fs_write_result_t *result) {
    if (!result) return NULL;

    json_object *json = json_object_new_object();
    json_object_object_add(json, "success", json_object_new_boolean(result->success));

    if (result->success) {
        json_object_object_add(json, "bytes_written", json_object_new_int64(result->bytes_written));
    }

    if (result->error_message) {
        json_object_object_add(json, "error", json_object_new_string(result->error_message));
    }

    const char *json_str = json_object_to_json_string(json);
    char *result_str = strdup(json_str);
    json_object_put(json);

    return result_str;
}

char* fs_info_result_to_json(fs_info_result_t *result) {
    if (!result) return NULL;

    json_object *json = json_object_new_object();
    json_object_object_add(json, "success", json_object_new_boolean(result->success));

    if (result->info) {
        json_object_object_add(json, "info", json_object_get(result->info));
    }

    if (result->error_message) {
        json_object_object_add(json, "error", json_object_new_string(result->error_message));
    }

    const char *json_str = json_object_to_json_string(json);
    char *result_str = strdup(json_str);
    json_object_put(json);

    return result_str;
}

char* fs_op_result_to_json(fs_op_result_t *result) {
    if (!result) return NULL;

    json_object *json = json_object_new_object();
    json_object_object_add(json, "success", json_object_new_boolean(result->success));

    if (result->error_message) {
        json_object_object_add(json, "error", json_object_new_string(result->error_message));
    }

    const char *json_str = json_object_to_json_string(json);
    char *result_str = strdup(json_str);
    json_object_put(json);

    return result_str;
}
