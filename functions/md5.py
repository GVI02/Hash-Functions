from numpy import uint8, uint64, uint32

from utils import congruent, blocks, rotl


def md5(text: bytes) -> str:
    """
    Implementation of MD5 algorithm as specified in RFC1321.\n
    Input: String to be hashed.\n
    Output: 128-bit (16 byte) hash in the form of a hex string (32 characters).\n
    """

    # Transform input to list of numpy  uint8. This  ensured each byte actually has 8 bits. Numbers in Python only have
    # as many  bits as  needed to represent them. For  example 4 is only 3 bits in  memory (0b100). This makes  bit-wise
    # operations inconsistent. We could use 32-bit integers from the beginning as that's the main 'unit' of the RFC. But
    # I think using fixed length bytes makes it easier to understand the Pre-processing operations.

    text: list[uint8] = [uint8(byte) for byte in text]

    # Original message length as 2 32bit words
    length_64 = uint64(len(text) * 8)
    oml = [
        uint32((length_64 & 0xFFFFFFFF00000000) >> 32),
        uint32((length_64 & 0x00000000FFFFFFFF))
    ]

    # ================================================= Pre-processing =================================================

    '''
    The original message is assumed to be composed of an arbitrary number  of  bits,  not necessarily  a multiple of 8.
    So before the message digest  can be calculated we  have to pad the message to a size divisible by 512. Even if the
    size if already divisible by 512 the message is always padded.
    '''

    # 1. Append '1' bit to the message.
    # We cant actually append just one bit, or at least I haven't figured out how to, so we append '10000000' and
    # compensate for the 7 extra bits in later calculations.

    text.append(uint8(0b10000000))

    # 2. Append '0' bits to the message.
    # The amount of bits added is the minimum so that the (ml + extra bits + oml) % 512 == 0
    # We already know that @oml is 64 bits long.

    ml = len(text) * 8 - 7

    padding = 0  # 1 <= padding <= 512
    for i in range(0, 513):
        if congruent(ml + i, 448, 512):
            padding = i
            break

    extra_bytes = int((padding - 7) / 8)  # Remember we compensate for the 7 extra '0's we have already added
    text.extend(extra_bytes * [uint8(0b00000000)])

    # After the message has been padded we can combine the bytes into 32-bit words.

    words = []
    for i in range(0, len(text) - 3, 4):
        b1 = uint32(text[i]) << 24
        b2 = uint32(text[i + 1]) << 16
        b3 = uint32(text[i + 2]) << 8
        b4 = uint32(text[i + 3])
        words.append(b1 | b2 | b3 | b4)

    # 3. Append the original length of the message as 2 32-bit words to the message
    # Words are appended low-order word first
    words.extend(reversed(oml))

    # ==================================================================================================================

    # ========================================== Computing the Message Digest ==========================================

    # A buffer composed of 4 32-bit words is used to compute the digest
    # Worlds are labeled as: A, B, C, D

    A = uint32(0x67452301)
    B = uint32(0xefcdab89)
    C = uint32(0x98badcfe)
    D = uint32(0x10325476)

    # Define auxiliary functions
    # Each function takes in 3 32-bit words and returns a single 32-bit word
    F = lambda x, y, z: (x & y) | (~x & z)
    G = lambda x, y, z: (x & z) | (y & ~z)
    H = lambda x, y, z: x ^ y ^ z
    I = lambda x, y, z: y ^ (x | ~z)

    # Define T element table
    # These values are constructed from the sine function
    # Here

    # Process each 512-bit block

    for M in blocks(words):

        X = []
        for j in range(0, 16):
            X.append(M[j])

        AA = A
        BB = B
        CC = C
        DD = D

        # Round 1
        A = B + (rotl(A + F(B, C, D) + X[k] + T[i], s))



if __name__ == "__main__":
    md5(b"abcde")