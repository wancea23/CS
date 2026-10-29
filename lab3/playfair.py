import sys
import unicodedata

ALPHABET = "AĂÂBCDEFGHIÎKLMNOPQRSȘTȚUVWXYZ"
ROWS = 5
COLS = 6
FILLER = "X"
SPARE_FILLER = "Q"
MIN_KEY_LENGTH = 7
ALLOWED_RANGE = "'A'-'Z', 'a'-'z' and Ă Â Î Ș Ț (ă â î ș ț)"
VALID_CHARACTERS = set(ALPHABET + ALPHABET.lower() + "Jj" + "ŞşŢţ" + " ")
CEDILLA_TO_COMMA = str.maketrans("ŞşŢţ", "ȘșȚț")
MENU = "Operation (1 - encrypt, 2 - decrypt, 0 - exit): "


def invalid_characters(text):
    text = unicodedata.normalize("NFC", text)
    return sorted({ch for ch in text if ch not in VALID_CHARACTERS})


def letters_only(text):
    text = unicodedata.normalize("NFC", text).translate(CEDILLA_TO_COMMA)
    return text.upper().replace("J", "I").replace(" ", "")


def build_matrix(key):
    order = []
    for ch in letters_only(key) + ALPHABET:
        if ch not in order:
            order.append(ch)
    return [order[r * COLS:(r + 1) * COLS] for r in range(ROWS)]


def find_positions(matrix):
    positions = {}
    for r, row in enumerate(matrix):
        for c, ch in enumerate(row):
            positions[ch] = (r, c)
    return positions


def make_pairs(text):
    pairs = []
    i = 0
    while i < len(text):
        first = text[i]
        second = text[i + 1] if i + 1 < len(text) else None
        if second is None or second == first:
            pairs.append(first + (SPARE_FILLER if first == FILLER else FILLER))
            i += 1
        else:
            pairs.append(first + second)
            i += 2
    return pairs


def split_cryptogram(text):
    if len(text) % 2 == 1:
        return None, f"The number of letters must be even, it is {len(text)}."
    pairs = [text[i:i + 2] for i in range(0, len(text), 2)]
    doubles = [p for p in pairs if p[0] == p[1]]
    if doubles:
        error = "A cryptogram cannot have a pair of equal letters: "
        return None, error + " ".join(doubles)
    return pairs, None


def transform_pair(pair, matrix, positions, step):
    (r1, c1), (r2, c2) = positions[pair[0]], positions[pair[1]]
    if r1 == r2:
        return matrix[r1][(c1 + step) % COLS] + matrix[r2][(c2 + step) % COLS]
    if c1 == c2:
        return matrix[(r1 + step) % ROWS][c1] + matrix[(r2 + step) % ROWS][c2]
    return matrix[r1][c2] + matrix[r2][c1]


def encrypt(pairs, matrix):
    positions = find_positions(matrix)
    return [transform_pair(p, matrix, positions, 1) for p in pairs]


def decrypt(pairs, matrix):
    positions = find_positions(matrix)
    return [transform_pair(p, matrix, positions, -1) for p in pairs]


def read_letters(prompt, what, min_length=1):
    while True:
        text = input(prompt)
        bad = invalid_characters(text)
        if bad:
            print("Invalid characters: " + ", ".join(f"'{ch}'" for ch in bad))
            print(f"Use only {ALLOWED_RANGE}. Spaces are ignored.")
            continue
        letters = letters_only(text)
        if len(letters) < min_length:
            print(f"The {what} must have at least {min_length} letters, "
                  f"it has {len(letters)}.")
            continue
        return letters


def read_choice():
    while True:
        choice = input(MENU).strip()
        if choice in ("0", "1", "2"):
            return choice
        print("Type 1, 2 or 0.")


def print_matrix(matrix):
    print("Matrix:")
    for row in matrix:
        print("    " + " ".join(row))


def run_encryption(matrix):
    text = read_letters("Message: ", "message")
    pairs = make_pairs(text)
    print("Prepared message: " + " ".join(pairs))
    print("Cryptogram: " + "".join(encrypt(pairs, matrix)))


def run_decryption(matrix):
    while True:
        text = read_letters("Cryptogram: ", "cryptogram", 2)
        pairs, error = split_cryptogram(text)
        if error is None:
            break
        print(error)
    result = decrypt(pairs, matrix)
    print("Decrypted pairs: " + " ".join(result))
    print("Decrypted message: " + "".join(result))
    print(f"Remove the filler letters {FILLER}/{SPARE_FILLER} "
          "and add the spaces by hand.")


def main():
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("Playfair cipher for Romanian (31 letters, J is written as I)")
    while True:
        choice = read_choice()
        if choice == "0":
            break
        key = read_letters("Key: ", "key", MIN_KEY_LENGTH)
        matrix = build_matrix(key)
        print_matrix(matrix)
        if choice == "1":
            run_encryption(matrix)
        else:
            run_decryption(matrix)
        print()


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print()
