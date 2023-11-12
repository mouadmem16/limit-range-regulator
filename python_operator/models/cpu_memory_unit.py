class CpuMemoryUnit(object):
    
    def __init__(self, cpu=0, memory=0):
        self._cpu = cpu
        self._memory = memory

    def get_memory(self):
        return self._memory
    
    def get_cpu(self):
        return self._cpu
    
    def set_memory(self, memory):
        self._memory = memory
    
    def set_cpu(self, cpu):
        self._cpu = cpu
    
