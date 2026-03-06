# LIS (Lucas Index System) - Minimal build

CC := clang
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)

BUILD_DIR := build
LIB_DIR := lib
INC := -I.
CFLAGS := -std=c11 -O3 -Wall -Wextra $(INC)
LDFLAGS :=

LIB_STATIC := $(LIB_DIR)/liblis.a
LIB_SHARED := $(LIB_DIR)/liblis.dylib
ifeq ($(UNAME_S),Linux)
    LIB_SHARED := $(LIB_DIR)/liblis.so
    CFLAGS += -fPIC
    LDFLAGS += -shared -fPIC
else ifeq ($(UNAME_S),Darwin)
    LDFLAGS += -dynamiclib -install_name @rpath/liblis.dylib
endif

SOURCES := lis.c
OBJECTS := $(addprefix $(BUILD_DIR)/, $(SOURCES:.c=.o))

.DEFAULT_GOAL := all

all: $(LIB_STATIC) $(LIB_SHARED)

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(LIB_DIR):
	@mkdir -p $(LIB_DIR)

$(BUILD_DIR)/%.o: %.c | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

$(LIB_STATIC): $(OBJECTS) | $(LIB_DIR)
	@echo "Archiving: $@"
	@ar rcs $@ $^

$(LIB_SHARED): $(OBJECTS) | $(LIB_DIR)
	@echo "Linking: $@"
	@$(CC) $(LDFLAGS) -o $@ $^

clean:
	@rm -rf $(BUILD_DIR) $(LIB_DIR)

.PHONY: all clean

