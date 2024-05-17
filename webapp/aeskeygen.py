import secrets

def generate_aes_key():
    # Generate a random 256-bit (32-byte) key
    key = secrets.token_hex(32)
    with open("aes_key.txt", "w") as key_file:
        key_file.write(key)

if __name__ == "__main__":
    generate_aes_key()

