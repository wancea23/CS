import sys

PC1_TABLE = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

PC2_TABLE = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

IP_TABLE = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

E_TABLE = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

S_BOXES = [
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
    ],
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
    ],
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
    ],
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    ],
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    ],
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    ],
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    ]
]

P_TABLE = [
    16, 7, 20, 21,
    29, 12, 28, 17,
    1, 15, 23, 26,
    5, 18, 31, 10,
    2, 8, 24, 14,
    32, 27, 3, 9,
    19, 13, 30, 6,
    22, 11, 4, 25
]

IP_INV_TABLE = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]


def hex_to_bits(hex_str, bit_len=64):
    val = int(hex_str, 16)
    return [(val >> (bit_len - 1 - i)) & 1 for i in range(bit_len)]


def bits_to_hex(bits):
    val = 0
    for b in bits:
        val = (val << 1) | b
    hex_len = len(bits) // 4
    return f"{val:0{hex_len}X}"


def bits_to_str(bits, group=4):
    s = "".join(str(b) for b in bits)
    if group:
        return " ".join(s[i:i + group] for i in range(0, len(s), group))
    return s


def permute(bits, table):
    return [bits[idx - 1] for idx in table]


def left_rotate(bits, n):
    return bits[n:] + bits[:n]


def xor_bits(a, b):
    return [x ^ y for x, y in zip(a, b)]


def generate_subkeys(key_64_bits, verbose=False):
    k_plus = permute(key_64_bits, PC1_TABLE)
    c = k_plus[:28]
    d = k_plus[28:]

    if verbose:
        print(f"K+ (56 bits): {bits_to_str(k_plus, 7)}")
        print(f"C0 (28 bits): {bits_to_str(c, 7)}")
        print(f"D0 (28 bits): {bits_to_str(d, 7)}\n")

    subkeys = []
    for round_idx in range(16):
        shift = SHIFT_SCHEDULE[round_idx]
        c = left_rotate(c, shift)
        d = left_rotate(d, shift)
        cd_concat = c + d
        sub_k = permute(cd_concat, PC2_TABLE)
        subkeys.append(sub_k)

        if verbose:
            print(f"Round {round_idx + 1:2d} (shift {shift}):")
            print(f"  C{round_idx + 1:02d} = {bits_to_str(c, 7)}")
            print(f"  D{round_idx + 1:02d} = {bits_to_str(d, 7)}")
            print(f"  K{round_idx + 1:02d} = {bits_to_str(sub_k, 6)}")

    return subkeys


def feistel_f(r_32_bits, k_48_bits, verbose=False):
    e_r = permute(r_32_bits, E_TABLE)
    xor_res = xor_bits(e_r, k_48_bits)
    sbox_out = []
    for i in range(8):
        block_6 = xor_res[i * 6:(i + 1) * 6]
        row = (block_6[0] << 1) | block_6[5]
        col = (block_6[1] << 3) | (block_6[2] << 2) | (block_6[3] << 1) | block_6[4]
        val = S_BOXES[i][row][col]
        bits_4 = [(val >> (3 - b)) & 1 for b in range(4)]
        sbox_out.extend(bits_4)

    p_out = permute(sbox_out, P_TABLE)

    if verbose:
        print(f"    E(R)     : {bits_to_str(e_r, 6)}")
        print(f"    E(R) ^ K : {bits_to_str(xor_res, 6)}")
        print(f"    S-Boxes  : {bits_to_str(sbox_out, 4)}")
        print(f"    P(S)     : {bits_to_str(p_out, 4)}")

    return p_out


def des_process_block(block_64_bits, subkeys, is_decrypt=False, verbose=False):
    ip_bits = permute(block_64_bits, IP_TABLE)
    left = ip_bits[:32]
    right = ip_bits[32:]

    round_keys = list(reversed(subkeys)) if is_decrypt else subkeys
    mode_str = "Decryption" if is_decrypt else "Encryption"

    if verbose:
        print(f"--- DES {mode_str} Block Trace ---")
        print(f"IP: {bits_to_str(ip_bits, 4)}")
        print(f"L0: {bits_to_str(left, 4)}")
        print(f"R0: {bits_to_str(right, 4)}\n")

    for round_idx in range(16):
        k = round_keys[round_idx]
        f_res = feistel_f(right, k, verbose=(verbose and round_idx == 0))
        new_right = xor_bits(left, f_res)
        new_left = right
        left, right = new_left, new_right

        if verbose:
            print(f"Round {round_idx + 1:2d}: L = {bits_to_str(left, 8)} | R = {bits_to_str(right, 8)}")

    pre_output = right + left

    if verbose:
        print(f"\nFinal Swap (R16 L16): {bits_to_str(pre_output, 4)}")

    ciphertext_bits = permute(pre_output, IP_INV_TABLE)

    if verbose:
        print(f"IP^-1 Result        : {bits_to_str(ciphertext_bits, 4)}")
        print(f"Hex output          : {bits_to_hex(ciphertext_bits)}\n")

    return ciphertext_bits


def des_encrypt_block(block_64_bits, subkeys, verbose=False):
    return des_process_block(block_64_bits, subkeys, is_decrypt=False, verbose=verbose)


def des_decrypt_block(block_64_bits, subkeys, verbose=False):
    return des_process_block(block_64_bits, subkeys, is_decrypt=True, verbose=verbose)


def pad_pkcs7(data_bytes):
    pad_len = 8 - (len(data_bytes) % 8)
    return data_bytes + bytes([pad_len] * pad_len)


def unpad_pkcs7(data_bytes):
    if not data_bytes or len(data_bytes) % 8 != 0:
        raise ValueError("Invalid padded block length")
    pad_len = data_bytes[-1]
    if pad_len < 1 or pad_len > 8:
        raise ValueError("Invalid PKCS#7 padding byte")
    if data_bytes[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Corrupt PKCS#7 padding")
    return data_bytes[:-pad_len]


def bytes_to_bits(byte_data):
    bits = []
    for b in byte_data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits


def bits_to_bytes(bit_list):
    byte_arr = bytearray()
    for i in range(0, len(bit_list), 8):
        byte_val = 0
        for b in bit_list[i:i + 8]:
            byte_val = (byte_val << 1) | b
        byte_arr.append(byte_val)
    return bytes(byte_arr)


def des_encrypt_text(plaintext_str, key_hex):
    key_bits = hex_to_bits(key_hex, 64)
    subkeys = generate_subkeys(key_bits)

    plain_bytes = plaintext_str.encode("utf-8")
    padded = pad_pkcs7(plain_bytes)

    cipher_hex_blocks = []
    for i in range(0, len(padded), 8):
        block_bytes = padded[i:i + 8]
        block_bits = bytes_to_bits(block_bytes)
        enc_bits = des_encrypt_block(block_bits, subkeys)
        cipher_hex_blocks.append(bits_to_hex(enc_bits))

    return "".join(cipher_hex_blocks)


def des_decrypt_text(cipher_hex, key_hex):
    if len(cipher_hex) % 16 != 0:
        raise ValueError(f"Ciphertext hex length must be a multiple of 16 (got {len(cipher_hex)})")

    key_bits = hex_to_bits(key_hex, 64)
    subkeys = generate_subkeys(key_bits)

    decrypted_bytes = bytearray()
    for i in range(0, len(cipher_hex), 16):
        block_hex = cipher_hex[i:i + 16]
        block_bits = hex_to_bits(block_hex, 64)
        dec_bits = des_decrypt_block(block_bits, subkeys)
        decrypted_bytes.extend(bits_to_bytes(dec_bits))

    plain_bytes = unpad_pkcs7(bytes(decrypted_bytes))
    return plain_bytes.decode("utf-8")


def verify_grabbe_example():
    print("=" * 78)
    print("RUNNING OFFICIAL J. ORLIN GRABBE DES REFERENCE VERIFICATION")
    print("=" * 78)

    m_hex = "0123456789ABCDEF"
    k_hex = "133457799BBCDFF1"
    expected_c_hex = "85E813540F0AB405"

    m_bits = hex_to_bits(m_hex, 64)
    k_bits = hex_to_bits(k_hex, 64)

    print(f"Plaintext M : {m_hex}")
    print(f"Key K       : {k_hex}")
    print(f"Expected C  : {expected_c_hex}\n")

    subkeys = generate_subkeys(k_bits, verbose=True)

    k1_expected_str = "000110 110000 001011 101111 111111 000111 000001 110010"
    k1_actual_str = bits_to_str(subkeys[0], 6)
    assert k1_actual_str == k1_expected_str, f"K1 mismatch: {k1_actual_str} != {k1_expected_str}"
    print("[PASS] Subkey K1 matches Grabbe reference perfectly!")

    k16_expected_str = "110010 110011 110110 001011 000011 100001 011111 110101"
    k16_actual_str = bits_to_str(subkeys[15], 6)
    assert k16_actual_str == k16_expected_str, f"K16 mismatch: {k16_actual_str} != {k16_expected_str}"
    print("[PASS] Subkey K16 matches Grabbe reference perfectly!\n")

    c_bits = des_encrypt_block(m_bits, subkeys, verbose=True)
    c_hex = bits_to_hex(c_bits)

    assert c_hex == expected_c_hex, f"Ciphertext mismatch: {c_hex} != {expected_c_hex}"
    print(f"[PASS] Encryption output {c_hex} matches Grabbe reference {expected_c_hex} 100%!")

    dec_bits = des_decrypt_block(c_bits, subkeys, verbose=False)
    dec_hex = bits_to_hex(dec_bits)
    assert dec_hex == m_hex, f"Decryption mismatch: {dec_hex} != {m_hex}"
    print(f"[PASS] Decryption round-trip output {dec_hex} matches original Plaintext {m_hex} 100%!\n")
    print("=" * 78)


def demonstrate_avalanche_effect():
    print("=" * 78)
    print("DES AVALANCHE EFFECT EXPERIMENTAL ANALYSIS")
    print("=" * 78)

    m_hex = "0123456789ABCDEF"
    k_hex = "133457799BBCDFF1"

    m_bits = hex_to_bits(m_hex, 64)
    k_bits = hex_to_bits(k_hex, 64)
    subkeys = generate_subkeys(k_bits)

    c_base = des_encrypt_block(m_bits, subkeys)
    c_base_hex = bits_to_hex(c_base)

    print(f"Base Plaintext : {m_hex} -> Ciphertext: {c_base_hex}")

    m_flipped = list(m_bits)
    m_flipped[0] ^= 1
    m_flipped_hex = bits_to_hex(m_flipped)

    c_flipped = des_encrypt_block(m_flipped, subkeys)
    c_flipped_hex = bits_to_hex(c_flipped)

    diff_bits = sum(b1 ^ b2 for b1, b2 in zip(c_base, c_flipped))
    diff_percent = (diff_bits / 64) * 100

    print(f"Flipped Plaintext (bit 1 flipped): {m_flipped_hex}")
    print(f"New Ciphertext                   : {c_flipped_hex}")
    print(f"Ciphertext bits changed          : {diff_bits} / 64 ({diff_percent:.2f}%)\n")

    print("Round-by-round Hamming distance between state vectors:")
    ip_base = permute(m_bits, IP_TABLE)
    l_base, r_base = ip_base[:32], ip_base[32:]

    ip_flip = permute(m_flipped, IP_TABLE)
    l_flip, r_flip = ip_flip[:32], ip_flip[32:]

    print(f"  Round  0 (Initial): {sum(x ^ y for x, y in zip(l_base + r_base, l_flip + r_flip))} bits different")

    for round_idx in range(16):
        k = subkeys[round_idx]
        f_b = feistel_f(r_base, k)
        l_base, r_base = r_base, xor_bits(l_base, f_b)

        f_f = feistel_f(r_flip, k)
        l_flip, r_flip = r_flip, xor_bits(l_flip, f_f)

        diff = sum(x ^ y for x, y in zip(l_base + r_base, l_flip + r_flip))
        print(f"  Round {round_idx + 1:2d}           : {diff:2d} / 64 bits different ({diff / 64 * 100:5.1f}%)")

    print("\nConclusion: By Round 4-5, half the bits are thoroughly scrambled (ideal Avalanche property).")
    print("=" * 78)


def interactive_cli():
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("   DES (Data Encryption Standard) Cipher - Lab 4 Cryptography")
    print("   Author: Ion Moroșanu, FAF-242 | TUM 2026")
    print("   Based on: NIST FIPS 46-3 & J. Orlin Grabbe Illustrated Spec")
    print("=" * 70)

    default_key = "133457799BBCDFF1"

    while True:
        print("\nChoose an option:")
        print("  1. Encrypt text message (UTF-8, PKCS#7 padded)")
        print("  2. Decrypt text message (UTF-8)")
        print("  3. Encrypt 64-bit Hex block (with detailed round trace)")
        print("  4. Decrypt 64-bit Hex block")
        print("  5. Run Grabbe Test Vector Verification (Self-Test)")
        print("  6. Run Avalanche Effect Demonstration")
        print("  0. Exit")

        choice = input("\nEnter choice (0-6): ").strip()

        if choice == "0":
            print("Exiting DES tool. Goodbye!")
            break

        elif choice == "1":
            text = input("Enter plaintext message: ")
            key_in = input(f"Enter 16-hex-digit key [default: {default_key}]: ").strip()
            if not key_in:
                key_in = default_key
            try:
                cipher_hex = des_encrypt_text(text, key_in)
                print(f"\n[+] Encrypted Hex Ciphertext:\n    {cipher_hex}")
            except Exception as e:
                print(f"[-] Error: {e}")

        elif choice == "2":
            cipher_hex = input("Enter ciphertext hex: ").strip().replace(" ", "")
            key_in = input(f"Enter 16-hex-digit key [default: {default_key}]: ").strip()
            if not key_in:
                key_in = default_key
            try:
                decrypted = des_decrypt_text(cipher_hex, key_in)
                print(f"\n[+] Decrypted Plaintext Message:\n    {decrypted}")
            except Exception as e:
                print(f"[-] Error during decryption: {e}")

        elif choice == "3":
            block_hex = input("Enter 16-hex-digit plaintext block [e.g. 0123456789ABCDEF]: ").strip().replace(" ", "")
            if not block_hex:
                block_hex = "0123456789ABCDEF"
            key_in = input(f"Enter 16-hex-digit key [default: {default_key}]: ").strip()
            if not key_in:
                key_in = default_key
            try:
                m_bits = hex_to_bits(block_hex, 64)
                k_bits = hex_to_bits(key_in, 64)
                subkeys = generate_subkeys(k_bits, verbose=True)
                c_bits = des_encrypt_block(m_bits, subkeys, verbose=True)
                print(f"[+] Final Ciphertext: {bits_to_hex(c_bits)}")
            except Exception as e:
                print(f"[-] Error: {e}")

        elif choice == "4":
            block_hex = input("Enter 16-hex-digit ciphertext block [e.g. 85E813540F0AB405]: ").strip().replace(" ", "")
            if not block_hex:
                block_hex = "85E813540F0AB405"
            key_in = input(f"Enter 16-hex-digit key [default: {default_key}]: ").strip()
            if not key_in:
                key_in = default_key
            try:
                c_bits = hex_to_bits(block_hex, 64)
                k_bits = hex_to_bits(key_in, 64)
                subkeys = generate_subkeys(k_bits, verbose=False)
                m_bits = des_decrypt_block(c_bits, subkeys, verbose=True)
                print(f"[+] Final Decrypted Plaintext Block: {bits_to_hex(m_bits)}")
            except Exception as e:
                print(f"[-] Error: {e}")

        elif choice == "5":
            verify_grabbe_example()

        elif choice == "6":
            demonstrate_avalanche_effect()

        else:
            print("Invalid option. Please choose between 0 and 6.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        verify_grabbe_example()
        demonstrate_avalanche_effect()
    else:
        try:
            interactive_cli()
        except (EOFError, KeyboardInterrupt):
            print("\nTerminated.")
