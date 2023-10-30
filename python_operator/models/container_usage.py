class ContainerUsage(object):
    def __init__(self, container_name=None, cpu=0.0, memory=0.0):
        self._cpu = cpu
        self._memory = memory
        self._container_name = container_name

    def set_cpu(self, cpu):
        self._cpu = cpu

    def set_memory(self, memory):
        self._memory = memory

    def set_container_name(self, container_name):
        self._container_name = container_name

    def set_cpu(self):
        return self._cpu 

    def set_memory(self):
        return self._memory

    def set_container_name(self):
        return self._container_name 
