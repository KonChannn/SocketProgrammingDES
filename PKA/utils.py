import hashlib
import base64

# Function to generate RSA key pair (already given)
def generate_key_pair():
    p = 61
    q = 53
    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Select public exponent 'e'
    e = 17  # Typically a small prime
    d = mod_inverse(e, phi_n)  # Compute private exponent 'd'

    return (e, n), (d, n)

def mod_inverse(a, m):
    # Extended Euclidean Algorithm to find the modular inverse of a mod m
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

# Function to encrypt a message using a public key (RSA)
def encrypt_message(message, public_key):
    e, n = public_key
    # Encrypt each character of the message
    encrypted_message = [pow(ord(char), e, n) for char in message]
    # Encode the encrypted message as a Base64 string
    return base64.b64encode(bytes(str(encrypted_message), 'utf-8')).decode('utf-8')

# Function to decrypt a message using a private key (RSA)
def decrypt_message(encrypted_message, private_key):
    d, n = private_key
    # Decode the Base64 string to get the encrypted message back
    encrypted_message = base64.b64decode(encrypted_message).decode('utf-8')
    encrypted_message = eval(encrypted_message)  # Convert the string back to a list of numbers
    # Decrypt each encrypted integer using the private key
    return ''.join([chr(pow(char, d, n)) for char in encrypted_message])

# Function to sign data with a private key
def sign_data(data, private_key):
    """
    Sign a message using the RSA private key.
    Args:
        data (str): The message to be signed.
        private_key (tuple): Private key (d, n).
    Returns:
        int: The RSA signature as an integer.
    """
    try:
        d, n = private_key
        data_hash = int(hashlib.sha256(data.encode('utf-8')).hexdigest(), 16)
        
        # Ensure the hash is in the range of the modulus size (n)
        padded_hash = data_hash % n  # Padding the hash to fit within the modulus size
        
        signed_data = pow(padded_hash, d, n)  # RSA signature using private key
        return signed_data
    except Exception as e:
        print(f"Error signing data: {e}")
        return None

# Function to verify a signature using a public key
def verify_signature(data, signature, public_key):
    """
    Verify the RSA signature of a message.
    Args:
        data (str): The original message.
        signature (int): The signature to be verified.
        public_key (tuple): Public key (e, n).
    Returns:
        bool: True if signature is valid, False otherwise.
    """
    try:
        e, n = public_key
        data_hash = int(hashlib.sha256(data.encode('utf-8')).hexdigest(), 16)
        
        # Ensure the signature and hash are in the range of the modulus size (n)
        padded_signature = signature % n
        padded_hash = data_hash % n

        decrypted_signature = pow(padded_signature, e, n)
        return decrypted_signature == padded_hash  # Check if signature matches the hash
    except Exception as e:
        print(f"Error verifying signature: {e}")
        return False

# Example usage:
if __name__ == '__main__':
    # Generate RSA keys
    public_key, private_key = generate_key_pair()

    # Example message
    data = "some_data_to_encrypt"

    # Sign the message with the private key
    signature = sign_data(data, private_key)
    print(f"Signature: {signature}")

    # Verify the signature with the public key
    is_valid = verify_signature(data, signature, public_key)
    print(f"Signature valid: {is_valid}")

    # Encrypt the message with the public key
    encrypted_message = encrypt_message(data, public_key)
    print(f"Encrypted message: {encrypted_message}")

    # Decrypt the message with the private key
    decrypted_message = decrypt_message(encrypted_message, private_key)
    print(f"Decrypted message: {decrypted_message}")
