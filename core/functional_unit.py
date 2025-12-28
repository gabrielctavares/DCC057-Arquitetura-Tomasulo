from core.reservation_station import ReservationStation


class FunctionalUnit:
    def __init__(self, name, latency):
        self.name = name 
        self.latency = latency 
        self.rs: ReservationStation = None
    
    def process(self):
        pass


class AddFunctionalUnit(FunctionalUnit):
    def __init__(self):
        super().__init__("FPAdd", 3)

    def process(self):
        if self.rs.op == "FADD":
            return self.rs.Vj + self.rs.Vk
        elif self.rs.op == "FSUB":
            return self.rs.Vj - self.rs.Vk
        else:
            raise ValueError(f"Operação desconhecida na unidade de adição: {self.rs.op}")
        
class MulFunctionalUnit(FunctionalUnit):
    def __init__(self):
        super().__init__("FPMul", 5)

    def process(self):
        if self.rs.op == "FMUL":
            return self.rs.Vj * self.rs.Vk
        elif self.rs.op == "FDIV":
            return self.rs.Vj / self.rs.Vk
        else:
            raise ValueError(f"Operação desconhecida na unidade de multiplicação: {self.rs.op}")
        
class MemFunctionalUnit(FunctionalUnit):
    def __init__(self):
        super().__init__("FPMem", 2)
    def process(self):
        pass