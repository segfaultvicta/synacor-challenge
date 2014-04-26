import sys, struct, logging

class Memory:
	def __init__(self):
		self.store = []

	def load(self, dump):
		self.store = dump

	def size(self):
		return len(self.store)

	def at(self, memloc):
		return self.store[memloc]

class Register:
	def __init__(self, initial_value, register_index):
		self.value = initial_value
		self.index = register_index #for debugging purposes

	def set(self, value):
		logging.debug("Setting register {0} with data {1}".format(self.index, value))
		self.value = value

	def get(self):
		logging.debug("Fetching register {0} value: {1}".format(self.index, self.value))
		return self.value

class Vm:
	codes = ['halt', 'set', 'push', 'pop', 'eq', 'gt', 'jmp', 'jt', 'jf', 'add', 'mult', 'mod', 'and', 'or', 'not', 'rmem', 'wmem', 'call', 'ret', 'out', 'in', 'noop']

	def __init__(self):
		self.memory = Memory()
		self.registers = []
		self.stack = []
		self.position = 0
		self.running = True
		self.unpacker = struct.Struct('<H')
		for i in range(8):
			self.registers.append(Register(self.p(0), i))

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
			logging.info("------------------------")
			instruction = self.memory.at(self.position)
			code = Vm.codes[self.u(instruction)]
			logging.debug("{0}: instruction {1} resolves as opcode {2}".format(self.position, instruction, code))
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

	def opcodeHalt(self):
		"""stop execution and terminate the program. syntax: 0"""
		logging.info("{0}: HALT".format(self.position))
		self.running = False

	def opcodeSet(self):
		"""set register <a> to the value of <b>. syntax: 1 a b"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		logging.info("{0}: SET {1} {2} (set value of register :{3} to {4})".format(initial, a, b, register_index, self.u(b)))
		self.registers[register_index].set(b)
		self.advance()

	def opcodePush(self):
		self.advance()

	def opcodePop(self):
		self.advance()

	def opcodeEq(self):
		self.advance()

	def opcodeGt(self):
		self.advance()
	
	def opcodeJmp(self):
		"""jump to memory location <a>. syntax: 6 a"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		logging.info("{0}: JMP {1} (jump to {2})".format(initial, a, self.u(a)))
		self.position = self.u(a)

	def opcodeJt(self):
		"""if <a> is nonzero, jump to <b>. syntax: 7 a b"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		logging.info("{0}: JT {1} {2} (if {3} is nonzero, jump to {4})".format(initial, a, b, self.u(a), self.u(b)))
		if(self.u(a) != 0):
			self.position = self.u(b)
		else:
			self.advance()

	def opcodeJf(self):
		"""if <a> is zero, jump to <b>. syntax: 8 a b"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		logging.info("{0}: JF {1} {2} (if {3} is zero, jump to {4})".format(initial, a, b, self.u(a), self.u(b)))
		if(self.u(a) == 0):
			self.position = self.u(b)
		else:
			self.advance()

	def opcodeAdd(self):
		self.advance()

	def opcodeMult(self):
		self.advance()

	def opcodeMod(self):
		self.advance()

	def opcodeAnd(self):
		self.advance()

	def opcodeOr(self):
		self.advance()

	def opcodeNot(self):
		self.advance()

	def opcodeRmem(self):
		self.advance()

	def opcodeWmem(self):
		self.advance()

	def opcodeCall(self):
		self.advance()

	def opcodeRet(self):
		self.advance()
	
	def opcodeOut(self):
		"""write the character represented by ascii code <a> to the terminal. syntax: 19 a"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		char = a.decode(encoding="ASCII")
		logging.info("{0}: OUT {1} (print {2} to the terminal)".format(initial, a,char.replace("\n", "\\n")))
		sys.stdout.write(char)
		self.advance()
	
	def opcodeIn(self):
		self.advance()
	
	def opcodeNoop(self):
		logging.info("{0}: NOOP".format(self.position))
		self.advance()


logging.basicConfig(filename="synacorchallenge.log",filemode="w",level=logging.DEBUG)

vm = Vm()
logging.debug("VM initialised, loading challenge.bin...")
vm.loadFile("challenge.bin")
logging.debug("Challenge binary loaded into memory. Running VM...")
vm.run()