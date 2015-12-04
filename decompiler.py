import sys, struct

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

class Vm:
	codes = ['halt', 'set', 'push', 'pop', 'eq', 'gt', 'jmp', 'jt', 'jf', 'add', 'mult', 'mod', 'and', 'or', 'not', 'rmem', 'wmem', 'call', 'ret', 'out', 'in', 'noop']

	def __init__(self):
		self.memory = Memory()
		self.position = 5900
		self.running = True
		self.unpacker = struct.Struct('<H')

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

	def run(self, start, numcodes):
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

		if start != "":
			self.position = int(start)

		if numcodes == "":
			numcodes = 100
		else:
			numcodes = int(numcodes)

		i = 0

		while self.running and i <= numcodes:
			instruction = self.memory.at(self.position)
			try:
				code = Vm.codes[self.u(instruction)]
				print str(self.position) + " (" + str(hex(self.position * 2)) + "): " + dispatch[code]()
				i += 1
			except Exception, e:
				self.advance()

	def u(self, data):
		"""unpacks the data using self.unpacker"""
		return self.unpacker.unpack(data)[0]
	def p(self, value):
 		"""packs the value using self.unpacker"""
 		return self.unpacker.pack(value)
	def advance(self, increment=1):
		"""advances the memory register by increment."""
		self.position += increment
	def resolve(self, data, trueResolve = False):
		"""return string representation of data if literal, return strrep of register index if register address."""
		unpacked = self.u(data)
		if(unpacked < 32768):
			if (trueResolve):
				return data
			else:
				return str(unpacked)
		else:
			register_index = unpacked - 32768
			return "<" + str(register_index) + ">"
	def opcodeHalt(self):
		"""stop execution and terminate the program. syntax: 0"""
		self.advance()
		return "HALT"
	def opcodeSet(self):
		"""set register <a> to the value of <b>. syntax: 1 a b"""
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		self.advance()
		return r"SET <{0}> {1}".format(register_index, b)
	def opcodePush(self):
		"""push <a> onto the stack. syntax: 2 a"""
		self.advance()
		at = self.memory.at(self.position)
		a = self.resolve(at)
		self.advance()
		return r"PUSH {0}".format(a)
	def opcodePop(self):
		"""remove the top element from the stack and write it into <a>; empty stack = error. syntax: 3 a"""
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()

		return r"POP <{0}>".format(register_index)
	def opcodeEq(self):
		"""set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise. syntax: 4 a b c"""
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

		return r"EQ <{0}> {1} {2}".format(register_index, b, c)
	def opcodeGt(self):
		"""set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise. syntax: 5 a b c"""
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

		return r"GT <{0}> {1} {2}".format(register_index, b, c)
	def opcodeJmp(self):
		"""jump to memory location <a>. syntax: 6 a"""
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		self.advance()
		return r"JMP {0}".format(a)
	def opcodeJt(self):
		"""if <a> is nonzero, jump to <b>. syntax: 7 a b"""
		self.advance()
		a_at = self.memory.at(self.position)
		a = self.resolve(a_at)
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()
		return r"JT {0} {1}".format(a, b)
		
	def opcodeJf(self):
		"""if <a> is zero, jump to <b>. syntax: 8 a b"""
		self.advance()
		a_at = self.memory.at(self.position)
		a = self.resolve(a_at)
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()
		return r"JF {0} {1}".format(a, b)
		
	def opcodeAdd(self):
		"""assign into <a> the sum of <b> and <c> (modulo 32768). syntax: 9 a b c"""
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

		return r"ADD <{0}> {1} {2}".format(register_index, b, c)
	def opcodeMult(self):
		"""store into <a> the product of <b> and <c> (modulo 32768). syntax: 10 a b c"""
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

		return r"MULT <{0}> {1} {2}".format(register_index, b, c)
	def opcodeMod(self):
		"""store into <a> the remainder of <b> divided by <c>. syntax: 11 a b c"""
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

		return r"MOD <{0}> {1} {2}".format(register_index, b, c)
	def opcodeAnd(self):
		"""stores into <a> the bitwise and of <b> and <c>. syntax: 12 a b c"""
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

		return r"AND <{0}> {1} {2}".format(register_index, b, c)
	def opcodeOr(self):
		"""stores into <a> the bitwise or of <b> and <c>. syntax: 13 a b c"""
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

		return r"OR <{0}> {1} {2}".format(register_index, b, c)
	def opcodeNot(self):
		"""stores 15-bit bitwise inverse of <b> in <a>. syntax: 14 a b"""
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(self.memory.at(self.position))
		self.advance()

		return r"NOT <{0}> {1}".format(register_index, b)
	def opcodeRmem(self):
		"""read memory at address <b> and write it to <a>. syntax: 15 a b"""
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)

		self.advance()

		return r"RMEM <{0}> {1}".format(register_index, b)
	def opcodeWmem(self):
		"""write the value from <b> into memory at address <a>. syntax: 16 a b"""
		self.advance()

		a_at = self.memory.at(self.position)
		a = self.resolve(a_at)
		self.advance()

		b_at = self.memory.at(self.position)
		b = self.resolve(b_at)
		self.advance()

		return r"WMEM {0} {1}".format(a, b)
	def opcodeCall(self):
		"""write the address of the next instruction to the stack and jump to <a>. syntax: 17 a"""
		self.advance()
		a_at = self.memory.at(self.position)
		a = self.resolve(a_at)
		self.advance()
		return_address = self.position
		return r"CALL {0}".format(a)

	def opcodeRet(self):
		"""remove the top element from the stack and jump to it; empty stack = halt. syntax: 18"""
		self.advance()
		return r"RET"
		
	def opcodeOut(self):
		"""write the character represented by ascii code <a> to the terminal. syntax: 19 a"""
		self.advance()
		a = self.resolve(self.memory.at(self.position), True)
		char = a.decode(encoding="ASCII")

		self.advance()
		return r"OUT {0}".format(char.replace("\n", "\\n"))
	def opcodeIn(self):
		"""read a character from the terminal and write its ascii code to <a>. syntax: 20 a"""
		self.advance()

		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()

		return r"IN <{0}>".format(register_index)
	def opcodeNoop(self):
		self.advance()
		return r"NOOP"

vm = Vm()

vm.loadFile("001.mem")

vm.run(sys.argv[1], sys.argv[2])