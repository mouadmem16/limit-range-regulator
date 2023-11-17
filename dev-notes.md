
# to run the code in python command line
````
from kubernetes.config import load_kube_config
from kubernetes.client import CustomObjectsApi, CoreV1Api
from os import environ
print("Using default Kubernetes config")
load_kube_config(environ.get('KUBECONFIG'))
CUSTOM_API = CustomObjectsApi()
CORE_API = CoreV1Api()
````



