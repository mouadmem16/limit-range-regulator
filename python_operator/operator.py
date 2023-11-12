import kopf
import logging
from .config import Config
from .models.pod import Pod

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
        if name in Config.namespaces or len(Config.namespaces) == 0:
            # try:
                pods = Config.CORE_API.list_namespaced_pod(namespace=name).to_dict()
                for pod_spec in pods["items"]:
                    pod = Pod(spec=pod_spec)
                    logging.info(pod.get_forecasted_values())
            # except Exception as ex:
            #     logging.fatal(ex)
                stopped.wait(10)
