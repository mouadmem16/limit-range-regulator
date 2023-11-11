from .models.container import Container
import logging 
from .config import Config

def convert_list_tomap(containers):
    cont_map = dict()
    for cont in containers:
        cont_map[cont["name"]] = cont
    return cont_map

def containers_request_limit(pod):
    pod_name  = pod["metadata"]["name"]
    namespace = pod["metadata"]["namespace"]

    k8s_pod = Config.CORE_API.read_namespaced_pod(name=pod_name, namespace=namespace).to_dict()
    usage_containers = convert_list_tomap(pod["containers"])

    for container in k8s_pod["spec"]["containers"]: 
        container_name = container["name"]

        cont = Container(name=container_name)
        cont.set_usage(usage_containers[container_name])
        cont.set_limits(container)
        cont.set_requests(container)

        forecasted_values = cont.forecast_cpuram()

        logging.info("=======  the CPU/Memory of the container: {} -- pod: {}".format(container_name, pod_name))
        logging.info("=======  the calc request cpu : %s "%forecasted_values["requests"]["cpu"])
        logging.info("=======  the calc limit cpu : %s "%forecasted_values["limits"]["cpu"])
        logging.info("=======  the calc request mem : %s "%forecasted_values["requests"]["memory"])
        logging.info("=======  the calc limit mem : %s "%forecasted_values["limits"]["memory"])

        return forecasted_values
