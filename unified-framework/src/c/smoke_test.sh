echo "Hardware Configuration:" > smoke_test_output.txt
echo "======================" >> smoke_test_output.txt
echo "CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || uname -p)" >> smoke_test_output.txt
echo "Cores: $(sysctl -n hw.ncpu 2>/dev/null || nproc)" >> smoke_test_output.txt
echo "Memory: $(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1024 / 1024 / 1024 ))GB" >> smoke_test_output.txt
echo "Architecture: $(uname -m)" >> smoke_test_output.txt
echo "OS: $(uname -s) $(uname -r)" >> smoke_test_output.txt
echo "" >> smoke_test_output.txt
./bin/test_amx_functionality >> smoke_test_output.txt
echo "\r" >> smoke_test_output.txt
./bin/z5d_prime_gen >> smoke_test_output.txt
echo "\r" >> smoke_test_output.txt
./bin/demo_phase2 >> smoke_test_output.txt
echo "\r" >> smoke_test_output.txt
./bin/bench_z5d_phase2 --benchmark --samples 900 >> smoke_test_output.txt
echo "\r" >> smoke_test_output.txt
./bin/prime_generator --start 10^1 --count 1 >> smoke_test_output.txt
./bin/prime_generator --start 10^5 --count 1 >> smoke_test_output.txt
./bin/prime_generator --start 10^50 --count 1 >> smoke_test_output.txt
./bin/prime_generator --start 10^500 --count 1 >> smoke_test_output.txt
./bin/prime_generator --start 10^1000 --count 1 >> smoke_test_output.txt
./bin/prime_generator --start 10^1233 --count 1 >> smoke_test_output.txt
echo "\r" >> smoke_test_output.txt
