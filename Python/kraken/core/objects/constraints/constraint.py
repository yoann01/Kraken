"""Kraken - objects.Constraints.Constraint module.

Classes:
Constraint - Base Constraint.

"""

from kraken.core.kraken_system import ks
from kraken.core.configs.config import Config
from kraken.core.objects.scene_item import SceneItem

from kraken.core.maths.xfo import Xfo
from kraken.core.maths.mat44 import Mat44


class Constraint(SceneItem):
    """Constraint object."""

    def __init__(self, name, parent=None, metaData=None):
        super(Constraint, self).__init__(name, parent, metaData=metaData)

        self._constrainee = None
        self._constrainers = []
        self._maintainOffset = False
        self._flags = {}

    # =============
    # Name Methods
    # =============
    def getBuildName(self):
        """Returns the build name for the object.

        Returns:
            str: Name to be used in the DCC.

        """

        typeNameHierarchy = self.getTypeHierarchyNames()

        config = Config.getInstance()

        # If flag is set on object to use explicit name, return it.
        if config.getExplicitNaming() is True or \
                self.testFlag('EXPLICIT_NAME'):
                return self.getName()

        nameTemplate = config.getNameTemplate()

        # Get the token list for this type of object
        format = None
        for typeName in nameTemplate['formats'].keys():
            if typeName in typeNameHierarchy:
                format = nameTemplate['formats'][typeName]
                break

        if format is None:
            format = nameTemplate['formats']['default']

        objectType = None
        for eachType in typeNameHierarchy:
            if eachType in nameTemplate['types'].keys():
                objectType = eachType
                break

        altType = self.getMetaDataItem("altType")
        if altType is not None and nameTemplate['types'].get(altType, None) is not None:
            objectType = altType

        if objectType is None:
            objectType = 'default'

        # Generate a name by concatenating the resolved tokens together.
        builtName = ""
        skipSep = False
        for token in format:

            if token is 'sep':
                if not skipSep:
                    builtName += nameTemplate['separator']

            elif token is 'location':
                parent = self.getParent()
                if parent is None:
                    raise ValueError("constraint [%s] does not have a parent." % self.getName())
                component = parent.getComponent()
                if component is None:
                    raise ValueError("constraint [%s] parent [%s] does not have a component." % (self.getName(), parent))
                location = component.getLocation()

                if location not in nameTemplate['locations']:
                    raise ValueError("Invalid location on: " + self.getPath())

                altLocation = self.getMetaDataItem("altLocation")
                if altLocation is not None and altLocation in nameTemplate['locations']:
                    location = altLocation

                builtName += location

            elif token is 'type':
                builtName += nameTemplate['types'][objectType]

            elif token is 'name':
                builtName += self.getName()

            elif token is 'component':
                if self.getParent() is None:
                    skipSep = True
                    continue

                builtName += self.getParent().getComponent().getName()

            elif token is 'container':
                if self.getContainer() is None:
                    skipSep = True
                    continue

                builtName += self.getContainer().getName()

            else:
                raise ValueError("Unresolvabled token '" + token +
                    "' used on: " + self.getPath())

        return builtName

    # =============
    # Flag Methods
    # =============
    def setFlag(self, name):
        """Sets the flag of the specified name.

        Returns:
            bool: True if successful.

        """

        self._flags[name] = True

        return True

    def testFlag(self, name):
        """Tests if the specified flag is set.

        Args:
            name (str): Name of the flag to test.

        Returns:
            bool: True if flag is set.

        """

        return name in self._flags

    def clearFlag(self, name):
        """Clears the flag of the specified name.

        Args:
            name (str): Name of the flag to clear.

        Returns:
            bool: True if successful.

        """

        if name in self._flags:
            del self._flags[name]
            return True

        return False

    def getFlags(self):
        """Returns all flags set on this object.

        Returns:
            list: Flags set on this object.

        """

        return self._flags.keys()

    # ===============
    # Source Methods
    # ===============
    def getSources(self):
        """Returns the sources of the object.

        Returns:
            list: All sources of this object.

        """
        return super(Constraint, self).getSources() + self._constrainers

    # ===================
    # Constraint Methods
    # ===================
    def getMaintainOffset(self):
        """Returns the whether the constraint should maintain offset when it's
        built or not.

        Returns:
            bool: Whether the constraint should maintain offset or not.

        """

        return self._maintainOffset

    def setMaintainOffset(self, value):
        """Sets the constraint to maintain offset when creating the constraint.

        Args:
            value (bool): Whether the constraint should maintain offset or not.

        Returns:
            bool: True if successful.

        """

        if not isinstance(value, bool):
            raise TypeError("Value is not of type 'bool': " + str(value))

        self._maintainOffset = value

    def setConstrainee(self, constrainee):
        """Sets the constrainee object for this constraint.

        Args:
            constrainee (Object): Object that will be constrained.

        Returns:
            bool: True if successful.

        """

        self._constrainee = constrainee
        self._constrainee.addSource(self)

        return True

    def getConstrainee(self):
        """Returns the constrainee object for this constraint.

        Returns:
            bool: True if successful.

        """

        return self._constrainee

    def addConstrainer(self, kObject3D):
        """Adds a constrainer object to this constraint.

        Args:
            kObject3D (Object): kObject3D that will constrain the constrainee.

        Returns:
            bool: True if successful.

        """

        self._constrainers.append(None)
        self.setConstrainer(kObject3D, len(self._constrainers) - 1)

        return True

    def setConstrainer(self, kObject3D, index=0):
        """Sets the constrainer at the specified index.

        Args:
            kObject3D (object): Kraken 3D object.
            index (int): index of the constraint to set.

        Returns:
            bool: True if successful.

        """

        if not kObject3D.isTypeOf('Object3D'):
            raise Exception("'kObject3D' argument is not a valid instance type. '" +
                            kObject3D.getName() + "': " + str(type(kObject3D)) +
                            ". Must be an instance of 'Object3D'.")


        if kObject3D in self._constrainers:
            raise Exception("'kObject3D' argument is already a constrainer: '" +
                            kObject3D.getName() + "'.")

        self._constrainers[index] = kObject3D

        return True

    def removeConstrainerByIndex(self, index):
        """Removes a constrainer object by its index.

        Args:
            index (int): Index of the constrainer you want to remove.

        Returns:
            bool: True if successful.

        """

        if index > len(self._constrainers):
            raise IndexError("Index '{}' is out of range: {}".format(index, len(self._constrainers)))

        del self._constrainers[index]

        return True

    def getConstrainers(self):
        """Returns the constrainers of this constraint.

        Returns:
            list: Constrainer objects.

        """

        return self._constrainers

    def compute(self):
        """invokes the constraint and returns the resulting transform

        Returns:
            xfo: The result of the constraint in global space.

        """

        if self._constrainee is None:
            return None
        if len(self._constrainers) == 0:
            return None
        if self.getMaintainOffset():
            return self._constrainee.xfo

        cls = self.__class__.__name__
        ks.loadExtension('KrakenForCanvas')
        rtVal = ks.rtVal('KrakenForCanvas::Kraken%s' % cls)

        for c in self._constrainers:
            rtVal.addConstrainer('', ks.rtVal('Xfo', c.globalXfo).toMat44('Mat44'))

        # Using globalXfo here would cause a recursion
        return Xfo(rtVal.compute("Xfo",
                                 ks.rtVal('Xfo', self._constrainee.xfo).toMat44('Mat44')))

    def computeOffset(self):
        """Invokes the constraint and computes the offset

        Returns:
            xfo: The offset to be used for the constraint.

        """

        if self._constrainee is None:
            return Xfo()
        if len(self._constrainers) == 0:
            return Xfo()
        if not self.getMaintainOffset():
            return Xfo()

        cls = self.__class__.__name__
        ks.loadExtension('KrakenForCanvas')
        rtVal = ks.rtVal('KrakenForCanvas::Kraken%s' % cls)

        rtVal.offset = ks.rtVal('Mat44', Mat44())
        for c in self._constrainers:
            rtVal.addConstrainer('', ks.rtVal('Xfo', c.globalXfo).toMat44('Mat44'))

        return Xfo(rtVal.computeOffset("Xfo",
                                       ks.rtVal('Xfo', self._constrainee.xfo).toMat44('Mat44')))

    def evaluate(self):
        """Invokes the constraint causing the output value to be computed.

        Returns:
            bool: True if successful.

        """

        self.setFlag("HAS_EVALUATED")

        if self.getMaintainOffset() is False:
            self.getConstrainee().xfo = self.compute()
            return True

        return False

    # ====================
    # Persistence Methods
    # ====================
    def jsonEncode(self, saver):
        """Encodes the object to a JSON structure.

        Args:
            saver (Object): saver object.

        Returns:
            Dict: A JSON structure containing the data for this SceneItem.

        """

        classHierarchy = []
        for cls in type.mro(type(self)):
            if cls == object:
                break
            classHierarchy.append(cls.__name__)

        jsonData = {
            '__typeHierarchy__': classHierarchy,
            'name': self._name,
            'constrainee': self._constrainee.getName(),
            'constrainers': []
        }
        for cnstrnr in self._constrainers:
            jsonData['constrainers'].append(cnstrnr.getName())

        return jsonData

    def jsonDecode(self, loader, jsonData):
        """Returns the color of the object..

        Args:
            loader (Object): Loader object.
            jsonData (Dict): JSON object structure.

        Returns:
            bool: True if successful.

        """

        loader.registerConstructionCallback(jsonData['constrainee'], self.setConstrainee)

        for cnstrnr in jsonData['constrainers']:
            loader.registerConstructionCallback(cnstrnr, self.addConstrainer)

        return True
