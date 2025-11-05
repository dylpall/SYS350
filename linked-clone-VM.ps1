# Writes out names of vms to clone
$Getall = Get-VM | Where-Object {$_.Name -match "Base"}

Write-Host $Getall

# Ask for the name of VM to clone
$Source = Read-Host "Enter the name of the VM to clone"

# If error
if ($null -eq $Source) {
    Write-Host "VM '$Source' not found."
    exit
}

# new VM name
$NewName = Read-Host "Enter name for new VM"

# Get the parent disk of the VM for cloning
$ParentPath = "C:\Users\Public\Documents\Hyper-V\Virtual hard disks\$Source.vhdx"

# Assign path and name of new VM hard disk
$NewDiskPath = "C:\Users\Public\Documents\Hyper-V\Virtual hard disks\$NewName.vhdx"

# Creates differencing disk then creates new VM
$NewDisk = New-VHD -ParentPath $ParentPath -Path $NewDiskPath -Differencing
Write-Host "Creating new differencing disk....."
Start-Sleep -Seconds 5

# creates linked clone
New-VM -Name $NewName -MemoryStartupBytes 2GB -VHDPath $NewDisk.Path -Generation 2 