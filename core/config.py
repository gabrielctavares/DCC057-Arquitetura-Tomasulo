
WORD_SIZE = 4
ADD_RESERVATION_STATIONS = 3
MUL_RESERVATION_STATIONS = 2
MEM_RESERVATION_STATIONS = 2

ADD_LATENCY = 3
MUL_LATENCY = 5
MEM_LATENCY = 2


OPCODE_TABLE = {
    35: "LW",
    43: "SW",
    49: "FLD",
    57: "FSD",
    4:  "BEQ",
    5:  "BNE",
    17: "COP1",   # Floating Point
}
FP_FUNCT_TABLE = {
    0: "FADD",
    1: "FSUB",
    2: "FMUL",
    3: "FDIV",
}
FP_FMT_TABLE = {
    16: "S",
    17: "D"            
}

