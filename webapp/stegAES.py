import os
import secrets
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import cv2
from tqdm import tqdm

class AESCipher:
    def __init__(self, key):
        if len(key) != 64:
            raise ValueError("Key must be 64 hexadecimal characters (32 bytes).")
        self.key = bytes.fromhex(key)

    def encrypt(self, msg):
        msg = msg.encode('utf-8')
        padded_msg = self._pad(msg)
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(padded_msg)

    def decrypt(self, cipher_text):
        iv = cipher_text[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_msg = cipher.decrypt(cipher_text[16:])
        try:
            return self._unpad(decrypted_msg).decode('utf-8')
        except (UnicodeDecodeError, ValueError):
            raise ValueError("Incorrect decryption key or corrupted data.")

    def encrypt_bytes(self, data):
        padded_data = self._pad(data)
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(padded_data)

    def decrypt_bytes(self, cipher_text):
        iv = cipher_text[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(cipher_text[16:])
        return self._unpad(decrypted_data)

    def _pad(self, data):
        padding_len = 16 - (len(data) % 16)
        return data + bytes([padding_len] * padding_len)

    def _unpad(self, data):
        padding_len = data[-1]
        if padding_len < 1 or padding_len > 16:
            raise ValueError("Incorrect padding.")
        return data[:-padding_len]

class LSB:
    MAX_BIT_LENGTH = 32

    def __init__(self, img):
        self.image = img
        self.cur_x, self.cur_y, self.cur_channel = 0, 0, 0
        self.size_x, self.size_y, self.size_channel = img.shape

    def put_bit(self, bit):
        v = self.image[self.cur_x, self.cur_y][self.cur_channel]
        binaryV = bin(v)[2:].zfill(8)
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
        data_length = len(data).to_bytes(8, 'big')
        if len(data) > self.size_x * self.size_y * self.size_channel:
            raise ValueError("Image too small to embed data.")
        for byte in data_length:
            self.put_bits(bin(byte)[2:].zfill(8))

        for byte in data:
            self.put_bits(bin(byte)[2:].zfill(8))

    def extract(self):
        data_length_bits = self.read_bits(64)
        data_length = int(data_length_bits, 2)

        extracted_data = []
        for _ in range(data_length):
            byte = int(self.read_bits(8), 2)
            extracted_data.append(byte)
        return bytes(extracted_data)

class Activity:
    def __init__(self, image_path, message, zip_file_path, key_path, action, save):
        self.image_path = image_path
        self.message = message
        self.zip_file_path = zip_file_path
        self.key_path = key_path
        self.action = action
        self.save = save

    def execute(self):
        if self.action == "encode":
            return self.encode()
        elif self.action == "decode":
            return self.decode()

    def encode(self):
        cipher = self.cipher()
        cipher_text = cipher.encrypt(self.message)

        encrypted_zip = b''
        if self.zip_file_path:
            with open(self.zip_file_path, 'rb') as f:
                zip_contents = f.read()
            encrypted_zip = cipher.encrypt_bytes(zip_contents)

        combined_data = len(cipher_text).to_bytes(8, 'big') + cipher_text + len(encrypted_zip).to_bytes(8, 'big') + encrypted_zip
        
        image = cv2.imread(self.image_path)
        obj = LSB(image)
        obj.embed(combined_data)
        encoded_image_path = os.path.join(os.path.dirname(self.image_path), "encoded_" + os.path.basename(self.image_path))
        cv2.imwrite(encoded_image_path, obj.image)
        return encoded_image_path

    def decode(self):
        cipher = self.cipher()
        encoded_image = cv2.imread(self.image_path)
        obj = LSB(encoded_image)

        combined_data = obj.extract()
        cipher_text_len = int.from_bytes(combined_data[:8], 'big')
        cipher_text = combined_data[8:8+cipher_text_len]

        encrypted_zip_len = int.from_bytes(combined_data[8+cipher_text_len:16+cipher_text_len], 'big')
        encrypted_zip = combined_data[16+cipher_text_len:16+cipher_text_len+encrypted_zip_len]

        decrypted_message = cipher.decrypt(cipher_text)
        decrypted_zip = cipher.decrypt_bytes(encrypted_zip) if encrypted_zip_len > 0 else None
        return decrypted_message, decrypted_zip

    def cipher(self):
        if self.key_path and os.path.exists(self.key_path):
            with open(self.key_path, "r") as key_file:
                key = key_file.read().strip()
        else:
            raise ValueError("Key file not found.")
        return AESCipher(key)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AES + Steganography Tool")
    parser.add_argument("action", choices=["encode", "decode"], help="Action to perform")
    parser.add_argument("--message", help="Secret message to encode")
    parser.add_argument("--image", help="Path to the image file")
    parser.add_argument("--zip", help="Path to the zip file for encoding")
    parser.add_argument("--key", help="Path to the AES key file")
    parser.add_argument("--save", action="store_true", help="Save the decrypted message to a file")
    args = parser.parse_args()

    app = Activity(args.image, args.message, args.zip, args.key, args.action, args.save)
    try:
        result = app.execute()
        print("Result:", result)
    except Exception as e:
        print("An error occurred:", str(e))


