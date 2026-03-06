#!/usr/bin/env bash
# run_geodesic_mr_level2.sh
# Level-2 validation driver for Lopez Geodesic–MR.
# - Runs larger contiguous ranges
# - Optionally runs adversarial suites (if the Python script supports --from-file)
# - Optionally runs uniform 64-bit sampling (if the Python script supports --random/--shards/--seed)
# - Optionally runs witness-count grid search (if the Python script supports --grid-m; else loops m values on the 10M range)
#
# Defaults are safe; override via env or flags. macOS/Linux supported.

output="./gists/lopez_geodesic_mr.py.out.txt"
m=4

python ./gists/lopez_geodesic_mr.py --from 1000001     --to 3000001     --m $m  > $output    # ~10^6 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 10000001    --to 12000001    --m $m  >> $output   # ~10^7 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 10000001    --to 12000001    --m $m  >> $output   # ~10^7 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 100000001   --to 102000001   --m $m  >> $output   # ~10^8 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 1000000001  --to 1002000001  --m $m  >> $output   # ~10^9 band (1M odds)

python ./gists/lopez_geodesic_mr.py --from 10000000001         --to 10002000001         --m $m >> $output  # ~10^10 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 100000000001        --to 100002000001        --m $m >> $output  # ~10^11 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 1000000000001       --to 1000002000001       --m $m >> $output  # ~10^12 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 10000000000001      --to 10000002000001      --m $m >> $output  # ~10^13 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 100000000000001     --to 100000002000001     --m $m >> $output  # ~10^14 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 1000000000000001    --to 1000000002000001    --m $m >> $output  # ~10^15 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 10000000000000001   --to 10000000002000001   --m $m >> $output  # ~10^16 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 100000000000000001  --to 100000000002000001  --m $m >> $output  # ~10^17 band (1M odds)
python ./gists/lopez_geodesic_mr.py --from 1000000000000000001 --to 1000000000002000001 --m $m >> $output  # ~10^18 band (1M odds)

