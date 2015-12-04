import sys, struct, logging
global bump

class Memory:
	def __init__(self):
		self.store = []

	def load(self, dump):
		self.store = dump

	def size(self):
		return len(self.store)

	def at(self, memloc):
		return self.store[memloc]

	def write(self, memloc, data):
		self.store[memloc] = data

	def dump(self):
		return self.store

class Register:
	global bump
	def __init__(self, initial_value, register_index, vm):
		self.value = initial_value
		self.index = register_index #for debugging purposes
		self.vm = vm

	def set(self, value):
		bump.debug(r":{0} <-- {1}".format(self.index, self.vm.u(value)))
		self.value = value

	def get(self):
		return self.value

class Vm:
	codes = ['halt', 'set', 'push', 'pop', 'eq', 'gt', 'jmp', 'jt', 'jf', 'add', 'mult', 'mod', 'and', 'or', 'not', 'rmem', 'wmem', 'call', 'ret', 'out', 'in', 'noop']
	global bump

	def __init__(self):
		self.memory = Memory()
		self.registers = []
		self.stack = []
		self.position = 0
		self.running = True
		self.unpacker = struct.Struct('<H')
		for i in range(8):
			self.registers.append(Register(self.p(0), i, self))

	def loadFile(self, filename):
		dump = []
		for word in self.readFile(filename):
			dump.append(word)
		self.memory.load(dump)
	def readFile(self, filename):
		with open(filename, "rb") as f:
			while True:
				word = f.read(2)
				if word:
					yield word
				else:
					break

	def run(self):
		dispatch = {
			'halt': self.opcodeHalt,
			'set': self.opcodeSet,
			'push': self.opcodePush,
			'pop': self.opcodePop,
			'eq': self.opcodeEq,
			'gt': self.opcodeGt,
			'jmp': self.opcodeJmp,
			'jt': self.opcodeJt,
			'jf': self.opcodeJf,
			'add': self.opcodeAdd,
			'mult': self.opcodeMult,
			'mod': self.opcodeMod,
			'and': self.opcodeAnd,
			'or': self.opcodeOr,
			'not': self.opcodeNot,
			'rmem': self.opcodeRmem,
			'wmem': self.opcodeWmem,
			'call': self.opcodeCall,
			'ret': self.opcodeRet,
			'out': self.opcodeOut,
			'in': self.opcodeIn,
			'noop': self.opcodeNoop
		}

		while self.running:
			instruction = self.memory.at(self.position)
			code = Vm.codes[self.u(instruction)]
			dispatch[code]()

	def u(self, data):
		"""unpacks the data using self.unpacker"""
		return self.unpacker.unpack(data)[0]
	def p(self, value):
 		"""packs the value using self.unpacker"""
 		return self.unpacker.pack(value)
	def advance(self, increment=1):
		"""advances the memory register by increment."""
		self.position += increment
	def resolve(self, data):
		"""return data if data is a literal value, return register contents if data is a register address."""
		unpacked = self.u(data)
		if(unpacked < 32768):
			return data
		else:
			register_index = unpacked - 32768
			data = self.registers[register_index].get()
			return data
	def debugresolve(self, data):
		"""return string representation of data if literal, return strrep of register index if register address."""
		unpacked = self.u(data)
		if(unpacked < 32768):
			return str(unpacked)
		else:
			register_index = unpacked - 32768
			data = self.registers[register_index].get()
			return ":" + str(register_index) + "(" + str(self.u(data)) + ")"
	def opcodeHalt(self):
		"""stop execution and terminate the program. syntax: 0"""
		bump.debug("{0}: HALT".format(self.position))
		self.running = False
	def opcodeSet(self):
		"""set register <a> to the value of <b>. syntax: 1 a b"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		bump.debug("{0}: SET :{1} {2}".format(initial, register_index, self.debugresolve(b)))
		self.registers[register_index].set(b)
		self.advance()
	def opcodePush(self):
		"""push <a> onto the stack. syntax: 2 a"""
		initial = self.position
		self.advance()
		at = self.memory.at(self.position)
		a = self.resolve(at)
		self.advance()
		bump.debug("{0}: PUSH {1}".format(initial, self.debugresolve(at)))
		self.stack.append(a)
		bump.debug("{0} elements in stack.".format(len(self.stack)))
	def opcodePop(self):
		"""remove the top element from the stack and write it into <a>; empty stack = error. syntax: 3 a"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()

		data = self.stack.pop()

		bump.debug("{0}: POP :{1} ({2})".format(initial, register_index, self.u(data)))
		self.registers[register_index].set(data)
		bump.debug("{0} elements in stack.".format(len(self.stack)))
	def opcodeEq(self):
		"""set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise. syntax: 4 a b c"""
		initial = self.position
		self.advance()

		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()

		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()

		c_at = self.memory.at(self.position)
		c = self.resolve(c_at)
		self.advance()

		bump.debug("{0}: EQ :{1} {2} {3}".format(initial, register_index, self.debugresolve(b_at), self.debugresolve(c_at)))

		if(b == c):
			self.registers[register_index].set(self.p(1))
		else:
			self.registers[register_index].set(self.p(0))
	def opcodeGt(self):
		"""set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise. syntax: 5 a b c"""
		initial = self.position
		self.advance()

		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()

		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()

		c_at = self.memory.at(self.position)
		c = self.resolve(c_at)
		self.advance()

		bump.debug("{0}: GT :{1} {2} {3}".format(initial, register_index, self.debugresolve(b_at), self.debugresolve(c_at)))

		if(self.u(b) > self.u(c)):
			self.registers[register_index].set(self.p(1))
		else:
			self.registers[register_index].set(self.p(0))
	def opcodeJmp(self):
		"""jump to memory location <a>. syntax: 6 a"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		bump.debug("{0}: JMP {1}".format(initial, self.debugresolve(a)))
		self.position = self.u(a)
	def opcodeJt(self):
		"""if <a> is nonzero, jump to <b>. syntax: 7 a b"""
		initial = self.position
		self.advance()
		a_at = self.memory.at(self.position)
		a = self.resolve(a_at)
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		bump.debug("{0}: JT {1} {2}".format(initial, self.debugresolve(a_at), self.debugresolve(b_at)))
		if(self.u(a) != 0):
			self.position = self.u(b)
		else:
			self.advance()
	def opcodeJf(self):
		"""if <a> is zero, jump to <b>. syntax: 8 a b"""
		initial = self.position
		self.advance()
		a_at = self.memory.at(self.position)
		a = self.resolve(a_at)
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		bump.debug("{0}: JF {1} {2}".format(initial, self.debugresolve(a_at), self.debugresolve(b_at)))
		if(self.u(a) == 0):
			self.position = self.u(b)
		else:
			self.advance()
	def opcodeAdd(self):
		"""assign into <a> the sum of <b> and <c> (modulo 32768). syntax: 9 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()
		c_at = self.memory.at(self.position)
		c = self.resolve(c_at)
		self.advance()

		bump.debug("{0}: ADD :{1} {2} {3}".format(initial, register_index, self.debugresolve(b_at), self.debugresolve(c_at)))

		int_b = self.u(b)
		int_c = self.u(c)
		result = (int_b + int_c) % 32768

		self.registers[register_index].set(self.p(result))
	def opcodeMult(self):
		"""store into <a> the product of <b> and <c> (modulo 32768). syntax: 10 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()
		c_at = self.memory.at(self.position)
		c = self.resolve(c_at)
		self.advance()

		bump.debug("{0}: MULT :{1} {2} {3}".format(initial, register_index, self.debugresolve(b_at), self.debugresolve(c_at)))

		int_b = self.u(b)
		int_c = self.u(c)
		result = (int_b * int_c) % 32768

		self.registers[register_index].set(self.p(result))
	def opcodeMod(self):
		"""store into <a> the remainder of <b> divided by <c>. syntax: 11 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()
		c_at = self.memory.at(self.position)
		c = self.resolve(c_at)
		self.advance()

		bump.debug("{0}: MOD :{1} {2} {3}".format(initial, register_index, self.debugresolve(b_at), self.debugresolve(c_at)))

		int_b = self.u(b)
		int_c = self.u(c)
		result = int_b % int_c

		self.registers[register_index].set(self.p(result))
	def opcodeAnd(self):
		"""stores into <a> the bitwise and of <b> and <c>. syntax: 12 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()
		c_at = self.memory.at(self.position)
		c = self.resolve(c_at)
		self.advance()

		bump.debug("{0}: AND :{1} {2} {3}".format(initial, register_index, self.debugresolve(b_at), self.debugresolve(c_at)))

		int_b = self.u(b)
		int_c = self.u(c)
		result = int_b & int_c

		self.registers[register_index].set(self.p(result))
	def opcodeOr(self):
		"""stores into <a> the bitwise or of <b> and <c>. syntax: 13 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()
		c_at = self.memory.at(self.position)
		c = self.resolve(c_at)
		self.advance()

		bump.debug("{0}: OR :{1} {2} {3}".format(initial, register_index, self.debugresolve(b_at), self.debugresolve(c_at)))

		int_b = self.u(b)
		int_c = self.u(c)
		result = int_b | int_c

		self.registers[register_index].set(self.p(result))
	def opcodeNot(self):
		"""stores 15-bit bitwise inverse of <b> in <a>. syntax: 14 a b"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(self.memory.at(self.position))
		self.advance()

		bump.debug("{0}: NOT :{1} {2}".format(initial, register_index, self.debugresolve(b_at)))

		result = (~(self.u(b)) & ((1 << 15) - 1))

		self.registers[register_index].set(self.p(result))
	def opcodeRmem(self):
		"""read memory at address <b> and write it to <a>. syntax: 15 a b"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		#b contains the address which we need to read
		readdata = self.resolve(self.memory.at(self.u(b)))
		self.advance()

		bump.debug("{0}: RMEM :{1} {2}".format(initial, register_index, self.debugresolve(b_at)))
		self.registers[register_index].set(readdata)
	def opcodeWmem(self):
		"""write the value from <b> into memory at address <a>. syntax: 16 a b"""
		initial = self.position
		self.advance()

		a_at = self.memory.at(self.position)
		a = self.resolve(a_at)
		self.advance()

		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()

		bump.debug("{0}: WMEM {1} {2}".format(initial, self.debugresolve(a_at), self.debugresolve(b_at)))
		self.memory.write(self.u(a),b)
	def opcodeCall(self):
		"""write the address of the next instruction to the stack and jump to <a>. syntax: 17 a"""
		initial = self.position
		self.advance()
		a_at = self.memory.at(self.position)
		a = self.resolve(a_at)
		self.advance()
		return_address = self.position

		bump.debug("{0}: CALL {1} (writing next instruction address ({2}) to stack)".format(initial, self.debugresolve(a_at), return_address))
		self.stack.append(self.p(return_address))
		self.position = self.u(a)
	def opcodeRet(self):
		"""remove the top element from the stack and jump to it; empty stack = halt. syntax: 18"""
		return_address = self.stack.pop()
		bump.debug("{0}: RET (returning to {1})".format(self.position, self.u(return_address)))
		self.position = self.u(return_address)
	def opcodeOut(self):
		"""write the character represented by ascii code <a> to the terminal. syntax: 19 a"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		char = a.decode(encoding="ASCII")
		bump.debug("{0}: OUT {1}".format(initial,char.replace("\n", "\\n")))
		sys.stdout.write(char)
		self.advance()
	def opcodeIn(self):
		"""read a character from the terminal and write its ascii code to <a>. syntax: 20 a"""
		ch = sys.stdin.read(1)

		if ch == "!":
			bump.debug("WARNING: BECOMING SELF-AWARE")
			self.aware()
		else:
			initial = self.position
			self.advance()

			a = self.memory.at(self.position)
			register_index = self.u(a) - 32768
			self.advance()

			bump.debug("{0}: IN :{1}".format(initial, register_index))

			self.registers[register_index].set(self.p(ord(ch)))
	def opcodeNoop(self):
		bump.debug("{0}: NOOP".format(self.position))
		self.advance()

	def aware(self):
		# munch the rest of the line from stdin and see if it's a recognised command
		line = sys.stdin.readline()
		w = line.split(' ')
		fw = w[0].strip()
		print fw
		if fw == "save":
			filename = "";
			try:
				filename = w[1].strip()
			except Exception, e:
				filename = "001"
			print ">>> Save to: " + filename + "\n"
			memfilename = filename + ".mem"
			f = open(filename, 'w')
			f2 = open(memfilename, 'w')
			f.write(str(self.position) + "\n")
			for reg in self.registers:
				f.write(str(self.u(reg.get())) + "\n")
			for i in self.stack:
				f.write(str(self.u(i)) + "\n");
			for m in self.memory.dump():
				f2.write(m)
			f.close()
			f2.close()
		elif fw == "load":
			filename = "";
			try:
				filename = w[1].strip()
			except Exception, e:
				filename = "001"
			print ">>> Load from: " + filename + "\n"
			memfilename = filename + ".mem"
			f = open(filename, 'r')
			position_str = f.readline()
			self.position = int(position_str)
			for reg_n in xrange(0,7):
				self.registers[reg_n].set(self.p(int(f.readline())))
			self.stack = []
			for line in f:
				self.stack.append(self.p(int(line)))
			self.loadFile(memfilename)
			f.close()
		elif fw == "setreg":
			# do another thing
			reg_n = int(w[1].strip())

			reg_data = self.p(int(w[2].strip()))
			print r">>> Setting Register {0} to {1}".format(reg_n, reg_data)
			self.registers[reg_n].set(reg_data)
		elif fw == "barfreg":
			i = 0
			for reg in self.registers:
				print r">>> Register {0} contains {1}".format(i, self.u(reg.get()))
				i += 1
		elif fw == "barfstack":
			i = 0
			for item in self.stack:
				print r">>> Stack @{0} contains {1}".format(i, self.u(item))
				i += 1
		elif fw == "logging":
			print ">>> Logging!"
			if w[1].strip() == "on":
				print ">>> Logging: ON"
				bump.flag(True)
			elif w[1].strip() == "off":
				print ">>> Logging: OFF"
				bump.flag(False)
		else:
			print ">>> Unrecognised command."

class Bump:
	def __init__(self, filename, vm, initialFlag):
		self.vm = vm
		self.debugFlag = initialFlag
		self.dest = open(filename, 'w')

	def debug(self, string):
		# log string if self.debug is true
		if(self.debugFlag):
			logging.debug(string)

	def flag(self, onIfTrue):
		self.debugFlag = onIfTrue


vm = Vm()

logging.basicConfig(filename='challenge.log', level=logging.DEBUG)

bump = Bump("challenge.log", vm, False)

vm.loadFile("challenge.bin")
vm.run()
