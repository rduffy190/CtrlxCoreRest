import ctrlx_api
import pprint
import json
import time

def read_data(event):
    pprint.pprint(json.dumps(event.data))
if __name__ == '__main__':

    api = ctrlx_api.CtrlxApi(ip_addr='192.168.10.184',usr='boschrexroth', password='boschrexroth',
                             cert_path='webserver_custom_cert.pem', key_path='webserver_custom_key.pem')
    ok, _  = api.connect()
    dl_node = ctrlx_api.CtrXNode(api)
    r = dl_node.read_node('motion/axs/CoeAxis/cfg/lim/pos-max')
    pprint.pprint(r.json())
    r = dl_node.meta_data('motion/axs/CoeAxis/cfg/lim/pos-max')
    pprint.pprint(r.json())
    data = dict()
    data['type'] = 'double'
    data['value'] = 10.5
    dl_node.write_node('motion/axs/CoeAxis/cfg/lim/pos-max',json.dumps(data))
    time.sleep(1)
    dl_node = ctrlx_api.CtrXNode(api)
    r = dl_node.read_node('motion/axs/CoeAxis/cfg/lim/pos-max')
    pprint.pprint(r.json())
    r = dl_node.browse_node('motion/axs')
    pprint.pprint(r.json())
    data = dict()
    data['type'] = 'string'
    data['value'] = 'Created_Axis'
    r = dl_node.create_node('motion/axs', json.dumps(data))
    time.sleep(2)
    r = dl_node.browse_node('motion/axs')
    pprint.pprint(r.json())
    r = dl_node.delete_node('motion/axs/Created_Axis')
    time.sleep(2)
    r = dl_node.browse_node('motion/axs')
    pprint.pprint(r.json())
    settings = ctrlx_api.CtrlxSubscriptionSettings('12', '1000', '10000', ['custom-app/simple-dot-net/test-points'],keepaliveInterval='100000')
    subscription = ctrlx_api.CtrlXSubscription(api)
    subscription.create_subscription(settings)
    subscription.register_with_subscriptoin('12', read_data)
    time.sleep(30)
    subscription.close_subscription()
