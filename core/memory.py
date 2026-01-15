import struct


class DataMemory:
    def __init__(self, size_bytes=512):
        self.size = size_bytes
        self.mem = [0] * size_bytes

    def check_addr(self, addr, length):
        if addr < 0 or addr + length > self.size:
            raise ValueError(f"Acesso inválido à memória: addr={addr}")

    # ---------- LOAD ----------

    def load_word(self, addr):
        self.check_addr(addr, 4)
        value = 0
        for i in range(4):
            value |= self.mem[addr + i] << (i * 8)
        return value

    def load_double(self, addr):
        self.check_addr(addr, 8)
        data = bytes(self.mem[addr:addr+8])
        return struct.unpack('<d', data)[0]

    def load_dword(self, addr):
        self.check_addr(addr, 8)
        data = bytes(self.mem[addr:addr+8])
        return struct.unpack('<q', data)[0]


    # ---------- STORE ----------

    def store_word(self, addr, value):
        self.check_addr(addr, 4)
        for i in range(4):
            self.mem[addr + i] = (value >> (i * 8)) & 0xFF


    def store_double(self, addr, value):
        self.check_addr(addr, 8)
        data = struct.pack('<d', value)  # double IEEE-754, little endian
        for i in range(8):
            self.mem[addr + i] = data[i]



    def store_dword(self, addr, value):
        self.check_addr(addr, 8)
        data = struct.pack('<q', value)
        for i in range(8):
            self.mem[addr + i] = data[i]

    # ---------- VISUALIZAÇÃO ----------

    def dump_doubles(self):
        out = []
        for addr in range(0, self.size, 8):
            out.append({
                "Addr": addr,
                "Value": self.load_double(addr)
            })
        return out
