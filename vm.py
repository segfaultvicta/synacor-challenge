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
			logging.debug("Request made to register {0} and is being summarily ignored, lol".format(register))
			return data

	def opcodeHalt(self):
		"""stop execution and terminate the program. syntax: 0"""
		logging.debug("HALT")
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
		self.advance()
	def opcodeJt(self):
		self.advance()
	def opcodeJf(self):
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
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		logging.debug("OUT {0}".format(a))
		char = a.decode(encoding="ASCII")
		sys.stdout.write(char)
		self.advance()
	
	def opcodeIn(self):
		self.advance()
	
	def opcodeNoop(self):
		logging.debug("NOOP")
		self.advance()


logging.basicConfig(filename="synacorchallenge.log",filemode="w",level=logging.DEBUG)

vm = Vm()
logging.debug("VM initialised, loading challenge.bin...")
vm.loadFile("challenge.bin")
logging.debug("Challenge binary loaded into memory. Running VM...")
vm.run()