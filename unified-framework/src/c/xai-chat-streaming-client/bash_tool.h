/**
 * @file bash_tool.h
 * @brief Bash Command Execution Tool
 * 
 * Implements bash command execution with proper sandboxing, output capture,
 * and timeout handling for the XAI chat agent.
 */

#ifndef BASH_TOOL_H
#define BASH_TOOL_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <json-c/json.h>

// Command result structure
typedef struct {
    char *stdout_output;
    char *stderr_output;
    int exit_code;
    int timed_out;
    char *error_message;
} bash_result_t;

// Tool definition functions
json_object* bash_tool_definition(void);

// Command execution
bash_result_t* bash_execute(const char *command, const char *working_dir, int timeout);
void bash_result_destroy(bash_result_t *result);
char* bash_result_to_json(bash_result_t *result);

// Command validation
int bash_validate_command(const char *command);

#endif // BASH_TOOL_H
