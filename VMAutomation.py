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
    ip = summary.guest.ipAddress if summary.guest.ipAddress else "N/A"
    state = summary.runtime.powerState
    cpu = summary.config.numCpu
    memory = int(summary.config.memorySizeMB) / 1024


    return {
        "Name": vm_name,
        "IP": ip,
        "Power State": state,
        "CPU": cpu,
        "Memory (GB)": int(memory)
    }



def search_vms(content):
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    global vm_name
    vm_name = input("Enter the name of the VM or hit enter to return all VMs: ")
    vms = container.view

    if vm_name: 
        found = False
        for vm in vms:
            if vm_name == vm.name:
                vm_info = get_vm(vm)
                print("Printing info for:", vm.name)
                print(json.dumps(vm_info, indent=4))
                found = True
                break
        if not found:
            print("No VM found with the name:", vm_name)
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



def poweron():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ")
    vms = container.view

    if vm_name: 
        found = False
        for vm in vms:
            if vm_name == vm.name:
                vm_info = get_vm(vm)
                if summary.runtime.powerState == "poweredOn":
                    print(vm_name, "is already running")
                    break
                elif summary.runtime.powerState == "poweredOff":
                    print(vm_name, "is being powered on...") 
                    task = [vm.PowerOn()]
                found = True
                break
        if not found:
            print("No VM found with the name:", vm_name)



def poweroff():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ")
    vms = container.view

    if vm_name:
        found = False
        for vm in vms:
            if vm_name == vm.name:
                vm_info = get_vm(vm)
                if summary.runtime.powerState == "poweredOff":
                    print(vm_name, "is already powered off")
                    break
                elif summary.runtime.powerState == "poweredOn":
                    print(vm_name, "is being powered off...")  
                    task = [vm.PowerOff()]
                found = True
                break
        if not found:
            print("No VM found with the name:", vm_name)



def create_snapshot():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ")
    vms = container.view

    if vm_name:
        found = False
        for vm in vms:
            if vm_name == vm.name: #Checks for match
                vm_info = get_vm(vm)

                # Name for the snapshot
                snapshot_name = input("Enter name for snapshot: ") 
                 
                # Description for snapshot
                snapshot_description = input("Enter snapshot description: ")
                snapshot_memory = bool(input("Snapshot memory (True/False): ")) 
                
                # Creating the snapshot
                vm.CreateSnapshot_Task(
                name=snapshot_name, 
                description=snapshot_description, 
                memory=snapshot_memory,
                quiesce=False
                )
                found = True
                break
        if not found:
            print("No VM found with the name:", vm_name)



def tweak_vm():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ")
    vms = container.view

    if vm_name:
        found = False
        for vm in vms:
            if vm_name == vm.name:
                vm_info = get_vm(vm)
                config_spec = vim.vm.ConfigSpec()
                new_memory = int(input("Enter new memory amount in gb: "))
                new_memory_mb = (new_memory * 1024)
                new_cpu = int(input("Enter new amount of CPUs: "))
                config_spec.memoryMB = new_memory_mb
                config_spec.numCPUs = new_cpu


                print("Changing Memory and CPU count for", vm_name)
                task = vm.ReconfigVM_Task(config_spec)
                found = True
                break
        if not found:
            print("No VM found with the name:", vm_name)



def restart_vm():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ")
    vms = container.view
    if vm_name:
        found = False
        for vm in vms:
            if vm_name == vm.name:
                vm_info = get_vm(vm)
                if summary.runtime.powerState == "poweredOff":
                    print(vm_name, "is powered off...")
                    power_input = input("Power on? (y/n): ")
                    if power_input == 'y' or power_input == 'Y':
                        task = [vm.PowerOn()]
                    else:
                        print("Returning to menu...")
                        break
                elif summary.runtime.powerState == "poweredOn":
                    print(vm_name, "is being restarted...")
                    try:
                        vm.RebootGuest()
                    except:
                        vm.ResetVM_Task()
                found = True
                break
        if not found:
            print("No VM found with the name:", vm_name)



def Delete_VM():
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_name = input("Enter the name of the VM: ")
    vms = container.view

    if vm_name:
        found = False
        for vm in vms:
            if vm_name == vm.name:
                vm_info = get_vm(vm)
                confirm = input("Are you sure you want to delete? (y/n): ")
                if confirm == 'y' or confirm == 'Y':
                    print("Deleting:", vm_name)
                    task = vm.Destroy_Task()
                else:
                    print("Returning to menu...")
                    break
                found = True
                break
        if not found:
            print("No VM found with the name:", vm_name)



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


