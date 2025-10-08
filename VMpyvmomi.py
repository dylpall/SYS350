import getpass
import ssl
from pyVim.connect import SmartConnect
from pyVmomi import vim
import re
import json

def auth():
    """authenticate to vcenter server"""
    hostname,username = get_connect_details()
    print(f"Enter vCenter credentials for {username}")
    passwd = getpass.getpass()
    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    s.verify_mode = ssl.CERT_NONE
    si = SmartConnect(host=hostname, user=username, pwd=passwd, sslContext=s)
    return si

def get_connect_details():
    """gets the vcenter hostname and username from vcenter-conf.json"""
    global hostname
    with open('vcenter-conf.json') as f:
        config = json.load(f)
        vcenter_info = config['vcenter'][0]
        hostname = vcenter_info['vcenterhost']
        username = vcenter_info['vcenteradmin']
    return hostname,username


def basic_info(auth):
    """gets basic connection info after connecting"""
    about_info = auth.content.about
    
    print(about_info)
    print(about_info.fullName)

def session_info(auth):
    """Returns information about the current session"""
    global hostname
    session_info = auth.content.sessionManager.currentSession
    print(f"\nHostname: {hostname}")
    print(f'User: {session_info.userName}')
    print(f'IP: {session_info.ipAddress}')
    
def vm_info(auth, search_name=None, return_list=False):
    """Returns VMs and related info"""
    all_content = auth.RetrieveContent()

    root_folder = all_content.rootFolder
    content_type = [vim.VirtualMachine]
    view_containers = all_content.viewManager.CreateContainerView(root_folder,content_type, True)
    
    children = view_containers.view

    if return_list is True and search_name == None:
        vm_list = [child for child in children]
        return vm_list
    elif return_list is True:
        vm_list = []
        regex_search = re.compile(search_name, re.IGNORECASE)
        for child in children:
            if regex_search.search(child.summary.config.name) is not None:
                vm_list.append(child)
        return vm_list

    if search_name == None:
        for child in children:
            format_vm_info(child)
    else:
        regex_search = re.compile(search_name, re.IGNORECASE)
        for child in children:    
            if regex_search.search(child.summary.config.name) is not None:
                format_vm_info(child)


def format_vm_info(child):
    """formats information about each vm"""
    summary = child.summary
    print(f"\nName: {child.config.name}")
    print(f"IP: {child.guest.ipAddress}")
    print(f'Power State: {child.runtime.powerState}')
    print(f'CPU: {child.config.hardware.numCPU}')
    mem_gig = int(child.config.hardware.memoryMB) / 1024
    print(f'Memory: {mem_gig.__int__()} GB')


auth_object = auth()
basic_info(auth_object)
session_info(auth_object)
vm_info(auth_object)
vm_info(auth_object,'pallatroni')