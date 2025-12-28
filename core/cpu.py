from core.config import ADD_LATENCY, MEM_LATENCY, MEM_RESERVATION_STATIONS, MUL_LATENCY, WORD_SIZE, ADD_RESERVATION_STATIONS, MUL_RESERVATION_STATIONS
from core.instruction import Instruction
from core.memory import DataMemory
from core.registers import Registers
from core.reservation_station import ReservationStation
from core.functional_unit import  AddFunctionalUnit, MemFunctionalUnit, MulFunctionalUnit

class TomasuloCPU:
    def __init__(self, program):
        self.program = program
        self.pc = 0
        self.cycle = 0

        self.regs = Registers()
        self.memory = DataMemory()

        self.rs_add = [ReservationStation(f"Add{i}") for i in range(ADD_RESERVATION_STATIONS)]
        self.rs_mul = [ReservationStation(f"Mul{i}") for i in range(MUL_RESERVATION_STATIONS)]        
        self.rs_load = [ReservationStation(f"Load{i}") for i in range(MEM_RESERVATION_STATIONS)]
        self.rs_store = [ReservationStation(f"Store{i}") for i in range(MEM_RESERVATION_STATIONS)]
        

        self.fu_add = AddFunctionalUnit()
        self.fu_mul = MulFunctionalUnit()
        self.fu_mem = MemFunctionalUnit()

    def fetch(self):
        idx = self.pc // WORD_SIZE
        if idx < len(self.program):
            return Instruction(self.program[idx])
        return None

    # ---------------- Issue ----------------
    def issue(self):
        instr = self.fetch()
        if instr is None:
            return

        print(f"Issuing instruction at PC={self.pc}: {instr}")

        rs_pool = None
        match instr.name:
            case "FADD.D" | "FSUB.D": rs_pool = self.rs_add
            case "FMUL.D" | "FDIV.D": rs_pool = self.rs_mul                                  
            case "LW": rs_pool = self.rs_load
            case "SW": rs_pool = self.rs_store
            case "FLD": pass
            case "FSD": pass
            case "BEQ" | "BNEZ" | "BNE": 
                self.pc += WORD_SIZE
                return
            case _:
                raise ValueError(f"Instrução desconhecida: {instr.name}")

        for rs in rs_pool:
            if not rs.busy:
                rs.busy = True
                rs.op = instr.name
                rs.dest = instr.rd

                rs.Vj = self.regs.fp[instr.rs] if self.regs.qi[instr.rs] is None else None
                rs.Qj = self.regs.qi[instr.rs]

                rs.Vk = self.regs.fp[instr.rt] if self.regs.qi[instr.rt] is None else None
                rs.Qk = self.regs.qi[instr.rt]

                self.regs.qi[instr.rd] = rs.name
                self.pc += WORD_SIZE
                return
        print(f"Nenhuma estação de reserva disponível para instrução em PC={self.pc}: {instr}")
        
        
        # ---------------- Write Result (CDB) ----------------
    def write_result(self):
        for fu in [self.fu_add, self.fu_mul, self.fu_mem]:
            
            if fu.rs and fu.rs.time == 0:
                tag = fu.rs.name
                
                if fu.rs.op in ("SW", "FSD"):
                    fu.process(fu.rs, self.memory)
                    fu.rs.clear()
                    fu.rs = None
                    return
                
                result = fu.process(fu.rs)
                
                for i in range(32):
                    if self.regs.qi[i] == tag:
                        self.regs.fp[i] = result
                        self.regs.qi[i] = None

                for rs in self.rs_add + self.rs_mul:
                    if rs.Qj == tag:
                        rs.Vj = result
                        rs.Qj = None
                    if rs.Qk == tag:
                        rs.Vk = result
                        rs.Qk = None

                fu.rs.clear()
                fu.rs = None
                return

    # ---------------- Execute ----------------
    def execute(self):
        for fu, pool in [
            (self.fu_add, self.rs_add),
            (self.fu_mul, self.rs_mul),
            (self.fu_mem, self.rs_load + self.rs_store)
        ]:
            if fu.rs:
                fu.rs.time -= 1
            else:
                for rs in pool:
                    if rs.ready():
                        fu.rs = rs
                        rs.time = fu.latency
                        break
  

    def step(self):
        self.cycle += 1
        self.write_result()
        self.execute()
        self.issue()

    def finished(self):
        return self.pc >= len(self.program) * WORD_SIZE


