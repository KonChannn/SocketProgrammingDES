import hashlib
import base64

# Function to generate RSA key pair (already given)
def generate_key_pair():
    p, q = 61, 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17  # Public exponent
    d = pow(e, -1, phi)  # Private exponent
    return (e, n), (d, n)

# Function to encrypt a message using a public key (already given)


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
    d, n = private_key
    # Hash the data first to ensure the signature is of fixed length
    data_hash = hashlib.sha256(data.encode()).hexdigest()
    # Convert the hash to an integer and sign it with the private key
    signed_data = pow(int(data_hash, 16), d, n)
    return signed_data

# Function to verify a signature using a public key
def verify_signature(data, signature, public_key):
    e, n = public_key
    # Hash the data to match the signature
    data_hash = hashlib.sha256(data.encode()).hexdigest()
    # Verify the signature by comparing it to the decrypted value of the signature
    decrypted_signature = pow(signature, e, n)
    return decrypted_signature == int(data_hash, 16)
