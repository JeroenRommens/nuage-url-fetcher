#!/usr/bin/python
"""
Usage:
  nuage-url-fetcher [options]
  nuage-url-fetcher (-h | --help)
  
Options:
  -h --help               Show this screen
  -v --version            Show version
  --vsd=<string>          IP of VSD
  --enterprise=<string>   Enterprise name
  --nsg-name=<string>     Name of Network Services Gateway (NSG)
"""

from docopt import docopt
from vspk import v5_0 as vsdk
import time
import json
from proton.handlers import MessagingHandler,EndpointStateHandler
from proton.reactor import Container, DurableSubscription
from optparse import OptionParser
import threading

def ampqWorker():
    """thread worker function"""
    oAmqpClient = AmqpClient()
    Container(Recv(oAmqpClient), EndPointHandler()).run()
    return

def getargs():
    return docopt(__doc__, version="nuage-url-fetcher 0.0.1")

def execute():
    main(getargs())

def main(args):
    api_url = "https://"+str(args['--vsd'])+":8443"
    try:
        session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url=api_url)
        session.start()
        csproot = session.user
    except:
        print("ERROR: Could not establish connection to VSD API")
        sys.exit(1)

    enterprise_filter_str = 'name == "'+str(args['--enterprise'])+'"'
    enterprise = csproot.enterprises.get_first(filter=enterprise_filter_str)

    t = threading.Thread(target=ampqWorker)
    t.start()
    time.sleep(1)
    #Get NSG object based on Name
    nsg_filter_str = 'name == "'+str(args['--nsg-name'])+'"'
    nsg = enterprise.ns_gateways.get_first(filter=nsg_filter_str)
    #Create job object to trigger notify_nsg_registration
    job = vsdk.NUJob(command="NOTIFY_NSG_REGISTRATION")
    #Trigger Job on NSG object
    nsg.create_child(job)
    

class AmqpClient():
    def __init__(self):
        #Initialize Defaults
        self.bClusterMode = False
        self.bDurableSubscription = False
        self.sUserName = "jmsclient%40csp"
        self.sPassword = "jmsclient"
        self.sClientId = "Amqp Client"
        self.sTopicName = "topic://topic/CNAMessages"
        self.sQueueName = "queue://queue/CNAQueue"
        self.isTopic = False

        self.sPort = "5672"
        self.lUrls = []
        self.lUrls.append('jmsclient%40csp:jmsclient@10.167.1.60:5672')

class Recv(MessagingHandler):
    def __init__(self, aInOAmqpClient):
        super(Recv, self).__init__()
        self.oAmqpClient = aInOAmqpClient
        self.received = 0

    def on_start(self, event):
        #Set the client id So that It is easy to Identify.
        event.container.container_id=self.oAmqpClient.sClientId
        conn = event.container.connect(urls=self.oAmqpClient.lUrls,heartbeat=1000)

        if self.oAmqpClient.bDurableSubscription:
            durable = DurableSubscription()
            if self.oAmqpClient.isTopic:
                event.container.create_receiver(conn, self.oAmqpClient.sTopicName, options=durable)
            else:
                event.container.create_receiver(conn, self.oAmqpClient.sQueueName, options=durable)
        else:
            event.container.create_receiver(conn, self.oAmqpClient.sTopicName)
        #self.oAmqpClient.nsg.create_child(self.oAmqpClient.job)

    def on_message(self, event):
        urlFound = False
        message = event.message.body
        if "nsgnotification" in message:
            json_acceptable_message = message.replace("'", "\"")
            message_dict = json.loads(json_acceptable_message)
            entities = message_dict['entities']
            entities_dict = entities[0]
            try:
                message_dict = entities_dict['message']
            except:
                pass
            try:   
                print(str(message_dict['link']))
                urlFound = True
            except:
                pass
        if urlFound:
            event.connection.close()
        
    def on_disconnected(self, event):
        pass

class EndPointHandler(EndpointStateHandler):
    def __init__(self):
        super(EndPointHandler, self).__init__()

    def on_connection_opened(self, event):
        super(EndPointHandler, self).on_connection_opened(event)

if __name__ == "__main__":
    main(getargs())



