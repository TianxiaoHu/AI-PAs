#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@ Author: Tianxiao Hu
@ StudentNumber:14300240007
@ Platform: Mac OS X 10.12.3 Sierra, Anaconda 2.7.12 interpreter， build succeeded
for Introduction to Artificial Intelligence, homework #1
'''

import os

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
		return len(self.data)==0

	def __repr__(self):
		return '<Priority Queue> ' + str(self.data)


class Node(object):

	def __init__(self, name):
		self.name = name
		self.neighbor = {}

	def add_edge(self, node, cost):
		self.neighbor[node.name] = cost

	def show_edge(self):
		print self.neighbor

	def __repr__(self):
		return '<Node> ' + self.name


class Graph(object):
	def __init__(self, nodedict={}):
		self.nodedict = nodedict

	def add_node(self, new_node):
		self.nodedict[new_node.name] = new_node

	def have_node(self, node_name):
		return self.nodedict.has_key(node_name)


def read_graph_from_file(filepath):
	graph = Graph()
	f = open(filepath)             
	line = f.readline()            
	while line:
		if line == '':
			break

		[spoint, epoint, cost] = line.strip().split(' ')

		if not graph.have_node(spoint):
			newnode = Node(spoint)
			graph.add_node(newnode)
		if not graph.have_node(epoint):
			newnode = Node(epoint)
			graph.add_node(newnode)

		graph.nodedict[spoint].add_edge(graph.nodedict[epoint], int(cost))
		line = f.readline()

	f.close()
	return graph

def ucs(graph, snode, enode):
	pqueue = PriorityQueue()
	pqueue.put_and_update(graph.nodedict[snode], 0, snode)
	visited = []
	# print pqueue
	while not pqueue.empty():
		node, nodecost, pathrecord = pqueue.pop()
		# print 'current visit:', node.name
		if node.name == enode:
			return pathrecord
		visited.append(node.name)
		# print 'visited:', visited
		for neighbor, path in node.neighbor.items():
			# print neighbor, path
			if neighbor not in visited:
				pqueue.put_and_update(graph.nodedict[neighbor], nodecost + path, pathrecord+'->'+neighbor)
				# print pqueue
		# print 
	return 'Failed to find a path to Goal'

def main():
	workdir = os.getcwd()
	inputfile = os.path.join(workdir, 'input.txt')
	outputfile = os.path.join(workdir, 'output.txt')

	search_graph = read_graph_from_file(inputfile)
	result = ucs(search_graph, 'Start', 'Goal')
	f = open(outputfile, 'w')
	f.write(result)
	f.close()

if __name__ == '__main__':
	main()
