#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>

#define MAX_K_ITERATIONS 100  // Maximum iterations for k loop in theta prime computation
// Function to compute theta'(n, k) = phi * ((n mod phi) / phi)^k
// Using GMP for high precision

int main() {
    // Set default precision to 1200 bits (about 360 decimal digits, enough for RSA-100)
    mpf_set_default_prec(1200);

    // Initialize GMP floats
    mpf_t n, phi, mod, div, power, theta, one, five, sqrt_five, two, quotient, floor_q, frac_part;
    mpf_inits(n, phi, mod, div, power, theta, one, five, sqrt_five, two, quotient, floor_q, frac_part, NULL);

    // Set constants
    mpf_set_ui(one, 1);
    mpf_set_ui(five, 5);
    mpf_set_ui(two, 2);
    mpf_sqrt(sqrt_five, five);
    mpf_add(phi, one, sqrt_five);
    mpf_div(phi, phi, two);  // phi = (1 + sqrt(5)) / 2

    // Set n to RSA-100
    const char *n_str = "1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139";
    mpf_set_str(n, n_str, 10);

    // Loop over k
    for (int k = 0; k < MAX_K_ITERATIONS; k++) {  // Increase max k
        // Compute mod = n mod phi
        mpf_div(quotient, n, phi);
        mpf_floor(floor_q, quotient);
        mpf_mul(quotient, floor_q, phi);
        mpf_sub(mod, n, quotient);  // mod = n - floor(n/phi) * phi

        // Compute div = mod / phi
        mpf_div(div, mod, phi);  // This should be the fractional part

        // Compute power = div^k
        mpf_set_ui(power, 1);  // Start with 1
        for (int i = 0; i < k; i++) {
            mpf_mul(power, power, div);
        }

        // Compute theta = phi * power
        mpf_mul(theta, phi, power);

        // Round to nearest integer
        mpf_t half;
        mpf_init(half);
        mpf_set_d(half, 0.5);
        mpf_add(theta, theta, half);
        mpz_t theta_int;
        mpz_init(theta_int);
        mpf_get_z(theta_int, theta);  // Rounds towards zero after adding 0.5

        // Check if theta_int is prime
        if (mpz_probab_prime_p(theta_int, 25) > 0) {  // Probabilistic primality test
            // Check if theta_int divides n
            mpz_t q_test, p_test, n_mpz;
            mpz_init(q_test);
            mpz_init(p_test);
            mpz_init(n_mpz);
            mpf_get_z(n_mpz, n);

            mpz_div(q_test, n_mpz, theta_int);
            mpz_mul(p_test, theta_int, q_test);

            if (mpz_cmp(p_test, n_mpz) == 0) {
                // Found!
                gmp_printf("Found p: %Zd\n", theta_int);
                gmp_printf("Found q: %Zd\n", q_test);
                mpz_clear(theta_int);
                mpf_clear(half);
                break;
            }
            mpz_clears(q_test, p_test, n_mpz, NULL);
        }

        // Clean up
        mpz_clear(theta_int);
        mpf_clear(half);
    }

    // Clear GMP variables
    mpf_clears(n, phi, mod, div, power, theta, one, five, sqrt_five, two, quotient, floor_q, frac_part, NULL);

    return 0;
}