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

class Vm:
	codes = ['halt', 'set', 'push', 'pop', 'eq', 'gt', 'jmp', 'jt', 'jf', 'add', 'mult', 'mod', 'and', 'or', 'not', 'rmem', 'wmem', 'call', 'ret', 'out', 'in', 'noop']

	def __init__(self):
		self.memory = Memory()
		self.stack = []
		self.position = 0
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
			logging.debug("Instruction read as {0}, converting to integer to lookup opcode...".format(instruction))
			code = Vm.codes[self.u(instruction)]
			logging.debug("Encountered opcode {0}, calling function...".format(code))
			dispatch[code]()

	def u(self, data):
		"""unpacks the data using self.unpacker"""
		return self.unpacker.unpack(data)[0]

	def advance(self, increment=1):
		"""advances the memory register by increment."""
		self.position += increment

	def resolve(self, data):
		"""return data if data is a literal value, return register contents if data is a register address."""
		unpacked = self.u(data)
		if(unpacked < 32768):
			return data
		else:
			register = unpacked - 32768
			logging.warning("Request made to register {0} and is being summarily ignored, lol".format(register))
			return data

	def opcodeHalt(self):
		"""stop execution and terminate the program. syntax: 0"""
		logging.info("{0}: HALT".format(self.position))
		self.running = False

	def opcodeSet(self):
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
		logging.info("{0}: JMP {1} (jmp {2})".format(initial, a, self.u(a)))
		self.position = self.u(a)

	def opcodeJt(self):
		"""if <a> is nonzero, jump to <b>. syntax: 7 a b"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		logging.info("{0}: JT {1} {2} (jt {3} {4})".format(initial, a, b, self.u(a), self.u(b)))
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
		logging.info("{0}: JF {1} {2} (jf {3} {4})".format(initial, a, b, self.u(a), self.u(b)))
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
		logging.info("{0}: OUT {1} (out {2})".format(initial, a,char.replace("\n", "\\n")))
		sys.stdout.write(char)
		self.advance()
	
	def opcodeIn(self):
		self.advance()
	
	def opcodeNoop(self):
		logging.info("{0}: NOOP".format(self.position))
		self.advance()


logging.basicConfig(filename="synacorchallenge.log",filemode="w",level=logging.INFO)

vm = Vm()
logging.debug("VM initialised, loading challenge.bin...")
vm.loadFile("challenge.bin")
logging.debug("Challenge binary loaded into memory. Running VM...")
vm.run()