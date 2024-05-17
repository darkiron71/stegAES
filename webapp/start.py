import subprocess
import os

def generate_ssl_certificate():
    command = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", "key.pem", "-out", "cert.pem", "-days", "365", "-nodes",
        "-subj", "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=example.com"
    ]
    try:
        subprocess.run(command, check=True)
        print("SSL certificate and key have been successfully generated.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while generating the SSL certificate: {e}")

def start_gunicorn(command):
    subprocess.run(command)

def get_user_choice():
    while True:
        print("Choose an option:")
        print("1. Purge the encoded files and aes_key files after creation")
        print("2. Save the most recent aes_key to the server and keep all encoded files in the upload folder")
        choice = input("Enter 1 or 2: ").strip()
        
        if choice in ["1", "2"]:
            return choice
        else:
            print("Invalid choice. Please enter 1 or 2.")

def confirm_choice(choice):
    confirmation = input(f"You chose option {choice}. Are you sure? (y/n): ").strip().lower()
    return confirmation == 'y'

if __name__ == "__main__":
    if not os.path.exists("key.pem") or not os.path.exists("cert.pem"):
        generate_ssl_certificate()

    choice = get_user_choice()
    
    if confirm_choice(choice):
        if choice == "1":
            command = [
                "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", 
                "--certfile=cert.pem", "--keyfile=key.pem", "--timeout", "300", "wsgi_app_purge:app"
            ]
        else:
            command = [
                "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", 
                "--certfile=cert.pem", "--keyfile=key.pem", "--timeout", "300",  "wsgi_app:app"
            ]
        
        start_gunicorn(command)
    else:
        print("Operation cancelled.")

