class Registers:
    def __init__(self):
        self.fp = [0.0] * 32 # registradores de ponto flutuante
        
        self.fp[0] = 2.0  # valor inicial para testes
        self.fp[2] = -1.0
        self.fp[4] = -1.0
        self.fp[6] = -1.0

        self.qi = [None] * 32 # tags das estações de reserva que irão escrever nos registradores
