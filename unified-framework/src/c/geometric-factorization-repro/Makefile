# Makefile for Geometric Factorization Reproduction
# Minimal C implementation of multi-pass golden ratio factorization

CC = clang
CFLAGS = -std=c99 -Wall -Wextra -O3 -I/opt/homebrew/include -I.. -I../4096-pipeline
LDFLAGS = -L/opt/homebrew/lib -lmpfr -lgmp -lm -lssl -lcrypto

TARGET = bin/geometric_factorization_repro
SOURCES = main.c ../z5d_predictor.c golden_spiral.c
OBJECTS = lib/main.o lib/z5d_predictor.o lib/golden_spiral.o

.PHONY: all clean dirs

all: dirs $(TARGET)

dirs:
	mkdir -p bin lib

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

lib/main.o: main.c
	$(CC) $(CFLAGS) -c $< -o $@

lib/z5d_predictor.o: ../z5d_predictor.c
	$(CC) $(CFLAGS) -c $< -o $@

lib/golden_spiral.o: golden_spiral.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TARGET) $(OBJECTS)
	rm -rf bin lib

.PHONY: all clean dirs