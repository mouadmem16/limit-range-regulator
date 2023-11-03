class CpuRamUnit(object):
    
    def __init__(self, cpu=0, ram=0):
        self._cpu = cpu
        self._ram = ram

    def get_memory(self):
        return self._ram
    
    def get_cpu(self):
        return self._cpu
    
    def set_memory(self, ram):
        self._ram = ram
    
    def set_cpu(self, cpu):
        self._cpu = cpu
    
