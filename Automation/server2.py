import json

from ncclient import manager
import xml.dom.minidom
import xmltodict
import socket

node = "127.0.0.1"

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


def Main():
    host = "127.0.0.1"
    port = 5000

    mySocket = socket.socket()
    mySocket.bind((host, port))

    mySocket.listen(5)
    conn, addr = mySocket.accept()
    print ("Connection from: " + str(addr))
    while True:
        message = conn.recv(1024).decode()
        if message == "show hostname":
                message = getHostname(node)
        elif message == 'show version':
            message = getVersion(node)
        elif message.startswith('hostname'):
            message = setHostname(node, message)
        else:
            message = 'I dont understand'
        conn.send(message.encode())
    conn.close()

if __name__ == '__main__':
        Main()
