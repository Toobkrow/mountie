# -*- coding: utf-8 -*-
# Copyright 2012 Daniel Anthofer
# Modification and distribution under terms of
# GNU GPL v. 3 is permitted
# http://www.gnu.org/licenses/gpl-3.0.txt

import curses
import dbus
import os


class CursesInterface:
	'''methods:
		start_interface()
		update_strlist(strlist) change displayed content
	args:
		comdict: dictionary of key to press : function
			called with index of highlighted list element
			function must return string to display at bottom
		strlist: list of string (per line)
		helpstr: string at top display keys/functions (default move/quit)
		errortext: string at bottom (default empty)
	'''

	#def __init__(self, comdict, strlist[, helpstr[, errortext]]) {{{
	def __init__(self, comdict, strlist, \
								helpstr = 'up/down: k/j\tquit: q/ESC', \
								errortext = ''):
		'''args:
			comdict: dictionary of key to press : function(index of cursorline)
			strlist: list of string (per line)
			helpstr: string at the top to display keys/functions (default move/quit)
			errortext: string at the bottom (default empty)
		'''
		self.comdict = comdict
		self.strlist = strlist
		self.helpstr = helpstr
		self.errortext = errortext
		self.cursorline = 1
	# }}}

	def end_interface(self): # {{{
		self.stdscr.erase()
		self.stdscr.refresh()
		curses.curs_set(1)
		curses.nocbreak()
		curses.echo()
		curses.endwin()
	# }}}

	def update_strlist(self, strlist): # {{{
		self.strlist = strlist
	# }}}

	def mainloop(self): # {{{
		while True:
			self.stdscr.clear()
			self.maxy, self.maxx = self.stdscr.getmaxyx()
			self.stdscr.addstr(0, 0, self.helpstr, curses.A_BOLD)

			for i in range(1,len(self.strlist)+1):
				self.linestr = self.strlist[i-1]
				if self.cursorline == i:
					while len(self.linestr) < self.maxx: #just for the eyes
						self.linestr += (' ')
					self.stdscr.addstr(i, 0, self.linestr, curses.A_REVERSE)
				else:
					self.stdscr.addstr(i, 0, self.linestr)

			self.stdscr.addstr(self.maxy-1, 0, self.errortext, curses.A_BOLD)
			self.stdscr.refresh()

			self.errortext = ''
			c = self.stdscr.getch()
			if chr(c) in self.comdict.keys():
				self.errortext = self.comdict[chr(c)](self.cursorline - 1)
			elif c == curses.KEY_UP or chr(c) == 'k':
				if self.cursorline > 1:
					self.cursorline -=1
			elif c == curses.KEY_DOWN or chr(c) == 'j':
				if self.cursorline < len(self.strlist):
					self.cursorline +=1
			elif c == 27 or chr(c) == 'q': #27=ESC
				self.end_interface()
				break
	# }}}

	def start_interface(self): # {{{
		self.stdscr = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.stdscr.keypad(1)
		curses.curs_set(0)
		self.mainloop()
	# }}}





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

		self.devicefile = self.get_filesystem_property('org.freedesktop.UDisks.Device', 'DeviceFile')
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





class Mountie:

	def __init__(self): # {{{
		self.devList = createDevList()
		self.comdict = { \
			'm' : self.toggleMounted, \
			'o' : self.openFilesystem, \
			'l' : self.openFilesystem, \
			# 'ą' is equal to right arrow key
			'ą' : self.openFilesystem, \
			'\n' : self.openFilesystem \
		}
		self.helpstr = "up/down: k/j\tmount/unmount: m\topen: o/l\tquit: q/Esc"
		self.cursesInterface = CursesInterface( \
				self.comdict, self.getStringList(), self.helpstr)
	# }}}

	def toggleMounted(self, index): # {{{
		if self.devList[index].mounted():
			try:
				self.devList[index].unmount()
			except:
				return "error: unable to unmount: device may be busy"

		else:
			try:
				self.devList[index].mount()
			except:
				return "error: unable to mount"

		self.cursesInterface.update_strlist(self.getStringList())
		return ""
	# }}}

	def openFilesystem(self, index): # {{{
		if not self.devList[index].mounted():
			self.toggleMounted(index)
		if self.devList[index].mounted():
			os.system("ranger "+self.devList[index].mountpoint)
		else:
			return "error: unable to mount"
		return ""
	# }}}

	def getStringList(self): # {{{
		strlist = []
		for device in self.devList:
			txt = device.label + "\t" + device.devicefile
			if device.mounted():
				txt += "\t" + device.mountpoint
			strlist.append(txt)
		return strlist
	# }}}

if __name__ == '__main__':
	mountie = Mountie()
	mountie.cursesInterface.start_interface()
