import os
import logging
from kubernetes.client import CustomObjectsApi, CoreV1Api

class Config(object):
    namespaces: list = list()
    CUSTOM_API: CustomObjectsApi = None
    CORE_API: CoreV1Api = None

    def __init__(self):
        try:
            Config.namespaces = os.environ['NAMESPACES'].split(",")
        except Exception as ex:
            self.show_usage("NAMESPACES", ex)
        
    def show_usage(self, attribut, ex):
        logging.info("""
            There are some env variables that have to be set
            * The env variable NAMESPACES to define the selectable namespaces
                   NAMESPACES=default,kube-system,....
        """)
        logging.fatal(f"You have to fill the {attribut} env variable !!")
        logging.fatal(f"{ex}")

    @staticmethod
    def define_API():
        if Config.CUSTOM_API is None:
            Config.CUSTOM_API = CustomObjectsApi()
        if Config.CORE_API is None:
            Config.CORE_API = CoreV1Api()