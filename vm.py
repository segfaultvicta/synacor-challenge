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

	def __init__(self):
		self.memory = Memory()

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

	def debug(self):
		print ("Hey look, it's working!")
		size_of_memory = self.memory.size()
		print("Size of memory is {0}".format(size_of_memory))
		print('Memory at memloc 100 is {0}'.format(self.memory.at(100)))

vm = Vm()
vm.loadFile("challenge.bin")

vm.debug()