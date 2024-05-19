# stegAES.py
# Steganography with AES-256 Encryption -- Supports encrypted messages and zip files

## Requirements

    python3 (run.sh script will auto check and attempt to install if able)  

## Dependencies 

    flask==2.0.3
    Werkzeug==2.0.3
    pycryptodome==3.14.1
    opencv-python-headless==4.9.0.80
    tqdm==4.62.3
    gunicorn==22.0.0
    flask-executor==1.0.0
    pillow==9.1.0

## Install Dependencies 

Auto

    chmod +x run.sh
    ./run.sh

Manual:

    pip install -r requirements.txt 
    
*If you receive errors while running stegAES.py or run.sh you may need to add flask and gunicorn to your PATH
    
*On Linux or macOS, add the export line to your .bashrc, .bash_profile, or .zshrc:

    echo 'export PATH=$PATH:/path/to/executable_folder' >> ~/.bashrc

*You will need to do this for both gunicorn and flask if terminal says it is unable to find it. You can typically find the executable with the 'which' command.

*Ex:

    which gunicorn

* On Windows, you can add it through the System Properties -> Environment Variables, then edit the PATH variable and add the path to the executable folder.


## About

stegAES supports embedding both text-based messages and zip files into an image. (Do keep in mind the amount of data you can embed will depend on host image file size. The larger the host image file, the more data you can store.) 

The stegAES.py script offers a comprehensive solution combining AES encryption with steganography techniques, designed for secure message transmission and concealed data embedding within images. Here's a breakdown of its functionalities:

AES Encryption: The script implements the AES (Advanced Encryption Standard) algorithm for secure message encryption. AESCipher class provides methods for encrypting and decrypting messages using a 64-character key. It ensures data confidentiality by employing symmetric key encryption and CBC (Cipher Block Chaining) mode.
Steganography: LSB (Least Significant Bit) steganography is utilized for hiding encrypted data within image files. LSB class facilitates embedding data into images by replacing the least significant bits of pixel values, ensuring minimal visual distortion.

Encoding: The script allows users to encode a secret message into an image along with an optional zip file. It encrypts the message, combines it with the zip file (if provided), embeds the combined data into the image using LSB steganography, and saves the resulting encoded image.

Decoding: Users can decode the hidden message from an encoded image. The script extracts the encrypted data from the image using LSB steganography, decrypts it using the provided key, and optionally saves the decrypted message to a file. Additionally, it extracts and saves any attached zip file.

Command-line Interface: The script provides a command-line interface using argparse, allowing users to specify the action (encode or decode), image file path, message, key file path, zip file path, and whether to save the decrypted message.

This versatile tool finds applications in secure communication, data hiding, and digital forensics, offering a blend of encryption and steganography techniques to protect sensitive information while maintaining data integrity and confidentiality.


## How-To use stegAES.py

  Make run.sh executable

      chmod +x run.sh 
  
  Auto Run Guide:

    ./run.sh

  Manual:

  Generating an aes_key: First you must genreate your secret aes_key which will be used to encrypt/decrypt the data (KEEP THIS SAFE)

      python3 aeskeygen.py
  Make note of the key name!

  Encoding: 

      python3 stegAES.py --image <image_file.png> --message "Your Secret Message" --zip <zipaname.zip> (optional) --key aes_key.txt encode

  Decoding: 

      python3 stegAES.py --image <image_file_encoded.png> --save (optional if you want to save the message to a file) --zip <outputfilename.zip> (optional if you want to save the zip file) --key aes_key.txt decode 

# Options

    --zip = "Path to the zip file"
    --message = "Secret message for encoding"
    --image = "Path to the image file"
    --key = "Path to the key file"
    --save = "Save the decrypted message to a file"
    endode = "Tells program to execute encoding action"
    decode = "Tells program to execute decoding action"

# Extras 

dummydata.py= will auto generate a dummy zip file specified in MB. In the example below this will create 2MB dummydata zip file 

    python3 dummydata.py <#>
    ex: python3 dummydata.py 2

aeskeygen.py = will auto create AES key needed for encryption/decryption

      python3 aeskeygen.py 


black_marble.png = 24 MB NASA sourced image for example host image file 

    black_marble.png 

# Example

## Encoding:
![Alt Text](https://github.com/darkiron71/stegAES/blob/main/Encoding_example.png)

## Decoding:
![Alt Text](https://github.com/darkiron71/stegAES/blob/main/Decoding_example.png)

## Host Image before Encoding: 
![Alt Text](https://github.com/darkiron71/stegAES/blob/main/black_marble.png)

## Host Image after Encoding:
![Alt Text](https://github.com/darkiron71/stegAES/blob/main/black_marble_encoded_1.png)

## Decoded Files: 

![Alt Text](https://github.com/darkiron71/stegAES/blob/main/Decoded_zip.png)


![Alt Text](https://github.com/darkiron71/stegAES/blob/main/Secret_message_file.png)


![Alt Text](https://github.com/darkiron71/stegAES/blob/main/Secret_Message_decoded_file.png)

![Alt Text](https://github.com/darkiron71/stegAES/blob/main/Files_inside_zip.png)


# WebApp Version

![Alt Text](https://github.com/darkiron71/stegAES/blob/main/WebGUI.png)

Included in the main directory is a webapp directory which has the necessary requirements to run a self hosted https server. This provides an interactive GUI interface.     

## Configuration and Setup: 

The application initializes with Flask through the use of gunicorn, configuring an upload folder and setting a file size limit to 100 MB. It ensures that the necessary directories exist and starts a background thread to periodically purge old files from the upload directory.

## Getting started

Change into the webapp directory. Begin the interactive startup script labled: start.py. The start up script will check to see if there is already an SSL certificate in the root directory. If no certificate exist, it will auto create the SSL certs and place it in the directory. This allows for an encrypted https connection. 

Auto:
From the main directory execute the run.sh script and select #2 for webapp
    
    ./run.sh

Manual: 
Change to the webapp directory.

     cd webapp
     python3 start.py

You can adjust the gunicorn server parameters in the start.py file. 

Follow prompts to pick your appropriate version. Version#1 will auto purge aes_key.txt files and encoded images in the uploads folder every 2 minutes and after every decoding process. Version#2 will keep the latest aes_key.txt file and all encoded images in the uploads folder. You will need to delete these manually. 

![Alt Text](https://github.com/darkiron71/stegAES/blob/main/start_py_ssl_key_gen_startup.png)


## Image Encoding and Decoding:

Encoding: Users can upload an image, a message, and optionally, a ZIP file and a cryptographic key. The application supports the conversion of JPEG images to PNG to ensure compatibility with the encoding process. It utilizes an Activity class from the stegAES.py module to embed the message (and the ZIP file, if provided) into the image using the provided key.

Decoding: Users upload an encoded image and the corresponding key. The application decodes the image to extract the hidden message and any embedded files, repackaging them into a downloadable ZIP file.

## Key Generation:

It offers a functionality to generate a secure 256-bit AES key, which users can download for their encoding or decoding activities.

Encoding:

![Alt Text](https://github.com/darkiron71/stegAES/blob/main/encoding_GUI.png)

Decoding:

![Alt Text](https://github.com/darkiron71/stegAES/blob/main/decoding_GUI.png)

## File Handling and Cleanup:

The application includes several routes for file handling, including mechanisms to download the encoded or decoded files.
Cleanup processes are built in to ensure the security and efficiency of the system by deleting temporary files after operations or on a scheduled basis. (As long as you use #1 in the start.py script. #2 will keep the most recent aes_key.txt file and encoded images in the uploads folder. You will need to manually delete these if option #2 is selected.) 

## Security and Performance Enhancements:

Utilizes Flask's secure file handling capabilities to mitigate risks associated with file uploads.
Implements background threads and Flask Executor for asynchronous tasks, enhancing the application’s performance and responsiveness.


## Self Hosted Application 

To serve this application to other users outside of 127.0.0.1:8000 you must allow port 8000/tcp through your host firewall.

Linux:

ufw
   
    sudo ufw allow 8000/tcp
    sudo ufw enable
    sudo ufw reload
or

iptables

    sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
    sudo service iptables save


Windows: 

    You can set to alllow new inbound rule in windows defender firewall. Add inbound TCP port 8000 and allow the connection. 

Mac:

    Configure firewall options in systems preference window, click on "Security & Privacy" Allow Incoming Connections on macOS
    Step 1: Open System Preferences
        Click on the Apple logo in the top left corner of your screen.
        Select "System Preferences" from the dropdown menu.
    Step 2: Open Security & Privacy
        In the System Preferences window, click on "Security & Privacy."
    Step 3: Go to the Firewall Tab
        Click on the "Firewall" tab.
    Step 4: Unlock the Settings
       Click on the lock icon in the bottom left corner of the window.
        Enter your admin username and password when prompted.
    Step 5: Configure Firewall Options
        Click on the "Firewall Options" button.
    Step 6: Add an Application
        Click on the "+" button to add an application.
        Navigate to your terminal application (typically found in /Applications/Utilities/Terminal.app).
        Click "Add."
    Step 7: Allow Incoming Connections
        Ensure that the newly added application (Terminal) is set to "Allow incoming connections."
        Click "OK" to close the Firewall Options window.
        Click the lock icon again to prevent further changes.
    Verify Firewall Settings
    In the "Firewall" tab, ensure that the firewall is turned on and that Terminal is listed as allowed to accept incoming connections.

