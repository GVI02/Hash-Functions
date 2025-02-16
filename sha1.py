from numpy import uint8, uint32, uint64
from binascii import hexlify


def print_bytes(list_of_bytes: list[uint8]):
    """Helper function to print a list of 8bit integers as 32-bit words"""
    out = []
    for i in range(0, len(list_of_bytes) - 3, 4):
        b1 = f"{list_of_bytes[i    ]:02X}"
        b2 = f"{list_of_bytes[i + 1]:02X}"
        b3 = f"{list_of_bytes[i + 2]:02X}"
        b4 = f"{list_of_bytes[i + 3]:02X}"

        out.append(f"{b1}{b2}{b3}{b4}")
    print(" ".join(out))


def print_words(list_of_words: list[uint32]):
    """Helper function to print a list of 32-bit words"""
    print(" ".join([f"{word:08X}" for word in list_of_words]))


def congruent(a: int, b: int, m: int) -> bool:
    """Return whether a and b are congruent modulo m"""
    diff = a - b
    return diff % m == 0


def blocks(words: list) -> list:
    """Helper function to split list of 32-bit words into chunks of 16. Each chunk has 512 bits"""
    for i in range(0, len(words), 16):
        yield words[i:i + 16]


def leftrotate(X: uint32, n: int):
    return uint32((X << n) | (X >> 32 - n))


def sha1(text: str) -> str:
    """
    Implementation of SHA-1 algorithm as specified in RFC3174.\n
    Input: String to be hashed.\n
    Output: 160-bit (20 byte) hash in the form of a string.\n
    Text encoding is assumed to be UTF-8.
    """

    # Original message length as 8 uint8 values
    length_64 = uint64(len(text.encode("utf-8")) * 8)
    oml = [
        uint8((length_64 & 0xFF00000000000000) >> 56),
        uint8((length_64 & 0x00FF000000000000) >> 48),
        uint8((length_64 & 0x0000FF0000000000) >> 40),
        uint8((length_64 & 0x000000FF00000000) >> 32),
        uint8((length_64 & 0x00000000FF000000) >> 24),
        uint8((length_64 & 0x0000000000FF0000) >> 16),
        uint8((length_64 & 0x000000000000FF00) >> 8),
        uint8((length_64 & 0x00000000000000FF))
    ]

    # Transform input to list of numpy uint32. This ensured each byte actually has 8 bits.
    # Numbers in Python only have as many bits as needed to represent them. For example
    # 4 is only 3 bits in memory (0b100). This makes bit-wise operations inconsistent.
    # We could use 32-bit integers from the beginning as that's the main 'unit' of the
    # RFC. But I think using fixed length bytes makes it easier to understand the
    # Pre-processing operations.

    text: list[uint8] = [uint8(byte) for byte in text.encode("utf-8")]

    # ====================== Pre-processing ======================

    # The idea of the pre-processing step is to transform the message into a bitstream that
    # can be split into blocks of 512 bits. Subsequent operations are performed on these blocks.

    # 1. Append '1' bit to the message.
    # We cant actually append just one bit, so we append '10000000' and compensate for the
    # 7 extra bits in later calculations.

    text.append(uint8(0b10000000))

    # 2. Append '0' bits to the message.
    # The amount of bits added is the minimum so that the (ml + extra bits + oml) % 512 == 0
    # We already know that @oml is 64 bits long.

    ml = len(text) * 8 - 7

    extra_bits = 0
    for i in range(0, 513):
        if congruent(ml + i, 448, 512):
            extra_bits = i
            break

    extra_bytes = int((extra_bits - 7) / 8)  # Remember we compensate for the 7 extra '0's we have already added
    text.extend(extra_bytes * [uint8(0b00000000)])

    # 3. Append the original length of the message as 2 32-bit words to the message
    text.extend(oml)

    # Now we can convert the array of 8-bit values into 32-bit words as the computation of
    # the digest expects 32-bit values.

    words = []
    for i in range(0, len(text) - 3, 4):
        b1 = uint32(text[i]) << 24
        b2 = uint32(text[i + 1]) << 16
        b3 = uint32(text[i + 2]) << 8
        b4 = uint32(text[i + 3])
        words.append(b1 | b2 | b3 | b4)

    # ============================================================

    # =============== Computing the Message Digest ===============

    # The message digest is computed using 2 buffers each made from 5 32-bit words
    # and a sequence of 80 32-bit words.
    # The first buffer has the words: A, B, C, D, E
    # The second buffer has the words: H0, H1, H2, H3, H4
    # The 80 words are labeled: W(0), W(1) ... W(79)
    # The padded message is split into 16 word chunks - M(0), M(1)...M(n)
    # A single 32-bit word buffer TEMP is also used

    # 1. Initialize H buffers
    # The H buffers would be placed as constants outside the function, but again they remain
    # for simplicity and ease of following the algorithm.

    H0 = uint32(0x67452301)
    H1 = uint32(0xEFCDAB89)
    H2 = uint32(0x98BADCFE)
    H3 = uint32(0x10325476)
    H4 = uint32(0xC3D2E1F0)

    # 2. Calculate message digest

    for W in blocks(words):

        A = H0
        B = H1
        C = H2
        D = H3
        E = H4

        for t in range(16, 80):
            W.append(leftrotate(
                W[t - 3] ^ W[t - 8] ^ W[t - 14] ^ W[t - 16],
                1
            ))

        for t in range(80):
            if 0 <= t <= 19:
                f = (B & C) | ((~B) & D)
                K = uint32(0x5A827999)
            elif 20 <= t <= 39:
                f = B ^ C ^ D
                K = uint32(0x6ED9EBA1)
            elif 40 <= t <= 59:
                f = (B & C) | (B & D) | (C & D)
                K = uint32(0x8F1BBCDC)
            else:
                f = B ^ C ^ D
                K = uint32(0xCA62C1D6)

            TEMP = leftrotate(A, 5) + f + E + W[t] + K
            E = D
            D = C
            C = leftrotate(B, 30)
            B = A
            A = TEMP

        H0 = H0 + A
        H1 = H1 + B
        H2 = H2 + C
        H3 = H3 + D
        H4 = H4 + E

    # 3 Output the result as a string
    # The H buffers now hold the resulting hash. This is what makes the hash function fixed
    # length. We have 5 32-bit words so the output will always be 160-bits no matter how long
    # the input text is.

    result = bytearray()

    for H_buffer in [H0, H1, H2, H3, H4]:
        result.append(uint8((H_buffer & 0xFF000000) >> 24))
        result.append(uint8((H_buffer & 0x00FF0000) >> 16))
        result.append(uint8((H_buffer & 0x0000FF00) >> 8))
        result.append(uint8(H_buffer & 0x000000FF))

    return hexlify(result).decode("utf-8")


if __name__ == '__main__':
    message = "qdwqdwqdqw"
    print(sha1(message))
