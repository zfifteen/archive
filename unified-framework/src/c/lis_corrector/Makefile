# LIS Corrector (Z5D seed + LIS + MR)

CC := clang
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)

SRC_DIR := .
BUILD_DIR := build
LIB_DIR := lib

INC := -I. -I../lis -I..
CFLAGS := -std=c11 -O3 -Wall -Wextra $(INC)
LDFLAGS :=

# Detect MPFR/GMP locations (Homebrew/Unix fallbacks)
GMP_INCLUDE := $(shell \
    if test -f /opt/homebrew/include/gmp.h; then echo -I/opt/homebrew/include; \
    elif test -f /usr/local/include/gmp.h; then echo -I/usr/local/include; \
    elif test -f /usr/include/gmp.h; then echo -I/usr/include; \
    else echo ""; fi)

MPFR_INCLUDE := $(shell \
    if test -f /opt/homebrew/include/mpfr.h; then echo -I/opt/homebrew/include; \
    elif test -f /usr/local/include/mpfr.h; then echo -I/usr/local/include; \
    elif test -f /usr/include/mpfr.h; then echo -I/usr/include; \
    else echo ""; fi)

MPFR_LDFLAGS := $(shell \
    if test -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib -lmpfr -lgmp; \
    elif test -f /usr/local/lib/libmpfr.a -o -f /usr/local/lib/libmpfr.dylib; then echo -L/usr/local/lib -lmpfr -lgmp; \
    elif test -f /usr/lib/libmpfr.so; then echo -L/usr/lib -lmpfr -lgmp; \
    else echo -lmpfr -lgmp; fi)

CFLAGS += $(GMP_INCLUDE) $(MPFR_INCLUDE)

LIB_SHARED := $(LIB_DIR)/liblis_corrector.dylib
ifeq ($(UNAME_S),Linux)
    LIB_SHARED := $(LIB_DIR)/liblis_corrector.so
    CFLAGS += -fPIC
    LDFLAGS += -shared -fPIC
else ifeq ($(UNAME_S),Darwin)
    LDFLAGS += -dynamiclib -install_name @rpath/liblis_corrector.dylib
endif

OBJECTS := $(BUILD_DIR)/lis_corrector.o

.DEFAULT_GOAL := all

all: $(LIB_SHARED)

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(LIB_DIR):
	@mkdir -p $(LIB_DIR)

$(BUILD_DIR)/%.o: %.c | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

$(LIB_SHARED): $(OBJECTS) | $(LIB_DIR)
	@echo "Linking: $@"
	@$(CC) $(LDFLAGS) -o $@ $^ -L../lis/lib -llis -L../lib -lz5d $(MPFR_LDFLAGS) \
		-Wl,-rpath,../lib -Wl,-rpath,../lis/lib -Wl,-rpath,/opt/homebrew/lib -Wl,-rpath,/usr/local/lib

clean:
	@rm -rf $(BUILD_DIR) $(LIB_DIR)

.PHONY: all clean
