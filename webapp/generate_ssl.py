import subprocess
import os

def generate_ssl_certificate():
    # Define the OpenSSL command
    command = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", "key.pem", "-out", "cert.pem", "-days", "365", "-nodes",
        "-subj", "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"
    ]
    
    try:
        # Run the OpenSSL command
        subprocess.run(command, check=True)
        print("SSL certificate and key have been successfully generated.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while generating the SSL certificate: {e}")

if __name__ == "__main__":
    if os.path.exists("key.pem") or os.path.exists("cert.pem"):
        overwrite = input("key.pem and/or cert.pem already exist. Do you want to overwrite them? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            exit(0)
    
    generate_ssl_certificate()

