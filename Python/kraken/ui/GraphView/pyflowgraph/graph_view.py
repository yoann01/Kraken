#
# Copyright 2015-2017 Eric Thivierge
#

import copy
import math

from kraken.ui.Qt import QtWidgets, QtGui, QtCore

from node import Node
from connection import Connection

from selection_rect import SelectionRect

MANIP_MODE_NONE = 0
MANIP_MODE_SELECT = 1
MANIP_MODE_PAN = 2
MANIP_MODE_MOVE = 3
MANIP_MODE_ZOOM = 4

class GraphView(QtWidgets.QGraphicsView):

    nodeAdded = QtCore.Signal(Node)
    nodeRemoved = QtCore.Signal(Node)
    nodeNameChanged = QtCore.Signal(str, str)
    beginDeleteSelection = QtCore.Signal()
    endDeleteSelection = QtCore.Signal()

    beginConnectionManipulation = QtCore.Signal()
    endConnectionManipulation = QtCore.Signal()
    connectionAdded = QtCore.Signal(Connection)
    connectionRemoved = QtCore.Signal(Connection)

    beginNodeSelection = QtCore.Signal()
    endNodeSelection = QtCore.Signal()
    selectionChanged = QtCore.Signal(list, list)

    # During the movement of the nodes, this signal is emitted with the incremental delta.
    selectionMoved = QtCore.Signal(set, QtCore.QPointF)

    # After moving the nodes interactively, this signal is emitted with the final delta.
    endSelectionMoved = QtCore.Signal(set, QtCore.QPointF)



    _clipboardData = None

    _backgroundColor = QtGui.QColor(50, 50, 50)
    _gridPenS = QtGui.QPen(QtGui.QColor(44, 44, 44, 255), 0.5)
    _gridPenL = QtGui.QPen(QtGui.QColor(40, 40, 40, 255), 1.0)
    _gridSizeFine = 30
    _gridSizeCourse = 300

    _mouseWheelZoomRate = 0.0005

    _snapToGrid = False

    def __init__(self, parent=None):
        super(GraphView, self).__init__(parent)
        self.setObjectName('graphView')

        self.__graphViewWidget = parent

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Explicitly set the scene rect. This ensures all view parameters will be explicitly controlled
        # in the event handlers of this class.
        size = QtCore.QSize(600, 400)
        self.resize(size)
        self.setSceneRect(-size.width() * 0.5, -size.height() * 0.5, size.width(), size.height())

        self.setAcceptDrops(True)
        self.reset()


    def getGraphViewWidget(self):
        return self.__graphViewWidget


    ################################################
    ## Graph
    def reset(self):
        self.setScene(QtWidgets.QGraphicsScene())

        self.__connections = set()
        self.__nodes = {}
        self.__selection = set()

        self._manipulationMode = MANIP_MODE_NONE
        self._selectionRect = None

    def getGridSize(self):
        """Gets the size of the grid of the graph.

        Returns:
            int: Size of the grid.

        """

        return self._gridSizeFine

    def getSnapToGrid(self):
        """Gets the snap to grid value.

        Returns:
            Boolean: Whether snap to grid is active or not.

        """

        return self._snapToGrid

    def setSnapToGrid(self, snap):
        """Sets the snap to grid value.

        Args:
            snap (Boolean): True to snap to grid, false not to.

        """

        self._snapToGrid = snap


    ################################################
    ## Nodes

    def addNode(self, node, emitSignal=True):
        self.scene().addItem(node)
        self.__nodes[node.getName()] = node
        node.nameChanged.connect(self._onNodeNameChanged)

        if emitSignal:
            self.nodeAdded.emit(node)

        return node

    def removeNode(self, node, emitSignal=True):

        del self.__nodes[node.getName()]
        self.scene().removeItem(node)
        node.nameChanged.disconnect(self._onNodeNameChanged)

        if emitSignal:
            self.nodeRemoved.emit(node)


    def hasNode(self, name):
        return name in self.__nodes

    def getNode(self, name):
        if name in self.__nodes:
            return self.__nodes[name]
        return None

    def getNodes(self):
        return self.__nodes

    def _onNodeNameChanged(self, origName, newName ):
        if newName in self.__nodes and self.__nodes[origName] != self.__nodes[newName]:
            raise Exception("New name collides with existing node.")
        node = self.__nodes[origName]
        self.__nodes[newName] = node
        del self.__nodes[origName]
        self.nodeNameChanged.emit( origName, newName )


    def clearSelection(self, emitSignal=True):

        prevSelection = []
        if emitSignal:
            for node in self.__selection:
                prevSelection.append(node)

        for node in self.__selection:
            node.setSelected(False)
        self.__selection.clear()

        if emitSignal and len(prevSelection) != 0:
            self.selectionChanged.emit(prevSelection, [])

    def selectNode(self, node, clearSelection=False, emitSignal=True):
        prevSelection = []
        if emitSignal:
            for n in self.__selection:
                prevSelection.append(n)

        if clearSelection is True:
            self.clearSelection(emitSignal=False)

        if node in self.__selection:
            raise IndexError("Node is already in selection!")

        node.setSelected(True)
        self.__selection.add(node)

        if emitSignal:

            newSelection = []
            for n in self.__selection:
                newSelection.append(n)

            self.selectionChanged.emit(prevSelection, newSelection)


    def deselectNode(self, node, emitSignal=True):

        if node not in self.__selection:
            raise IndexError("Node is not in selection!")

        prevSelection = []
        if emitSignal:
            for n in self.__selection:
                prevSelection.append(n)

        node.setSelected(False)
        self.__selection.remove(node)

        if emitSignal:
            newSelection = []
            for n in self.__selection:
                newSelection.append(n)

            self.selectionChanged.emit(prevSelection, newSelection)

    def getSelectedNodes(self):
        return self.__selection


    def deleteSelectedNodes(self):
        self.beginDeleteSelection.emit()

        selectedNodes = self.getSelectedNodes()
        names = ""
        for node in selectedNodes:
            node.disconnectAllPorts()
            self.removeNode(node)

        self.endDeleteSelection.emit()


    def frameNodes(self, nodes):
        if len(nodes) == 0:
            return

        def computeWindowFrame():
            windowRect = self.rect()
            windowRect.setLeft(windowRect.left() + 16)
            windowRect.setRight(windowRect.right() - 16)
            windowRect.setTop(windowRect.top() + 16)
            windowRect.setBottom(windowRect.bottom() - 16)
            return windowRect

        nodesRect = None
        for node in nodes:
            nodeRectF = node.sceneTransform().mapRect(node.rect())
            nodeRect = QtCore.QRect(nodeRectF.x(), nodeRectF.y(), nodeRectF.width(), nodeRectF.height())
            if nodesRect is None:
                nodesRect = nodeRect
            else:
                nodesRect = nodesRect.united(nodeRect)


        windowRect = computeWindowFrame()

        scaleX = float(windowRect.width()) / float(nodesRect.width())
        scaleY = float(windowRect.height()) / float(nodesRect.height())
        if scaleY > scaleX:
            scale = scaleX
        else:
            scale = scaleY

        if scale < 1.0:
            self.setTransform(QtGui.QTransform.fromScale(scale, scale))
        else:
            self.setTransform(QtGui.QTransform())

        sceneRect = self.sceneRect()
        pan = sceneRect.center() - nodesRect.center()
        sceneRect.translate(-pan.x(), -pan.y())
        self.setSceneRect(sceneRect)

        # Update the main panel when reframing.
        self.update()


    def frameSelectedNodes(self):
        self.frameNodes(self.getSelectedNodes())

    def frameAllNodes(self):
        allnodes = []
        for name, node in self.__nodes.iteritems():
            allnodes.append(node)
        self.frameNodes(allnodes)

    def getSelectedNodesCentroid(self):
        selectedNodes = self.getSelectedNodes()

        leftMostNode = None
        topMostNode = None
        for node in selectedNodes:
            nodePos = node.getGraphPos()

            if leftMostNode is None:
                leftMostNode = node
            else:
                if nodePos.x() < leftMostNode.getGraphPos().x():
                    leftMostNode = node

            if topMostNode is None:
                topMostNode = node
            else:
                if nodePos.y() < topMostNode.getGraphPos().y():
                    topMostNode = node

        xPos = leftMostNode.getGraphPos().x()
        yPos = topMostNode.getGraphPos().y()
        pos = QtCore.QPoint(xPos, yPos)

        return pos


    def moveSelectedNodes(self, delta, emitSignal=True):
        for node in self.__selection:
            node.translate(delta.x(), delta.y())

        if emitSignal:
            self.selectionMoved.emit(self.__selection, delta)

    # After moving the nodes interactively, this signal is emitted with the final delta.
    def endMoveSelectedNodes(self, delta):
        self.endSelectionMoved.emit(self.__selection, delta)

    ################################################
    ## Connections

    def emitBeginConnectionManipulationSignal(self):
        self.beginConnectionManipulation.emit()


    def emitEndConnectionManipulationSignal(self):
        self.endConnectionManipulation.emit()


    def addConnection(self, connection, emitSignal=True):

        self.__connections.add(connection)
        self.scene().addItem(connection)
        if emitSignal:
            self.connectionAdded.emit(connection)
        return connection

    def removeConnection(self, connection, emitSignal=True):

        connection.disconnect()
        self.__connections.remove(connection)
        self.scene().removeItem(connection)
        if emitSignal:
            self.connectionRemoved.emit(connection)


    def connectPorts(self, srcNode, outputName, tgtNode, inputName):

        if isinstance(srcNode, Node):
            sourceNode = srcNode
        elif isinstance(srcNode, basestring):
            sourceNode = self.getNode(srcNode)
            if not sourceNode:
                raise Exception("Node not found:" + str(srcNode))
        else:
            raise Exception("Invalid srcNode:" + str(srcNode))


        sourcePort = sourceNode.getOutputPort(outputName)
        if not sourcePort:
            raise Exception("Node '" + sourceNode.getName() + "' does not have output:" + outputName)


        if isinstance(tgtNode, Node):
            targetNode = tgtNode
        elif isinstance(tgtNode, basestring):
            targetNode = self.getNode(tgtNode)
            if not targetNode:
                raise Exception("Node not found:" + str(tgtNode))
        else:
            raise Exception("Invalid tgtNode:" + str(tgtNode))

        targetPort = targetNode.getInputPort(inputName)
        if not targetPort:
            raise Exception("Node '" + targetNode.getName() + "' does not have input:" + inputName)

        connection = Connection(self, sourcePort.outCircle(), targetPort.inCircle())
        self.addConnection(connection, emitSignal=False)

        return connection

    ################################################
    ## Events

    def mousePressEvent(self, event):

        if event.button() is QtCore.Qt.MouseButton.LeftButton and self.itemAt(event.pos()) is None:
            self.beginNodeSelection.emit()
            self._manipulationMode = MANIP_MODE_SELECT
            self._mouseDownSelection = copy.copy(self.getSelectedNodes())
            self._selectionRect = SelectionRect(graph=self, mouseDownPos=self.mapToScene(event.pos()))

        elif event.button() is QtCore.Qt.MouseButton.MiddleButton:
            self.setCursor(QtCore.Qt.OpenHandCursor)
            self._manipulationMode = MANIP_MODE_PAN
            self._lastPanPoint = self.mapToScene(event.pos())

        elif event.button() is QtCore.Qt.MouseButton.RightButton:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self._manipulationMode = MANIP_MODE_ZOOM
            self._lastZoomPoint = self.mapToScene(event.pos())
            self._lastMousePos = event.pos()
            self._lastTransform = QtGui.QTransform(self.transform())
            self._lastSceneRect = self.sceneRect()
            self._lastSceneCenter = self._lastSceneRect.center()
            self._lastScenePos = self.mapToScene(event.pos())
            self._lastOffsetFromSceneCenter = self._lastScenePos - self._lastSceneCenter

        else:
            super(GraphView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()

        if self._manipulationMode == MANIP_MODE_SELECT:
            dragPoint = self.mapToScene(event.pos())
            self._selectionRect.setDragPoint(dragPoint)

            # This logic allows users to use ctrl and shift with rectangle
            # select to add / remove nodes.
            if modifiers == QtCore.Qt.ControlModifier:
                for name, node in self.__nodes.iteritems():

                    if node in self._mouseDownSelection:
                        if node.isSelected() and self._selectionRect.collidesWithItem(node):
                            self.deselectNode(node, emitSignal=False)
                        elif not node.isSelected() and not self._selectionRect.collidesWithItem(node):
                            self.selectNode(node, emitSignal=False)
                    else:
                        if not node.isSelected() and self._selectionRect.collidesWithItem(node):
                            self.selectNode(node, emitSignal=False)
                        elif node.isSelected() and not self._selectionRect.collidesWithItem(node):
                            if node not in self._mouseDownSelection:
                                self.deselectNode(node, emitSignal=False)

            elif modifiers == QtCore.Qt.ShiftModifier:
                for name, node in self.__nodes.iteritems():
                    if not node.isSelected() and self._selectionRect.collidesWithItem(node):
                        self.selectNode(node, emitSignal=False)
                    elif node.isSelected() and not self._selectionRect.collidesWithItem(node):
                        if node not in self._mouseDownSelection:
                            self.deselectNode(node, emitSignal=False)

            else:
                self.clearSelection(emitSignal=False)

                for name, node in self.__nodes.iteritems():
                    if not node.isSelected() and self._selectionRect.collidesWithItem(node):
                        self.selectNode(node, emitSignal=False)
                    elif node.isSelected() and not self._selectionRect.collidesWithItem(node):
                        self.deselectNode(node, emitSignal=False)

        elif self._manipulationMode == MANIP_MODE_PAN:
            delta = self.mapToScene(event.pos()) - self._lastPanPoint

            rect = self.sceneRect()
            rect.translate(-delta.x(), -delta.y())
            self.setSceneRect(rect)

            self._lastPanPoint = self.mapToScene(event.pos())

        elif self._manipulationMode == MANIP_MODE_MOVE:

            newPos = self.mapToScene(event.pos())
            delta = newPos - self._lastDragPoint
            self._lastDragPoint = newPos

            selectedNodes = self.getSelectedNodes()

            # Apply the delta to each selected node
            for node in selectedNodes:
                node.translate(delta.x(), delta.y())

        elif self._manipulationMode == MANIP_MODE_ZOOM:

           # How much
            delta = event.pos() - self._lastMousePos
            zoomFactor = 1.0
            if delta.x() > 0:
                zoomFactor = 1.0 + delta.x() / 100.0
            else:
                zoomFactor = 1.0 / (1.0 + abs(delta.x()) / 100.0)

            # Limit zoom to 3x
            if self._lastTransform.m22() * zoomFactor >= 2.0:
                return

            # Reset to when we mouse pressed
            self.setSceneRect(self._lastSceneRect)
            self.setTransform(self._lastTransform)

            # Center scene around mouse down
            rect = self.sceneRect()
            rect.translate(self._lastOffsetFromSceneCenter)
            self.setSceneRect(rect)

            # Zoom in (QGraphicsView auto-centers!)
            self.scale(zoomFactor, zoomFactor)

            newSceneCenter = self.sceneRect().center()
            newScenePos = self.mapToScene(self._lastMousePos)
            newOffsetFromSceneCenter = newScenePos - newSceneCenter

            # Put mouse down back where is was on screen
            rect = self.sceneRect()
            rect.translate(-1 * newOffsetFromSceneCenter)
            self.setSceneRect(rect)

            # Call udpate to redraw background
            self.update()


        else:
            super(GraphView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._manipulationMode == MANIP_MODE_SELECT:

            # If users simply clicks in the empty space, clear selection.
            if self.mapToScene(event.pos()) == self._selectionRect.pos():
                self.clearSelection(emitSignal=False)

            self._selectionRect.destroy()
            self._selectionRect = None
            self._manipulationMode = MANIP_MODE_NONE

            selection = self.getSelectedNodes()

            deselectedNodes = []
            selectedNodes = []

            for node in self._mouseDownSelection:
                if node not in selection:
                    deselectedNodes.append(node)

            for node in selection:
                if node not in self._mouseDownSelection:
                    selectedNodes.append(node)

            if selectedNodes != deselectedNodes:
                self.selectionChanged.emit(deselectedNodes, selectedNodes)

            self.endNodeSelection.emit()

        elif self._manipulationMode == MANIP_MODE_PAN:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._manipulationMode = MANIP_MODE_NONE

        elif self._manipulationMode == MANIP_MODE_ZOOM:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._manipulationMode = MANIP_MODE_NONE
            #self.setTransformationAnchor(self._lastAnchor)

        else:
            super(GraphView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):


        zoomFactor = 1.0 + event.delta() * self._mouseWheelZoomRate

        transform = self.transform()
        # Limit zoom to 3x
        if transform.m22() * zoomFactor >= 2.0:
            return

        sceneCenter = self.sceneRect().center()
        scenePoint = self.mapToScene(event.pos())
        posFromSceneCenter = scenePoint - sceneCenter

        rect = self.sceneRect()
        rect.translate(posFromSceneCenter)
        self.setSceneRect(rect)


        # Zoom in (QGraphicsView auto-centers!)
        self.scale(zoomFactor, zoomFactor)

        # Translate scene back to align original mouse press
        sceneCenter = self.sceneRect().center()
        scenePoint = self.mapToScene(event.pos())
        posFromSceneCenter = scenePoint - sceneCenter

        rect = self.sceneRect()
        posFromSceneCenter *= -1.0
        rect.translate(posFromSceneCenter)
        self.setSceneRect(rect)


        # Call udpate to redraw background
        self.update()


    ################################################
    ## Painting

    def drawBackground(self, painter, rect):

        oldTransform = painter.transform()
        painter.fillRect(rect, self._backgroundColor)

        left = int(rect.left()) - (int(rect.left()) % self._gridSizeFine)
        top = int(rect.top()) - (int(rect.top()) % self._gridSizeFine)

        # Draw horizontal fine lines
        gridLines = []
        painter.setPen(self._gridPenS)
        y = float(top)
        while y < float(rect.bottom()):
            gridLines.append(QtCore.QLineF( rect.left(), y, rect.right(), y ))
            y += self._gridSizeFine
        painter.drawLines(gridLines)

        # Draw vertical fine lines
        gridLines = []
        painter.setPen(self._gridPenS)
        x = float(left)
        while x < float(rect.right()):
            gridLines.append(QtCore.QLineF( x, rect.top(), x, rect.bottom()))
            x += self._gridSizeFine
        painter.drawLines(gridLines)

        # Draw thick grid
        left = int(rect.left()) - (int(rect.left()) % self._gridSizeCourse)
        top = int(rect.top()) - (int(rect.top()) % self._gridSizeCourse)

        # Draw vertical thick lines
        gridLines = []
        painter.setPen(self._gridPenL)
        x = left
        while x < rect.right():
            gridLines.append(QtCore.QLineF( x, rect.top(), x, rect.bottom() ))
            x += self._gridSizeCourse
        painter.drawLines(gridLines)

        # Draw horizontal thick lines
        gridLines = []
        painter.setPen(self._gridPenL)
        y = top
        while y < rect.bottom():
            gridLines.append(QtCore.QLineF( rect.left(), y, rect.right(), y ))
            y += self._gridSizeCourse
        painter.drawLines(gridLines)

        return super(GraphView, self).drawBackground(painter, rect)
