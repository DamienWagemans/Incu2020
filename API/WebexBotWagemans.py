from flask import Flask, request
import requests
from ncclient import manager
import xml.dom.minidom
import json

######### BOT INFO
bot_name = 'DamienWagemans@webex.bot'
roomid='Y2lzY29zcGFyazovL3VzL1JPT00vOTUwNTFkNmEtYzczNS0zZWNkLWI1OWMtZWVjMDliOTdlM2U4'
bot_access_token = 'YmZjNTc4MDktODQwMS00Y2U0LWEyMjQtZmM5N2NhMWY5MmFhMjNmMzNlMjItNDJk_PF84_consumer'
url='https://api.ciscospark.com/v1/messages?roomId=' + roomid
header = { 'content-type' : 'application/json; charset=utf-8',
           'authorization': 'Bearer ' + bot_access_token}

######### NEXUS
node = '127.0.0.1'

def connect(node):
    try:
        device_connection = manager.connect(host = node, port = '2222', username = 'admin', password = 'cisco!123', hostkey_verify = False, device_params={'name':'nexus'})
        return device_connection
    except:
        print("Unable to connect " + node)

def getHostname(node):
    device_connection = connect(node)
    hostname = """
               <show xmlns="http://www.cisco.com/nxos:1.0">
                   <hostname>
                   </hostname>
               </show>
               """
    netconf_output = device_connection.get(('subtree', hostname))
    xml_doc = xml.dom.minidom.parseString(netconf_output.xml)
    hostname = xml_doc.getElementsByTagName("mod:hostname")
    return "Hostname: "+str(hostname[0].firstChild.nodeValue)

def getVersion(node):
    device_connection = connect(node)
    ver = """
               <show xmlns="http://www.cisco.com/nxos:1.0">
                   <version>
                   </version>
               </show>
               """
    try:
        netconf_output = device_connection.get(('subtree', ver))
        xml_doc = xml.dom.minidom.parseString(netconf_output.xml)
        Version = xml_doc.getElementsByTagName("mod:nxos_ver_str")
        return "Version: "+str(Version[0].firstChild.nodeValue)
    except:
        return 'Unable to get the version'

def setHostname(node, message):
    device_connection = connect(node)
    HOSTNAME = '''
                <config>
                    <configure xmlns="http://www.cisco.com/nxos:1.0">
                        <__XML__MODE__exec_configure>
                            <hostname>
                                <name>%s</name>
                            </hostname>
                        </__XML__MODE__exec_configure>
                    </configure>
                </config>    
                '''
    hostname = message.replace('hostname ', '')
    config_str = HOSTNAME % (hostname)
    try:
        device_connection.edit_config(target='running', config=config_str)
        return (f"Hostname changed to {hostname}")
    except:
        return 'Unable to change the hostname'



######### Flask
app = Flask(__name__)

@app.route("/", methods= ['GET', 'POST'])
def sendMessage():
    webhook = request.json
    url = 'https://api.ciscospark.com/v1/messages'
    msg = {'roomId': webhook['data']['roomId']}
    sender = webhook['data']['personEmail']
    message = getMessage()
    if (sender != bot_name):
        if(message == 'help'):
            msg ['markdown'] = 'Welcome to Incubator 2020 bot,' \
                               'Here the available commands :' \
                               ' - show hostname' \
                               ' - show version' \
                               ' - hostname <>new_hostname_name>' \
                               ' - help'
        elif (message == 'show hostname'):
            msg['markdown'] = getHostname(node)
        elif message == 'show version':
            msg['markdown'] = getVersion(node)
        elif message.startswith('hostname'):
            msg['markdown'] = setHostname(node, message)
        else:
            msg['markdown'] = 'Sorry, command not found, type ''help'' to get help'
        requests.post(url, data=json.dumps(msg), headers=header, verify=True)


def getMessage():
    webhook = request.json
    url = 'https://api.ciscospark.com/v1/messages/' + webhook['data']['id']
    get_msgs = requests.get(url, headers=header, verify=True)
    print('hello')
    message = get_msgs.json()['text']
    return message

app.run(debug=True)