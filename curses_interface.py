# Copyright 2012 Daniel Anthofer
# Modification and distribution under terms of
# GNU GPL v. 3 is permitted
# http://www.gnu.org/licenses/gpl-3.0.txt

'''create a simple line-based curses interface'''

import curses

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
			if c in self.comdict.keys(): 
				self.errortext = self.comdict[c](self.cursorline - 1)
			elif c == curses.KEY_UP or c == 107: #k
				if self.cursorline > 1:
					self.cursorline -=1
			elif c == curses.KEY_DOWN or c == 106: #j
				if self.cursorline < len(self.strlist):
					self.cursorline +=1
			elif c == 27 or c == 113: #ESC or q
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
