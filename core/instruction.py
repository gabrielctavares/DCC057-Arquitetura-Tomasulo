from core.config import FP_FMT_TABLE, FP_FUNCT_TABLE, OPCODE_TABLE


class Instruction:
    def __init__(self, raw):
        self.raw = raw

        self.opcode = (raw >> 26) & 0b111111
        self.imm    = raw & 0xFFFF
        self.funct  = raw & 0b111111

        base = OPCODE_TABLE.get(self.opcode, "UNKNOWN")

        if base == "COP1":
            self.fmt = (raw >> 21) & 0b11111
            self.ft  = (raw >> 16) & 0b11111
            self.fs  = (raw >> 11) & 0b11111
            self.fd  = (raw >> 6)  & 0b11111

            self.rs = self.fs
            self.rt = self.ft
            self.rd = self.fd

        else:
            self.rs    = (raw >> 21) & 0b11111
            self.rt    = (raw >> 16) & 0b11111
            self.rd    = (raw >> 11) & 0b11111
            self.shamt = (raw >> 6)  & 0b11111

        self.name = self.__get_instruction_name__()

    def __str__(self):
        return (
            f"name={self.name} "
            f"op={self.opcode} "
            f"rs={self.rs} rt={self.rt} rd={self.rd}"
        )

    def __get_instruction_name__(self) -> str:
        base = OPCODE_TABLE.get(self.opcode, "UNKNOWN")

        if base == "COP1":
            fmt_name   = FP_FMT_TABLE.get(self.fmt)
            funct_name = FP_FUNCT_TABLE.get(self.funct)

            if fmt_name and funct_name:
                return f"{funct_name}.{fmt_name}"
            return "UNKNOWN_FP"

        if base == "BNE" and self.rt == 0:
            return "BNEZ"

        return base
