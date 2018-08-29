import numpy as np
import constant

class kec:
    def __init__(self, r=32):
        self._round = r

    def rot(self, d, s):
        '''
        pre-condition:
            len(bin(d)) == 8
        post-condition:
            s=0: return d
            s>0: right rotation
            s<0: left rotation
        '''
        if s==0:
            return d
        nleft = 8 - s
        nright = s
        if s<0:
          nleft = nleft - 8
          nright = (8+s)

        left = d>>nright
        right = d ^ (left<<nright)
        return (right << nleft) + left
    
    def theta(self, state):
        assert(state.shape==(4,4))
        row, col = state.shape
        for x in range(row):
            t, r = (x+1)%4, (x-1)%4
            Tx = state[t, 0] ^ state[t, 1] ^ state[t, 2] ^ state[t, 3]
            Rx = self.rot(state[r, 0], 1) ^ self.rot(state[r, 1], 1) ^ self.rot(state[r, 2], 1) ^ self.rot(state[r, 3], 1)
            for y in range(col):
                state[x, y] = state[x, y] ^ Tx ^ Rx

    def rho(self, state, sym):
        '''
        sym=0: self.rot: no rotation
        sym=-1: self.rot: left rotation
        sym=1: self.rot: right rotation
        '''
        shift = np.mat(constant.RHO)
        row, col = shift.shape

        for i in range(row):
            for j in range(col):
                state[i, j] = self.rot(state[i, j], sym * shift[i, j])

    def pi(self, state, ope):
        '''
        pre-condition:
            when encode, ope=constant.PI
            when decode, ope=constant.PIINV
        '''
        #place = (constant.PI)
        place = ope
        row, col = 4, 4

        tmp = np.empty((row, col))
        for i in range(row):
            for j in range(col):
                t = place[i][3-j]   #coordination transform
                tmp[t[0]][t[1]] = state[i, j]
        for i in range(row):
            for j in range(col):
                state[i, j] = tmp[i][j]

    def chi(self, state, S):
        '''
        pre-condition:
            when encode, S=constant.SBox
            when decode, S=constant.SBoxInv
        '''
        #c = constant.CHI
        #S = constant.SBox
        assert(state.shape==(4,4))

        row, col = state.shape
        for x in range(row):
            tmp = [0, 0, 0, 0]
            for i in range(7, -1, -1):
                t = 0
                for y in range(col):
                    t = (t<<1) + ((state[y,x] >> i) & 1)
                    #(state[x, y] & c[i])
                    #print(t)
                #print(t)
                t = S[t]
                #print(t)
                for j in range(4):
                    tmp[j] = (tmp[j]<<1) + ((t >> (3-j)) & 1)
                    #c[j+4])
            for y in range(col):
                state[y, x] = tmp[y]
                
    def iota(self, state, r):
        assert(state.shape == (4, 4))
        rc = constant.RC
        state[0, 3] = state[0, 3] ^ rc[r%63]
        
    def encode(self, message):
        
        assert(len(message) == 16)

        print("in encode")

        if type(message) == str:
            message = bytes([ord(c) for c in message])
        if not type(message) is bytes:
            raise Exception("the message {} must be str or bytes".format(message))
        
        state = np.mat(np.zeros((4,4), dtype="int32"))
        for l, m in enumerate(message):
            state[l//4, l%4] = m
            
        for r in range(self._round):
            #print("{}th edcode pi state\n {}".format(r, state))
            self.theta(state)
            #print("{}th edcode rho state\n {}".format(r, state))
            self.rho(state, -1)
            #print("{}th edcode pi state\n {}".format(r, state))
            self.pi(state, constant.PI)
            #print("{}th edcode chi state\n {}".format(r, state))
            self.chi(state, constant.SBox)
            #print("{}th edcode iota state\n {}".format(r, state))
            self.iota(state, r)
            #print("{}th edcode iota state\n {}".format(r, state))
            
        print("final state \n {}\n".format(state))
            
        en = bytes()
        for x in range(4):
            en += bytes([state[x, y] for y in range(4)])
            
        print("the encode bytes : {}\n".format(en))
        '''
        s = ""
        for b in en:
            s += chr(b)
        print("the encode string: {}".format(s))
        '''
        return en

    def decode(self, message):
        assert(len(message)==16)
        
        print("in decode")

        if type(message)==str:
            message = bytes([ord(c) for c in message])
        if not type(message) is bytes:
            raise Exception("the message {} must be str or bytes".format(message))

        state = np.mat(np.zeros((4,4), dtype="int32"))
        for l, m in enumerate(message):
            state[l//4, l%4] = m

        for r in range(self._round-1, -1, -1):
            self.iota(state, r)
            self.chi(state, constant.SBoxInv)
            self.pi(state, constant.PIINV)
            self.rho(state, 1)
            self.theta(state)

        print("final state \n {}\n".format(state))

        de = bytes()
        for x in range(4):
            de += bytes([state[x, y] for y in range(4)])

        print("the decode bytes : {}\n".format(de))
        '''
        s = ""
        for b in de:
            s += chr(b)
        print("the decode string: {}\n".format(s))
        '''
        return de


if __name__ == "__main__":
    kec = kec()
    message = "abcd" + "bcda" + "cdab" + "dabc"
    print("the message\n{}\n".format(message))

    en = kec.encode(message)
    kec.decode(en)
    



 
