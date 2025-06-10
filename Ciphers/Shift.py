'''
Symmetric cipher with integer key n performing an ASCII shift

Decode with key -n.

'''

def get_parameters():
    return {"encrypt": [("n", int, [], "Shift Key")], "decrypt": [("n", int, [], "Shift Key")]}

def encrypt(text, params): # Apply an n ASCII shift to a message M.
    n = params[0]
    chars = list(text)

    key = {"n": n}

    return [''.join( list( map( lambda c: chr(ord(c) + n) , chars) ) ), key]

def decrypt(text, params):
    params[0] *= -1

    key = {"n": n}

    return [encrypt(text, params), key]
