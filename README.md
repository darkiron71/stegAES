# stegAES.py
# Steganography with AES-128 Encryption -- Supports encrypted messages and zip files

## Requirements

    python3 
    pip3 

## Dependencies 

    opencv-python
    pycryptodome
    tqdm

## Install Dependencies 

    pip install -r requirements.txt

## About

stegAES supports embedding both text-based messages and zip files into an image. (Do keep in mind the amount of data you can embed will depend on host image file size. The larger the host image file, the more data you can store.) 

The stegAES.py script offers a comprehensive solution combining AES encryption with steganography techniques, designed for secure message transmission and concealed data embedding within images. Here's a breakdown of its functionalities:

AES Encryption: The script implements the AES (Advanced Encryption Standard) algorithm for secure message encryption. AESCipher class provides methods for encrypting and decrypting messages using a 32-character key. It ensures data confidentiality by employing symmetric key encryption and CBC (Cipher Block Chaining) mode.
Steganography: LSB (Least Significant Bit) steganography is utilized for hiding encrypted data within image files. LSB class facilitates embedding data into images by replacing the least significant bits of pixel values, ensuring minimal visual distortion.

Encoding: The script allows users to encode a secret message into an image along with an optional zip file. It encrypts the message, combines it with the zip file (if provided), embeds the combined data into the image using LSB steganography, and saves the resulting encoded image.

Decoding: Users can decode the hidden message from an encoded image. The script extracts the encrypted data from the image using LSB steganography, decrypts it using the provided key, and optionally saves the decrypted message to a file. Additionally, it extracts and saves any attached zip file.

Command-line Interface: The script provides a command-line interface using argparse, allowing users to specify the action (encode or decode), image file path, message, key file path, zip file path, and whether to save the decrypted message.

This versatile tool finds applications in secure communication, data hiding, and digital forensics, offering a blend of encryption and steganography techniques to protect sensitive information while maintaining data integrity and confidentiality.


## How-To use stegAES.py

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
