import kopf
import logging
from .helpers import containers_request_limit
from .config import Config

# noinspection PyUnusedLocal
@kopf.on.startup()
def startup_fn(settings: kopf.OperatorSettings, **_):
    logging.info("Operator is starting")
    # Settings of the Operator
    # settings.posting.enabled = False
    settings.posting.level = logging.WARNING
    settings.watching.connect_timeout = 1 * 60
    settings.watching.server_timeout = 10 * 60
    Config()

@kopf.daemon(version="v1", plural="namespaces")
def check_daemon(stopped, name,  **_):
    Config.define_API()
    while not stopped :
        if name in Config.namespaces:
            # try:
                k8s_metrics_pods = Config.CUSTOM_API.list_namespaced_custom_object(group="metrics.k8s.io", version="v1beta1", plural="pods", namespace=name)
                for pod in k8s_metrics_pods["items"]:
                    containers_req_lim = containers_request_limit(pod)
                    logging.info(containers_req_lim)
            # except Exception as ex:
            #     logging.fatal(ex)
                stopped.wait(10)
