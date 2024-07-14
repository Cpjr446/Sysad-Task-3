import os
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import argparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

def read_image(img_path):
    """Reads an image and returns the pixel data and metadata."""
    with Image.open(img_path) as img:
        exif_data = {}
        for tag_id in img.getexif():
            tag = TAGS.get(tag_id, tag_id)
            data = img.getexif()[tag_id]
            exif_data[tag] = data
        return np.array(img), exif_data

def write_image(img_path, img_data, metadata):
    """Writes an image with updated metadata."""
    img = Image.fromarray(img_data)
    img.save(img_path, exif=metadata.get("exif"))

def encrypt_data(data, key):
    """Encrypts the data using AES."""
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data)

def decrypt_data(encrypted_data, key):
    """Decrypts the data using AES."""
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_data[16:]) + decryptor.finalize()

def encode_data(image, encrypted_data):
    """Encodes the encrypted data into the least significant bits of the image."""
    data = np.frombuffer(encrypted_data, dtype=np.uint8)
    binary_data = np.unpackbits(data)
    image_flat = image.flatten()
    image_flat[:len(binary_data)] = (image_flat[:len(binary_data)] & 0xFE) | binary_data
    return image_flat.reshape(image.shape)

def decode_data(image):
    """Decodes the encrypted data from the least significant bits of the image."""
    binary_data = image.flatten() & 1
    data = np.packbits(binary_data)
    return bytes(data)

def encode_file(image_path, file_path, output_path, passphrase):
    """Encodes a file into an image using the provided passphrase."""
    image, metadata = read_image(image_path)
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    key = passphrase.encode().zfill(32)[:32]  # Ensure key is 32 bytes
    encrypted_data = encrypt_data(file_data, key)
    
    encoded_image = encode_data(image, encrypted_data)
    
    # Store the passphrase hint in metadata
    new_metadata = {"exif": metadata.get("exif")}
    new_metadata['UserComment'] = "Passphrase hint: steghide"
    
    write_image(output_path, encoded_image, new_metadata)
    print(f"File encoded and saved as {output_path}")

def decode_file(image_path, output_path, passphrase):
    """Decodes a file from an image using the provided passphrase."""
    image, metadata = read_image(image_path)
    
    encoded_data = decode_data(image)
    
    key = passphrase.encode().zfill(32)[:32]  # Ensure key is 32 bytes
    try:
        decrypted_data = decrypt_data(encoded_data, key)
    except:
        print("Decryption failed. Incorrect passphrase?")
        return
    
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    
    print(f"File decoded and saved as {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Steganography tool for hiding files in images.")
    parser.add_argument("-e", "--encode", action="store_true", help="Encode a file into an image")
    parser.add_argument("-d", "--decode", action="store_true", help="Decode a file from an image")
    parser.add_argument("-i", "--image", required=True, help="Path to the image file")
    parser.add_argument("-f", "--file", help="Path to the file to encode or decode")
    parser.add_argument("-o", "--output", required=True, help="Path for the output file")
    parser.add_argument("-p", "--passphrase", required=True, help="Passphrase for encoding/decoding")

    args = parser.parse_args()

    if args.encode:
        encode_file(args.image, args.file, args.output, args.passphrase)
    elif args.decode:
        decode_file(args.image, args.output, args.passphrase)
    else:
        print("Please specify either --encode or --decode")

if __name__ == "__main__":
    main()
