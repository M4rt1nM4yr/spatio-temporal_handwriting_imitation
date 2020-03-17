import matplotlib.pyplot as plt


class GraphNode:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.connectedNodes = set()

    def __str__(self):
        return str((self.x, self.y))


class EuclideanGraph:
    def __init__(self):
        self.nodes = dict()

    def checkForConsistency(self):
        for nodeKey, node in self.nodes.items():
            if node.x != nodeKey[0] or node.y != nodeKey[1]:
                raise RuntimeError('Key ' + str(nodeKey) + ' does not match node ' + str(node) + '!')
            for connectedNodeId in node.connectedNodes:
                if connectedNodeId not in self.nodes:
                    raise RuntimeError('Node ' + str(node) + ' points to non-existant node ' + str(connectedNodeId))
                connectedNode = self.nodes.get(connectedNodeId)
                if nodeKey not in connectedNode.connectedNodes:
                    raise RuntimeError('Unidirectional connection detected between ' + str(node)
                                       + ' and ' + str(connectedNode))

    def createNode(self, x, y):
        if (x, y) in self.nodes:
            raise RuntimeError('Node ' + str((x, y)) + ' already exists.')
        self.nodes[(x, y)] = GraphNode(x, y)
        return self.nodes.get((x, y))

    def nodeExists(self, pos):
        return pos in self.nodes

    def getNode(self, pos):
        return self.nodes.get(pos)

    def nodesConnected(self, nodeId1, nodeId2):
        node1 = self.getNode(nodeId1)
        node2 = self.getNode(nodeId2)
        if nodeId2 in node1.connectedNodes or nodeId1 in node2.connectedNodes:
            return True
        return False

    def removeConnection(self, nodeId1, nodeId2):
        # print('removeConnection(' + str(nodeId1) + ", " + str(nodeId2) + ')')
        node1 = self.getNode(nodeId1)
        node2 = self.getNode(nodeId2)
        if nodeId2 not in node1.connectedNodes or nodeId1 not in node2.connectedNodes:
            raise RuntimeError("Nodes are already disconnected!")
        node2.connectedNodes.remove(nodeId1)
        node1.connectedNodes.remove(nodeId2)

    def addConnection(self, nodeId1, nodeId2):
        # print('addConnection(' + str(nodeId1) + ", " + str(nodeId2) + ')')
        node1 = self.getNode(nodeId1)
        node2 = self.getNode(nodeId2)
        if nodeId2 in node1.connectedNodes or nodeId1 in node2.connectedNodes:
            raise RuntimeError("Nodes are already connected!")
        node2.connectedNodes.add(nodeId1)
        node1.connectedNodes.add(nodeId2)

    def removeNode(self, pos):
        # print('removeNode(' + str(pos) + ')')
        node = self.nodes.get(pos)
        for connectedNodePos in node.connectedNodes:
            connectedNode = self.nodes.get(connectedNodePos)
            connectedNode.connectedNodes.remove(pos)
        del self.nodes[pos]

    def plot(self, fmt_lines='k-', fmt_dots='k.'):
        self.checkForConsistency()
        for nodeId, node in self.nodes.items():
            plt.plot([node.x], [node.y], fmt_dots)
            for connectedNodeId in node.connectedNodes:
                connectedNode = self.nodes.get(connectedNodeId)
                needsDraw = False
                if connectedNode.x > node.x:
                    needsDraw = True
                elif connectedNode.x == node.x and connectedNode.y > node.y:
                    needsDraw = True
                if needsDraw:
                    plt.plot([node.x, connectedNode.x], [node.y, connectedNode.y], fmt_lines)
