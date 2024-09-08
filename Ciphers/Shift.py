'''
Symmetric cipher with integer key n performing an ASCII shift

Decode with key -n.

'''

def get_parameters():
    return {"encrypt": [("n", int, [])], "decrypt": [("n", int, [])]}

def encrypt(text, params): # Apply an n ASCII shift to a message M.
    n = params[0]
    chars = list(text)
    return ''.join( list( map( lambda c: chr(ord(c) + n) , chars) ) )

def decrypt(text, params):
    params[0] *= -1
    return encrypt(text, params)
