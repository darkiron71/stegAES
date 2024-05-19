import os
import subprocess
import sys

def main():
    # Step 0: Choose between CLI tool and webapp
    print("Please choose the application mode:")
    print("1: CLI tool")
    print("2: Webapp")
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "2":
        if input("Are you sure you want to start the webapp? (yes/no) ").lower() == "yes":
            print("Starting the webapp...")
            os.chdir("webapp")
            subprocess.run(['python3', 'start.py'], check=True)
            return
        else:
            print("Returning to the main menu...")
    
    elif choice != "1":
        print("Invalid choice. Exiting.")
        return

    # Step 1: Handle the AES key
    key_path = input("Enter the path to your AES key or press ENTER to generate one: ")
    if not key_path:
        # Generate a new key using aeskeygen.py
        key_path = "aes_key.txt"  # Default key file name
        if not os.path.exists(key_path):
            print("Generating a new AES key...")
            subprocess.run(['python', 'aeskeygen.py'], check=True)
        else:
            print(f"Key already exists at {key_path}")

    # Step 2: Choose to encode or decode
    action = ""
    while action not in ["encode", "decode"]:
        action = input("Do you want to 'encode' or 'decode'? ").lower()

    # Step 3: Specify the image file path
    image_path = input("Enter the path to the image file: ")

    # Conditional inputs based on action
    message = ""
    zip_file_path = ""
    if action == "encode":
        # Encoding specific inputs
        message = input("Enter the message you want to encode: ")
        if input("Do you want to embed a zip file? (yes/no) ").lower() == "yes":
            zip_file_path = input("Specify the path to the zip file: ")

    # For decoding, check if the user wants to save outputs
    save = False
    if action == "decode":
        save = input("Do you want to save the message to a file? (yes/no) ").lower() == "yes"
        if input("Is there a zip file to save? (yes/no) ").lower() == "yes":
            zip_file_path = input("Specify the path to save the extracted zip file: ")

    # Run the main script with the necessary arguments
    command = [
        'python', 'stegAES.py', action,
        '--image', image_path,
        '--key', key_path
    ]

    if message:
        command.extend(['--message', message])
    if zip_file_path:
        command.extend(['--zip', zip_file_path])
    if save:
        command.append('--save')

    print("Executing the command:", ' '.join(command))
    subprocess.run(command, check=True)

if __name__ == "__main__":
    main()
