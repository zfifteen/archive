with open('z5d_scaling_test.py', 'r') as f:
    content = f.read()

content = content.replace('trials = 20  # Reduced trials for scaling test', 'trials = 1000  # Increased trials for better accuracy')

with open('z5d_scaling_test.py', 'w') as f:
    f.write(content)

print("File edited")