import os
import kopf
import kubernetes as kube
import logging
from . import helpers

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
        if name == "kube-system":
            # try:
                k8s_metrics_pods = KUBE_CUSTOM_API.list_namespaced_custom_object(group="metrics.k8s.io", version="v1beta1", plural="pods", namespace=name)
                for pod in k8s_metrics_pods["items"]:
                    containers_req_lim = helpers.containers_request_limit(pod, KUBE_CORE_API)

                    logging.info(containers_req_lim)
            # except Exception as ex:
            #     logging.fatal(ex)
        stopped.wait(10)
