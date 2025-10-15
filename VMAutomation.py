from pyVim.connect import SmartConnect
from pyVmomi import vim
import ssl
import socket
import json
import getpass


def connect_vcenter():
    global content
    with open('vcenter-conf.json') as f:
        config = json.load(f)
    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    s.verify_mode = ssl.CERT_NONE
    hostname = config['vcenterhost']
    username = config['vcenteradmin']
    
    passw = getpass.getpass(prompt=f"Enter password for {username}: ")
    
    si=SmartConnect(host=hostname, user=username, pwd=passw, sslContext=s)
    aboutInfo=si.content.about
    print(aboutInfo.fullName)
    content = si.content
    return content

def get_vm(vm):
    global summary
    summary = vm.summary
    vm_name = summary.config.name
    state = summary.runtime.powerState
    cpu = summary.config.numCpu
    memory = int(summary.config.memorySizeMB) / 1024
    ip = summary.guest.ipAddress if summary.guest.ipAddress else "N/A"

    return {
        "Name": vm_name,
        "state": state,
        "cpu": cpu,
        "memory": memory,
        "ip": ip
    }

def search_vms(content):
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    global vm_name
    vm_name = input("Enter the name of the VM. (enter to return all VMs): ")
    vms = container.view

    if vm_name:
        found = False
        for vm in vms:
            if vm_name == vm.name:
                vm_info = get_vm(vm)
                print("Printing info...")
                print(json.dumps(vm_info, indent=4))
                found = True
                break
        if not found:
            print("No VM found")
    else:
        print("Listing all VMs:")
        for vm in vms:
            vm_info = get_vm(vm)
            print(json.dumps(vm_info, indent = 4))
            print("-------------------------------")

def session_info():
    source_ip = socket.gethostbyname(socket.gethostname())

    with open('vcenter-conf.json') as f:
        config = json.load(f)
    
    vcenter_server = config['vcenterhost']
    current_user = config['vcenteradmin']

    print('Source IP:', source_ip)
    print('vCenter Server:', vcenter_server)
    print('Current User:', current_user)
    print('-------------------------------')
            
# Menu func
def Menu(): 
    print ("1. Connect to vCenter")
    print ("2. Search VMs")
    print ("3. Show Current Connection Information")
    print ("4. Power on a VM")
    print ("5. Power off a VM")
    print ("6. Create a snapshot of a VM")
    print ("7. Tweak the CPUs or Memory of a VM")
    print ("8. Restart a VM")
    print ("9. Delete a VM")
    print ("10. Quit")

# While loop for menu
while True:
    Menu()
    choice=input("Enter your choice [1-10]: ")

    if choice=='1':
        print("Connecting to vCenter...")
        print('-------------------------------')
        connect_vcenter()

    elif choice=='2':
        print("Searching VMs...")
        print('-------------------------------')
        search_vms(content)

    elif choice=='3':
        print("Showing current connection information:")
        print('-------------------------------')
        session_info()
    
    elif choice=='4':
        print("Powering on a VM")
        print('-------------------------------')
        poweron()
    
    elif choice=='5':
        print("Powering off a VM")
        print('-------------------------------')
        poweroff()
    
    elif choice=='6':
        print("Creating a snapshot...")
        print('-------------------------------')
        create_snapshot()
    
    elif choice=='7':
        print("Tweaking VM's performance...")
        print('-------------------------------')
        tweak_vm()
    
    elif choice=='8':
        print("Restarting a VM...")
        print('-------------------------------')
        restart_vm()
    
    elif choice=='9':
        print("Deleting a VM...")
        print('-------------------------------')
        delete_vm()
    
    elif choice=='10':
        print("Exiting...")
        break
# in case of invalid input
    else:
        print("Invalid choice. Please enter a number between 1 and 10.")


