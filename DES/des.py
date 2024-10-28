from util import *
import base64

# Function to apply a permutation table to a given block
def permute(block, table):
    return [block[x-1] for x in table]

# Function to perform a left circular shift
def left_shift(block, n):
    return block[n:] + block[:n]

# Function to generate 16 round keys
# def generate_round_keys(key):
#     key = permute(key, pc1_table)
#     left, right = key[:28], key[28:]
#     round_keys = []
    
#     for shift in shift_schedule:
#         left = left_shift(left, shift)
#         right = left_shift(right, shift)
#         round_keys.append(permute(left + right, pc2_table))
    
#     return round_keys

def generate_round_keys(key):
    
    # Key into binary
    pc1_key_str = ''.join(key[bit - 1] for bit in pc1_table)

    
    # Split the 56-bit key into two 28-bit halves
    c0 = pc1_key_str[:28]
    d0 = pc1_key_str[28:]
    round_keys = []
    for round_num in range(16):
        # Perform left circular shift on C and D
        c0 = c0[shift_schedule[round_num]:] + c0[:shift_schedule[round_num]]
        d0 = d0[shift_schedule[round_num]:] + d0[:shift_schedule[round_num]]
        # Concatenate C and D
        cd_concatenated = c0 + d0

        # Apply the PC2 permutation
        round_key = ''.join(cd_concatenated[bit - 1] for bit in pc2_table)

        # Store the round key
        round_keys.append(round_key)
    return round_keys

# S-box substitution function
def s_box_substitution(block):
    output = []
    for i in range(8):
        row = (block[i*6] << 1) + block[i*6 + 5]
        col = (block[i*6 + 1] << 3) + (block[i*6 + 2] << 2) + (block[i*6 + 3] << 1) + block[i*6 + 4]
        output.extend(format(s_boxes[i][row][col], '04b'))
    return list(map(int, output))


def encryption(user_input, key):
    # Function to split the input into 8-byte blocks
    binary_key = str_to_bin(key)

    def split_into_blocks(input_string):
        return [input_string[i:i + 8] for i in range(0, len(input_string), 8)]
    
    # Function to pad the last block if it's less than 8 bytes
    def pad_block(block):
        # PKCS#5 padding
        padding_length = 8 - len(block)
        return block + chr(padding_length) * padding_length

    # Split user input into blocks
    blocks = split_into_blocks(user_input)

    encrypted_blocks = []

    for block in blocks:
        # Pad the block to 8 bytes
        if len(block) < 8:
            block = pad_block(block)

        binary_rep_of_input = str_to_bin(block)
        # Initialize lists to store round keys
        round_keys = generate_round_keys(binary_key)

        ip_result_str = ip_on_binary_rep(binary_rep_of_input)

        # Divide the initial permutation result into two halves
        lpt = ip_result_str[:32]
        rpt = ip_result_str[32:]

        # Perform 16 rounds of encryption
        for round_num in range(16):
            # Expand and permute RPT
            expanded_result = [rpt[i - 1] for i in e_box_table]
            expanded_result_str = ''.join(expanded_result)

            # XOR with the round key
            round_key_str = round_keys[round_num]
            xor_result_str = ''.join(str(int(expanded_result_str[i]) ^ int(round_key_str[i])) for i in range(48))

            # Split into 6-bit groups and apply S-box substitution
            six_bit_groups = [xor_result_str[i:i + 6] for i in range(0, 48, 6)]
            s_box_substituted = ''

            for i in range(8):
                row_bits = int(six_bit_groups[i][0] + six_bit_groups[i][-1], 2)
                col_bits = int(six_bit_groups[i][1:-1], 2)
                s_box_value = s_boxes[i][row_bits][col_bits]
                s_box_substituted += format(s_box_value, '04b')

            # Apply P permutation
            p_box_result = [s_box_substituted[i - 1] for i in p_box_table]

            # XOR with LPT
            lpt_list = list(lpt)
            new_rpt = ''.join(str(int(lpt_list[i]) ^ int(p_box_result[i])) for i in range(32))

            # Update LPT and RPT for the next round
            lpt, rpt = rpt, new_rpt

        # Final result after all rounds
        final_result = rpt + lpt
        final_cipher = [final_result[ip_inverse_table[i] - 1] for i in range(64)]
        final_cipher_str = ''.join(final_cipher)

        # Convert binary cipher to ASCII
        final_cipher_ascii = binary_to_ascii(final_cipher_str)
        encrypted_blocks.append(final_cipher_ascii)

    # Join all encrypted blocks into a single string
    encrypted_string = ''.join(encrypted_blocks)

    # Encode the final ciphertext in Base64
    base64_encoded = base64.b64encode(encrypted_string.encode('utf-8')).decode('utf-8')

    return base64_encoded


def decryption(final_cipher, key):
    # Convert the Base64 encoded ciphered text to bytes, then to a string
    decoded_bytes = base64.b64decode(final_cipher)
    decoded_cipher = decoded_bytes.decode('utf-8')

    # Convert the decoded cipher text and key to binary
    binary_key = str_to_bin(key)
    binary_cipher = str_to_bin(decoded_cipher)

    # print("binary_cipher", binary_cipher, len(binary_cipher))  # Debugging statement

    # Function to split the input into 8-byte blocks
    def split_into_blocks(input_string):
        return [input_string[i:i + 64] for i in range(0, len(input_string), 64)]

    # Split the final cipher into blocks
    blocks = split_into_blocks(binary_cipher)
    decrypted_blocks = []

    # Initialize lists to store round keys
    round_keys = generate_round_keys(binary_key)

    for block in blocks:
        # Apply Initial Permutation
        ip_dec_result_str = ip_on_binary_rep(block)

        lpt = ip_dec_result_str[:32]
        rpt = ip_dec_result_str[32:]

        # Perform 16 rounds of decryption
        for round_num in range(16):
            # Expand and permute RPT
            expanded_result = [rpt[i - 1] for i in e_box_table]
            expanded_result_str = ''.join(expanded_result)

            # Use the appropriate round key
            round_key_str = round_keys[15 - round_num]

            # XOR with the round key
            xor_result_str = ''.join(str(int(expanded_result_str[i]) ^ int(round_key_str[i])) for i in range(48))

            # Split into 6-bit groups and apply S-box substitution
            six_bit_groups = [xor_result_str[i:i + 6] for i in range(0, 48, 6)]
            s_box_substituted = ''

            for i in range(8):
                row_bits = int(six_bit_groups[i][0] + six_bit_groups[i][-1], 2)
                col_bits = int(six_bit_groups[i][1:-1], 2)
                s_box_value = s_boxes[i][row_bits][col_bits]
                s_box_substituted += format(s_box_value, '04b')

            # Apply P permutation
            p_box_result = [s_box_substituted[i - 1] for i in p_box_table]

            # XOR with LPT
            lpt_list = list(lpt)
            new_rpt = ''.join(str(int(lpt_list[i]) ^ int(p_box_result[i])) for i in range(32))

            # Update LPT and RPT for the next round
            lpt, rpt = rpt, new_rpt

        # Final result after all rounds
        final_result = rpt + lpt
        final_cipher = [final_result[ip_inverse_table[i] - 1] for i in range(64)]
        final_cipher_str = ''.join(final_cipher)

        # Convert binary cipher string to ASCII
        decrypted_blocks.append(binary_to_ascii(final_cipher_str))

    # Join all decrypted blocks into a single string
    decrypted_message = ''.join(decrypted_blocks)

    # Remove padding from the last block if necessary
    return decrypted_message