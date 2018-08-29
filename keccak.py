def KeccakError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Keccak(object):
    def __init__(self, f=1600):
        '''r, c'''
        self.r = down(f)
        self.c  = f - self.r
        #round
        self.n = 24
        
    def down(self, f):
        
        res = 2
        while res * 2 < f:
            res = res * 2

        return res

    def make(self, key, init):
        tmp = init
        for r in range(self.n+1):
            key.append(bytes.fromhex(tmp))

            tt = ""
            for e in tmp:
                t = S[int(e, 16)]
                t = hex(int(t, 2))[2:]
                tt += t
            tmp = tt

        
    def xor(self, bytesa, bytesb):
        assert(len(bytesa) == len(bytesb))
        return bytes([a ^ b for (a,b) in zip(bytesa, bytesb)])
    
    def rot(self, s, n, left=True):
        if left==True:
            return s[n:] + s[:n]
        l = len(s)
        return s[l-n:] + s[l-n:]
    
        '''
        tmp = s[n:] + s[:n]
        for i in range(len(s)):
            s[i] = tmp[i]
        return s
        '''
    
    def padding(self, message):
        '''10*1'''
        if type(message) is str:
            alist = [ord(c) for c in message]
            message = bytes(alist)
        elif type(message) is not bytes:
            raise KeccakError("The message is not str or bytes in Keccak.padding\n")

        r = self.r // 8
        l = len(message)
        mod = l % r

        if mod == 0:
            message += b'\x80' + (r-2) * b'\x00' + b'\x01'
        elif mod == 1:
            message += b'\x81'
        else:
            message += b'\x80' + (mod-2) * b'\x00' + b'\x01'

        return message
    
    def fill(self, state, message):
        for x in range(4):
            for y in range(4):
                state[x][y] = message[4*x+y]

    def list2str(self, state):
        res = b''
        for x in range(4):
            for y in range(4):
                res += state[x][y]
        return res
    
    def round(self, state, ith):

        #1 : theta
        C = [0] * 4
        for i in range(4):
            C[i] = state[i][0]
            for j in range(1,4):
                C[i] = self.xor(C[i], state[i][j])

        for i in range(4):
            tmp = self.xor(C[(i-1)%4], self.rot(C[i+1], 1))
            for j in range(4):
                state[i][j] = self.xor(tmp, state[i][j])

        #2 & 3
        tmp = [[0]*4]*4
        for x in range(4):
            for y in range(4):
                state[x][y] = self.rot(state[x][y], SHIFT[x][y])
                t = TRANS[x][y]
                tmp[t[0]][t[1]] = state[x][y]
        for x in range(4):
            for y in range(4):
                state[x][y] = tmp[x][y]
        
        #4
        for y in range(4):
            s = [''] * 8
            for x in range(4):
                ele = state[x][y][0]
                for i in range(8):
                    s[7-i] += (str((ele>>i) & 1))

            ss = ['']*4
            for ele in s: #8*4
                t = S[int(ele, 2)]
                for i in range(4):
                    ss[i] += t[i]
                    
            for x in range(4):
                state[x][y] = bytes([int(ss[x], 2)])

        #5
        a = state[0][0]
        state[0][0] = bytes([a[0] ^ RC[ith]])

    def keccak_f(self, message, key, init = "123456789abcdeff"):

        self.make(key, init)
        
        res = b""
        
        message = self.padding(message)

        l = len(message)
        state = [[0]*4]*4
        
        for i in range(0, l, 16):
            self.fill(state, message[i:i+16])

            
            for r in range(self.n):
                state = self.xor(state, key[r])
                self.round(state, r)
            state = self.xor(state, key[self.n])
            res += self.list2str(state)
        return res
    
    def roundinv(self, state, ith):
        #5
        a = state[0][0]
        state[0][0] = bytes([a[0] ^ RC[ith]])

        #4
        for y in range(4):
            s = [''] * 8
            for x in range(4):
                ele = state[x][y][0]
                for i in range(8):
                    s[7-i] += (str((ele>>i) & 1))

            ss = ['']*4
            for ele in s: #8*4
                t = S_INV[int(ele, 2)]
                ss[i] += t[i]
                    
            for x in range(4):
                state[x][y] = bytes([int(ss[x], 2)])

        #2 & 3
        tmp = [[0]*4]*4
        for x in range(4):
            for y in range(4):
                state[x][y] = self.rot(state[x][y], SHIFT[x][y], left=False)
                t = TRANS_INV[x][y]
                tmp[t[0]][t[1]] = state[x][y]
        for x in range(4):
            for y in range(4):
                state[x][y] = tmp[x][y]
        
        #1 : theta
        C = [0] * 4
        for i in range(4):
            C[i] = state[i][0]
            for j in range(1,4):
                C[i] = self.xor(C[i], state[i][j])

        for i in range(4):
            tmp = self.xor(C[(i-1)%4], self.rot(C[i+1], 1))
            for j in range(4):
                state[i][j] = self.xor(tmp, state[i][j])

    def keccak_inv(self, message, key, init = "123456789abcdeff"):
        self.make(key, init)
                              
                              
        res = b""
        
        #message = self.padding(message)

        l = len(message)
        state = [[0]*4]*4
        
        for i in range(0, l, 16):
            self.fill(state, message[i:i+16])

            
            for r in range(self.n, 0, -1):
                state = self.xor(state, key[r])
                self.round(state, r)
            state = self.xor(state, key[0])
            res += self.list2str(state)
        return res
        
        

