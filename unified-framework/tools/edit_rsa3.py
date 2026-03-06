with open('src/applications/primes/core/rsa_probe_validation.py', 'r') as f:
    content = f.read()

content = content.replace('    # Scale-adaptive search parameters\n    if n_digits >= 150:  # RSA-155+ scale\n        base_window = 1000\n        refinement_iterations = 3\n    elif n_digits >= 100:  # RSA-100+ scale  \n        base_window = 800\n        refinement_iterations = 2\n    elif n_digits >= 50:  # Large scale\n        base_window = 600\n        refinement_iterations = 2\n    elif n_digits >= 20:  # Medium scale\n        base_window = 400\n        refinement_iterations = 2\n    else:\n        base_window = 200\n        refinement_iterations = 1', '    # Scale-adaptive search parameters\n    if n_digits >= 150:  # RSA-155+ scale\n        base_window = 20000\n        refinement_iterations = 3\n    elif n_digits >= 100:  # RSA-100+ scale  \n        base_window = 15000\n        refinement_iterations = 2\n    elif n_digits >= 50:  # Large scale\n        base_window = 10000\n        refinement_iterations = 2\n    elif n_digits >= 20:  # Medium scale\n        base_window = 5000\n        refinement_iterations = 2\n    else:\n        base_window = 1000\n        refinement_iterations = 1')

with open('src/applications/primes/core/rsa_probe_validation.py', 'w') as f:
    f.write(content)

print("File edited")