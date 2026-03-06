#pragma once

typedef struct {
    const char *host;
    int port;
} config_t;

/**
 * Load host and port from command-line:
 *   --host <hostname> --port <portnumber>
 * Returns 0 on success.
 */
int load_config(config_t *cfg, int argc, char **argv);