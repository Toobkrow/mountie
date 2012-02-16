# Copyright 2012 Daniel Anthofer
# Modification and distribution under terms of
# GNU GPL v. 3 is permitted
# http://www.gnu.org/licenses/gpl-3.0.txtrg/licenses/gpl-3.0.txt

import dbus

system_bus = dbus.SystemBus()

#find devices
proxy = system_bus.get_object('org.freedesktop.UDisks', '/org/freedesktop/UDisks')
interface = dbus.Interface(proxy, 'org.freedesktop.UDisks')
list_devices = interface.get_dbus_method('EnumerateDevices')

print(list_devices())
filesystemproxy = system_bus.get_object('org.freedesktop.UDisks', list_devices()[-1])

#get properties of a device
filesystempropertiesinterface = dbus.Interface(filesystemproxy, 'org.freedesktop.DBus.Properties')
get_filesystem_property = filesystempropertiesinterface.get_dbus_method('Get')
print(get_property('org.freedesktop.UDisks.Device', 'DeviceIsMounted'))
print(get_property('org.freedesktop.UDisks.Device', 'DeviceIsPartition'))
print(get_property('org.freedesktop.UDisks.Device', 'DeviceMountPaths'))
print(get_property('org.freedesktop.UDisks.Device', 'DeviceIsReadOnly'))
print(get_property('org.freedesktop.UDisks.Device', 'IdUsage')) #filesystem, crypto, partitiontable, raid, other

print(get_property('org.freedesktop.UDisks.Device', 'IdType')) 	#filesystem: filesystemtype (i.e. vfat)
																																#crypto: cryptotype (i.e. crypto_LUKS)
																																#...

#unmount a device
filesystemmethodsinterface = dbus.Interface(filesystemproxy, 'org.freedesktop.UDisks.Device')
unmount_filesystem = filesystemmethodsinterface.get_dbus_method('FilesystemUnmount')
try:
	unmount_filesystem([])#array of option strings, even if it is empty
												#currently only the option 'force' is accepted
except dbus.exceptions.DBusException:
	print("Cannot unmount because file system on device is busy")

#mount a device
mountpoint = 'nowhere'
if get_property('org.freedesktop.UDisks.Device', 'IdUsage') == 'filesystem':
	filesystemtype = get_property('org.freedesktop.UDisks.Device', 'IdType')
	mount_filesystem = filesystemmethodsinterface.get_dbus_method('FilesystemMount')
	mountpoint = mount_filesystem(filesystemtype, []) #array of option strings, even if it is empty

