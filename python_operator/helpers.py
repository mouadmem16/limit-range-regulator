from kubernetes import utils
import logging

def usage_ram_cpu_pod(containers):
    return calculate_ram_cpu_pod(containers, "usage")

def request_ram_cpu_pod(containers):
    return calculate_ram_cpu_pod(containers, "requests")

def limit_ram_cpu_pod(containers):
    return calculate_ram_cpu_pod(containers, "limits")

def calculate_ram_cpu_pod(containers, query):
    """
    input values: [containers]
    output values: { 'memory': Decimal,'cpu': Decimal}
    """
    container_usage_result = {  'memory': 0,   'cpu': 0  }
    for container in containers:
        container_usage = None
        if query == "usage" and query in container:
            container_usage = container["usage"]  # For the metrics api
        elif query in container["resources"]:
            container_usage = container["resources"][query]
        else:
            logging.fatal(f"the {query} key doesn't exist")

        cpu_value = utils.parse_quantity(container_usage["cpu"])
        ram_value = utils.parse_quantity(container_usage["memory"])

        container_usage_result["memory"] += ram_value
        container_usage_result["cpu"] += cpu_value

        return container_usage_result
