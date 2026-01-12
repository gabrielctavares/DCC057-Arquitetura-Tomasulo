class DataMemory:
    def __init__(self, size_bytes=512):
        self.size = size_bytes
        self.mem = [0] * size_bytes

        # --- TESTE: padrão visível ---
        for i in range(8):
            self.mem[i] = i + 1


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
        value = 0
        for i in range(8):
            value |= self.mem[addr + i] << (i * 8)
        return value

    # ---------- STORE ----------

    def store_word(self, addr, value):
        self.check_addr(addr, 4)
        for i in range(4):
            self.mem[addr + i] = (value >> (i * 8)) & 0xFF

    def store_double(self, addr, value):
        self.check_addr(addr, 8)
        for i in range(8):
            self.mem[addr + i] = (value >> (i * 8)) & 0xFF

    # ---------- VISUALIZAÇÃO ----------

    def dump_words(self):
        """Retorna memória como lista de palavras (4 bytes)"""
        words = []
        for addr in range(0, self.size, 4):
            words.append({
                "Addr": addr,
                "Value": self.load_word(addr)
            })
        return words
