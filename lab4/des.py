import random
import string
import sys

IP_TABLE = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7,
]

RANDOM_CHARSET = string.ascii_letters + string.digits + "!@#$%&*?"


def validate_message(text):
    if len(text) != 8:
        return False, f"Message must be exactly 8 characters long (got {len(text)})."
    bad = [ch for ch in text if not (32 <= ord(ch) <= 126)]
    if bad:
        return False, (
            "Only printable ASCII characters (codes 32..126) are allowed: "
            + ", ".join(repr(ch) for ch in bad)
        )
    return True, None


def generate_random_message():
    return "".join(random.choice(RANDOM_CHARSET) for _ in range(8))


def bytes_to_bits(byte_data):
    bits = []
    for b in byte_data:
        for shift in range(7, -1, -1):
            bits.append((b >> shift) & 1)
    return bits


def bits_to_hex(bits):
    val = 0
    for b in bits:
        val = (val << 1) | b
    return f"{val:0{len(bits) // 4}X}"


def bits_to_str(bits, group=4):
    s = "".join(str(b) for b in bits)
    if group:
        return " ".join(s[i:i + group] for i in range(0, len(s), group))
    return s


def permute(bits, table):
    return [bits[idx - 1] for idx in table]


def print_ascii_reference_table():
    print("Table 1 - ASCII Character Set (Printable range 32..126):")
    print("-" * 74)
    rows = 24
    for r in range(rows):
        cells = []
        for col in range(4):
            code = 32 + col * rows + r
            if code <= 126:
                label = "SP" if code == 32 else chr(code)
                cells.append(f"{code:3d} 0x{code:02X} {label:<2}")
        print(" | ".join(cells))
    print("-" * 74)


def print_ip_table():
    print("Table 2 - DES Initial Permutation Table (IP):")
    print("-" * 74)
    for row_idx in range(8):
        row_vals = IP_TABLE[row_idx * 8:(row_idx + 1) * 8]
        formatted = " ".join(f"{v:2d}" for v in row_vals)
        half_note = "L0" if row_idx < 4 else "R0 (= L1)"
        out_start = row_idx * 8 + 1
        out_end = out_start + 7
        label = f"Row {row_idx + 1} (IP[{out_start:2d}..{out_end:2d}] -> {half_note:<9})"
        print(f"  {label}: {formatted}")
    print("-" * 74)


def compute_l1(data_bytes, show_ascii_table=True):
    m_bits = bytes_to_bits(data_bytes)
    m_hex = bits_to_hex(m_bits)

    print("\n" + "=" * 74)
    print("DES TASK 2.4 (n = 15, 15 mod 11 = 4) - COMPUTE L1 FROM 8-CHAR MESSAGE")
    print("=" * 74)

    if show_ascii_table:
        print_ascii_reference_table()
    print_ip_table()

    print("\nStep 1 - Convert 8-character input message to 64-bit binary block M:")
    hdr = f"{'Byte':<4} {'Char':<6} {'Dec':<5} {'Hex':<5} {'8-bit Binary':<12}"
    print(f"  {hdr} {'M Bit Positions'}")
    print("  " + "-" * 60)
    for idx, b in enumerate(data_bytes):
        ch_disp = repr(chr(b)) if 32 <= b <= 126 else f"0x{b:02X}"
        byte_bits = bits_to_str(m_bits[idx * 8:(idx + 1) * 8], 4)
        start_pos = idx * 8 + 1
        end_pos = start_pos + 7
        row_prefix = f"{idx + 1:<4} {ch_disp:<6} {b:<5} 0x{b:02X}  {byte_bits:<12}"
        print(f"  {row_prefix} M[{start_pos:2d}..{end_pos:2d}]")

    print(f"\n  M (Hex, 16 digits) : {m_hex}")
    print(f"  M (Bin, 64 bits)   : {bits_to_str(m_bits[:32], 4)}")
    print(f"                       {bits_to_str(m_bits[32:], 4)}")

    print("\nStep 2 - Apply Initial Permutation IP to 64-bit block M:")
    ip_bits = permute(m_bits, IP_TABLE)
    for row_idx in range(8):
        tbl_row = IP_TABLE[row_idx * 8:(row_idx + 1) * 8]
        out_row = ip_bits[row_idx * 8:(row_idx + 1) * 8]
        idx_str = " ".join(f"{p:2d}" for p in tbl_row)
        bit_str = "".join(str(bit) for bit in out_row)
        hex_byte = bits_to_hex(out_row)
        line_out = f"M[{idx_str}] -> {bit_str[:4]} {bit_str[4:]} (0x{hex_byte})"
        print(f"  Row {row_idx + 1}: {line_out}")

    print(f"\n  IP(M) (Hex)        : {bits_to_hex(ip_bits)}")
    print(f"  IP(M) (Bin)        : {bits_to_str(ip_bits[:32], 4)}")
    print(f"                       {bits_to_str(ip_bits[32:], 4)}")

    l0 = ip_bits[:32]
    r0 = ip_bits[32:]
    print("\nStep 3 - Split IP(M) into 32-bit halves L0 and R0:")
    print(f"  L0 (bits  1..32)   : {bits_to_str(l0, 4)} (Hex: {bits_to_hex(l0)})")
    print(f"  R0 (bits 33..64)   : {bits_to_str(r0, 4)} (Hex: {bits_to_hex(r0)})")

    l1 = r0
    print("\nStep 4 - Feistel Round 1 (L1 = R0; R1 = L0 XOR f(R0, K1)):")
    print("  Because L1 copies R0 directly, L1 does not depend on subkey K1.")
    print(f"  L1 (Bin, 4-bit)    : {bits_to_str(l1, 4)}")
    print(f"  L1 (Bin, 8-bit)    : {bits_to_str(l1, 8)}")
    print(f"  L1 (Hex, 8 digits) : {bits_to_hex(l1)}")
    print("=" * 74)
    return l0, r0, l1


def run_verification_tests():
    print("\n" + "=" * 74)
    print("RUNNING TASK 2.4 REFERENCE VERIFICATION TESTS")
    print("=" * 74)

    assert len(IP_TABLE) == 64 and sorted(IP_TABLE) == list(range(1, 65))
    print("[PASS] IP_TABLE contains all 64 unique bit positions 1..64.")

    l0_q11, r0_q11, l1_q11 = compute_l1(b"Alfabetu", show_ascii_table=False)
    assert bits_to_hex(l0_q11) == "FFC0E6A9"
    assert bits_to_hex(l1_q11) == "00FE0214"
    print("[PASS] TEMA 4 Q11 ('Alfabetu'): L0 = FFC0E6A9, L1 = R0 = 00FE0214.")

    grabbe_bytes = bytes.fromhex("0123456789ABCDEF")
    l0_gr, r0_gr, l1_gr = compute_l1(grabbe_bytes, show_ascii_table=False)
    assert bits_to_hex(l0_gr) == "CC00CCFF"
    assert bits_to_hex(l1_gr) == "F0AAF0AA"
    print("[PASS] Grabbe reference (0123456789ABCDEF): L0 = CC00CCFF, L1 = F0AAF0AA.")

    rnd_msg = generate_random_message()
    ok, err = validate_message(rnd_msg)
    assert ok and err is None
    _, r0_rnd, l1_rnd = compute_l1(rnd_msg.encode("ascii"), show_ascii_table=False)
    assert l1_rnd == r0_rnd and len(l1_rnd) == 32
    l1_rnd_hex = bits_to_hex(l1_rnd)
    print(f"[PASS] Random 8-char '{rnd_msg}': L1 = {l1_rnd_hex} (32 bits).")
    print("=" * 74)


def prompt_manual_message():
    while True:
        msg = input("Enter an 8-character ASCII message: ")
        ok, err = validate_message(msg)
        if not ok:
            print(f"[-] {err}")
            continue
        compute_l1(msg.encode("ascii"), show_ascii_table=True)
        break


def interactive_cli():
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 74)
    print("   DES Algorithm - Lab 4 Cryptography, Task 2.4 (n = 15, 15 mod 11 = 4)")
    print("   Student: Ion Moroșanu, FAF-242 | TUM 2026")
    print("   Objective: Given an 8-character message, find L1 (tables + steps)")
    print("=" * 74)

    while True:
        print("\nChoose an option:")
        print("  1. Enter an 8-character message manually and find L1")
        print("  2. Generate a random 8-character message and find L1")
        print("  3. Run reference verification tests (TEMA 4 Q11 & Grabbe)")
        print("  0. Exit")

        choice = input("\nEnter choice (0-3): ").strip()
        if choice == "0":
            print("Exiting DES Task 2.4 tool. Goodbye!")
            break
        elif choice == "1":
            prompt_manual_message()
        elif choice == "2":
            msg = generate_random_message()
            print(f"\n[+] Randomly generated 8-character message: {msg}")
            compute_l1(msg.encode("ascii"), show_ascii_table=True)
        elif choice == "3":
            run_verification_tests()
        else:
            print("Invalid option. Please choose between 0 and 3.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_verification_tests()
    else:
        try:
            interactive_cli()
        except (EOFError, KeyboardInterrupt):
            print("\nTerminated.")
