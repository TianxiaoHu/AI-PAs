class PriorityQueue(object):

	def __init__(self):
		self.data = []

	def queue_index(self, node):
		nodes = [x[0] for x in self.data]
		if node in nodes:
			return nodes.index(node)
		else:
			return None

	def put_and_update(self, node, cost, path):
		node_index = self.queue_index(node)
		if node_index != None and self.data[node_index][1] > cost:
			self.data[node_index][1] = cost
			self.data[node_index][2] = path
		elif node_index == None:
			self.data.append([node, cost, path])
		self.data = sorted(self.data, key=lambda x: x[1])

	def pop(self):
		if self.empty():
			print 'Warning: queue %s is empty', self.__name__
			return None
		else:
			return self.data.pop(0)

	def empty(self):
		return len(self.data) == 0

	def __repr__(self):
		return '<Priority Queue> ' + str(self.data)


class Node(object):

	def __init__(self, name):
		self.name = name
		self.neighbor = {}

	def add_edge(self, node, cost):
		if self.neighbor.has_key(node.name) and self.neighbor[node.name] > cost:
			self.neighbor[node.name] = cost
		elif not self.neighbor.has_key(node.name):
			self.neighbor[node.name] = cost

	def show_edge(self):
		print self.neighbor

	def __repr__(self):
		return '<Node> ' + self.name


class Graph(object):

	def __init__(self):
		self.nodedict = {}

	def add_node(self, new_node):
		self.nodedict[new_node.name] = new_node

	def have_node(self, node_name):
		return self.nodedict.has_key(node_name)

	def is_empty(self):
		return len(self.nodedict) == 0

	def clear(self):
		self.nodedict = dict()

	def __repr__(self):
		return str(self.nodedict)


def add_edge_from_input(line):
	[spoint, epoint, cost] = line.strip().split(' ')

	if not graph.have_node(spoint):
		newnode = Node(spoint)
		graph.add_node(newnode)
	if not graph.have_node(epoint):
		newnode = Node(epoint)
		graph.add_node(newnode)

	graph.nodedict[spoint].add_edge(graph.nodedict[epoint], float(cost))

def ucs(graph, snode, enode):
	if graph.is_empty() or snode not in graph.nodedict.keys() or enode not in graph.nodedict.keys():
		print 'Unreachable'
		return 
	pqueue = PriorityQueue()
	pqueue.put_and_update(graph.nodedict[snode], 0, snode)
	visited = []
	while not pqueue.empty():
		node, nodecost, pathrecord = pqueue.pop()
		if node.name == enode:
			print pathrecord
			return 
		visited.append(node.name)
		for neighbor, path in node.neighbor.items():
			if neighbor not in visited:
				pqueue.put_and_update(graph.nodedict[neighbor], nodecost + path, pathrecord+'->'+neighbor)
	print 'Unreachable'

graph = Graph()

def main():
	f = open('/Users/tianxiaohu/Desktop/hw1-test.in.txt')
	while True:
		try:
			line = f.readline().strip()
			# line = raw_input()
			if line == '':
				break
			if 'END' in line:
			# if line == 'END':
				ucs(graph, 'Start', 'Goal')
				graph.clear()
			else:
				add_edge_from_input(line)
		except EOFError:  
			f.close()
			break 

main()
