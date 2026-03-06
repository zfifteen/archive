/**
 * @file xai_client.h
 * @brief XAI Chat Streaming Client - Header
 * 
 * XAI API client for streaming chat completions with bash tool execution.
 * Integrates with GMP/MPFR for large number support as per framework requirements.
 */

#ifndef XAI_CLIENT_H
#define XAI_CLIENT_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <json-c/json.h>
#include <gmp.h>
#include <mpfr.h>

// Configuration constants
#define XAI_API_BASE_URL "https://api.x.ai/v1"
#define XAI_CHAT_ENDPOINT "/chat/completions"
#define MAX_MESSAGE_SIZE 1048576  // 1MB
#define MAX_CONVERSATION_HISTORY 100
#define DEFAULT_TIMEOUT 300  // 5 minutes
#define MPFR_PRECISION_BITS 256

// Model selection
typedef enum {
    XAI_MODEL_GROK_CODE_FAST_1,
    XAI_MODEL_GROK_4
} xai_model_t;

// Message role
typedef enum {
    ROLE_SYSTEM,
    ROLE_USER,
    ROLE_ASSISTANT
} message_role_t;

// Message structure
typedef struct {
    message_role_t role;
    char *content;
    char *tool_call_id;  // For tool responses
    json_object *tool_calls;  // For assistant tool calls
} message_t;

// Conversation context
typedef struct {
    message_t **messages;
    size_t message_count;
    size_t capacity;
} conversation_t;

// XAI Client configuration
typedef struct {
    char *api_key;
    char *base_url;  // For mock server override
    xai_model_t model;
    int timeout;
    int verbose;
} xai_config_t;

// Stream chunk callback
typedef void (*stream_callback_t)(const char *chunk, void *user_data);

// Response structure
typedef struct {
    char *data;
    size_t size;
    int status_code;
    char *error_message;
} response_t;

// Tool call structure
typedef struct {
    char *id;
    char *name;
    json_object *arguments;
} tool_call_t;

// Client API functions
xai_config_t* xai_config_create(const char *api_key, xai_model_t model);
void xai_config_destroy(xai_config_t *config);
void xai_config_set_base_url(xai_config_t *config, const char *base_url);

conversation_t* conversation_create(void);
void conversation_destroy(conversation_t *conv);
void conversation_add_message(conversation_t *conv, message_role_t role, const char *content);
void conversation_add_tool_response(conversation_t *conv, const char *tool_call_id, const char *content);

int xai_stream_chat(xai_config_t *config, conversation_t *conv, stream_callback_t callback, void *user_data);
tool_call_t* parse_tool_call(const char *json_str);
void tool_call_destroy(tool_call_t *tool_call);

// Utility functions
const char* model_to_string(xai_model_t model);
const char* role_to_string(message_role_t role);

#endif // XAI_CLIENT_H
