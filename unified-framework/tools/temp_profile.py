import sys; sys.path.append('.')
import poc_z5d_20bit_integration as poc
import random
random.seed(42)
semiprimes = poc.generate_semiprimes(10)  # small number
poc.poc_test_z5d(semiprimes, eps=1.0)