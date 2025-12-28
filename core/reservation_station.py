class ReservationStation:
    def __init__(self, name):
        self.name = name
        self.busy = False
        self.op = None # operação
        self.Vj = None # valor do operando j
        self.Vk = None # valor do operando k
        self.Qj = None # tag da estação que produzirá o operando j
        self.Qk = None # tag da estação que produzirá o operando k
        self.dest = None # registrador destino
        self.time = 0 # tempo restante para completar a operação
        self.A = None # endereço efetivo para operações de memória

    def ready(self):
        return self.busy and self.Qj is None and self.Qk is None # pronta para execução

    def clear(self):
        self.__init__(self.name)
