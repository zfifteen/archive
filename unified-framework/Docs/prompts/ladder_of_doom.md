Goal: Demonstrate the Ladder of Doom factorization method. This is a simple, but effective, method for retrieving the 
factors of RSA 4096 bit keys.
Create a factorization pipeline that integrates several aspects of Z5D.


- TODO: Search Windows: Create a mode to guide the predictor to specific key spaces.
- Done: Implementation of parallel and vectorized Z5D predictor functions: src/c/z5d_phase2.c 
- Prototyped (Needs Optimized C Apple AMX implementation): This self-contained Python script demonstrates a factorization 
  shortcut for semiprimes: https://gist.github.com/zfifteen/8e1869cdcecdfd2f3d11e3454bb33166
- TODO: Generate a csv report of found semi-primes and their factors, including statistical information.
