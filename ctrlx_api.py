import requests
import json
import sseclient
import threading

class CtrlxApi:
    def __init__(self, ip_addr, usr, password, cert_path='',key_path='', api_version = 'v2'):
        self.__ip_addr = ip_addr
        self.__usr = usr
        self.__password = password
        self.__api_url = '/api/' + api_version + '/'
        self.__header = json.loads(json.dumps(
            {'Content-Type': 'application/json;charset=UTF-8', 'Accept': 'application/json, text/plain, */*'}))
        self.__verify = False
        if cert_path != '' and key_path != '':
            self.__verify = cert_path
        self.__cert = (cert_path, key_path)

    def connect(self):
        auth_json = json.dumps({'name': self.__usr, 'password': self.__password}, separators=(',', ':'))
        url = 'https://' + self.__ip_addr + '/identity-manager'+self.__api_url+'auth/token'
        r = requests.post(url, data=auth_json, verify=self.__verify, headers=self.__header, cert = self.__cert)
        if not r.ok:
            return False, r.status_code

        resp = r.json()
        self.__header['Authorization'] = 'Bearer ' + resp['access_token']
        return True, r.status_code

    def read(self, ctrlx_url,stream = False):
        url = 'https://' + self.__ip_addr + '/' + ctrlx_url
        r = requests.get(url, verify=self.__verify, headers=self.__header,stream = stream, cert = self.__cert)
        return r

    def write(self, ctrlx_url, data):
        url = 'https://' + self.__ip_addr + '/' + ctrlx_url
        r = requests.put(url, verify=self.__verify, headers=self.__header, data=data, cert = self.__cert)
        return r

    def create(self, ctrlx_url, data):
        url = 'https://' + self.__ip_addr + '/' + ctrlx_url
        r = requests.post(url, verify=self.__verify, headers=self.__header, data=data, cert = self.__cert)
        return r

    def delete(self, ctrlx_url):
        url = 'https://' + self.__ip_addr + "/" + ctrlx_url
        r = requests.delete(url, verify=self.__verify, headers=self.__header, cert = self.__cert)
        return r
    def subscribe(self, ctrlx_url):
        url = 'https://' + self.__ip_addr + "/" + ctrlx_url
        header = {'accept':'text/event-stream', 'Authorization': 'Bearer ' + self.__header['Bearer']}
        r = requests.get(url, verify=self.__verify, headers=header, stream=True, cert = self.__cert)
        return r

    def get_api_url(self):
        return self.__api_url

class CtrlxSubscriptionSettings:
    def __init__(self,id,publishiterval,error_interval,nodes:list,keepaliveInterval = 3439503088):
        self.rules = dict()
        self.nodes = dict()
        self.rules['id'] = id
        self.rules['publishInterval'] = publishiterval
        self.rules['errorInterval'] = error_interval
        self.nodes['nodes'] = nodes
        self.rules['keepaliveInterval'] = keepaliveInterval

class CtrlXSubscription:
    def __init__(self, CtrlXApi:CtrlxApi):
        self.__api = CtrlXApi
        self.__url_preamble  = '/automation' + self.__api.get_api_url()
        self.__close = threading.Event()
        self.__worker = None
        self.__active = False

    def create_subscription(self, settings:CtrlxSubscriptionSettings):
        if self.__active:
            return False
        setting = dict()
        setting['properties'] = settings.rules
        setting['nodes'] = settings.nodes['nodes']
        str_json = json.dumps(setting)
        r = self.__api.create(self.__url_preamble+'events',str_json)
        return r

    def register_with_subscriptoin(self, id, fn_hdl):
        r = self.__api.read(self.__url_preamble + 'events/' + id, stream=True)
        if not r.ok: return False
        self.__worker = threading.Thread(target=self.__handle_subscription, args=(r, self.__close, fn_hdl))
        self.__worker.start()
        self.__active = True
        return True

    def close_subscription(self):
        self.__close.set()
        self.__worker.join()
        self.__active = False

    def __handle_subscription(self,r, close:threading.Event, fn_hdl):
        while not close.is_set():
            sse = sseclient.SSEClient(r)
            for event in sse.events():
                fn_hdl(event)
                if close.is_set():
                    break

class CtrXNode:
    def __init__(self,api:CtrlxApi):
        self.__api = api
        self.__url_preamble = 'automation' + self.__api.get_api_url() + "nodes/"

    def read_node(self,node_name):
        url = self.__url_preamble + node_name
        return self.__api.read(url)

    def write_node(self,node_name,data):
        url = self.__url_preamble + node_name
        return self.__api.write(url,data)

    def create_node(self,node_name,data):
        url = self.__url_preamble + node_name
        return self.__api.create(url,data)

    def delete_node(self,node_name):
        url = self.__url_preamble + node_name
        return self.__api.delete(url)

    def browse_node(self,node_name):
        url = self.__url_preamble + node_name + '?type=browse'
        return self.__api.read(url)

    def meta_data(self,node_name):
        url = self.__url_preamble + node_name + '?type=metadata'
        return self.__api.read(url)




