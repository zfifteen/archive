/**
 * @file bash_tool.c
 * @brief Bash Command Execution Tool - Implementation
 */

#include "bash_tool.h"
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <signal.h>
#include <errno.h>

// Create bash tool definition
json_object* bash_tool_definition(void) {
    json_object *tool = json_object_new_object();
    json_object_object_add(tool, "type", json_object_new_string("function"));
    
    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("bash"));
    json_object_object_add(function, "description", json_object_new_string("Execute bash commands"));
    
    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));
    
    json_object *properties = json_object_new_object();
    json_object *command_prop = json_object_new_object();
    json_object_object_add(command_prop, "type", json_object_new_string("string"));
    json_object_object_add(properties, "command", command_prop);
    json_object_object_add(parameters, "properties", properties);
    
    json_object *required = json_object_new_array();
    json_object_array_add(required, json_object_new_string("command"));
    json_object_object_add(parameters, "required", required);
    
    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(tool, "function", function);
    
    return tool;
}

// Validate command (basic security check)
int bash_validate_command(const char *command) {
    if (!command || strlen(command) == 0) {
        return 0;
    }
    
    // Basic validation - could be extended with more security checks
    if (strlen(command) > 10000) {
        return 0;
    }
    
    return 1;
}

// Execute bash command
bash_result_t* bash_execute(const char *command, const char *working_dir, int timeout) {
    if (!bash_validate_command(command)) {
        bash_result_t *result = calloc(1, sizeof(bash_result_t));
        result->error_message = strdup("Invalid command");
        result->exit_code = -1;
        return result;
    }
    
    bash_result_t *result = calloc(1, sizeof(bash_result_t));
    if (!result) {
        return NULL;
    }
    
    // Create pipes for stdout and stderr
    int stdout_pipe[2];
    int stderr_pipe[2];
    
    if (pipe(stdout_pipe) == -1 || pipe(stderr_pipe) == -1) {
        result->error_message = strdup("Failed to create pipes");
        result->exit_code = -1;
        return result;
    }
    
    pid_t pid = fork();
    
    if (pid == -1) {
        // Fork failed
        close(stdout_pipe[0]);
        close(stdout_pipe[1]);
        close(stderr_pipe[0]);
        close(stderr_pipe[1]);
        result->error_message = strdup("Failed to fork process");
        result->exit_code = -1;
        return result;
    }
    
    if (pid == 0) {
        // Child process
        close(stdout_pipe[0]);
        close(stderr_pipe[0]);
        
        dup2(stdout_pipe[1], STDOUT_FILENO);
        dup2(stderr_pipe[1], STDERR_FILENO);
        
        close(stdout_pipe[1]);
        close(stderr_pipe[1]);
        
        // Change working directory if specified
        if (working_dir && strlen(working_dir) > 0) {
            if (chdir(working_dir) != 0) {
                fprintf(stderr, "Failed to change directory to: %s\n", working_dir);
                exit(127);
            }
        }
        
        // Execute command
        execl("/bin/bash", "bash", "-c", command, (char *)NULL);
        
        // If execl fails
        fprintf(stderr, "Failed to execute command\n");
        exit(127);
    }
    
    // Parent process
    close(stdout_pipe[1]);
    close(stderr_pipe[1]);
    
    // Read stdout
    char stdout_buffer[4096];
    size_t stdout_size = 0;
    char *stdout_data = NULL;
    ssize_t n;
    
    while ((n = read(stdout_pipe[0], stdout_buffer, sizeof(stdout_buffer))) > 0) {
        char *new_data = realloc(stdout_data, stdout_size + n + 1);
        if (!new_data) {
            break;
        }
        stdout_data = new_data;
        memcpy(stdout_data + stdout_size, stdout_buffer, n);
        stdout_size += n;
        stdout_data[stdout_size] = '\0';
    }
    
    // Read stderr
    char stderr_buffer[4096];
    size_t stderr_size = 0;
    char *stderr_data = NULL;
    
    while ((n = read(stderr_pipe[0], stderr_buffer, sizeof(stderr_buffer))) > 0) {
        char *new_data = realloc(stderr_data, stderr_size + n + 1);
        if (!new_data) {
            break;
        }
        stderr_data = new_data;
        memcpy(stderr_data + stderr_size, stderr_buffer, n);
        stderr_size += n;
        stderr_data[stderr_size] = '\0';
    }
    
    close(stdout_pipe[0]);
    close(stderr_pipe[0]);
    
    // Wait for child with timeout
    int status;
    int wait_time = 0;
    int wait_result;
    
    while (wait_time < timeout) {
        wait_result = waitpid(pid, &status, WNOHANG);
        
        if (wait_result == pid) {
            break;
        } else if (wait_result == -1) {
            result->error_message = strdup("waitpid failed");
            result->exit_code = -1;
            free(stdout_data);
            free(stderr_data);
            return result;
        }
        
        sleep(1);
        wait_time++;
    }
    
    if (wait_result == 0) {
        // Timeout - kill the process
        kill(pid, SIGKILL);
        waitpid(pid, &status, 0);
        result->timed_out = 1;
        result->exit_code = -1;
    } else {
        result->timed_out = 0;
        if (WIFEXITED(status)) {
            result->exit_code = WEXITSTATUS(status);
        } else {
            result->exit_code = -1;
        }
    }
    
    result->stdout_output = stdout_data ? stdout_data : strdup("");
    result->stderr_output = stderr_data ? stderr_data : strdup("");
    
    return result;
}

void bash_result_destroy(bash_result_t *result) {
    if (!result) return;
    
    free(result->stdout_output);
    free(result->stderr_output);
    free(result->error_message);
    free(result);
}

char* bash_result_to_json(bash_result_t *result) {
    if (!result) return NULL;
    
    json_object *json = json_object_new_object();
    
    if (result->stdout_output) {
        json_object_object_add(json, "stdout", json_object_new_string(result->stdout_output));
    }
    
    if (result->stderr_output) {
        json_object_object_add(json, "stderr", json_object_new_string(result->stderr_output));
    }
    
    json_object_object_add(json, "exit_code", json_object_new_int(result->exit_code));
    json_object_object_add(json, "timed_out", json_object_new_boolean(result->timed_out));
    
    if (result->error_message) {
        json_object_object_add(json, "error", json_object_new_string(result->error_message));
    }
    
    const char *json_str = json_object_to_json_string(json);
    char *result_str = strdup(json_str);
    
    json_object_put(json);
    
    return result_str;
}
