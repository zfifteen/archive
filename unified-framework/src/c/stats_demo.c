#include "z5d_predictor.h"
#include <stdio.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <sys/time.h>

typedef struct { double n; double p; } known_t;
static const known_t KNOWN[] = {
    /* k=5 band */
    {  50000, 611953 }, {  60000, 746773 }, {  70000, 882377 },
    {  80000,1020379 }, {  90000,1159523 }, { 100000,1299709 },
    { 110000,1441049 }, { 120000,1583539 }, { 130000,1726943 },
    { 140000,1870667 },
    /* k=6 band */
    {  500000, 7368787 }, {  600000, 8960453 }, {  700000,10570841 },
    {  800000,12195257 }, {  900000,13834103 }, { 1000000,15485863 },
    { 1100000,17144489 }, { 1200000,18815231 }, { 1300000,20495843 },
    { 1400000,22182343 },
    /* k=7 band */
    {  5000000, 86028121 }, {  6000000,104395301 }, {  7000000,122949823 },
    {  8000000,141650939 }, {  9000000,160481183 }, { 10000000,179424673 },
    { 11000000,198491317 }, { 12000000,217645177 }, { 13000000,236887691 },
    { 14000000,256203161 },
    /* k=8 band */
    {  50000000, 982451653 }, {  60000000,1190494759 }, {  70000000,1400305337 },
    {  80000000,1611623773 }, {  90000000,1824261409 }, { 100000000,2038074743 },
    { 110000000,2252945251 }, { 120000000,2468776129 }, { 130000000,2685457421 },
    { 140000000,2902958801 },
    /* refs k=9..18 */
    { 1e9,  2.2801763489e10 }, { 1e10, 2.52097800623e11 },
    { 1e11, 2.760727302517e12 }, { 1e12, 2.9996224275833e13 },
    { 1e13, 3.23780508946331e14 }, { 1e14, 3.475385758524527e15 },
    { 1e15, 3.7124508045065437e16 }, { 1e16, 3.94906913903735329e17 },
    { 1e17, 4.185296581467695669e18 }, { 1e18, 4.4211790234832169331e19 }
};
static const int N_KNOWN = (int)(sizeof(KNOWN)/sizeof(KNOWN[0]));

/* -------- timing (high-res) -------- */
static double now_s(void){
    struct timeval tv;
    if (gettimeofday(&tv, NULL) == 0) {
        return tv.tv_sec + tv.tv_usec / 1e6;
    }
    return (double)clock() / CLOCKS_PER_SEC;
}

/* -------- helpers -------- */
static inline double absd(double x){ return x < 0 ? -x : x; }
static inline double rel_err(double got, double want){
    return (want==0.0) ? NAN : (got - want)/want;
}
static int band_from_n(double n){
    if (n >= 1e18) return 18;
    if (n >= 1e17) return 17;
    if (n >= 1e16) return 16;
    if (n >= 1e15) return 15;
    if (n >= 1e14) return 14;
    if (n >= 1e13) return 13;
    if (n >= 1e12) return 12;
    if (n >= 1e11) return 11;
    if (n >= 1e10) return 10;
    if (n >= 1e9)  return 9;
    if (n >= 1e8)  return 8;
    if (n >= 1e7)  return 7;
    if (n >= 1e6)  return 6;
    return 5;
}

typedef struct {
    int count;
    double sum_abs_rel;
    double max_abs_rel;
    double total_time_s;
} band_stats_t;

int main(void){
    const int MIN_BAND = 5, MAX_BAND = 18;
    band_stats_t bands[19]; /* index = band */
    memset(bands, 0, sizeof(bands));

    int csv = 0;
    const char* env = getenv("Z5D_CSV");
    if (env && (*env=='1')) csv = 1;
    FILE* fcsv = NULL;
    if (csv) {
        fcsv = fopen("z5d_known_stats.csv","w");
        if (fcsv) {
            fprintf(fcsv, "n,true_p,pred,abs_err,rel_err_percent,ppm,time_sec,band\n");
        } else {
            csv = 0; /* fall back silently */
        }
    }

    printf("Z5D Predictor Full Stats Run (KNOWN list, N=%d)\n", N_KNOWN);
    printf("-------------------------------------------------------------------------------\n");
    printf("%12s %20s %20s %12s %12s %12s\n","n","true_p","pred","abs_err","rel_err%","ppm");
    printf("-------------------------------------------------------------------------------\n");

    double global_sum_abs_rel = 0.0, global_max_abs_rel = 0.0;
    double T0 = now_s();
    for (int i=0;i<N_KNOWN;i++){
        double n = KNOWN[i].n, truep = KNOWN[i].p;

        double t0 = now_s();
        double pred = z5d_prime(n, 0.0, 0.0, Z5D_DEFAULT_KAPPA_GEO, 1);
        double t1 = now_s();
        double dt = t1 - t0;

        double err = pred - truep;
        double rel = rel_err(pred, truep);
        double abs_rel = fabs(rel);
        double ppm = rel * 1e6;

        printf("%12.0f %20.0f %20.6f %12.0f %12.6f %12.1f   (%.3g s)\n",
               n, truep, pred, err, 100.0*rel, ppm, dt);

        if (csv && fcsv) {
            int b = band_from_n(n);
            fprintf(fcsv, "%.0f,%.0f,%.6f,%.0f,%.6f,%.1f,%.9f,%d\n",
                    n, truep, pred, err, 100.0*rel, ppm, dt, b);
        }

        global_sum_abs_rel += abs_rel;
        if (abs_rel > global_max_abs_rel) global_max_abs_rel = abs_rel;

        int band = band_from_n(n);
        bands[band].count += 1;
        bands[band].sum_abs_rel += abs_rel;
        if (abs_rel > bands[band].max_abs_rel) bands[band].max_abs_rel = abs_rel;
        bands[band].total_time_s += dt;
    }
    double T1 = now_s();
    if (fcsv) fclose(fcsv);

    printf("-------------------------------------------------------------------------------\n");
    printf("GLOBAL  Mean |rel_err| = %.6f%%   Max |rel_err| = %.6f%%\n",
           100.0*(global_sum_abs_rel/N_KNOWN), 100.0*global_max_abs_rel);
    printf("GLOBAL  Total runtime %.6f sec (avg %.6f sec/pred)\n",
           (T1-T0), (T1-T0)/N_KNOWN);

    /* per-band summary */
    printf("\nPer-band summary:\n");
    printf("%6s %6s %18s %18s %18s\n","band","N","mean|rel|%","max|rel|%","avg_time_us");
    for (int b=MIN_BAND; b<=MAX_BAND; b++){
        if (bands[b].count == 0) continue;
        double mean_abs_rel = bands[b].sum_abs_rel / (double)bands[b].count;
        double max_abs_rel  = bands[b].max_abs_rel;
        double avg_us = (bands[b].total_time_s / (double)bands[b].count) * 1e6;
        printf("%6d %6d %18.6f %18.6f %18.2f\n",
               b, bands[b].count, 100.0*mean_abs_rel, 100.0*max_abs_rel, avg_us);
    }
    return 0;
}
