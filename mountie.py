# Copyright 2012 Daniel Anthofer
# Modification and distribution under terms of
# GNU GPL v. 3 is permitted
# http://www.gnu.org/licenses/gpl-3.0.txt

import curses_interface
import dbus_connection
import os

class Mountie:
	
	def __init__(self): # {{{
		self.devList = dbus_connection.createDevList()
		self.comdict = { \
			109 : self.toggleMounted, \
			111 : self.openFilesystem, \
			108 : self.openFilesystem \
		}
		self.helpstr = "up/down: k/j\tmount/unmount: m\topen: o/l\tquit: q"
		self.cursesInterface = curses_interface.CursesInterface( \
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

mountie = Mountie()
mountie.cursesInterface.start_interface()
