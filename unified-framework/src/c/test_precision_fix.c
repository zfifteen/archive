/*
 * Test for precision bug fix in geodesic_z5d_search.c
 * 
 * This test verifies that consecutive k values at extreme scales
 * produce distinct predictions and don't result in duplicate primes.
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    printf("Testing precision fix for geodesic_z5d_search.c\n");
    printf("================================================\n\n");
    
    // Test with the extreme k value from the issue
    unsigned long long test_k = 37124508045065437ULL;
    char command[256];
    
    printf("Testing with k_start = %llu (extreme scale)\n", test_k);
    
    // Use the Makefile-built executable
    snprintf(command, sizeof(command), "./bin/geodesic_z5d_search %llu 5", test_k);
    printf("Running: %s\n\n", command);
    
    FILE* fp = popen(command, "r");
    if (fp == NULL) {
        printf("ERROR: Failed to run test command\n");
        return 1;
    }
    
    char line[512];
    char previous_prime[64] = "";
    int distinct_primes = 0;
    int total_primes = 0;
    
    while (fgets(line, sizeof(line), fp) != NULL) {
        if (strncmp(line, "k=", 2) == 0) {
            // Extract prime from line format: "k=... Prime: ..."
            char* prime_start = strstr(line, "Prime: ");
            if (prime_start) {
                prime_start += 7; // Skip "Prime: "
                char current_prime[64];
                sscanf(prime_start, "%63s", current_prime);
                
                total_primes++;
                
                if (strlen(previous_prime) == 0 || strcmp(previous_prime, current_prime) != 0) {
                    distinct_primes++;
                    strcpy(previous_prime, current_prime);
                    printf("✓ k=%llu Prime: %s (distinct)\n", test_k + total_primes - 1, current_prime);
                } else {
                    printf("✗ k=%llu Prime: %s (DUPLICATE)\n", test_k + total_primes - 1, current_prime);
                }
            }
        }
    }
    
    pclose(fp);
    
    printf("\nTest Results:\n");
    printf("Total primes found: %d\n", total_primes);
    printf("Distinct primes: %d\n", distinct_primes);
    
    if (distinct_primes == total_primes && total_primes > 0) {
        printf("✅ SUCCESS: All primes are distinct - precision bug fixed!\n");
        return 0;
    } else {
        printf("❌ FAILURE: Found duplicate primes - precision bug still exists\n");
        return 1;
    }
}
