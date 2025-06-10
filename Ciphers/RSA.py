
'''
Textbook RSA encryption - asymmetric with public key (n, e).
'''

from Utilities import mod_expon

def get_parameters():
    return {"encrypt": [("Block Size", int, [], "Block Size"),
                        ("p", int, [("params[1] > 100**params[0]", "p must be greater than 100^Block Size")], "1st Prime"), 
                        ("q", int, [("params[2] > 100**params[0]", "q must be greater than 100^Block Size")], "2nd Prime"), 
                        ("e", int, [("gcd( (params[1] - 1) * (params[2] - 1), params[2]) == 1", "e must be coprime to (p - 1)(q - 1)")], "Public Exponent")
                        ], 
            "decrypt": [("Block Size", int, [], "Block Size"),
                        ("n", int, [], "Public Modulus"), 
                        ("d", int, [], "Private Exponent")
                        ]}



def encrypt(text, params):
    b = params[0]
    p = params[1]
    q = params[2]
    e = params[3]
    n = p * q
    tot = (p - 1) * (q - 1) # Euler's Totient Function for n = pq.
    
    text_blocks = [text[b*i:b*(i+1)] for i in range((len(text)//b) + 1)]

    if len(text_blocks[-1]) < b:
        text_blocks[-1] = text_blocks[-1] + ''.join(" " * (b - len(text_blocks[-1])))

    blocks = []

    for text_block in text_blocks:
        block = 0
        for c in text_block:
            block = block*1000 + ord(c)
        blocks.append(block)

    e_blocks = list(map(lambda x: str(mod_expon(x, e, n)), blocks))
    e_blocks = list(map(lambda x: "0" * (b*3 - len(x)) + x, e_blocks))

    key = {"Block Size": b, "p": p, "q": q, "n": p*q, "e": e, "d": 0} # d TEMP PLACEHOLDER

    return [' '.join(e_blocks), key]



def decrypt(text, params):
    b = params[0]
    n = params[1]
    d = params[2]

    blocks = [str(mod_expon(int(x), d, n)) for x in text.split(' ')]
    decrypted = ''.join(list(map(lambda x: (b*3 - len(x)) * "0" + x, blocks)))

    chars = [chr(int(decrypted[3*i:3*(i+1)])) for i in range(len(decrypted) // 3)]

    key = {"Block Size": b, "n": n, "d": d}

    return [''.join(chars), key]
