/**
 * @file xai_chat_client.c
 * @brief XAI Chat Streaming Client - Main Application
 * 
 * Interactive chat client that interfaces with XAI's API to enable Grok
 * as a local coding agent with bash execution capabilities.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include "xai_client.h"
#include "bash_tool.h"
#include "sse_parser.h"
#include "fs_tools.h"

// Global state for signal handling
static volatile int keep_running = 1;

void signal_handler(int signum) {
    (void)signum;
    keep_running = 0;
}

// Streaming callback context
typedef struct {
    int verbose;
    char *accumulated_content;
    json_object *tool_calls;
} stream_context_t;

// Stream callback
void stream_callback(const char *chunk, void *user_data) {
    stream_context_t *ctx = (stream_context_t *)user_data;
    
    if (!chunk) return;
    
    if (ctx->verbose) {
        printf("[DEBUG] Chunk: %s\n", chunk);
    }
    
    // Parse JSON chunk
    json_object *json = json_tokener_parse(chunk);
    if (!json) return;
    
    json_object *choices;
    if (!json_object_object_get_ex(json, "choices", &choices)) {
        json_object_put(json);
        return;
    }
    
    if (!json_object_is_type(choices, json_type_array) || json_object_array_length(choices) == 0) {
        json_object_put(json);
        return;
    }
    
    json_object *choice = json_object_array_get_idx(choices, 0);
    json_object *delta;
    
    if (json_object_object_get_ex(choice, "delta", &delta)) {
        // Handle content
        json_object *content;
        if (json_object_object_get_ex(delta, "content", &content)) {
            const char *content_str = json_object_get_string(content);
            if (content_str) {
                printf("%s", content_str);
                fflush(stdout);
                
                // Accumulate content
                if (!ctx->accumulated_content) {
                    ctx->accumulated_content = strdup(content_str);
                } else {
                    size_t old_len = strlen(ctx->accumulated_content);
                    size_t new_len = strlen(content_str);
                    char *new_content = realloc(ctx->accumulated_content, old_len + new_len + 1);
                    if (new_content) {
                        strcpy(new_content + old_len, content_str);
                        ctx->accumulated_content = new_content;
                    }
                }
            }
        }
        
        // Handle tool calls
        json_object *tool_calls;
        if (json_object_object_get_ex(delta, "tool_calls", &tool_calls)) {
            if (!ctx->tool_calls) {
                ctx->tool_calls = json_object_get(tool_calls);
            }
        }
    }
    
    json_object_put(json);
}

// Print usage
void print_usage(const char *prog_name) {
    printf("Usage: %s [options]\n", prog_name);
    printf("\nOptions:\n");
    printf("  --model <model>        Model to use (grok-code-fast-1 or grok-4)\n");
    printf("  --base-url <url>       Override API base URL (for mock server)\n");
    printf("  --timeout <seconds>    Request timeout (default: 300)\n");
    printf("  --verbose              Enable verbose output\n");
    printf("  --help                 Show this help message\n");
    printf("\nEnvironment Variables:\n");
    printf("  XAI_API_KEY           XAI API key (required)\n");
    printf("  XAI_BASE_URL          Override API base URL\n");
    printf("\nExamples:\n");
    printf("  %s\n", prog_name);
    printf("  %s --model grok-4\n", prog_name);
    printf("  %s --base-url http://localhost:8080/v1\n", prog_name);
}

int main(int argc, char *argv[]) {
    // Parse command line arguments
    xai_model_t model = XAI_MODEL_GROK_CODE_FAST_1;
    char *base_url = NULL;
    int timeout = DEFAULT_TIMEOUT;
    int verbose = 0;
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            return 0;
        } else if (strcmp(argv[i], "--model") == 0 && i + 1 < argc) {
            i++;
            if (strcmp(argv[i], "grok-4") == 0) {
                model = XAI_MODEL_GROK_4;
            } else if (strcmp(argv[i], "grok-code-fast-1") == 0) {
                model = XAI_MODEL_GROK_CODE_FAST_1;
            } else {
                fprintf(stderr, "Unknown model: %s\n", argv[i]);
                return 1;
            }
        } else if (strcmp(argv[i], "--base-url") == 0 && i + 1 < argc) {
            i++;
            base_url = argv[i];
        } else if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) {
            i++;
            timeout = atoi(argv[i]);
        } else if (strcmp(argv[i], "--verbose") == 0) {
            verbose = 1;
        } else {
            fprintf(stderr, "Unknown option: %s\n", argv[i]);
            print_usage(argv[0]);
            return 1;
        }
    }
    
    // Get API key
    const char *api_key = getenv("XAI_API_KEY");
    if (!api_key) {
        fprintf(stderr, "Error: XAI_API_KEY environment variable not set\n");
        return 1;
    }
    
    // Override base URL from environment if not specified
    if (!base_url) {
        const char *env_base_url = getenv("XAI_BASE_URL");
        if (env_base_url) {
            base_url = (char *)env_base_url;
        }
    }
    
    // Initialize GMP/MPFR
    mpfr_t test_val;
    mpfr_init2(test_val, MPFR_PRECISION_BITS);
    mpfr_set_d(test_val, 1.0, MPFR_RNDN);
    mpfr_clear(test_val);
    
    // Create configuration
    xai_config_t *config = xai_config_create(api_key, model);
    if (!config) {
        fprintf(stderr, "Error: Failed to create configuration\n");
        return 1;
    }
    
    config->timeout = timeout;
    config->verbose = verbose;
    
    if (base_url) {
        xai_config_set_base_url(config, base_url);
    }
    
    // Create conversation
    conversation_t *conv = conversation_create();
    if (!conv) {
        fprintf(stderr, "Error: Failed to create conversation\n");
        xai_config_destroy(config);
        return 1;
    }

    // Create filesystem state
    fs_session_state_t *fs_state = fs_state_create();
    if (!fs_state) {
        fprintf(stderr, "Error: Failed to create filesystem state\n");
        conversation_destroy(conv);
        xai_config_destroy(config);
        return 1;
    }

    // Add system prompt
    conversation_add_message(conv, ROLE_SYSTEM,
        "You are a helpful coding assistant with bash execution and filesystem manipulation capabilities. "
        "You have access to structured filesystem tools (ls, cd, pwd, read_file, write_file, file_info, mkdir, rm) "
        "for common operations, and bash for complex tasks. Always explain what you're doing and why.");
    
    // Setup signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    printf("XAI Chat Streaming Client\n");
    printf("=========================\n");
    printf("Model: %s\n", model_to_string(model));
    printf("Base URL: %s\n", config->base_url);
    printf("\nType 'exit' to quit, 'help' for commands\n\n");
    
    char input[4096];
    
    while (keep_running) {
        printf("You> ");
        fflush(stdout);
        
        if (!fgets(input, sizeof(input), stdin)) {
            break;
        }
        
        // Remove trailing newline
        input[strcspn(input, "\n")] = 0;
        
        if (strlen(input) == 0) {
            continue;
        }
        
        if (strcmp(input, "exit") == 0 || strcmp(input, "quit") == 0) {
            break;
        }
        
        if (strcmp(input, "help") == 0) {
            printf("\nCommands:\n");
            printf("  exit, quit  - Exit the chat\n");
            printf("  help        - Show this help\n");
            printf("  clear       - Clear conversation history\n\n");
            continue;
        }
        
        if (strcmp(input, "clear") == 0) {
            conversation_destroy(conv);
            conv = conversation_create();
            conversation_add_message(conv, ROLE_SYSTEM, 
                "You are a helpful coding assistant with bash execution capabilities.");
            printf("Conversation cleared.\n\n");
            continue;
        }
        
        // Add user message
        conversation_add_message(conv, ROLE_USER, input);
        
        printf("\nGrok> ");
        fflush(stdout);
        
        // Stream response
        stream_context_t ctx = {0};
        ctx.verbose = verbose;
        
        int result = xai_stream_chat(config, conv, stream_callback, &ctx);
        
        printf("\n\n");
        
        if (result != 0) {
            fprintf(stderr, "Error: Failed to stream chat\n");
            continue;
        }
        
        // Add assistant response to conversation
        if (ctx.accumulated_content) {
            conversation_add_message(conv, ROLE_ASSISTANT, ctx.accumulated_content);
            free(ctx.accumulated_content);
        }
        
        // Handle tool calls
        if (ctx.tool_calls) {
            printf("[Executing tools...]\n\n");

            size_t num_calls = json_object_array_length(ctx.tool_calls);
            for (size_t i = 0; i < num_calls; i++) {
                json_object *tool_call = json_object_array_get_idx(ctx.tool_calls, i);
                json_object *id_obj, *func_obj, *name_obj, *args_obj;

                if (!json_object_object_get_ex(tool_call, "id", &id_obj)) continue;
                if (!json_object_object_get_ex(tool_call, "function", &func_obj)) continue;
                if (!json_object_object_get_ex(func_obj, "name", &name_obj)) continue;
                if (!json_object_object_get_ex(func_obj, "arguments", &args_obj)) continue;

                const char *tool_id = json_object_get_string(id_obj);
                const char *tool_name = json_object_get_string(name_obj);

                // Parse arguments
                json_object *tool_args = json_tokener_parse(json_object_get_string(args_obj));

                if (strcmp(tool_name, "bash") == 0) {
                    json_object *cmd_obj;

                    if (tool_args && json_object_object_get_ex(tool_args, "command", &cmd_obj)) {
                        const char *command = json_object_get_string(cmd_obj);

                        printf("$ %s\n", command);

                        // Execute command
                        bash_result_t *bash_result = bash_execute(command, fs_state_get_directory(fs_state), 60);

                        if (bash_result->stdout_output && strlen(bash_result->stdout_output) > 0) {
                            printf("%s", bash_result->stdout_output);
                        }

                        if (bash_result->stderr_output && strlen(bash_result->stderr_output) > 0) {
                            fprintf(stderr, "%s", bash_result->stderr_output);
                        }

                        printf("\n");

                        // Add tool response to conversation
                        char *result_json = bash_result_to_json(bash_result);
                        if (result_json) {
                            conversation_add_tool_response(conv, tool_id, result_json);
                            free(result_json);
                        }

                        bash_result_destroy(bash_result);
                    }
                } else if (strcmp(tool_name, "pwd") == 0) {
                    char *cwd = fs_pwd(fs_state);
                    printf("pwd\n%s\n\n", cwd ? cwd : "");

                    json_object *result_json = json_object_new_object();
                    json_object_object_add(result_json, "current_directory", json_object_new_string(cwd ? cwd : ""));
                    const char *json_str = json_object_to_json_string(result_json);
                    conversation_add_tool_response(conv, tool_id, json_str);
                    json_object_put(result_json);
                    free(cwd);
                } else if (strcmp(tool_name, "cd") == 0) {
                    json_object *path_obj;

                    if (tool_args && json_object_object_get_ex(tool_args, "path", &path_obj)) {
                        const char *path = json_object_get_string(path_obj);
                        printf("cd %s\n", path);

                        fs_cd_result_t *cd_result = fs_cd(fs_state, path);
                        char *result_json = fs_cd_result_to_json(cd_result);

                        if (cd_result->success) {
                            printf("Changed to: %s\n\n", cd_result->current_directory);
                        } else {
                            printf("Error: %s\n\n", cd_result->error_message);
                        }

                        if (result_json) {
                            conversation_add_tool_response(conv, tool_id, result_json);
                            free(result_json);
                        }

                        fs_cd_result_destroy(cd_result);
                    }
                } else if (strcmp(tool_name, "ls") == 0) {
                    const char *path = ".";
                    int show_hidden = 0;
                    int long_format = 1;

                    if (tool_args) {
                        json_object *path_obj, *hidden_obj, *long_obj;
                        if (json_object_object_get_ex(tool_args, "path", &path_obj)) {
                            path = json_object_get_string(path_obj);
                        }
                        if (json_object_object_get_ex(tool_args, "show_hidden", &hidden_obj)) {
                            show_hidden = json_object_get_boolean(hidden_obj);
                        }
                        if (json_object_object_get_ex(tool_args, "long_format", &long_obj)) {
                            long_format = json_object_get_boolean(long_obj);
                        }
                    }

                    printf("ls %s%s\n", show_hidden ? "-a " : "", path);

                    fs_list_result_t *ls_result = fs_ls(fs_state, path, show_hidden, long_format);
                    char *result_json = fs_list_result_to_json(ls_result);

                    if (ls_result->success && ls_result->entries) {
                        size_t num_entries = json_object_array_length(ls_result->entries);
                        for (size_t j = 0; j < num_entries; j++) {
                            json_object *entry = json_object_array_get_idx(ls_result->entries, j);
                            json_object *name_obj;
                            if (json_object_object_get_ex(entry, "name", &name_obj)) {
                                printf("%s\n", json_object_get_string(name_obj));
                            }
                        }
                        printf("\n");
                    } else if (!ls_result->success) {
                        printf("Error: %s\n\n", ls_result->error_message);
                    }

                    if (result_json) {
                        conversation_add_tool_response(conv, tool_id, result_json);
                        free(result_json);
                    }

                    fs_list_result_destroy(ls_result);
                } else if (strcmp(tool_name, "read_file") == 0) {
                    json_object *path_obj, *lines_obj;
                    int max_lines = 1000;

                    if (tool_args && json_object_object_get_ex(tool_args, "path", &path_obj)) {
                        const char *path = json_object_get_string(path_obj);

                        if (json_object_object_get_ex(tool_args, "max_lines", &lines_obj)) {
                            max_lines = json_object_get_int(lines_obj);
                        }

                        printf("read_file %s\n", path);

                        fs_read_result_t *read_result = fs_read(fs_state, path, max_lines);
                        char *result_json = fs_read_result_to_json(read_result);

                        if (read_result->success) {
                            printf("%s", read_result->content);
                            if (read_result->truncated) {
                                printf("\n[truncated]\n");
                            }
                            printf("\n");
                        } else {
                            printf("Error: %s\n\n", read_result->error_message);
                        }

                        if (result_json) {
                            conversation_add_tool_response(conv, tool_id, result_json);
                            free(result_json);
                        }

                        fs_read_result_destroy(read_result);
                    }
                } else if (strcmp(tool_name, "write_file") == 0) {
                    json_object *path_obj, *content_obj, *append_obj;
                    int append = 0;

                    if (tool_args && json_object_object_get_ex(tool_args, "path", &path_obj) &&
                        json_object_object_get_ex(tool_args, "content", &content_obj)) {

                        const char *path = json_object_get_string(path_obj);
                        const char *content = json_object_get_string(content_obj);

                        if (json_object_object_get_ex(tool_args, "append", &append_obj)) {
                            append = json_object_get_boolean(append_obj);
                        }

                        printf("write_file %s %s\n", append ? ">>" : ">", path);

                        fs_write_result_t *write_result = fs_write(fs_state, path, content, append);
                        char *result_json = fs_write_result_to_json(write_result);

                        if (write_result->success) {
                            printf("Wrote %zu bytes\n\n", write_result->bytes_written);
                        } else {
                            printf("Error: %s\n\n", write_result->error_message);
                        }

                        if (result_json) {
                            conversation_add_tool_response(conv, tool_id, result_json);
                            free(result_json);
                        }

                        fs_write_result_destroy(write_result);
                    }
                } else if (strcmp(tool_name, "file_info") == 0) {
                    json_object *path_obj;

                    if (tool_args && json_object_object_get_ex(tool_args, "path", &path_obj)) {
                        const char *path = json_object_get_string(path_obj);
                        printf("file_info %s\n", path);

                        fs_info_result_t *info_result = fs_info(fs_state, path);
                        char *result_json = fs_info_result_to_json(info_result);

                        if (info_result->success && info_result->info) {
                            printf("%s\n\n", json_object_to_json_string_ext(info_result->info, JSON_C_TO_STRING_PRETTY));
                        } else {
                            printf("Error: %s\n\n", info_result->error_message);
                        }

                        if (result_json) {
                            conversation_add_tool_response(conv, tool_id, result_json);
                            free(result_json);
                        }

                        fs_info_result_destroy(info_result);
                    }
                } else if (strcmp(tool_name, "mkdir") == 0) {
                    json_object *path_obj, *recursive_obj;
                    int recursive = 0;

                    if (tool_args && json_object_object_get_ex(tool_args, "path", &path_obj)) {
                        const char *path = json_object_get_string(path_obj);

                        if (json_object_object_get_ex(tool_args, "recursive", &recursive_obj)) {
                            recursive = json_object_get_boolean(recursive_obj);
                        }

                        printf("mkdir%s %s\n", recursive ? " -p" : "", path);

                        fs_op_result_t *mkdir_result = fs_mkdir(fs_state, path, recursive);
                        char *result_json = fs_op_result_to_json(mkdir_result);

                        if (mkdir_result->success) {
                            printf("Directory created\n\n");
                        } else {
                            printf("Error: %s\n\n", mkdir_result->error_message);
                        }

                        if (result_json) {
                            conversation_add_tool_response(conv, tool_id, result_json);
                            free(result_json);
                        }

                        fs_op_result_destroy(mkdir_result);
                    }
                } else if (strcmp(tool_name, "rm") == 0) {
                    json_object *path_obj, *recursive_obj;
                    int recursive = 0;

                    if (tool_args && json_object_object_get_ex(tool_args, "path", &path_obj)) {
                        const char *path = json_object_get_string(path_obj);

                        if (json_object_object_get_ex(tool_args, "recursive", &recursive_obj)) {
                            recursive = json_object_get_boolean(recursive_obj);
                        }

                        printf("rm%s %s\n", recursive ? " -r" : "", path);

                        fs_op_result_t *rm_result = fs_rm(fs_state, path, recursive);
                        char *result_json = fs_op_result_to_json(rm_result);

                        if (rm_result->success) {
                            printf("Removed\n\n");
                        } else {
                            printf("Error: %s\n\n", rm_result->error_message);
                        }

                        if (result_json) {
                            conversation_add_tool_response(conv, tool_id, result_json);
                            free(result_json);
                        }

                        fs_op_result_destroy(rm_result);
                    }
                }

                if (tool_args) {
                    json_object_put(tool_args);
                }
            }

            json_object_put(ctx.tool_calls);

            // After executing tools, get assistant's response about the results
            printf("\nGrok> ");
            fflush(stdout);

            stream_context_t follow_up_ctx = {0};
            follow_up_ctx.verbose = verbose;

            result = xai_stream_chat(config, conv, stream_callback, &follow_up_ctx);

            printf("\n\n");

            if (result == 0 && follow_up_ctx.accumulated_content) {
                conversation_add_message(conv, ROLE_ASSISTANT, follow_up_ctx.accumulated_content);
                free(follow_up_ctx.accumulated_content);
            }

            // Handle any additional tool calls (recursive tool execution)
            if (follow_up_ctx.tool_calls) {
                json_object_put(follow_up_ctx.tool_calls);
                // TODO: Could implement recursive tool calls here if needed
            }
        }
    }
    
    printf("\nGoodbye!\n");

    // Cleanup
    fs_state_destroy(fs_state);
    conversation_destroy(conv);
    xai_config_destroy(config);

    return 0;
}
