#pragma once
#include "config.h"

typedef struct server server_t;

/**
 * Initialize and return a new server instance.
 */
server_t *server_new(const config_t *cfg);

/**
 * Run the server event loop (blocks until process exit).
 */
void server_run(server_t *srv);

/**
 * Cleanup and free all server resources.
 */
void server_free(server_t *srv);