import os
import kopf
import kubernetes as kube
import logging
from . import helpers
import bitmath

# noinspection PyUnusedLocal
@kopf.on.startup()
def startup_fn(settings: kopf.OperatorSettings, **_):
    print("Operator is starting")
    # Settings of the Operator
    # settings.posting.enabled = False
    settings.posting.level = logging.WARNING
    settings.watching.connect_timeout = 1 * 60
    settings.watching.server_timeout = 10 * 60

    # Setup Kubernetes API server
    if os.environ.get('KUBERNETES_PORT', None):
        print("Using in-cluster Kubernetes config")
        kube.config.load_incluster_config()
    else:
        print("Using default Kubernetes config")
        kube.config.load_kube_config(os.environ.get('KUBECONFIG'))
    
    # Declaration of constant vars
    global KUBE_CUSTOM_API, KUBE_CORE_API
    KUBE_CUSTOM_API = kube.client.CustomObjectsApi()
    KUBE_CORE_API = kube.client.CoreV1Api()

@kopf.daemon(version="v1", plural="namespaces")
def check_daemon(stopped, name,  **_):
    while not stopped :
        if name == "default":
            try:
                k8s_metrics_pods = KUBE_CUSTOM_API.list_namespaced_custom_object(group="metrics.k8s.io", version="v1beta1", plural="pods", namespace=name)
                for pod in k8s_metrics_pods["items"]:
                    k8s_pod = KUBE_CORE_API.read_namespaced_pod(name=pod["metadata"]["name"], namespace=name).to_dict()

                    box_usage = helpers.usage_ram_cpu_pod(pod["containers"])
                    box_request = helpers.request_ram_cpu_pod(k8s_pod["spec"]["containers"])
                    box_limit = helpers.limit_ram_cpu_pod(k8s_pod["spec"]["containers"])

                    box_usage_mem_bytes = bitmath.Byte(float(box_usage["memory"]))
                    box_request_mem_bytes = bitmath.Byte(float(box_request["memory"]))
                    box_limit_mem_bytes = bitmath.Byte(float(box_limit["memory"]))

                    # Calculating the request memory for the pod
                    mem_calc_request_bytes = ( box_request_mem_bytes + box_usage_mem_bytes)/2
                    mem_calc_request_bp = mem_calc_request_bytes.best_prefix(system=bitmath.NIST)
                    mem_request_to_string = str(int(mem_calc_request_bp.prefix_value)) + mem_calc_request_bp.unit[:-1]

                    # Calculating the limit memory for the pod
                    mem_calc_limit_bytes = ( box_limit_mem_bytes + box_usage_mem_bytes)/2 + box_usage_mem_bytes/4
                    mem_calc_limit_bp = mem_calc_limit_bytes.best_prefix(system=bitmath.NIST)
                    mem_limit_to_string = str(int(mem_calc_limit_bp.prefix_value)) + mem_calc_limit_bp.unit[:-1]

                    logging.info("=======  the usage mem %s : "%str(box_usage_mem_bytes.best_prefix(system=bitmath.NIST)))
                    logging.info("=======  the request mem %s : "%str(box_request_mem_bytes.best_prefix(system=bitmath.NIST)))
                    logging.info("=======  the limit mem %s : "%str(box_limit_mem_bytes.best_prefix(system=bitmath.NIST)))
                    logging.info("=======  the calc request mem %s : "%mem_request_to_string)
                    logging.info("=======  the calc limit mem %s : "%mem_limit_to_string)

            except Exception as ex:
                logging.fatal(ex)
        stopped.wait(10)
