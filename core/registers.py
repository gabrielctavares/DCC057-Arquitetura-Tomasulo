class RegistersFloat:
    def __init__(self):
        self.val = [0.0] * 32 # registradores de ponto flutuante
        self.qi = [None] * 32 # tags das estações de reserva que irão escrever nos registradores


class RegistersInt:
    def __init__(self):
        self.val = [0] * 32 # registradores inteiros
        self.qi = [None] * 32 # tags das estações de reserva que irão escrever nos registradores