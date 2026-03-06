import random
import string
import os

# Function to generate random string of given length with specified character set
def generate_random_string(length, chars=string.ascii_letters + string.digits + string.punctuation):
    return ''.join(random.choice(chars) for _ in range(length))

# Target total inputs
total_inputs = 5000
inputs = []

# 1. Empty input (1)
inputs.append("")

# 2. Single characters (94 from printable ASCII)
for char in string.printable:
    inputs.append(char)

# 3. Short numerical strings (100)
for i in range(100):
    length = random.randint(2, 10)
    inputs.append(''.join(random.choice(string.digits) for _ in range(length)))

# 4. Short alphabetical strings (100)
for i in range(100):
    length = random.randint(2, 10)
    inputs.append(''.join(random.choice(string.ascii_letters) for _ in range(length)))

# 5. Short alphanumeric strings (100)
for i in range(100):
    length = random.randint(2, 10)
    inputs.append(generate_random_string(length, string.ascii_letters + string.digits))

# 6. Short special char mixed strings (100)
for i in range(100):
    length = random.randint(2, 10)
    inputs.append(generate_random_string(length))

# 7. Medium length strings (various types, 500 total)
for i in range(125):
    length = random.randint(11, 30)
    inputs.append(generate_random_string(length, string.digits))  # Numerical
    inputs.append(generate_random_string(length, string.ascii_letters))  # Alphabetical
    inputs.append(generate_random_string(length, string.ascii_letters + string.digits))  # Alphanumeric
    inputs.append(generate_random_string(length))  # Mixed with special chars

# 8. Longer strings (various types, 400 total)
for i in range(100):
    length = random.randint(31, 100)
    inputs.append(generate_random_string(length, string.digits))  # Numerical
    inputs.append(generate_random_string(length, string.ascii_letters))  # Alphabetical
    inputs.append(generate_random_string(length, string.ascii_letters + string.digits))  # Alphanumeric
    inputs.append(generate_random_string(length))  # Mixed with special chars

# 9. Textual excerpts with repetition (50)
texts = [
    "Call me Ishmael.",
    "Some years ago",
    "Never mind how long",
    "I thought I would sail",
    "Watery part of world"
]
for text in texts:
    inputs.append(text)
    inputs.append(text + " " + text)
    inputs.append(text + " " + text + " " + text)
    inputs.append(text * 2)
    inputs.append(text * 3)
    inputs.append(text * 4)
    inputs.append(text * 5)
    inputs.append(text * 6)
    inputs.append(text * 7)
    inputs.append(text * 8)

# Fill remaining slots with random strings to reach 5000
remaining = total_inputs - len(inputs)
for i in range(remaining):
    length = random.randint(1, 100)
    inputs.append(generate_random_string(length))

# Shuffle the inputs to avoid sequential bias
random.shuffle(inputs)

# Save to file
with open('large_input_set.txt', 'w') as f:
    for inp in inputs:
        # Escape commas and newlines to avoid CSV issues later
        escaped = inp.replace(',', ';').replace('\n', ' ')
        f.write(escaped + '\n')

print(f"Generated {len(inputs)} inputs and saved to large_input_set.txt")
