#include "http.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <civetweb.h>

static void json_escape(const char *in, char *out, size_t out_sz) {
    size_t j = 0;
    for (size_t i = 0; in[i] && j + 2 < out_sz; ++i) {
        unsigned char c = (unsigned char)in[i];
        switch (c) {
            case '\"': if (j+2 < out_sz) { out[j++]='\\'; out[j++]='\"'; } break;
            case '\\': if (j+2 < out_sz) { out[j++]='\\'; out[j++]='\\'; } break;
            case '\n': if (j+2 < out_sz) { out[j++]='\\'; out[j++]='n'; } break;
            case '\r': if (j+2 < out_sz) { out[j++]='\\'; out[j++]='r'; } break;
            case '\t': if (j+2 < out_sz) { out[j++]='\\'; out[j++]='t'; } break;
            default:
                if (c < 0x20) {
                    if (j + 6 < out_sz) j += snprintf(out + j, out_sz - j, "\\u%04x", c);
                } else {
                    out[j++] = c;
                }
        }
    }
    out[j] = '\0';
}

static int count_handler(struct mg_connection *conn, void *cbdata) {
    (void)cbdata;
    const char *reply = "{ \"count\": 42 }";
    mg_printf(conn,
              "HTTP/1.1 200 OK\r\n"
              "Content-Type: application/json\r\n"
              "Content-Length: %zu\r\n"
              "\r\n"
              "%s",
              strlen(reply), reply);
    return 1;
}

static int echo_handler(struct mg_connection *conn, void *cbdata) {
    (void)cbdata;
    const struct mg_request_info *req_info = mg_get_request_info(conn);
    char msg_raw[256] = "";
    
    if (req_info->query_string) {
        mg_get_var(req_info->query_string, strlen(req_info->query_string),
                   "msg", msg_raw, sizeof(msg_raw));
    }
    
    char msg_esc[512];
    json_escape(msg_raw, msg_esc, sizeof(msg_esc));
    
    char buf[1024];
    int len = snprintf(buf, sizeof(buf),
                       "{ \"echo\": \"%s\" }", msg_esc);
    mg_printf(conn,
              "HTTP/1.1 200 OK\r\n"
              "Content-Type: application/json\r\n"
              "Content-Length: %d\r\n"
              "\r\n"
              "%s",
              len, buf);
    return 1;
}

static int health_handler(struct mg_connection *conn, void *cbdata) {
    (void)cbdata;
    const char *reply = "{ \"status\": \"ok\" }";
    mg_printf(conn,
              "HTTP/1.1 200 OK\r\n"
              "Content-Type: application/json\r\n"
              "Content-Length: %zu\r\n"
              "\r\n"
              "%s",
              strlen(reply), reply);
    return 1;
}

http_server_t *http_server_new(const config_t *cfg) {
    char listen[64];
    snprintf(listen, sizeof(listen), "%s:%d", cfg->host, cfg->port);

    const char *options[] = {
        "listening_ports", listen,
        NULL
    };
    struct mg_context *ctx = mg_start(NULL, NULL, options);
    if (!ctx) {
        fprintf(stderr, "Failed to start HTTP server on %s\n", listen);
        return NULL;
    }

    mg_set_request_handler(ctx, "/tools/count", count_handler, NULL);
    mg_set_request_handler(ctx, "/tools/echo",  echo_handler,  NULL);
    mg_set_request_handler(ctx, "/healthz", health_handler, NULL);

    http_server_t *s = malloc(sizeof(*s));
    if (!s) {
        fprintf(stderr, "Failed to allocate memory for http_server_t\n");
        mg_stop(ctx);
        return NULL;
    }
    if (!s) {
        mg_stop(ctx);
        return NULL;
    }
    s->ctx = ctx;
    return s;
}

void http_server_free(http_server_t *srv) {
    if (!srv) return;
    mg_stop(srv->ctx);
    free(srv);
}