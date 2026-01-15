class Registers:
    def __init__(self):
        # Registradores de ponto flutuante
        self.fp = [0.0] * 32

        # Tags das estações de reserva
        self.qi = [None] * 32

        # ---- VALORES INICIAIS PARA TESTE DO LOOP ----
        self.fp[2] = 1.0    # $f2
        self.fp[3] = 2.0    # $f3
        self.fp[5] = 1.0    # $f5

        self.fp[4] = 3.0    # $f4 → contador do loop
