from .cpu_memory_unit import CpuMemoryUnit
from kubernetes.utils import parse_quantity
from si_prefix import si_parse, si_format
from bitmath import Byte, NIST

class Container(object):

    def __init__(self, cpu=0.0, memory=0.0, spec=None):
        self._spec               = spec
        self._name               = self._spec["name"]
        self._usage              = CpuMemoryUnit(cpu, memory)
        self._requests           = CpuMemoryUnit(cpu, memory)
        self._limits             = CpuMemoryUnit(cpu, memory)
        self.set_limits(self._spec)
        self.set_requests(self._spec)
        self._forecast_requests  = {"cpu": self._requests.get_cpu(), "memory": self._requests.get_memory()}
        self._forecast_limits    = {"cpu": self._limits.get_cpu(), "memory": self._limits.get_memory()}

    def set_usage(self, container):
        container_memory_cpu = container["usage"]
        self._usage = self._calculate_memory_cpu_container(container_memory_cpu)

    def set_limits(self, container):
        container_memory_cpu = container["resources"]["limits"]
        self._limits = self._calculate_memory_cpu_container(container_memory_cpu)

    def set_requests(self, container):
        container_memory_cpu = container["resources"]["requests"]
        self._requests = self._calculate_memory_cpu_container(container_memory_cpu)

    def set_name(self, name):
        self._name = name

    def get_usage(self):
        return self._usage 
    
    def get_limits(self):
        return self._limitss 
    
    def get_requests(self):
        return self._requestss 

    def get_name(self):
        return self._name 

    def get_forecast_requests(self):
        return self._forecast_requests 

    def get_forecast_limits(self):
        return self._forecast_limits 

    def _calculate_memory_cpu_container(self, container):
        """
        input values: container
        output values: CpuMemoryUnit
        """
        container_memory_cpu: CpuMemoryUnit = None

        cpu_value, memory_value = (0, 0)
        if container != None:
            if "cpu" in container:
                cpu_value = si_parse(container["cpu"])
            if "memory" in container:
                memory_value = parse_quantity(container["memory"])
            
        container_memory_cpu = CpuMemoryUnit(cpu=cpu_value, memory=memory_value)

        return container_memory_cpu
    
    def _regulazing_cpu_value(self, cpu):
        si_units = {'y': 10**(-24), 'z': 10**(-21), 'a': 10**(-18), 'f': 10**(-15), 'p': 10**(-12), 'µ': 10**(-6), 'k': 10**3, 'M': 10**6, 'G': 10**9, 'T': 10**12, 'P': 10**15, 'E': 10**18, 'Z': 10**21, 'Y': 10**24}
        if cpu[-1] in si_units.keys():
            result = '%.2f' %(float(cpu[:-1]) * si_units[cpu[-1]] == 0)
            if float(result) != 0:
                return result
        if cpu[-1] in "mn1234567890":
            return cpu
        return "1m"

    def forecast_cpumemory(self):
        # Calculating the memory
        box_usage_mem_bytes = Byte(float(self._usage.get_memory()))
        box_request_mem_bytes = Byte(float(self._requests.get_memory()))
        box_limit_mem_bytes = Byte(float(self._limits.get_memory()))

        mem_calc_request_bytes = ( box_request_mem_bytes + box_usage_mem_bytes)/2
        if(mem_calc_request_bytes < box_usage_mem_bytes):
            mem_calc_request_bytes = box_usage_mem_bytes
        mem_calc_request_bp = mem_calc_request_bytes.best_prefix(system=NIST)
        mem_request_to_string = str(int(mem_calc_request_bp.prefix_value)) + mem_calc_request_bp.unit[:-1]

        mem_calc_limit_bytes = ( box_limit_mem_bytes + box_usage_mem_bytes)/2 + box_usage_mem_bytes/4
        if(mem_calc_limit_bytes <= box_usage_mem_bytes):
            mem_calc_limit_bytes = 1.5 * box_usage_mem_bytes
        if(mem_calc_limit_bytes <= mem_calc_request_bytes):
            mem_calc_limit_bytes = 1.5 * mem_calc_request_bytes
        mem_calc_limit_bp = mem_calc_limit_bytes.best_prefix(system=NIST)
        mem_limit_to_string = str(int(mem_calc_limit_bp.prefix_value)) + mem_calc_limit_bp.unit[:-1]

        # Calculating the cpu
        cpu_calc_request = ( self._requests.get_cpu() + self._usage.get_cpu())/2
        if(cpu_calc_request < self._usage.get_cpu()):
            cpu_calc_request = self._usage.get_cpu()
        cpu_request_to_string = si_format(cpu_calc_request).replace(' ', '')
        cpu_request_to_string = self._regulazing_cpu_value(cpu_request_to_string)

        cpu_calc_limit = ( self._limits.get_cpu() + self._usage.get_cpu())/2 + self._usage.get_cpu()/4
        if(cpu_calc_limit <= self._usage.get_cpu()):
            cpu_calc_limit = 1.5 * self._usage.get_cpu()
        if(cpu_calc_limit <= cpu_calc_request):
            cpu_calc_limit = 1.5 * cpu_calc_request
        cpu_limit_to_string = si_format(cpu_calc_limit).replace(' ', '')
        cpu_limit_to_string = self._regulazing_cpu_value(cpu_limit_to_string)

        self._forecast_requests  = {"cpu": cpu_request_to_string, "memory": mem_request_to_string}
        self._forecast_limits    = {"cpu": cpu_limit_to_string, "memory": mem_limit_to_string}

    def __repr__(self):
        return "{ \"requests\": { \"cpu\": %s, \"memory\":%s } , \"limits\": { \"cpu\": %s, \"memory\":%s } }"%(
            self._forecast_requests["cpu"], self._forecast_requests["memory"],
            self._forecast_limits["cpu"], self._forecast_limits["memory"]
        )
    