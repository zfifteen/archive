#!/usr/bin/env bash

log='arctan_geodesic_story.out.txt'

echo "# Stability across seeds (should keep the same ballpark CI):" > $log
python ./arctan_geodesic_story.py --N 200000 --bins 24 --quantile --bootstrap 200 --seed 7 >> $log
python ./arctan_geodesic_story.py --N 200000 --bins 24 --quantile --bootstrap 200 --seed 1337 >> $log

echo "# Sensitivity to bin count (uplift shouldn’t hinge on binning resolution):" >> $log
python ./arctan_geodesic_story.py --N 200000 --bins 16 --quantile --bootstrap 200 --seed 42 >> $log
python ./arctan_geodesic_story.py --N 200000 --bins 32 --quantile --bootstrap 200 --seed 42 >> $log

echo "# Scale up N (CI should tighten; effect should nudge upward toward the large-N regime):" >> $log
python ./arctan_geodesic_story.py --N 500000 --bins 24 --quantile --bootstrap 200 --seed 42 >> $log

