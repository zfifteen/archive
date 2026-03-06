#include "server.h"
#include "http.h"
#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>

#ifdef APPLE_M1_MAX_OPTIMIZED
#include <sys/sysctl.h>
#include <sys/resource.h>
#include <pthread.h>
#endif

struct server {
    http_server_t *http;
};

static volatile sig_atomic_t keep_running = 1;
static void handle_sigint(int sig) { (void)sig; keep_running = 0; }

server_t *server_new(const config_t *cfg) {
#ifdef APPLE_M1_MAX_OPTIMIZED
    // Apple M1 Max optimizations
    printf("Apple M1 Max optimizations enabled\n");

    // Set process priority for performance
    setpriority(PRIO_PROCESS, 0, -10);

    // Query system info for M1 Max
    size_t size = sizeof(int);
    int ncpu;
    if (sysctlbyname("hw.ncpu", &ncpu, &size, NULL, 0) == 0) {
        printf("Detected %d CPU cores\n", ncpu);
    }
#endif

    http_server_t *http = http_server_new(cfg);
    if (!http) return NULL;
    server_t *srv = malloc(sizeof(*srv));
    if (!srv) {
        http_server_free(http);
        return NULL;
    }
    srv->http = http;
    return srv;
}

void server_run(server_t *srv) {
    (void)srv; // Use srv parameter if needed in future
    signal(SIGINT, handle_sigint);
    while (keep_running) {
        sleep(1);
    }
    printf("\nShutting down...\n");
}

void server_free(server_t *srv) {
    if (!srv) return;
    http_server_free(srv->http);
    free(srv);
}