/**
 * @file sse_parser.h
 * @brief Server-Sent Events (SSE) Parser
 * 
 * Parses Server-Sent Events streaming responses from XAI API.
 */

#ifndef SSE_PARSER_H
#define SSE_PARSER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <json-c/json.h>

// SSE event types
typedef enum {
    SSE_EVENT_DATA,
    SSE_EVENT_DONE,
    SSE_EVENT_ERROR
} sse_event_type_t;

// SSE event structure
typedef struct {
    sse_event_type_t type;
    char *data;
    char *event;
    char *id;
} sse_event_t;

// SSE parser state
typedef struct {
    char *buffer;
    size_t buffer_size;
    size_t buffer_capacity;
} sse_parser_t;

// Parser functions
sse_parser_t* sse_parser_create(void);
void sse_parser_destroy(sse_parser_t *parser);
sse_event_t* sse_parser_feed(sse_parser_t *parser, const char *data, size_t size);
void sse_event_destroy(sse_event_t *event);

#endif // SSE_PARSER_H
