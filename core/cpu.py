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

        self.branch_pending = False
        self.branch_instr = None


    def fetch(self):
        idx = self.pc // WORD_SIZE
        if idx < len(self.program):
            return Instruction(self.program[idx])
        return None

  
    def issue(self):
        busy_rs = any(rs.busy for rs in self.rs_add + self.rs_mul + self.rs_load + self.rs_store)
        if busy_rs or self.branch_pending:
            return

        instr = self.fetch()
        if instr is None:
            return

        print(f"Issuing instruction at PC={self.pc}: {instr}")

        rs_pool = None
        match instr.name:
            case "FADD.D" | "FSUB.D":
                rs_pool = self.rs_add
            case "FMUL.D" | "FDIV.D":
                rs_pool = self.rs_mul
            case "LW" | "FLD":
                rs_pool = self.rs_load
            case "SW" | "FSD":
                rs_pool = self.rs_store
            case "BEQ" | "BNE" | "BNEZ":
                self.branch_pending = True
                self.branch_instr = instr
                return

            case _:
                raise ValueError(f"Instrução desconhecida: {instr.name}")

        for rs in rs_pool:
            if not rs.busy:
                rs.busy = True
                rs.op = instr.name

                imm = instr.imm if instr.imm < 0x8000 else instr.imm - 0x10000

                # -------- LOAD / STORE --------
                if instr.name in ("LW", "SW", "FLD", "FSD"):
                    rs.Vj = self.regs.fp[instr.rs] if self.regs.qi[instr.rs] is None else None
                    rs.Qj = self.regs.qi[instr.rs]
                    rs.A = imm

                    if instr.name in ("LW", "FLD"):
                        rs.dest = instr.rt
                        rs.Vk = rs.Qk = None
                        self.regs.qi[instr.rt] = rs.name
                    else:
                        rs.dest = None
                        rs.Vk = self.regs.fp[instr.rt] if self.regs.qi[instr.rt] is None else None
                        rs.Qk = self.regs.qi[instr.rt]

                    self.pc += WORD_SIZE
                    return

                # -------- FP ALU --------
                rs.dest = instr.rd

                rs.Vj = self.regs.fp[instr.rs] if self.regs.qi[instr.rs] is None else None
                rs.Qj = self.regs.qi[instr.rs]

                rs.Vk = self.regs.fp[instr.rt] if self.regs.qi[instr.rt] is None else None
                rs.Qk = self.regs.qi[instr.rt]

                self.regs.qi[instr.rd] = rs.name
                self.pc += WORD_SIZE
                return

        print(f"Nenhuma RS disponível para PC={self.pc}: {instr}")


    def resolve_branch(self):
        instr = self.branch_instr

        imm = instr.imm if instr.imm < 0x8000 else instr.imm - 0x10000

        rs_val = self.regs.fp[instr.rs]
        rt_val = self.regs.fp[instr.rt] if instr.name != "BNEZ" else 0

        take = False
        if instr.name == "BEQ":
            take = (rs_val == rt_val)
        elif instr.name == "BNE":
            take = (rs_val != rt_val)
        elif instr.name == "BNEZ":
            take = (rs_val != 0)

        # PC base = PC + 4
        next_pc = self.pc + WORD_SIZE

        # Branch tomado → deslocamento relativo
        if take:
            next_pc += imm << 2

        self.pc = next_pc

        self.branch_pending = False
        self.branch_instr = None


    # ---------------- Write Result ----------------
    def write_result(self):
        for fu in [self.fu_add, self.fu_mul, self.fu_mem]:
            if fu.rs and fu.rs.time == 0:
                tag = fu.rs.name

                if fu.rs.op in ("SW", "FSD"):
                    self.fu_mem.process(self.memory)
                    fu.rs.clear()
                    fu.rs = None
                    return

                result = fu.process(self.memory) if fu is self.fu_mem else fu.process()

                for i in range(32):
                    if self.regs.qi[i] == tag:
                        self.regs.fp[i] = result
                        self.regs.qi[i] = None

                for rs in self.rs_add + self.rs_mul + self.rs_store:
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
    def loop_finished(self):
        if self.fu_add.rs or self.fu_mul.rs or self.fu_mem.rs:
            return False

        for rs in self.rs_add + self.rs_mul + self.rs_load + self.rs_store:
            if rs.busy:
                return False

        return True

    
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

        if self.branch_pending:
            if self.loop_finished():
                self.resolve_branch()
        else:
            self.issue()


    def finished(self):
        busy_rs = any(
            rs.busy for rs in
            self.rs_add + self.rs_mul + self.rs_load + self.rs_store
        )
        return (
            self.pc >= len(self.program) * WORD_SIZE
            and not busy_rs
            and not self.branch_pending
        )
