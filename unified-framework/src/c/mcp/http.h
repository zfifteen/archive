#pragma once
#include "config.h"
#include <civetweb.h>

/**
 * Opaque handle to the HTTP server.
 */
typedef struct {
    struct mg_context *ctx;
} http_server_t;

/**
 * Start HTTP server, register endpoints, return handle.
 */
http_server_t *http_server_new(const config_t *cfg);

/**
 * Stop server and free resources.
 */
void http_server_free(http_server_t *srv);