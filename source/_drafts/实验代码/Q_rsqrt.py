class Float32:
    """
    sign bin : 1 bit and aways 0
    expo bins : 8 bits
    base bins : 23 bits
    """
    def __init__(self, x=1):
        assert x > 0
        self.val = x
        self.expo = 0
        self.base = None
        while not 1 <= x < 2:
            if x >= 2:
                x /= 2
                self.expo += 1
            else:
                x *= 2
                self.expo -= 1
        self.expo = "{:0>8}".format(bin(127+self.expo)[2:][-8:])
        self.base = "{:0<23}".format(self._dec2bin(x))

    def _setBits(self, bits):
        assert len(bits) == 32
        self.expo = bits[1:9]
        self.base = bits[9:]
        self.val = 2**(int(self.expo,2)-127)*(1+1/int(self.base[::-1], 2))


    def __str__(self):
        return "Float32: {} [0 {} {}]".format(self.val, self.expo, self.base)

    def _dec2bin(self, x):
        x -= int(x)
        bins = []
        while x:
            x *= 2
            bins.append('1' if x>=1.0 else '0')
            x -= int(x)
        return "".join(bins)

    def toInt32(self):
        i = Int32()
        i._setBits('0' + self.expo + self.base)
        return i

    def __mul__(self, x):
        if type(x) in (Float32, Int32):
            return Float32(self.val * x.val)
        else:
            return Float32(self.val * x)

    def __add__(self, x):
        if type(x) in (Float32, Int32):
            return Float32(self.val + x.val)
        else:
            return Float32(self.val + x)

    def __sub__(self, x):
        if type(x) in (Float32, Int32):
            return Float32(self.val - x.val)
        else:
            return Float32(self.val - x)

class Int32:
    def __init__(self, x=1):
        self.bits = "{:0>32}".format(bin(x)[2:])

    def _setBits(self, bits):
        self.bits = bits


    @property
    def val(self):
        return int(self.bits, base=2)

    @val.setter
    def val(self, _val):
        self.bits = "{:0>32}".format(bin(_val)[2:])

    def toFloat32(self):
        f = Float32()
        f._setBits(self.bits)
        return f

    def __str__(self):
        return "Int32: {}, [{} {} {}]".format(self.val,\
                                        self.bits[0],\
                                        self.bits[1:9],\
                                        self.bits[9:])
    def __rshift__(self, x):
        i = Int32()
        i._setBits('0' + self.bits[:-1])
        return i

    def __sub__(self, x):
        if type(x) in (Float32, Int32):
            return Int32(self.val - x.val)
        else:
            return Int32(self.val - x)

    def __add__(self, x):
        if type(x) in (Float32, Int32):
            return Int32(self.val + x.val)
        else:
            return Int32(self.val + x)

    def __mul__(self, x):
        if type(x) in (Float32, Int32):
            return Int32(self.val * x.val)
        else:
            return Int32(self.val * x)


def Q_rsqrt(number):
    number = Float32(number)
    x2 = number * 0.5
    y  = number
    i  = y.toInt32()                # evil floating point bit level hacking

    i  = Int32(0x5f375a86) - ( i >> 1 )               # what the fuck?
    y  = i.toFloat32()
    for i in range(3):
        y  = y * ( Float32(1.5) - ( x2 * y * y ) )   # 1st iteration
        # y  = y * ( Float32(1.5) - ( x2 * y * y ) )   # 2nd iteration, this can be removed
    return y.val

x = 0.15625
print(Q_rsqrt(x))
print(1/x**0.5)
