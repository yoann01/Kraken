"""Kraken - objects.components.component_input port module.

Classes:
ComponentInputPort -- Component input port representation.

"""

from kraken.core.objects.scene_item import SceneItem
from kraken.core.objects.object_3d import Object3D
from kraken.core.objects.attributes.attribute import Attribute


class ComponentInputPort(SceneItem):
    """Component Input Object."""

    def __init__(self, name, parent, dataType, metaData=None):
        super(ComponentInputPort, self).__init__(name, parent=parent, metaData=metaData)
        self._dataType = None
        self._connection = None
        self._target = None
        self._index = 0
        self._sourceIndex = None

        self.setDataType(dataType)


    # =================
    # DataType Methods
    # =================
    def setDataType(self, dataType):
        """Sets the data type for this input.

        Args:
            dataType (str): Type of input source.

        Returns:
            bool: True if successful.

        """

        # TODO: Need to implement data type validation!
        # Currently can set to anything.

        self._dataType = dataType

        return True

    def getDataType(self):
        """Returns the data type for this input.

        Returns:
            str: Data type of this input.

        """

        return self._dataType


    # ====================
    # Connections Methods
    # ====================
    def isConnected(self):
        """Checks if there is a connection.

        Returns:
            bool: Whether it is connected or not.

        """

        return self._connection is not None

    def getConnection(self):
        """Gets the connection of this input.

        Returns:
            Connection object or None if not set.

        """

        return self._connection

    def setConnection(self, connectionObj, index=0):
        """Sets the connection to the component output.

        Args:
            connectionObj (ComponentOutputPort): Output object to connect to.

        Returns:
            bool: True if successful.

        """

        if connectionObj.getDataType() != self.getDataType() and connectionObj.getDataType()[:-2] != self.getDataType():
            raise TypeError("Data Type mismatch! Cannot connect '" +
                            connectionObj.getDataType() + "' to '" + self.getDataType())

        if connectionObj is self.getConnection():
            raise ValueError("'connectionObj' is already set as the connection.")

        self._connection = connectionObj
        connectionObj._addConnection(self)
        self.__setIndex(index)

        return True

    def removeConnection(self):
        """Removes the connection to the component output.

        Returns:
            bool: True if successful.

        """

        self._connection._removeConnection(self)
        self._connection = None

        return True

    def canConnectTo(self, otherPort):
        """Tests whether or not this port can connect to the other port.

        Args:
            otherPort (Port): Port to test if able to connect to.

        Returns:
            bool: True if can connect, false otherwise.

        """

        if otherPort.isTypeOf('ComponentInputPort'):
            return False

        if self.getDataType() != otherPort.getDataType():

            outDataType = otherPort.getDataType()
            inDataType = self.getDataType()

            # Outports of Array types can be connected to inports of the array element type..
            if not (outDataType.startswith(inDataType) and outDataType.endswith('[]')):
                return False

        if self.getParent() == otherPort.getParent():
            return False

        return True


    # ===============
    # Target Methods
    # ===============
    def setTarget(self, target):
        """Sets the target for this input.

        Args:
            target (Object): Kraken object that is the target of this input.

        Returns:
            bool: True if successful.

        """

        self._target = target

        return True

    def getTarget(self):
        """Returns the target of the input.

        Returns:
            Object, the target of the input.

        """

        return self._target


    # ==============
    # Index Methods
    # ==============
    def getIndex(self):
        """Gets the index of the connection.

        Returns:
            Integer, the index of the connection.

        """

        return self._index

    def __setIndex(self, index):
        """Sets the index of the connection.

        Args:
            index (int): The index to set this to.

        Returns:
            bool: True if successful.

        """

        # if you see an error calling this or the previous public
        # version of this you will need to refactor your code to call
        # setConnection(target, index = 12) for example.

        self._index = index

        # register the source
        # this is relevant for traversing for build order
        target = self.getTarget()
        connectedTarget = self._connection.getTarget()

        if isinstance(connectedTarget, list):
            connectedTarget = connectedTarget[self._index]

        # Why do we need these if constrainTo and connect add the source?
        # Where is _sourceIndex supposed to be used?
        # if self._sourceIndex is None:
        #     self._sourceIndex = target.addSource(connectedTarget)
        # else:
        #     target.setSource(self._sourceIndex, connectedTarget)

        if isinstance(target, Attribute):
            target.connect(connectedTarget)

        elif isinstance(target, Object3D):
            target.removeAllConstraints()
            target.constrainTo(connectedTarget, maintainOffset=False)

        return True
