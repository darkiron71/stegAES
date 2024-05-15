import os
import secrets

def generate_aes_key(key_size=32):  # Set default key size to 32 bytes (256 bits)
    # Generate a random key of the specified length (in bytes)
    key = secrets.token_hex(key_size)
    return key

def generate_file_name(base_name):
    # Generate a file name with an ascending number appended to the end (e.g., aes_key_1.txt)
    if os.path.exists(base_name):
        count = 1
        while True:
            name, ext = os.path.splitext(base_name)
            new_file_name = f'{name}_{count}{ext}'
            if not os.path.exists(new_file_name):
                return new_file_name
            count += 1
    else:
        return base_name

def write_aes_key_to_file(aes_key, file_name='aes_key.txt'):
    file_name = generate_file_name(file_name)
    with open(file_name, 'w') as f:
        f.write(aes_key)
    print(f"Key file generated: {file_name}")
    print(f"AES Key: {aes_key}")

# Generate AES key (size: 32 bytes) and write it to file
aes_key = generate_aes_key(32)  # Generate a 32-byte AES key (256 bits)
write_aes_key_to_file(aes_key)
