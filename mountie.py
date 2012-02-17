# Copyright 2012 Daniel Anthofer
# Modification and distribution under terms of
# GNU GPL v. 3 is permitted
# http://www.gnu.org/licenses/gpl-3.0.txt

import dbus_connection

# this implementation of a userinterface only serves
# as a testbed and is not yet suitable for everyday usage

commandList = dict()
devList = dbus_connection.createDevList()

def mount_fs(number_str): # {{{
	number = int(number_str)
	if not devList[number:]:
		print("invalid index")
		return
	devList[number].mount()
	print("mountpoint",devList[number].mountpoint)
# }}}
commandList['mount'] = mount_fs

def unmount_fs(number_str): # {{{
	number = int(number_str)
	if not devList[number:]:
		print("invalid index")
		return
	try:
		devList[number].unmount()
	except:
		if devList[number].mounted():
			print("device busy")
		else:
			print("device not mounted")
# }}}
commandList['unmount'] = unmount_fs

def list_fs(): # {{{
	count = 0
	for i in devList:
		print(count,i.devicefile)
		count += 1
# }}}
commandList['list'] = list_fs

def exit_prog(): # {{{
  quit()
# }}}
commandList['exit'] = exit_prog

inputString = ['']

while True:
	inputString = input("-->").split()
	if inputString[1:]:
		try:
			commandList[inputString[0]](inputString[1])
		except KeyError: #wrong command
			print('mount number; unmount number; list; exit')
		except TypeError: #wrong number or type of arguments
			print('mount number; unmount number; list; exit')
	else:
		try:
			commandList[inputString[0]]()
		except KeyError: #wrong command
			print('mount number; unmount number; list; exit')
		except TypeError: #wrong number or type of arguments
			print('mount number; unmount number; list; exit')
