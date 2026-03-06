/**
 * @file mock_xai_server.c
 * @brief Mock XAI API Server for Testing
 * 
 * Simulates XAI API behavior for testing the chat streaming client.
 * Supports streaming SSE responses and tool call simulation.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <json-c/json.h>

#define DEFAULT_PORT 8080
#define BUFFER_SIZE 65536

static volatile int keep_running = 1;

void signal_handler(int signum) {
    (void)signum;
    keep_running = 0;
}

// Send SSE chunk
void send_sse_chunk(int client_fd, const char *data) {
    char response[4096];
    snprintf(response, sizeof(response), "data: %s\n\n", data);
    send(client_fd, response, strlen(response), 0);
    usleep(50000);  // 50ms delay for realistic streaming
}

// Handle chat completion request
void handle_chat_request(int client_fd, const char *request_body) {
    // Parse request
    json_object *request = json_tokener_parse(request_body);
    if (!request) {
        const char *error_response = "HTTP/1.1 400 Bad Request\r\n\r\n";
        send(client_fd, error_response, strlen(error_response), 0);
        return;
    }
    
    json_object *messages;
    if (!json_object_object_get_ex(request, "messages", &messages)) {
        const char *error_response = "HTTP/1.1 400 Bad Request\r\n\r\n";
        send(client_fd, error_response, strlen(error_response), 0);
        json_object_put(request);
        return;
    }
    
    // Get last user message
    size_t num_messages = json_object_array_length(messages);
    const char *user_message = NULL;
    
    for (size_t i = num_messages; i > 0; i--) {
        json_object *msg = json_object_array_get_idx(messages, i - 1);
        json_object *role, *content;
        
        if (json_object_object_get_ex(msg, "role", &role) &&
            strcmp(json_object_get_string(role), "user") == 0 &&
            json_object_object_get_ex(msg, "content", &content)) {
            user_message = json_object_get_string(content);
            break;
        }
    }
    
    // Send HTTP headers for SSE
    const char *headers = 
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/event-stream\r\n"
        "Cache-Control: no-cache\r\n"
        "Connection: keep-alive\r\n"
        "\r\n";
    send(client_fd, headers, strlen(headers), 0);
    
    // Determine response based on user message
    int request_tool_call = 0;
    const char *command_to_run = NULL;
    
    if (user_message) {
        if (strstr(user_message, "list files") || strstr(user_message, "ls")) {
            request_tool_call = 1;
            command_to_run = "ls -la";
        } else if (strstr(user_message, "date") || strstr(user_message, "time")) {
            request_tool_call = 1;
            command_to_run = "date";
        } else if (strstr(user_message, "pwd") || strstr(user_message, "directory")) {
            request_tool_call = 1;
            command_to_run = "pwd";
        }
    }
    
    if (request_tool_call && command_to_run) {
        // Send tool call response
        json_object *response = json_object_new_object();
        json_object *choices = json_object_new_array();
        json_object *choice = json_object_new_object();
        
        json_object_object_add(choice, "index", json_object_new_int(0));
        
        json_object *delta = json_object_new_object();
        json_object *tool_calls = json_object_new_array();
        json_object *tool_call = json_object_new_object();
        
        json_object_object_add(tool_call, "id", json_object_new_string("call_123"));
        json_object_object_add(tool_call, "type", json_object_new_string("function"));
        
        json_object *function = json_object_new_object();
        json_object_object_add(function, "name", json_object_new_string("bash"));
        
        json_object *arguments = json_object_new_object();
        json_object_object_add(arguments, "command", json_object_new_string(command_to_run));
        json_object_object_add(function, "arguments", json_object_new_string(json_object_to_json_string(arguments)));
        
        json_object_object_add(tool_call, "function", function);
        json_object_array_add(tool_calls, tool_call);
        json_object_object_add(delta, "tool_calls", tool_calls);
        
        json_object_object_add(choice, "delta", delta);
        json_object_array_add(choices, choice);
        json_object_object_add(response, "choices", choices);
        
        send_sse_chunk(client_fd, json_object_to_json_string(response));
        json_object_put(response);
    } else {
        // Send text response
        const char *response_text = user_message && strlen(user_message) > 0 ?
            "I'm a mock XAI server. I received your message and I'm here to help! " :
            "Hello! I'm a mock XAI server for testing. How can I help you?";
        
        size_t text_len = strlen(response_text);
        for (size_t i = 0; i < text_len; i += 10) {
            json_object *response = json_object_new_object();
            json_object *choices = json_object_new_array();
            json_object *choice = json_object_new_object();
            
            json_object_object_add(choice, "index", json_object_new_int(0));
            
            json_object *delta = json_object_new_object();
            
            char chunk[11];
            size_t chunk_len = (i + 10 <= text_len) ? 10 : text_len - i;
            strncpy(chunk, response_text + i, chunk_len);
            chunk[chunk_len] = '\0';
            
            json_object_object_add(delta, "content", json_object_new_string(chunk));
            json_object_object_add(choice, "delta", delta);
            json_object_array_add(choices, choice);
            json_object_object_add(response, "choices", choices);
            
            send_sse_chunk(client_fd, json_object_to_json_string(response));
            json_object_put(response);
        }
    }
    
    // Send [DONE] marker
    const char *done_marker = "data: [DONE]\n\n";
    send(client_fd, done_marker, strlen(done_marker), 0);
    
    json_object_put(request);
}

int main(int argc, char *argv[]) {
    int port = DEFAULT_PORT;
    
    // Parse arguments
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--port") == 0 && i + 1 < argc) {
            port = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--help") == 0) {
            printf("Usage: %s [--port PORT]\n", argv[0]);
            printf("\nOptions:\n");
            printf("  --port PORT    Listen port (default: 8080)\n");
            printf("  --help         Show this help\n");
            return 0;
        }
    }
    
    // Create socket
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return 1;
    }
    
    // Set socket options
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(server_fd);
        return 1;
    }
    
    // Bind socket
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);
    
    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(server_fd);
        return 1;
    }
    
    // Listen
    if (listen(server_fd, 5) < 0) {
        perror("listen");
        close(server_fd);
        return 1;
    }
    
    printf("Mock XAI API Server running on port %d\n", port);
    printf("Press Ctrl+C to stop\n\n");
    
    // Setup signal handler
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Accept connections
    while (keep_running) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(server_fd, &readfds);
        
        struct timeval tv;
        tv.tv_sec = 1;
        tv.tv_usec = 0;
        
        int activity = select(server_fd + 1, &readfds, NULL, NULL, &tv);
        
        if (activity < 0) {
            if (!keep_running) break;
            perror("select");
            continue;
        }
        
        if (activity == 0) {
            continue;
        }
        
        int client_fd = accept(server_fd, NULL, NULL);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }
        
        printf("Client connected\n");
        
        // Read request
        char buffer[BUFFER_SIZE];
        ssize_t bytes_read = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
        
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            
            // Find request body (after headers)
            char *body = strstr(buffer, "\r\n\r\n");
            if (body) {
                body += 4;
                
                // Check if it's a POST to /v1/chat/completions
                if (strstr(buffer, "POST /v1/chat/completions") != NULL) {
                    handle_chat_request(client_fd, body);
                } else {
                    const char *not_found = "HTTP/1.1 404 Not Found\r\n\r\n";
                    send(client_fd, not_found, strlen(not_found), 0);
                }
            }
        }
        
        close(client_fd);
        printf("Client disconnected\n\n");
    }
    
    close(server_fd);
    printf("\nServer stopped\n");
    
    return 0;
}
