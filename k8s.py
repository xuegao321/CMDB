from kubernetes import client, config

def init():
    with open('token.txt', 'r') as file:
        Token = file.read().strip('\n')

    APISERVER = 'https://k8s-apiserver.guokr.net:6443'
    configuration = client.Configuration()
    configuration.host = APISERVER
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": "Bearer " + Token}
    client.Configuration.set_default(configuration)

def get_namespaces():
    v1 = client.CoreV1Api()
    for ns in v1.list_namespace().items:
        print(ns.metadata.name)

def get_pod():
    # Do calls
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

def get_services():
    v1 = client.CoreV1Api()
    ret = v1.list_service_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s t%s t%s t%s t%s n" % 
              (i.kind, i.metadata.namespace, i.metadata.name, i.spec.cluster_ip, i.spec.ports ))


def main():
    init()
    get()


if __name__ == '__main__':
    main()
