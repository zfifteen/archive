# Makefile for Geometric Factorization Optimized Demo
# Minimal C implementation of multi-pass golden ratio factorization

CC = clang
CFLAGS = -std=c99 -Wall -Wextra -O3 -march=native -I/opt/homebrew/include -I.. -I../4096-pipeline
LDFLAGS = -L/opt/homebrew/lib -lmpfr -lgmp -lm -lssl -lcrypto

TARGET = bin/geometric_factorization_optimized_demo
PREDICTOR_TARGET = bin/predictor_optimization
SOURCES = main.c ../z5d_predictor.c golden_spiral.c
PREDICTOR_SOURCES = predictor_optimization.c
OBJECTS = lib/main.o lib/z5d_predictor.o lib/golden_spiral.o
PREDICTOR_OBJECTS = lib/predictor_optimization.o

.PHONY: all clean dirs predictor

all: dirs $(TARGET)

predictor: dirs $(PREDICTOR_TARGET)

dirs:
	mkdir -p bin lib

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

$(PREDICTOR_TARGET): $(PREDICTOR_OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

lib/main.o: main.c
	$(CC) $(CFLAGS) -c $< -o $@

lib/z5d_predictor.o: ../z5d_predictor.c
	$(CC) $(CFLAGS) -c $< -o $@

lib/golden_spiral.o: golden_spiral.c
	$(CC) $(CFLAGS) -c $< -o $@

lib/predictor_optimization.o: predictor_optimization.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TARGET) $(PREDICTOR_TARGET) $(OBJECTS) $(PREDICTOR_OBJECTS)
	rm -rf bin lib

.PHONY: all clean dirs predictor