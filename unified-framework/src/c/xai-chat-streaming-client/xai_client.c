/**
 * @file xai_client.c
 * @brief XAI Chat Streaming Client - Implementation
 */

#include "xai_client.h"
#include "sse_parser.h"
#include "fs_tools.h"

// Context for streaming write callback
typedef struct {
    stream_callback_t callback;
    void *user_data;
    char *buffer;
    size_t buffer_size;
    size_t buffer_capacity;
} stream_write_context_t;

// CURL write callback for streaming - processes data incrementally
static size_t stream_write_callback(void *ptr, size_t size, size_t nmemb, void *user_data) {
    size_t realsize = size * nmemb;
    stream_write_context_t *ctx = (stream_write_context_t *)user_data;

    // Grow buffer if needed
    while (ctx->buffer_size + realsize >= ctx->buffer_capacity) {
        size_t new_capacity = ctx->buffer_capacity * 2;
        char *new_buffer = realloc(ctx->buffer, new_capacity);
        if (!new_buffer) {
            return 0;
        }
        ctx->buffer = new_buffer;
        ctx->buffer_capacity = new_capacity;
    }

    // Append incoming data to buffer
    memcpy(ctx->buffer + ctx->buffer_size, ptr, realsize);
    ctx->buffer_size += realsize;
    ctx->buffer[ctx->buffer_size] = '\0';

    // Process complete SSE events from buffer
    char *line_start = ctx->buffer;
    char *line_end;
    char *last_processed = ctx->buffer;

    while ((line_end = strstr(line_start, "\n")) != NULL) {
        *line_end = '\0';

        // Check for "data:" prefix
        if (strncmp(line_start, "data:", 5) == 0) {
            char *data_content = line_start + 5;

            // Skip leading whitespace
            while (*data_content == ' ') {
                data_content++;
            }

            // Check for [DONE] marker
            if (strcmp(data_content, "[DONE]") == 0) {
                last_processed = line_end + 1;
                break;
            }

            // Parse JSON data and call callback immediately
            if (strlen(data_content) > 0) {
                ctx->callback(data_content, ctx->user_data);
            }
        }

        last_processed = line_end + 1;
        line_start = line_end + 1;
    }

    // Remove processed data from buffer
    size_t remaining = ctx->buffer_size - (last_processed - ctx->buffer);
    if (remaining > 0 && last_processed != ctx->buffer) {
        memmove(ctx->buffer, last_processed, remaining);
        ctx->buffer_size = remaining;
        ctx->buffer[ctx->buffer_size] = '\0';
    } else if (last_processed != ctx->buffer) {
        ctx->buffer_size = 0;
        ctx->buffer[0] = '\0';
    }

    return realsize;
}

// Create configuration
xai_config_t* xai_config_create(const char *api_key, xai_model_t model) {
    if (!api_key) {
        return NULL;
    }
    
    xai_config_t *config = calloc(1, sizeof(xai_config_t));
    if (!config) {
        return NULL;
    }
    
    config->api_key = strdup(api_key);
    config->base_url = strdup(XAI_API_BASE_URL);
    config->model = model;
    config->timeout = DEFAULT_TIMEOUT;
    config->verbose = 0;
    
    return config;
}

void xai_config_destroy(xai_config_t *config) {
    if (!config) return;
    
    free(config->api_key);
    free(config->base_url);
    free(config);
}

void xai_config_set_base_url(xai_config_t *config, const char *base_url) {
    if (!config || !base_url) return;
    
    free(config->base_url);
    config->base_url = strdup(base_url);
}

// Create conversation
conversation_t* conversation_create(void) {
    conversation_t *conv = calloc(1, sizeof(conversation_t));
    if (!conv) {
        return NULL;
    }
    
    conv->capacity = 10;
    conv->messages = calloc(conv->capacity, sizeof(message_t *));
    if (!conv->messages) {
        free(conv);
        return NULL;
    }
    
    return conv;
}

void conversation_destroy(conversation_t *conv) {
    if (!conv) return;
    
    for (size_t i = 0; i < conv->message_count; i++) {
        if (conv->messages[i]) {
            free(conv->messages[i]->content);
            free(conv->messages[i]->tool_call_id);
            if (conv->messages[i]->tool_calls) {
                json_object_put(conv->messages[i]->tool_calls);
            }
            free(conv->messages[i]);
        }
    }
    
    free(conv->messages);
    free(conv);
}

void conversation_add_message(conversation_t *conv, message_role_t role, const char *content) {
    if (!conv || !content) return;
    
    if (conv->message_count >= conv->capacity) {
        size_t new_capacity = conv->capacity * 2;
        message_t **new_messages = realloc(conv->messages, new_capacity * sizeof(message_t *));
        if (!new_messages) return;
        
        conv->messages = new_messages;
        conv->capacity = new_capacity;
    }
    
    message_t *msg = calloc(1, sizeof(message_t));
    if (!msg) return;
    
    msg->role = role;
    msg->content = strdup(content);
    msg->tool_call_id = NULL;
    msg->tool_calls = NULL;
    
    conv->messages[conv->message_count++] = msg;
}

void conversation_add_tool_response(conversation_t *conv, const char *tool_call_id, const char *content) {
    if (!conv || !tool_call_id || !content) return;
    
    if (conv->message_count >= conv->capacity) {
        size_t new_capacity = conv->capacity * 2;
        message_t **new_messages = realloc(conv->messages, new_capacity * sizeof(message_t *));
        if (!new_messages) return;
        
        conv->messages = new_messages;
        conv->capacity = new_capacity;
    }
    
    message_t *msg = calloc(1, sizeof(message_t));
    if (!msg) return;
    
    msg->role = ROLE_USER;
    msg->content = strdup(content);
    msg->tool_call_id = strdup(tool_call_id);
    msg->tool_calls = NULL;
    
    conv->messages[conv->message_count++] = msg;
}

// Model to string
const char* model_to_string(xai_model_t model) {
    switch (model) {
        case XAI_MODEL_GROK_CODE_FAST_1:
            return "grok-code-fast-1";
        case XAI_MODEL_GROK_4:
            return "grok-4";
        default:
            return "grok-code-fast-1";
    }
}

// Role to string
const char* role_to_string(message_role_t role) {
    switch (role) {
        case ROLE_SYSTEM:
            return "system";
        case ROLE_USER:
            return "user";
        case ROLE_ASSISTANT:
            return "assistant";
        default:
            return "user";
    }
}

// Build request JSON
static json_object* build_request_json(xai_config_t *config, conversation_t *conv) {
    json_object *request = json_object_new_object();
    json_object_object_add(request, "model", json_object_new_string(model_to_string(config->model)));
    json_object_object_add(request, "stream", json_object_new_boolean(1));
    
    // Add messages
    json_object *messages = json_object_new_array();
    for (size_t i = 0; i < conv->message_count; i++) {
        message_t *msg = conv->messages[i];
        json_object *jmsg = json_object_new_object();
        json_object_object_add(jmsg, "role", json_object_new_string(role_to_string(msg->role)));
        json_object_object_add(jmsg, "content", json_object_new_string(msg->content));
        
        if (msg->tool_call_id) {
            json_object_object_add(jmsg, "tool_call_id", json_object_new_string(msg->tool_call_id));
        }
        
        if (msg->tool_calls) {
            json_object_object_add(jmsg, "tool_calls", json_object_get(msg->tool_calls));
        }
        
        json_object_array_add(messages, jmsg);
    }
    json_object_object_add(request, "messages", messages);
    
    // Add tool definitions
    json_object *tools = json_object_new_array();

    // Bash tool (for complex operations, pipes, etc.)
    json_object *bash_tool = json_object_new_object();
    json_object_object_add(bash_tool, "type", json_object_new_string("function"));

    json_object *function = json_object_new_object();
    json_object_object_add(function, "name", json_object_new_string("bash"));
    json_object_object_add(function, "description", json_object_new_string("Execute bash commands in local environment"));

    json_object *parameters = json_object_new_object();
    json_object_object_add(parameters, "type", json_object_new_string("object"));

    json_object *properties = json_object_new_object();
    json_object *command_prop = json_object_new_object();
    json_object_object_add(command_prop, "type", json_object_new_string("string"));
    json_object_object_add(command_prop, "description", json_object_new_string("The bash command to execute"));
    json_object_object_add(properties, "command", command_prop);

    json_object_object_add(parameters, "properties", properties);

    json_object *required = json_object_new_array();
    json_object_array_add(required, json_object_new_string("command"));
    json_object_object_add(parameters, "required", required);

    json_object_object_add(function, "parameters", parameters);
    json_object_object_add(bash_tool, "function", function);
    json_object_array_add(tools, bash_tool);

    // Add filesystem tools
    json_object_array_add(tools, fs_tool_pwd_definition());
    json_object_array_add(tools, fs_tool_cd_definition());
    json_object_array_add(tools, fs_tool_ls_definition());
    json_object_array_add(tools, fs_tool_read_definition());
    json_object_array_add(tools, fs_tool_write_definition());
    json_object_array_add(tools, fs_tool_info_definition());
    json_object_array_add(tools, fs_tool_mkdir_definition());
    json_object_array_add(tools, fs_tool_rm_definition());

    json_object_object_add(request, "tools", tools);
    
    return request;
}

// Stream chat with SSE
int xai_stream_chat(xai_config_t *config, conversation_t *conv, stream_callback_t callback, void *user_data) {
    if (!config || !conv || !callback) {
        return -1;
    }

    CURL *curl = curl_easy_init();
    if (!curl) {
        return -1;
    }

    // Build request
    json_object *request = build_request_json(config, conv);
    const char *json_str = json_object_to_json_string(request);

    if (config->verbose) {
        printf("Request: %s\n", json_str);
    }

    // Prepare URL
    char url[512];
    snprintf(url, sizeof(url), "%s%s", config->base_url, XAI_CHAT_ENDPOINT);

    // Setup streaming context
    stream_write_context_t write_ctx = {0};
    write_ctx.callback = callback;
    write_ctx.user_data = user_data;
    write_ctx.buffer_capacity = 4096;
    write_ctx.buffer = malloc(write_ctx.buffer_capacity);
    if (!write_ctx.buffer) {
        curl_easy_cleanup(curl);
        json_object_put(request);
        return -1;
    }
    write_ctx.buffer_size = 0;
    write_ctx.buffer[0] = '\0';

    // Setup curl
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_POST, 1L);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_str);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, stream_write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &write_ctx);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, config->timeout);

    // Headers
    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");

    char auth_header[512];
    snprintf(auth_header, sizeof(auth_header), "Authorization: Bearer %s", config->api_key);
    headers = curl_slist_append(headers, auth_header);

    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    // Perform request - callback processes data incrementally during this call
    CURLcode res = curl_easy_perform(curl);

    // Cleanup
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    json_object_put(request);
    free(write_ctx.buffer);

    return (res == CURLE_OK) ? 0 : -1;
}

// Parse tool call from JSON
tool_call_t* parse_tool_call(const char *json_str) {
    if (!json_str) return NULL;
    
    json_object *json = json_tokener_parse(json_str);
    if (!json) return NULL;
    
    tool_call_t *tool_call = calloc(1, sizeof(tool_call_t));
    if (!tool_call) {
        json_object_put(json);
        return NULL;
    }
    
    json_object *id_obj, *name_obj, *args_obj;
    
    if (json_object_object_get_ex(json, "id", &id_obj)) {
        tool_call->id = strdup(json_object_get_string(id_obj));
    }
    
    if (json_object_object_get_ex(json, "function", &name_obj)) {
        json_object *fname_obj;
        if (json_object_object_get_ex(name_obj, "name", &fname_obj)) {
            tool_call->name = strdup(json_object_get_string(fname_obj));
        }
        
        if (json_object_object_get_ex(name_obj, "arguments", &args_obj)) {
            tool_call->arguments = json_object_get(args_obj);
        }
    }
    
    json_object_put(json);
    return tool_call;
}

void tool_call_destroy(tool_call_t *tool_call) {
    if (!tool_call) return;
    
    free(tool_call->id);
    free(tool_call->name);
    if (tool_call->arguments) {
        json_object_put(tool_call->arguments);
    }
    free(tool_call);
}
