import logging
from .container import Container
from ..config import Config
from ..helpers import convert_list_tomap

class Pod(object):
    
    def __init__(self, spec):
        if(spec == None): 
            logging.fatal("spec attribute is not given in the pod creation")
        self._name  = spec["metadata"]["name"]
        self._namespace = spec["metadata"]["namespace"]
        self._spec = spec
    
    def forcast(self):
        
        k8s_metrics_pod = Config.CUSTOM_API.get_namespaced_custom_object(group="metrics.k8s.io", version="v1beta1", plural="pods", namespace=self._namespace, name=self._name)
        # k8s_pod = Config.CORE_API.read_namespaced_pod(name=self._name, namespace=self._namespace).to_dict()
        usage_containers = convert_list_tomap(k8s_metrics_pod["containers"])

        forecasted_values = dict()
        for container in self._spec["spec"]["containers"]: 
            container_name = container["name"]

            cont = Container(name=container_name)
            cont.set_usage(usage_containers[container_name])
            cont.set_limits(container)
            cont.set_requests(container)

            forecasted_values[container_name] = cont.forecast_cpuram()

            logging.info("=======  the CPU/Memory of the container: {} -- pod: {}".format(container_name, self._name))
            logging.info("=======  the calc request cpu : %s "%forecasted_values[container_name]["requests"]["cpu"])
            logging.info("=======  the calc limit cpu : %s "%forecasted_values[container_name]["limits"]["cpu"])
            logging.info("=======  the calc request mem : %s "%forecasted_values[container_name]["requests"]["memory"])
            logging.info("=======  the calc limit mem : %s "%forecasted_values[container_name]["limits"]["memory"])

        return forecasted_values

        