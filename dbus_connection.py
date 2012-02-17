# Copyright 2012 Daniel Anthofer
# Modification and distribution under terms of
# GNU GPL v. 3 is permitted
# http://www.gnu.org/licenses/gpl-3.0.txt

'''createDevList() returns a list of FileSystemDevice instances
of currently avaliable file systems'''

import dbus

# FileSystemDevice(devicefilepath, system_bus) {{{
class FileSystemDevice:
	'''attributes:
		devicefile
		fstype
		label
		size
		mountpoint
	methods:
		mounted
		mount
		unmount
	'''

	def __init__(self, devicefilepath, system_bus):
		self.filesystemproxy = system_bus.get_object('org.freedesktop.UDisks', devicefilepath)
		self.filesystempropertiesinterface = dbus.Interface(self.filesystemproxy, 'org.freedesktop.DBus.Properties')
		self.get_filesystem_property = self.filesystempropertiesinterface.get_dbus_method('Get')
		if not self.get_filesystem_property('org.freedesktop.UDisks.Device', 'IdUsage') == 'filesystem':
			raise TypeError('not a filesystem')
		self.filesystemmethodsinterface = dbus.Interface(self.filesystemproxy, 'org.freedesktop.UDisks.Device')

		self.devicefile = devicefilepath
		self.fstype = self.get_filesystem_property('org.freedesktop.UDisks.Device', 'IdType')
		self.label = self.get_filesystem_property('org.freedesktop.UDisks.Device', 'IdLabel')
		self.size = self.get_filesystem_property('org.freedesktop.UDisks.Device', 'DeviceSize')
		if self.get_filesystem_property('org.freedesktop.UDisks.Device', 'DeviceIsMounted'):
			self.mountpoint = str( self.get_filesystem_property('org.freedesktop.UDisks.Device', 'DeviceMountPaths')[0] )
		else:
			self.mountpoint = None
		
		self.mount_fs = self.filesystemmethodsinterface.get_dbus_method('FilesystemMount')
		self.unmount_fs = self.filesystemmethodsinterface.get_dbus_method('FilesystemUnmount')
		
	def mounted(self):
		return bool(self.get_filesystem_property('org.freedesktop.UDisks.Device', 'DeviceIsMounted'))

	def mount(self):
		self.mountpoint = str( self.mount_fs(self.fstype, []) )

	def unmount(self):
		self.unmount_fs([])
# }}}

system_bus = dbus.SystemBus()
proxy = system_bus.get_object('org.freedesktop.UDisks', '/org/freedesktop/UDisks')
interface = dbus.Interface(proxy, 'org.freedesktop.UDisks')
list_devices = interface.get_dbus_method('EnumerateDevices')

def createDevList():
	devList = []
	for devfile in list_devices():
		try:
			devList.append(FileSystemDevice(devfile, system_bus))
		except TypeError:
			pass # skip devicefiles with i.e. partition tables
	return devList
