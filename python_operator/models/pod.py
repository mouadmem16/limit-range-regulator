import logging
from .container import Container
from ..config import Config
from ..helpers import convert_list_tomap
from kubernetes.client.exceptions import ApiException

class Pod(object):
    
    def __init__(self, spec):
        if(spec == None): 
            logging.fatal("spec attribute is not given in the pod creation")
        self._name  = spec["metadata"]["name"]
        self._namespace = spec["metadata"]["namespace"]
        self._spec = spec
        self._forecasted_values = list()
    
    def get_forecasted_values(self):
        if(len(self._forecasted_values) == 0):
            self.forcast()
        return self._forecasted_values

    def get_name(self):
        return self._name

    def get_namespace(self):
        return self._namespace

    def forcast(self):
        usage_containers = dict()
        is_pod_metrics = True
        try:
            k8s_metrics_pod = Config.CUSTOM_API.get_namespaced_custom_object(group="metrics.k8s.io", version="v1beta1", plural="pods", namespace=self._namespace, name=self._name)
            usage_containers = convert_list_tomap(k8s_metrics_pod["containers"])            
        except ApiException:
            logging.fatal(f"The pod {self._name} doesn't have CPU/RAM metrics")
            is_pod_metrics = False

        for container in self._spec["spec"]["containers"]:
            cont = Container(spec=container)

            if is_pod_metrics:
                cont.set_usage(usage_containers[cont.get_name()])
                cont.forecast_cpumemory()

            self._forecasted_values.append(cont)
            
            logging.info("=======  the CPU/Memory of the container: {} -- pod: {}".format(cont.get_name(), self._name))
            logging.info("=======  the calc request cpu : %s "%cont.get_forecast_requests()["cpu"])
            logging.info("=======  the calc limit cpu : %s "%cont.get_forecast_limits()["cpu"])
            logging.info("=======  the calc request mem : %s "%cont.get_forecast_requests()["memory"])
            logging.info("=======  the calc limit mem : %s "%cont.get_forecast_limits()["memory"])
    

        