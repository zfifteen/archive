#include "server.h"
#include <stdio.h>

int main(int argc, char **argv) {
    config_t cfg;
    if (load_config(&cfg, argc, argv) != 0) {
        fprintf(stderr, "Usage: %s --host <host> --port <port>\n", argv[0]);
        return 1;
    }

    server_t *srv = server_new(&cfg);
    if (!srv) {
        fprintf(stderr, "Failed to initialize server\n");
        return 1;
    }

    printf("MCP Server starting on %s:%d\n", cfg.host, cfg.port);
    server_run(srv);
    server_free(srv);
    return 0;
}