with open('z5d_scaling_test.py', 'r') as f:
    content = f.read()

# Change trials and timeout
content = content.replace('            trials = 1000  # Increased trials for better accuracy', '            trials = 1000 * (2 ** ((bits - 16) // 16))  # Adaptive trials based on bit size')
content = content.replace('            timeout = 15  # 15 second timeout per test', '            timeout = 15 + 15 * ((bits - 16) // 16)  # Adaptive timeout')

with open('z5d_scaling_test.py', 'w') as f:
    f.write(content)

print("File edited")