import ctrlx_api
import pprint
import json
import time
import os
def read_data(event):
    pprint.pprint(json.dumps(event.data))
if __name__ == '__main__':
    # Create API Object
    api = ctrlx_api.CtrlxApi(ip_addr='192.168.1.1',usr='boschrexroth', password='boschrexroth')
    # Connect to the Ctrlx Core
    ok, _  = api.connect()
    # Create A node object using the API
    dl_node = ctrlx_api.CtrXNode(api)
    # read the data layer node for the max position limit of an axis called CoeAxis
    r = dl_node.read_node('motion/axs/CoeAxis/cfg/lim/pos-max')
    pprint.pprint(r.json())
    # get the meta data of a data layer node
    r = dl_node.meta_data('motion/axs/CoeAxis/cfg/lim/pos-max')
    pprint.pprint(r.json())
    data = dict()
    # format for so that the json library will dump it as a proper Json String
    data['type'] = 'double'
    data['value'] = 10.5
    dl_node.write_node('motion/axs/CoeAxis/cfg/lim/pos-max',json.dumps(data))
    time.sleep(1)
    # rad the update happened
    r = dl_node.read_node('motion/axs/CoeAxis/cfg/lim/pos-max')
    pprint.pprint(r.json())
    # browse the axis folder to read all configured axis
    r = dl_node.browse_node('motion/axs')
    pprint.pprint(r.json())
    data = dict()
    # set data up for axis creation
    data['type'] = 'string'
    data['value'] = 'Created_Axis'
    # create request on axis
    r = dl_node.create_node('motion/axs', json.dumps(data))
    time.sleep(2)
    # confirm axis is created
    r = dl_node.browse_node('motion/axs')
    pprint.pprint(r.json())
    # delete axis
    r = dl_node.delete_node('motion/axs/Created_Axis')
    time.sleep(2)
    # confirm deletion
    r = dl_node.browse_node('motion/axs')
    pprint.pprint(r.json())
    # create a subscription
    subscription_id = 'Hello_Subscription'
    settings = ctrlx_api.CtrlxSubscriptionSettings(subscription_id, '1000', '10000', ['custom-app/simple-dot-net/test-points'],keepaliveInterval='100000')
    ctrlx_api.create_subscription(api,settings)
    subscription = ctrlx_api.CtrlXSubscription(api)
    subscription.subscribe(subscription_id, read_data)
    # let subscription run for 30 s
    time.sleep(30)
    # unsubscribe to the data
    subscription.unsubscribe()
    # close subscription
    ctrlx_api.close_subscription(api,subscription_id)
