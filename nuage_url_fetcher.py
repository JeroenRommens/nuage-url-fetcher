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
import sys
from proton.handlers import MessagingHandler,EndpointStateHandler
from proton.reactor import Container, DurableSubscription
from optparse import OptionParser
import threading

username = "jmsclient"
password = "jmsclient"
login_enterprise = "csp"

def ampqWorker(username, password, login_enterprise, vsd_ip):
    """thread worker function"""
    oAmqpClient = AmqpClient(username, password, login_enterprise, vsd_ip)
    Container(Recv(oAmqpClient), EndPointHandler()).run()
    return

def getargs():
    return docopt(__doc__, version="nuage-url-fetcher 0.0.1")

def execute():
    main(getargs())

def main(args):
    vsd_ip = str(args['--vsd'])
    api_url = "https://"+vsd_ip+":8443"
    try:
        session = vsdk.NUVSDSession(username=username, password=password, enterprise=login_enterprise, api_url=api_url)
        session.start()
        csproot = session.user
    except:
        print("ERROR: Could not establish connection to VSD API")
        sys.exit(1)

    enterprise_name = str(args['--enterprise'])
    enterprise_filter_str = 'name == "'+enterprise_name+'"'
    enterprise = csproot.enterprises.get_first(filter=enterprise_filter_str)

    if enterprise == None:
      print("ERROR: Could not find enterprise with name "+enterprise_name)
      sys.exit(1)

    #Get NSG object based on Name
    nsg_name = str(args['--nsg-name'])
    nsg_filter_str = 'name == "'+nsg_name+'"'
    nsg = enterprise.ns_gateways.get_first(filter=nsg_filter_str)

    if nsg == None:
      print("ERROR: Could not find NSG with name "+nsg_name)
      sys.exit(1)

    if nsg.bootstrap_status == "ACTIVE" or nsg.bootstrap_status == "CERTIFICATE_SIGNED":
      print("ERROR: NSG is already in a state where a URL can't be extracted")
      sys.exit(1)

    bootstraps = nsg.bootstraps.get()
    bootstrap = bootstraps[0]
    
    if bootstrap.installer_id == None:
      #print("Installer ID not defined ")
      existing_user = enterprise.users.get_first(filter="dummy")
      #print(str(existing_user.to_dict()))
      if existing_user == None:
        new_user = vsdk.NUUser(email="dummy@dummy.com",first_name="dummy",last_name="dummy",user_name="dummy",password="Alcateldc",mobileNumber="+32444444444")
        enterprise.create_child(new_user)
        bootstrap.installer_id = new_user.id
        bootstrap.save()
      else:
        bootstrap.installer_id = existing_user.id
        bootstrap.save()

    #Starting the AMQP Client to capture the event
    t = threading.Thread(target=ampqWorker, args=(username, password, login_enterprise, vsd_ip,))
    t.start()
    
    #Sleep 1s before triggering the NOTIFY event
    time.sleep(1)

    #Create job object to trigger notify_nsg_registration
    job = vsdk.NUJob(command="NOTIFY_NSG_REGISTRATION")
    #Trigger Job on NSG object
    nsg.create_child(job)
    

class AmqpClient():
    def __init__(self,username, password, login_enterprise, vsd_ip):
        #Initialize Defaults
        self.bClusterMode = False
        self.bDurableSubscription = False
        self.sUserName = username+"%40"+login_enterprise
        self.sPassword = password
        self.sClientId = "Amqp Client"
        self.sTopicName = "topic://topic/CNAMessages"
        self.sQueueName = "queue://queue/CNAQueue"
        self.isTopic = False

        self.sPort = "5672"
        self.lUrls = []
        self.lUrls.append(self.sUserName+":"+self.sPassword+"@"+vsd_ip+":"+self.sPort)

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



