from kubernetes import utils
from .models.container_usage import ContainerUsage
import logging 
from si_prefix import si_parse
import bitmath
import si_prefix

def usage_ram_cpu_container(container):
    container_ram_cpu = container["usage"]
    return calculate_ram_cpu_container(container_ram_cpu)

def request_ram_cpu_container(container):
    container_ram_cpu = container["resources"]["requests"]
    return calculate_ram_cpu_container(container_ram_cpu)

def limit_ram_cpu_container(container):
    container_ram_cpu = container["resources"]["limits"]
    return calculate_ram_cpu_container(container_ram_cpu)

def calculate_ram_cpu_container(container):
    """
    input values: container
    output values: ContainerUsage
    """
    container_ram_cpu: ContainerUsage = None

    cpu_value, ram_value = (0, 0)
    if container != None:
        if "cpu" in container:
            cpu_value = si_parse(container["cpu"])
        if "memory" in container:
            ram_value = utils.parse_quantity(container["memory"])
        
    container_ram_cpu = ContainerUsage(cpu=cpu_value, memory=ram_value)

    return container_ram_cpu

def convert_list_tomap(containers):
    cont_map = dict()
    for cont in containers:
        cont_map[cont["name"]] = cont
    return cont_map

def containers_request_limit(pod, KUBE_CORE_API):
    pod_name  = pod["metadata"]["name"]
    namespace = pod["metadata"]["namespace"]
    
    k8s_pod = KUBE_CORE_API.read_namespaced_pod(name=pod_name, namespace=namespace).to_dict()
    usage_containers = convert_list_tomap(pod["containers"])
    containers_request_limit = dict()

    for container in k8s_pod["spec"]["containers"]: 
        container_name = container["name"]

        box_usage = usage_ram_cpu_container(usage_containers[container_name])
        box_request = request_ram_cpu_container(container)
        box_limit = limit_ram_cpu_container(container)

        box_usage_mem_bytes = bitmath.Byte(float(box_usage.get_memory()))
        box_request_mem_bytes = bitmath.Byte(float(box_request.get_memory()))
        box_limit_mem_bytes = bitmath.Byte(float(box_limit.get_memory()))

        mem_calc_request_bytes = ( box_request_mem_bytes + box_usage_mem_bytes)/2
        mem_calc_request_bp = mem_calc_request_bytes.best_prefix(system=bitmath.NIST)
        mem_request_to_string = str(int(mem_calc_request_bp.prefix_value)) + mem_calc_request_bp.unit[:-1]

        mem_calc_limit_bytes = ( box_limit_mem_bytes + box_usage_mem_bytes)/2 + box_usage_mem_bytes/4
        mem_calc_limit_bp = mem_calc_limit_bytes.best_prefix(system=bitmath.NIST)
        mem_limit_to_string = str(int(mem_calc_limit_bp.prefix_value)) + mem_calc_limit_bp.unit[:-1]

        # Calculating the request cpu for the pods
        # Calculating the limit cpu for the pods
        box_usage_cpu = box_usage.get_cpu()
        box_request_cpu = box_request.get_cpu()
        box_limit_cpu = box_limit.get_cpu()

        cpu_calc_request = ( box_request_cpu + box_usage_cpu)/2
        cpu_request_to_string = si_prefix.si_format(cpu_calc_request).replace(' ', '')

        cpu_calc_limit = ( box_limit_cpu + box_usage_cpu)/2 + box_usage_cpu/4
        cpu_limit_to_string = si_prefix.si_format(cpu_calc_limit).replace(' ', '')

        logging.info("=======  the CPU/Memory of the container: {} -- pod: {}".format(container_name, pod_name))
        # logging.info("=======  the usage cpu %s : "%str(box_usage_cpu))
        # logging.info("=======  the request cpu %s : "%str(box_request_cpu))
        # logging.info("=======  the limit cpu %s : "%str(box_limit_cpu))
        logging.info("=======  the calc request cpu : %s "%cpu_request_to_string)
        logging.info("=======  the calc limit cpu : %s "%cpu_limit_to_string)

        # logging.info("=======  the usage mem %s : "%str(box_usage_mem_bytes.best_prefix(system=bitmath.NIST)))
        # logging.info("=======  the request mem %s : "%str(box_request_mem_bytes.best_prefix(system=bitmath.NIST)))
        # logging.info("=======  the limit mem %s : "%str(box_limit_mem_bytes.best_prefix(system=bitmath.NIST)))
        logging.info("=======  the calc request mem : %s "%mem_request_to_string)
        logging.info("=======  the calc limit mem : %s "%mem_limit_to_string)

        containers_request_limit[container_name] = {"requests": {"cpu": cpu_request_to_string, "memory": mem_request_to_string}, "limits": {"cpu": cpu_limit_to_string, "memory": mem_limit_to_string}}
        
    return containers_request_limit