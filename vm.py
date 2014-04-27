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
		"""push <a> onto the stack. syntax: 2 a"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		self.advance()

		logging.info("{0}: PUSH {1} (push {2} to the stack)".format(initial, a, self.u(a)))
		self.stack.append(a)

	def opcodePop(self):
		"""remove the top element from the stack and write it into <a>; empty stack = error. syntax: 3 a"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()

		data = self.stack.pop()

		logging.info("{0}: POP {1} (pop {2} from the stack and write to :{3}".format(initial, a, data, register_index))
		self.registers[register_index].set(data)

	def opcodeEq(self):
		"""set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise. syntax: 4 a b c"""
		initial = self.position
		self.advance()

		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()

		b = self.resolve(self.memory.at(self.position))
		self.advance()

		c = self.resolve(self.memory.at(self.position))
		self.advance()

		logging.info("{0}: EQ {1} {2} {3} (if {4} = {5}, set :{6} to 1. Else set it to 0)".format(initial, a, b, c, self.u(b), self.u(c), register_index))

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

		b = self.resolve(self.memory.at(self.position))
		self.advance()

		c = self.resolve(self.memory.at(self.position))
		self.advance()

		logging.info("{0}: GT {1} {2} {3} (if {4} > {5}, set :{6} to 1. Else set it to 0)".format(initial, a, b, c, self.u(b), self.u(c), register_index))

		if(self.u(b) > self.u(c)):
			self.registers[register_index].set(self.p(1))
		else:
			self.registers[register_index].set(self.p(0))
	
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
		"""assign into <a> the sum of <b> and <c> (modulo 32768). syntax: 9 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		self.advance()
		c = self.resolve(self.memory.at(self.position))
		self.advance()

		logging.info("{0}: ADD {1} {2} {3} (add {4} and {5} and place the result in :{6})".format(initial, a, b, c, self.u(b), self.u(c), register_index))

		int_b = self.u(b)
		int_c = self.u(c)
		result = (int_b + int_c) % 32768

		logging.debug("{0} + {1} = {2}".format(int_b, int_c, result))
		self.registers[register_index].set(self.p(result)) 

	def opcodeMult(self):
		"""store into <a> the product of <b> and <c> (modulo 32768). syntax: 10 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		self.advance()
		c = self.resolve(self.memory.at(self.position))
		self.advance()

		logging.info("{0}: MULT {1} {2} {3} (multiply {4} and {5} and place the result in :{6})".format(initial, a, b, c, self.u(b), self.u(c), register_index))

	def opcodeMod(self):
		"""store into <a> the remainder of <b> divided by <c>. syntax: 11 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		self.advance()
		c = self.resolve(self.memory.at(self.position))
		self.advance()

		logging.info("{0}: MOD {1} {2} {3} (divide {4} and {5} and store the remainder in :{6})".format(initial, a, b, c, self.u(b), self.u(c), register_index))

	def opcodeAnd(self):
		"""stores into <a> the bitwise and of <b> and <c>. syntax: 12 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		self.advance()
		c = self.resolve(self.memory.at(self.position))
		self.advance()

		logging.info("{0}: AND {1} {2} {3} (store the bitwise and of {4} and {5} in :{6})".format(initial, a, b, c, self.u(b), self.u(c), register_index))

		int_b = self.u(b)
		int_c = self.u(c)
		result = int_b & int_c
		logging.debug("{0} & {1} = {2}".format(int_b, int_c, result))

		self.registers[register_index].set(self.p(result))

	def opcodeOr(self):
		"""stores into <a> the bitwise or of <b> and <c>. syntax: 13 a b c"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		self.advance()
		c = self.resolve(self.memory.at(self.position))
		self.advance()

		logging.info("{0}: OR {1} {2} {3} (store the bitwise or of {4} and {5} in :{6})".format(initial, a, b, c, self.u(b), self.u(c), register_index))

		int_b = self.u(b)
		int_c = self.u(c)
		result = int_b | int_c
		logging.debug("{0} | {1} = {2}".format(int_b, int_c, result))

		self.registers[register_index].set(self.p(result))

	def opcodeNot(self):
		"""stores 15-bit bitwise inverse of <b> in <a>. syntax: 14 a b"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		self.advance()

		logging.info("{0}: NOT {1} {2} (store the bitwise not of {3} in :{4})".format(initial, a, b, self.u(b), register_index))

		result = (~(self.u(b)) & ((1 << 15) - 1))
		logging.debug("~{0} = {1}".format(b, result))

		self.registers[register_index].set(self.p(result))

	def opcodeRmem(self):
		"""read memory at address <b> and write it to <a>. syntax: 15 a b"""
		initial = self.position
		self.advance()
		a = self.memory.at(self.position)
		register_index = self.u(a) - 32768
		self.advance()
		b = self.resolve(self.memory.at(self.position))
		#b contains the address which we need to read
		readdata = self.resolve(self.memory.at(self.u(b)))
		self.advance()

		logging.info("{0}: RMEM {1} {2} (read {3} at address {4} and write it to :{5})".format(initial, a, b, readdata, self.u(b), register_index))

	def opcodeWmem(self):
		"""write the value from <b> into memory at address <a>. syntax: 16 a b"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		self.advance()
		b = self.memory.at(self.position)
		register_index = self.u(b) - 32768
		readdata = self.registers[register_index].get()
		self.advance()

		logging.info("{0}: WMEM {1} {2} (write {3} from :{4} into memory at address {5})".format(initial, a, b, readdata, register_index, self.u(b)))

	def opcodeCall(self):
		"""write the address of the next instruction to the stack and jump to <a>. syntax: 17 a"""
		initial = self.position
		self.advance()
		a = self.resolve(self.memory.at(self.position))
		self.advance()
		return_address = self.position

		logging.info("{0}: CALL {1} (writing next instruction address ({2}) to stack and jumping to {3})".format(initial, a, return_address, self.u(a)))
		self.stack.append(self.p(return_address))
		self.position = self.u(a)

	def opcodeRet(self):
		"""remove the top element from the stack and jump to it; empty stack = halt. syntax: 18"""
		return_address = self.stack.pop()
		logging.info("{0}: RET (returning to {1})".format(self.position, return_address))
		self.position = return_address
	
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
		"""read a character from the terminal and write its ascii code to <a>. syntax: 20 a"""
		initial = self.position
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