import random
import math

def is_prime(n):
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def generate_prime(min_value, max_value):
    """Generate a prime number within a given range."""
    prime = random.randint(min_value, max_value)
    while not is_prime(prime):
        prime = random.randint(min_value, max_value)
    return prime

def mod_inverse(e, phi):
    """Compute the modular inverse of e modulo phi."""
    for d in range(2, phi):
        if (d * e) % phi == 1:
            return d
    raise ValueError("Inverse does not exist")

def generate_keys(p, q):
    """Generate RSA public and private keys."""
    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose e such that 1 < e < phi and gcd(e, phi) = 1
    e = random.randint(2, phi)
    while math.gcd(e, phi) != 1:
        e = random.randint(2, phi)

    # Compute d, the modular inverse of e
    d = mod_inverse(e, phi)

    # Public key (e, n) and private key (d, n)
    return ((e, n), (d, n))

def encrypt(public_key, plaintext):
    """Encrypt a plaintext message using the public key."""
    e, n = public_key
    # Convert plaintext to integers and encrypt
    ciphertext = [(ord(ch) ** e) % n for ch in plaintext]
    return ciphertext

def decrypt(private_key, ciphertext):
    """Decrypt a ciphertext message using the private key."""
    d, n = private_key
    # Decrypt ciphertext and convert back to characters
    plaintext = ''.join([chr((ch ** d) % n) for ch in ciphertext])
    return plaintext

def sign(private_key, message):
    """Sign a message using the private key."""
    return encrypt(private_key, message)

def verify(public_key, message, signature):
    """Verify a signed message using the public key."""
    decrypted_signature = decrypt(public_key, signature)
    return decrypted_signature == message

# Example usage
p = generate_prime(1000, 5000)
q = generate_prime(1000, 5000)
while p == q:
    q = generate_prime(1000, 5000)

public_key, private_key = generate_keys(p, q)
message = "Hello world"

# Encrypt and decrypt a message
encrypted_message = encrypt(public_key, message)
print("Encrypted message:", encrypted_message)

decrypted_message = decrypt(private_key, encrypted_message)
print("Decrypted message:", decrypted_message)

# Sign and verify a message
signature_message = sign(private_key, message)
print("Signature of the message:", signature_message)

is_verified = verify(public_key, message, signature_message)
print("Message verification:", "Verified" if is_verified else "Not verified")
