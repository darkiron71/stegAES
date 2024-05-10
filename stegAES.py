import argparse
import cv2
from Crypto.Cipher import AES
import os
from tqdm import tqdm
import secrets
from Crypto.Random import get_random_bytes

class AESCipher:
    def __init__(self, key):
        if len(key) != 32:
            raise ValueError("Key must be 32 characters.")
        self.key = key
        self.iv = get_random_bytes(16)  # Generate a random IV for CBC mode
        self.cipher = AES.new(self.key.encode(), AES.MODE_CBC, self.iv)

    def encrypt(self, msg):
        msg = msg.encode('utf-8')  # Convert message to bytes
        padded_msg = self._pad(msg)
        return self.iv + self.cipher.encrypt(padded_msg)

    def decrypt(self, cipher_text):
        iv = cipher_text[:16]  # Extract IV from cipher text
        cipher = AES.new(self.key.encode(), AES.MODE_CBC, iv)
        decrypted_msg = cipher.decrypt(cipher_text[16:])
        unpadded_msg = self._unpad(decrypted_msg).decode('utf-8')
        return unpadded_msg

    def _pad(self, msg):
        padding_len = 16 - (len(msg) % 16)
        return msg + bytes([padding_len] * padding_len)

    def _unpad(self, msg):
        return msg[:-msg[-1]]

class LSB:
    MAX_BIT_LENGTH = 32

    def __init__(self, img):
        self.image = img
        self.cur_x, self.cur_y, self.cur_channel = 0, 0, 0
        self.size_x, self.size_y, self.size_channel = img.shape

    def put_bit(self, bit):
        v = self.image[self.cur_x, self.cur_y][self.cur_channel]
        binaryV = bin(v)[2:]
        if binaryV[-1] != bit:
            binaryV = binaryV[:-1] + bit
        self.image[self.cur_x, self.cur_y][self.cur_channel] = int(binaryV, 2)
        self.next()

    def put_bits(self, bits):
        for bit in bits:
            self.put_bit(bit)

    def next(self):
        if self.cur_channel < self.size_channel - 1:
            self.cur_channel += 1
        elif self.cur_y < self.size_y - 1:
            self.cur_channel = 0
            self.cur_y += 1
        elif self.cur_x < self.size_x - 1:
            self.cur_channel = 0
            self.cur_y = 0
            self.cur_x += 1
        else:
            raise Exception("End of image reached")

    def read_bit(self):
        v = self.image[self.cur_x, self.cur_y][self.cur_channel]
        return bin(v)[-1]

    def read_bits(self, length):
        bits = ''
        for _ in range(length):
            bits += self.read_bit()
            self.next()
        return bits

    def embed(self, data):
        data_length = len(data).to_bytes(8, 'big')  # Use 8 bytes for length to support larger files
        if len(data) > self.size_x * self.size_y * self.size_channel:
            raise ValueError("Image too small to embed data.")
        for byte in data_length:
            self.put_bits(bin(byte)[2:].zfill(8))

        for chunk in tqdm(range(0, len(data), self.MAX_BIT_LENGTH), desc="Embedding", ncols=70):
            for b in data[chunk:chunk+self.MAX_BIT_LENGTH]:
                self.put_bits(bin(b)[2:].zfill(8))

    def extract(self):
        data_length_bits = self.read_bits(64)  # Read 64 bits for length to support larger files
        data_length = int(data_length_bits, 2)

        extracted_data = []
        for chunk in tqdm(range(0, data_length, self.MAX_BIT_LENGTH), desc="Extracting", ncols=70):
            for _ in range(min(self.MAX_BIT_LENGTH, data_length - chunk)):
                byte = int(self.read_bits(8), 2)
                extracted_data.append(byte)

        return bytes(extracted_data)

    def save(self, dstPath):
        cv2.imwrite(dstPath, self.image)

class Activity:
    def __init__(self, image_path, message, zip_file_path, key_path, action, save):
        self.image_path = image_path
        self.message = message
        self.zip_file_path = zip_file_path
        self.key_path = key_path
        self.action = action
        self.save = save
        self.key_file = "aes_key.txt"

        if not os.path.exists(self.key_file) and self.key_path:
            self.copy_key_file()  # Copy provided key file to local directory

    def copy_key_file(self):
        os.system(f'cp {self.key_path} {self.key_file}')

    def read_key_from_file(self):
        if self.key_path:
            with open(self.key_path, "r", encoding="utf-8") as key_file:
                return key_file.read().strip()
        elif os.path.exists(self.key_file):
            with open(self.key_file, "r", encoding="utf-8") as key_file:
                return key_file.read().strip()
        else:
            raise ValueError("Key file not found.")

    def generate_key(self):
        key = secrets.token_hex(16)  # Generate a random hex key of 32 characters
        with open(self.key_file, "w", encoding="utf-8") as key_file:
            key_file.write(key)

    def cipher(self):
        key = self.read_key_from_file()  # Read the key from the file
        if len(key) != 32:
            raise ValueError("Key must be 32 characters.")
        return AESCipher(key)

    def encode(self):
        cipher = self.cipher()
        cipher_text = cipher.encrypt(self.message)
        combined_data = len(cipher_text).to_bytes(8, 'big') + cipher_text  # Use 8 bytes for length to support larger files
        if self.zip_file_path:
            with open(self.zip_file_path, 'rb') as f:
                zip_contents = f.read()
            if len(zip_contents) > (os.path.getsize(self.image_path) * 3) // 8:
                raise ValueError("Zip file too large for the host image.")
            combined_data += zip_contents
        image = cv2.imread(self.image_path)
        obj = LSB(image)
        obj.embed(combined_data)
        base_dir, original_filename = os.path.split(self.image_path)
        filename_no_extension, _ = os.path.splitext(original_filename)
        encoded_image_path = os.path.join(base_dir, self.get_unique_filename(filename_no_extension + "_encoded.png"))
        obj.save(encoded_image_path)
        print("Encoded image saved as:", encoded_image_path)

    def decode(self):
        cipher = self.cipher()
        encoded_image = cv2.imread(self.image_path)
        obj = LSB(encoded_image)
        
        combined_data_with_zip = obj.extract()
        cipher_text_len = int.from_bytes(combined_data_with_zip[:8], 'big')  # Use 8 bytes for length to support larger files
        cipher_text = combined_data_with_zip[8:8+cipher_text_len]
        decrypted_message = cipher.decrypt(cipher_text)
        
        print("Decrypted message:", decrypted_message)  # Display the decrypted message to the terminal
        
        # Save the decrypted message to a file only if the --save flag is provided
        if self.save:
            try:
                with open(self.get_unique_filename("decrypted_message.txt"), "w", encoding="utf-8") as f:
                    f.write(decrypted_message)
                print("Decrypted message saved as:", self.get_unique_filename("decrypted_message.txt"))
            except Exception as e:
                print("An error occurred while writing to the file:", str(e))
        else:
            print("No --save flag provided to save the message.")
        
        # Save the zip file to a file
        if self.zip_file_path:
            try:
                with open(self.zip_file_path, 'wb') as f:
                    f.write(combined_data_with_zip[8+cipher_text_len:])
                print("Zip file saved:", self.zip_file_path)
            except Exception as e:
                print("An error occurred while writing to the zip file:", str(e))
        else:
            print("No --zip <filename.zip> flag was provided for saving the zip file.")

    def execute(self):
        if self.action == "encode":
            self.encode()
        elif self.action == "decode":
            self.decode()
    
    def get_unique_filename(self, filename):
        """
        Appends a suffix to the filename if it already exists.
        """
        count = 1
        new_filename = filename
        while os.path.exists(new_filename):
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_{count}{ext}"
            count += 1
        return new_filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AES + Steganography")
    parser.add_argument("action", choices=["encode", "decode"], help="Action to perform: encode or decode")
    parser.add_argument("--zip", dest="zip_file_path", help="Path to the zip file")
    parser.add_argument("--message", help="Secret message for encoding")
    parser.add_argument("--image", help="Path to the image file")
    parser.add_argument("--key", help="Path to the key file")
    parser.add_argument("--save", action="store_true", help="Save the decrypted message to a file")

    args = parser.parse_args()

    app = Activity(args.image, args.message, args.zip_file_path, args.key, args.action, args.save)
    try:
        app.execute()
    except Exception as e:
        print("An error occurred:", str(e))



