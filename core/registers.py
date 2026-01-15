class Registers:
    def __init__(self):
        self.fp = [0.0] * 32 # registradores de ponto flutuante
        self.qi = [None] * 32 # tags das estações de reserva que irão escrever nos registradores
