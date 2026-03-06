/**
 * @file sse_parser.c
 * @brief Server-Sent Events (SSE) Parser - Implementation
 */

#include "sse_parser.h"

// Create SSE parser
sse_parser_t* sse_parser_create(void) {
    sse_parser_t *parser = calloc(1, sizeof(sse_parser_t));
    if (!parser) {
        return NULL;
    }
    
    parser->buffer_capacity = 4096;
    parser->buffer = malloc(parser->buffer_capacity);
    if (!parser->buffer) {
        free(parser);
        return NULL;
    }
    
    parser->buffer_size = 0;
    
    return parser;
}

void sse_parser_destroy(sse_parser_t *parser) {
    if (!parser) return;
    
    free(parser->buffer);
    free(parser);
}

// Feed data to parser and extract events
sse_event_t* sse_parser_feed(sse_parser_t *parser, const char *data, size_t size) {
    if (!parser || !data || size == 0) {
        return NULL;
    }
    
    // Grow buffer if needed
    while (parser->buffer_size + size >= parser->buffer_capacity) {
        size_t new_capacity = parser->buffer_capacity * 2;
        char *new_buffer = realloc(parser->buffer, new_capacity);
        if (!new_buffer) {
            return NULL;
        }
        parser->buffer = new_buffer;
        parser->buffer_capacity = new_capacity;
    }
    
    // Append data to buffer
    memcpy(parser->buffer + parser->buffer_size, data, size);
    parser->buffer_size += size;
    parser->buffer[parser->buffer_size] = '\0';
    
    // Parse SSE format: "data: {...}\n\n" or "data: [DONE]\n\n"
    char *line_start = parser->buffer;
    char *line_end;
    sse_event_t *event = NULL;
    
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
                event = calloc(1, sizeof(sse_event_t));
                if (event) {
                    event->type = SSE_EVENT_DONE;
                }
                break;
            }
            
            // Parse JSON data
            if (strlen(data_content) > 0) {
                event = calloc(1, sizeof(sse_event_t));
                if (event) {
                    event->type = SSE_EVENT_DATA;
                    event->data = strdup(data_content);
                }
                break;
            }
        }
        
        line_start = line_end + 1;
    }
    
    // Reset buffer after processing
    if (event) {
        parser->buffer_size = 0;
    }
    
    return event;
}

void sse_event_destroy(sse_event_t *event) {
    if (!event) return;
    
    free(event->data);
    free(event->event);
    free(event->id);
    free(event);
}
