/**
 * @file lis_corrector.h
 * @brief LIS-enhanced nth-prime correction using Z5D seed (Proof of Concept)
 */

#ifndef LIS_CORRECTOR_H
#define LIS_CORRECTOR_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Correct the n-th prime using a Z5D seed p0 and LIS (wheel-210 + Lucas) with MR.
 *
 * @param n            target prime index (1-indexed)
 * @param window       max absolute distance from seed to search (in integers)
 * @param out_prime    [out] exact n-th prime (when return 0)
 * @param out_mr_calls [out] number of MR verifications performed
 * @param out_baseline [out] number of wheel-210 candidates considered
 * @return 0 on success; non-zero on failure (not found within window)
 */
int lis_correct_nth_prime(uint64_t n, uint64_t window,
                          uint64_t* out_prime,
                          uint64_t* out_mr_calls,
                          uint64_t* out_baseline);

#ifdef __cplusplus
}
#endif

#endif /* LIS_CORRECTOR_H */

