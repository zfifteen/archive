CC = gcc
CFLAGS = -O3 -Wall -Wextra -pthread -Icivetweb/include
LDFLAGS = -Lcivetweb -lcivetweb

# Detect Apple M1 Max and apply optimizations
UNAME_M := $(shell uname -m)
ifeq ($(UNAME_M),arm64)
    # Apple M1 Max specific optimizations
    CFLAGS += -march=armv8.4-a+fp16+rcpc+dotprod+crypto -mtune=apple-m1 -mcpu=apple-m1
    CFLAGS += -ffast-math -funroll-loops -fomit-frame-pointer
    CFLAGS += -DAPPLE_M1_MAX_OPTIMIZED=1
endif

SRC = main.c config.c server.c http.c
OBJ = $(SRC:.c=.o)
TARGET = mcp-server

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)