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
            if len(Config.namespaces) == 0:
                raise Exception("The env var NAMESPACES is Empty")
            if(Config.namespaces[0].lower() == "all"):
                Config.namespaces.clear()
        except Exception:
            self.show_usage("NAMESPACES")
        
    def show_usage(self, attribut):
        logging.info("""
            There are some env variables that have to be set
            * The env variable NAMESPACES to define the selectable namespaces
                   NAMESPACES=default,kube-system,.... OR NAMESPACES=ALL
        """)
        raise Exception(f"You have to fill the {attribut} env variable !!")

    @staticmethod
    def define_API():
        if Config.CUSTOM_API is None:
            Config.CUSTOM_API = CustomObjectsApi()
        if Config.CORE_API is None:
            Config.CORE_API = CoreV1Api()