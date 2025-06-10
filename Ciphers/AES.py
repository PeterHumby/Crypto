'''

Simple implementation of AES with options for 128, 196, or 256 based on parameters chosen.

Slow due to use of polynomials.

'''

from galois import GF, Poly
import numpy as np

irr = Poly([1, 0, 0, 0, 1, 1, 0, 1, 1], GF(2))
F = GF(2**8, irreducible_poly=irr)

''' Block/Hex/Poly utility functions '''

def transpose(block):
    m = len(block)
    n = len(block[0])

    t_block = [[0 for i in range(m)] for i in range(n)]


    for i in range(m):
        for j in range(n):
            t_block[j][i] = block[i][j]
    
    return t_block

def poly_blocks(text): # Break an input in suitable 4x4 blocks of bytes.
    b = list(map(lambda x: int(hex(ord(x)), 16), list(text)))

    b_field = list(map(lambda x: F(x), b))

    entries = [b[16*i:16*(i + 1)] + ([int('0xA0', 16)] * (16 - len(b[16*i:16*(i + 1)]))) for i in range(int(np.ceil(len(b) / 16)))]
    
    blocks = [transpose([[Poly.Int(entries[i][4*j + k]) for k in range(4)] for j in range(4)]) for i in range(len(entries))]
    
    return blocks

def poly_to_hex(p): # Convert an up to degree 7 polynomial over GF(2) to a corresponding hex value
    binary = [0] * 8
    for i in p.nonzero_degrees:
        binary[7 - i] = 1
    out = [2**(7-i) * binary[i] for i in range(8)]
    return hex(sum(out))

def block_to_hex(block): # Convert entries in a block to corresponding hex values.
    hex_block = []
    for row in block:
        hex_row = []
        for p in row:
            hex_row.append(poly_to_hex(p))
        hex_block.append(hex_row)
    
    return hex_block

def block_to_str(block):
    block = block_to_hex(block)
    text_block = []
    for row in block:
        text_row = []
        for x in row:
            text_row.append(chr(int(x, 16)))
        text_block.append(text_row)
    text_block = transpose(text_block)

    text_block = list(map(lambda r: ''.join(r), text_block))

    return ''.join(text_block)

def rot(l):
    l_new = []
    n = len(l)
    for i in range(n):
        l_new.append(l[(i + 1) % n])
    
    return l_new


''' Cipher functions '''

def mix_columns(block):
    block = transpose(block) # Switch row and columns spaces for easier enumeration.
    mixed_block = []

    k = [Poly.Int(0x02), Poly.Int(0x03)]
    for col in block:
        mixed_col = []
        mixed_col.append( ((k[0] * col[0]) % irr) +  ((k[1] * col[1]) % irr) + col[2] + col[3] )
        mixed_col.append( col[0] + ((k[0] * col[1]) % irr) +  ((k[1] * col[2]) % irr) + col[3] )
        mixed_col.append( col[0] + col[1] + ((k[0] * col[2]) % irr) +  ((k[1] * col[3]) % irr) )
        mixed_col.append( ((k[1] * col[0]) % irr) + col[1] + col[2] +  ((k[0] * col[3]) % irr) )
        mixed_block.append(mixed_col)

    return transpose(mixed_block)

def sub_box(p): # Polynomial/Hex substitution.

    c = [1, 1, 0, 0, 0, 1, 1, 0]

    if p != 0:
        q = int(np.reciprocal(F(str(p))))
    else:
        q = p

    bits = list(bin(q)[2:])
    
    b = ([0] * (8 - len(bits))) + bits
    
    b = list(map(lambda x: int(x), b))[::-1]

    d = [(b[i] + b[(i + 4) % 8] + b[(i + 5) % 8] + b[(i + 6) % 8] + b[(i + 7) % 8] + c[i]) % 2 for i in range(8)][::-1]


    out = [2**(7-i) * d[i] for i in range(8)]

    return Poly.Int(sum(out))

def sub_word(w): # Word (list of polynomials) substitution.
    return list(map(lambda x: sub_box(x), w))

def sub_block(block): # Block (list of words) substitution.
    s_block = []
    for row in block:
        row = sub_word(row)
        s_block.append(row)
    return s_block

def shift_rows(block):

    shift_block = []
    for i in range(len(block)):
        b = block[i]
        d = []
        n = len(b)
        for j in range(n):
            d.append(b[(i + j) % n])
        shift_block.append(d)
    return shift_block

def key_expansion(key, Nk, Nr):

    key = [key[2*i:2*(i+1)] for i in range(len(key)//2)] # Break key into hex bytes
    key = list(map(lambda x: Poly.Int(int(x, 16)), key)) # Convert to polynomials
    key = [key[4*i:4*(i+1)] for i in range(len(key)//4)] # Break k into words

    Rcon = [[0x01, 0x00, 0x00, 0x00], [0x02, 0x00, 0x00, 0x00], [0x04, 0x00, 0x00, 0x00], [0x08, 0x00, 0x00, 0x00], [0x10, 0x00, 0x00, 0x00],
            [0x20, 0x00, 0x00, 0x00], [0x40, 0x00, 0x00, 0x00], [0x80, 0x00, 0x00, 0x00], [0x1b, 0x00, 0x00, 0x00], [0x36, 0x00, 0x00, 0x00]]
    
    r_key_schedule = key

    for i in range(Nk, 4*(Nr + 1)):
        if i % Nk == 0:

            w = [r_key_schedule[i - Nk][j] + sub_word(rot(r_key_schedule[i-1]))[j] + Poly.Int(Rcon[(i//Nk)-1][j]) for j in range(4)]
            r_key_schedule.append(w)
        
        elif ((i + 4) % 8 == 0) and (Nr == 14): # Only applies in AES256
            w = [(r_key_schedule[i - Nk][j] + sub_word(r_key_schedule[i-1])[j]) for j in range(4)]
            r_key_schedule.append(w)
        
        else:
            
            w = [(r_key_schedule[i - Nk][j] + r_key_schedule[i-1][j]) for j in range(4)]
            r_key_schedule.append(w)
        
        

    r_key_schedule = [r_key_schedule[4*i:4*(i+1)] for i in range(len(r_key_schedule) // 4)]

    return r_key_schedule

def add_round_key(block, r_key):    
    
    r_key = transpose(r_key)

    for i in range(4):
        for j in range(4):
            block[i][j] += r_key[i][j]
              
    return block


''' Inverse Cipher functions '''

def inv_mix_columns(block):
    block = transpose(block) # Switch row and columns spaces for easier enumeration.
    mixed_block = []

    k = [Poly.Int(0x0e), Poly.Int(0x09), Poly.Int(0x0d), Poly.Int(0x0b)]
    for col in block:
        mixed_col = []
        mixed_col.append( ((k[0] * col[0]) % irr) +  ((k[3] * col[1]) % irr) + ((k[2] * col[2]) % irr) + ((k[1] * col[3]) % irr) )
        mixed_col.append( ((k[1] * col[0]) % irr) +  ((k[0] * col[1]) % irr) + ((k[3] * col[2]) % irr) + ((k[2] * col[3]) % irr) )
        mixed_col.append( ((k[2] * col[0]) % irr) +  ((k[1] * col[1]) % irr) + ((k[0] * col[2]) % irr) + ((k[3] * col[3]) % irr) )
        mixed_col.append( ((k[3] * col[0]) % irr) +  ((k[2] * col[1]) % irr) + ((k[1] * col[2]) % irr) + ((k[0] * col[3]) % irr) )
        mixed_block.append(mixed_col)

    return transpose(mixed_block)

def inv_sub_box(p):

    c = [1, 0, 1, 0, 0, 0, 0, 0]

    bits = list(bin(p)[2:])
    
    bits = ([0] * (8 - len(bits))) + bits

    bits = list(map(lambda x: int(x), bits))[::-1]

    d = [(bits[(i+2)%8] + bits[(i+5)%8] + bits[(i+7)%8] + c[i]) % 2 for i in range(8)][::-1]

    dec = sum([2**(7-i) * d[i] for i in range(8)])

    if dec == 0:
        return Poly.Int(0)
    else:
        return Poly.Int(int(np.reciprocal(F(str(Poly.Int(dec)))))) # Invert the corresponding polynomial

def inv_sub_word(w):
    return list(map(lambda x: inv_sub_box(x), w))

def inv_sub_block(block):
    s_block = []
    for row in block:
        row = inv_sub_word(row)
        s_block.append(row)
    return s_block

def inv_shift_rows(block):
    shift_block = []
    for i in range(len(block)):
        b = block[i]
        d = []
        n = len(b)
        for j in range(n):
            d.append(b[(j - i) % n])
        shift_block.append(d)
    return shift_block


''' Encryption/Decryption'''

def encrypt_block(block, Nr, r_key_schedule):
    block = add_round_key(block, r_key_schedule[0])
    
    for r in range(1, Nr):

        block = sub_block(block)

        block = shift_rows(block)

        block = mix_columns(block)
 
        block = add_round_key(block, r_key_schedule[r])

    block = sub_block(block)
    block = shift_rows(block)
    block = add_round_key(block, r_key_schedule[-1])

    return block

def decrypt_block(block, Nr, r_key_schedule):
    r_key_schedule = r_key_schedule[::-1] # Reverse the key schedule

    block = add_round_key(block, r_key_schedule[0])
    
    for r in range(1, Nr):

        block = inv_shift_rows(block)

        block = inv_sub_block(block)

        block = add_round_key(block, r_key_schedule[r])

        block = inv_mix_columns(block)

    block = inv_shift_rows(block)

    block = inv_sub_block(block)
    
    block = add_round_key(block, r_key_schedule[-1])

    return block

def check_key(key_length, key):

    key = ''.join(key.split(' '))
    
    if key_length == 128:
        (Nk, Nr) = (4, 10)
    elif key_length == 192:
        (Nk, Nr) = (6, 12)
    else:
        (Nk, Nr) = (8, 14)

    if len(key) != (Nk*8):
        return False
    
    if len(list(set(key) - set(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "A", "b", "B", "c", "C", "d", "D", "e", "E", "f", "F"]) ) ) > 0:
        return False
    
    return True

def get_parameters():
    return {"encrypt": [("Key Length", int, [("params[0] in [128, 192, 256]", "Key length must be 128 (AES-128), 192 (AES-192), or 256 (AES-256)")], "Key Length"),
                        ("Key", str, [("AES.check_key(params[0], params[1])", "Key contain the same number of bits as the selected key length.")], "Hexadecimal Key String")], 
            "decrypt": [("Key Length", int, [("params[0] in [128, 192, 256]", "Key length must be 128 (AES-128), 192 (AES-192), or 256 (AES-256)")], "Key Length"),
                        ("Key", str, [("AES.check_key(params[0], params[1])", "Key contain the same number of bits as the selected key length.")], "Hexadecimal Key String")]}
            
def encrypt(text, params):
    blocks = poly_blocks(text)

    if params[0] == 128:
        (Nk, Nr) = (4, 10)
    elif params[0] == 192:
        (Nk, Nr) = (6, 12)
    else:
        (Nk, Nr) = (8, 14)

    key = params[1]

    key_sched = key_expansion(key, Nk, Nr)

    encrypted_blocks = []
    for block in blocks:
        print(list(block_to_str(block)))
        encrypted_block = encrypt_block(block, Nr, key_sched)
        encrypted_blocks.append(encrypted_block)
        print(list(block_to_str(encrypted_block)))
    
    result = ''.join(list(map(lambda x: block_to_str(x), encrypted_blocks)))

    key = {"Key Length": params[0], "Nk": Nk, "Nr": Nr, "Key": key}

    return (result, key)

def decrypt(text, params):

    blocks = poly_blocks(text)

    if params[0] == 128:
        (Nk, Nr) = (4, 10)
    elif params[0] == 192:
        (Nk, Nr) = (6, 12)
    else:
        (Nk, Nr) = (8, 14)

    key = params[1]

    key_sched = key_expansion(key, Nk, Nr)

    decrypted_blocks = []
    for block in blocks:
        print(list(block_to_str(block)))
        decrypted_block = decrypt_block(block, Nr, key_sched)
        decrypted_blocks.append(decrypted_block)
        print(list(block_to_str(decrypted_block)))

        

    result = ''.join(list(map(lambda x: block_to_str(x), decrypted_blocks)))

    key = {"Key Length": params[0], "Nk": Nk, "Nr": Nr, "Key": key}

    return (result, key)


