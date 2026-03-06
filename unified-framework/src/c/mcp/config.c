#include "config.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>

int load_config(config_t *cfg, int argc, char **argv) {
    // Set defaults
    cfg->host = "127.0.0.1";
    cfg->port = 8080;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--host") == 0 && i + 1 < argc) {
            cfg->host = argv[++i];
        }
        else if (strcmp(argv[i], "--port") == 0 && i + 1 < argc) {
            char *endptr;
            errno = 0;
            long port = strtol(argv[++i], &endptr, 10);
            if (errno != 0 || *endptr != '\0' || port < 1 || port > 65535) {
                fprintf(stderr, "Invalid port number: %s (must be 1-65535)\n", argv[i]);
                return -1;
            }
            cfg->port = (int)port;
        }
    }
    
    return 0;
}