from core.config import ADD_LATENCY, MEM_LATENCY, MEM_RESERVATION_STATIONS, MUL_LATENCY, WORD_SIZE, ADD_RESERVATION_STATIONS, MUL_RESERVATION_STATIONS
from core.instruction import Instruction
from core.memory import DataMemory
from core.registers import RegistersFloat, RegistersInt
from core.reservation_station import ReservationStation
from core.functional_unit import  AddFunctionalUnit, MemFunctionalUnit, MulFunctionalUnit

class TomasuloCPU:
    def __init__(self, program):
        self.program = program
        self.pc = 0
        self.cycle = 0

        self.regs_float = RegistersFloat()
        self.regs_int = RegistersInt()
        self.memory = DataMemory()

        self.rs_add = [ReservationStation(f"Add{i}") for i in range(ADD_RESERVATION_STATIONS)]
        self.rs_mul = [ReservationStation(f"Mul{i}") for i in range(MUL_RESERVATION_STATIONS)]        
        self.rs_load = [ReservationStation(f"Load{i}") for i in range(MEM_RESERVATION_STATIONS)]
        self.rs_store = [ReservationStation(f"Store{i}") for i in range(MEM_RESERVATION_STATIONS)]
        

        self.fu_add = AddFunctionalUnit()
        self.fu_mul = MulFunctionalUnit()
        self.fu_mem = MemFunctionalUnit()
        
        self.init_state()
        self.init_memory()

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

        # ---------------- INTEIRO  ----------------
        if instr.name == "DADDUI":
            imm = instr.imm if instr.imm < 0x8000 else instr.imm - 0x10000
            print(f"  Executando DADDUI R{instr.rt}, R{instr.rs}, {imm}")
            self.regs_int.val[instr.rt] = self.regs_int.val[instr.rs] + imm
            self.pc += WORD_SIZE
            return        

        if instr.name in ("BEQ", "BNE", "BNEZ"):
            imm = instr.imm if instr.imm < 0x8000 else instr.imm - 0x10000

            rs = self.regs_int.val[instr.rs]
            rt = self.regs_int.val[instr.rt] if instr.name != "BNEZ" else None

            take = False
            if instr.name == "BEQ":
                take = rs == rt
            elif instr.name == "BNE":
                take = rs != rt
            elif instr.name == "BNEZ":
                take = rs != 0

            next_pc = self.pc + WORD_SIZE  # PC + 4

            if take:
                next_pc = next_pc + (imm << 2)

            print(
                f"  Executando {instr.name} com rs={rs} rt={rt}, "
                f"desvio para {next_pc}"
            )

            self.pc = next_pc
            return
        
        rs_pool = None
        match instr.name:
            case "FADD.D" | "FSUB.D": rs_pool = self.rs_add
            case "FMUL.D" | "FDIV.D": rs_pool = self.rs_mul                                  
            case "LW" | "LD" | "FLD": rs_pool = self.rs_load
            case "SW" | "SD" | "FSD": rs_pool = self.rs_store  
                    
            case _:
                raise ValueError(f"Instrução desconhecida: {instr.name}")

        for rs in rs_pool:
            if not rs.busy:
                rs.busy = True
                rs.op = instr.name
                # sign extend do imediato
                imm = instr.imm if instr.imm < 0x8000 else instr.imm - 0x10000

                # -----------------------------
                # LOAD / STORE (LW, SW, FLD, FSD)
                # -----------------------------
                if instr.name in ("LW", "LD", "FLD", "SW", "SD", "FSD"):

                    # base SEMPRE inteiro
                    if self.regs_int.qi[instr.rs] is None:
                        rs.Vj = self.regs_int.val[instr.rs]
                        rs.Qj = None
                    else:
                        rs.Vj = None
                        rs.Qj = self.regs_int.qi[instr.rs]

                    rs.A = imm
                    rs.op = instr.name

                    # -------- LOAD --------
                    if instr.name in ("LW", "LD"):
                        rs.dest = instr.rt
                        rs.Vk = rs.Qk = None
                        self.regs_int.qi[instr.rt] = rs.name

                    elif instr.name == "FLD":
                        rs.dest = instr.rt
                        rs.Vk = rs.Qk = None
                        self.regs_float.qi[instr.rt] = rs.name

                    # -------- STORE --------
                    else:
                        rs.dest = None
                        if instr.name in ("SW", "SD"):
                            if self.regs_int.qi[instr.rt] is None:
                                rs.Vk = self.regs_int.val[instr.rt]
                                rs.Qk = None
                            else:
                                rs.Vk = None
                                rs.Qk = self.regs_int.qi[instr.rt]
                        else:  # FSD
                            if self.regs_float.qi[instr.rt] is None:
                                rs.Vk = self.regs_float.val[instr.rt]
                                rs.Qk = None
                            else:
                                rs.Vk = None
                                rs.Qk = self.regs_float.qi[instr.rt]

                    self.pc += WORD_SIZE
                    return
                # -----------------------------
                # FP ALU (FADD.D, FSUB.D, FMUL.D, FDIV.D)
                # -----------------------------
                rs.dest = instr.rd  # destino SEMPRE FP

                # Operando rs (FP)
                if self.regs_float.qi[instr.rs] is None:
                    rs.Vj = self.regs_float.val[instr.rs]
                    rs.Qj = None
                else:
                    rs.Vj = None
                    rs.Qj = self.regs_float.qi[instr.rs]

                # Operando rt (FP)
                if self.regs_float.qi[instr.rt] is None:
                    rs.Vk = self.regs_float.val[instr.rt]
                    rs.Qk = None
                else:
                    rs.Vk = None
                    rs.Qk = self.regs_float.qi[instr.rt]

                # Marca o destino FP como pendente
                self.regs_float.qi[instr.rd] = rs.name

                self.pc += WORD_SIZE
                return
            

        print(f"Nenhuma estação de reserva disponível para instrução em PC={self.pc}: {instr}")
        
        # ---------------- Write Result (CDB) ----------------
    def write_result(self):
        for fu in [self.fu_add, self.fu_mul, self.fu_mem]:
            if fu.rs and fu.rs.time <= 0:
                tag = fu.rs.name

                # STORE: efetiva na memória e libera a RS
                if fu.rs.op in ("SW", "SD", "FSD"):
                    self.fu_mem.process(self.memory)
                    fu.rs.clear()
                    fu.rs = None
                    return

                # gera resultado
                if fu is self.fu_mem:
                    result = fu.process(self.memory)
                else:
                    result = fu.process()

                # escreve no registrador aguardando esta tag
                for i in range(32):
                    if self.regs_int.qi[i] == tag:
                        self.regs_int.val[i] = result
                        self.regs_int.qi[i] = None

                    if self.regs_float.qi[i] == tag:
                        self.regs_float.val[i] = result
                        self.regs_float.qi[i] = None


                # broadcast (CDB): atualiza dependências
                for rs in self.rs_add + self.rs_mul + self.rs_store + self.rs_load:
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
            if fu.rs and fu.rs.time > 0:
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

    def init_state(self):
        self.regs_float.val[0] = 2.0
        self.regs_float.val[2] = -1.0
        self.regs_float.val[4] = -1.0
        self.regs_float.val[6] = -1.0
        
    def init_memory(self):
        for i in range(32):
            self.memory.store_double(i * 8, float(i + 1))

    # Vetor B
        for i in range(32):
            self.memory.store_double(256 + i * 8, 10.0)
        
