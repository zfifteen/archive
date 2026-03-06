with open('src/applications/primes/core/rsa_probe_validation.py', 'r') as f:
    content = f.read()

content = content.replace('    # Scale-adaptive search parameters\n    if n_digits >= 150:  # RSA-155+ scale\n        base_window = 100\n        refinement_iterations = 3\n    elif n_digits >= 100:  # RSA-100+ scale  \n        base_window = 75\n        refinement_iterations = 2\n    else:\n        base_window = 50\n        refinement_iterations = 1', '    # Scale-adaptive search parameters\n    if n_digits >= 150:  # RSA-155+ scale\n        base_window = 500\n        refinement_iterations = 3\n    elif n_digits >= 100:  # RSA-100+ scale  \n        base_window = 300\n        refinement_iterations = 2\n    elif n_digits >= 50:  # Large scale\n        base_window = 200\n        refinement_iterations = 2\n    else:\n        base_window = 100\n        refinement_iterations = 1')

with open('src/applications/primes/core/rsa_probe_validation.py', 'w') as f:
    f.write(content)

print("File edited")