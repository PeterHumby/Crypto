'''

SHA-3 Permutation-based Hash Encryption

'''


def state_array(M, w): # Convert a string M to a 5 x 5 x w bit array.
    M = list(''.join(list(map(lambda x: bin(ord(x))[2:], list(M)))))
    M = list(map(lambda x: int(x), M))
    print(M)
    S = [ [ [0] * 5 ] * 5 ] * w
    
    for z in range(w):
        for y in range(5):
            for x in range(5):
                print(x, y, z, M[w * (5*y + x) + z])
                #print(w * (5*y + x) + z)
                #print(M[w * (5*y + x) + z])
                S[z][y][x] = M[w * (5*y + x) + z]
                
    return S

def array_to_string(S): # Convert a state array to a string.
    w = len(S)
    lanes = []

    for i in range(5):
        lane = []
        for j in range(5):
            string = ''.join([str(S[k][j][i]) for k in range(w)])
            lane.append(string)
        lanes.append(lane)
    
    planes = list(map(lambda x: ''.join(x), lanes))

    print(planes)
# Access array bit in position (x, y, z) as S[z][y][x].

def display_slice(s):
    for row in s:
        print(row)

def display_array(S):
    for s in S:
        display_slice(s)
        print("\n")

def theta():
    pass










S = state_array("hello world", 2)

display_array(S)

array_to_string(S)
