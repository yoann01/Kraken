"""Kraken - objects.object_3d module.

Classes:
Object3D - Base Object3D Object.

"""

import re
import logging

from kraken.log import getLogger


from kraken.core.configs.config import Config
from kraken.core.objects.scene_item import SceneItem
from kraken.core.maths import decodeValue
from kraken.core.maths.xfo import Xfo
from kraken.core.maths.rotation_order import RotationOrder
from kraken.core.objects.attributes.attribute_group import AttributeGroup
from kraken.core.objects.attributes.bool_attribute import BoolAttribute

from kraken.core.objects.constraints.constraint import Constraint
from kraken.core.objects.constraints.orientation_constraint import OrientationConstraint
from kraken.core.objects.constraints.pose_constraint import PoseConstraint
from kraken.core.objects.constraints.position_constraint import PositionConstraint
from kraken.core.objects.constraints.scale_constraint import ScaleConstraint
from kraken.core.objects.operators.operator import Operator

logger = getLogger('kraken')
logger.setLevel(logging.INFO)


class Object3D(SceneItem):
    """Kraken base object type for any 3D object."""

    def __init__(self, name, parent=None, flags=None, metaData=None):
        super(Object3D, self).__init__(name, parent=parent, metaData=metaData)
        self._children = []
        self._flags = {}
        self._attributeGroups = []
        self._constraints = []
        self._xfo = Xfo()
        self._ro = RotationOrder()
        self._color = None

        self._implicitAttrGrp = AttributeGroup("implicitAttrGrp", self)
        self._visibility = BoolAttribute('visibility',
                                         True,
                                         self._implicitAttrGrp)

        self._shapeVisibility = BoolAttribute('ShapeVisibility',
                                              True,
                                              self._implicitAttrGrp)

        if parent is not None:
            parent.addChild(self)

        if flags is not None:
            assert type(flags) is str, "Flags argument must be a comma separated string."

            for flag in flags.replace(' ', '').split(','):
                if not re.match("[\w]*$", flag):
                    msg = "{} '{}' {} ({}: {}) {}\n".format("Invalid flag", flag, "set on", self.getName(), self.getPath(), ". Alphanumeric and underscores only!")
                    logger.warn(msg)
                    continue

                self.setFlag(flag)

    # ==================
    # Property Methods
    # ==================
    @property
    def xfo(self):
        """Gets xfo property of this Object3D.

        Returns:
            Xfo: Xfo property of this Object3D.

        """

        return self._xfo

    @xfo.setter
    def xfo(self, value):
        """Sets xfo of this Object3D.

        Note:
            In Python, objects are always referenced, meaning to get a unique
            instance, an explicit clone is required. In KL, structs are passed
            by value, meaning that every assignment of a struct causes a clone.

            This means that in KL it is impossible for 2 objects to reference
            the same KL math object. This is an important performance feature
            of KL.

            The members of the KL Math objects have this property. 2 Xfos
            cannot share the same tr value. Here we implcitly clone the math
            object to ensure the same behavior as in KL.

        Args:
            value (Xfo): Vector to set the xfo by.

        Returns:
            bool: True if successful.

        """

        self._xfo = value.clone()

        return True


    @property
    def ro(self):
        """Gets Rotation Order property of this Object3D.

        Returns:
            RotationOrder: Rotation Order property of this Object3D.

        """

        return self._ro

    @ro.setter
    def ro(self, value):
        """Sets Rotation Order of this Object3D.

        Note:
            In Python, objects are always referenced, meaning to get a unique
            instance, an explicit clone is required. In KL, structs are passed
            by value, meaning that every assignment of a struct causes a clone.

            This means that in KL it is impossible for 2 objects to reference
            the same KL math object. This is an important performance feature
            of KL.

            The members of the KL Math objects have this property. 2 Xfos
            cannot share the same tr value. Here we implcitly clone the math
            object to ensure the same behavior as in KL.

        Args:
            value (RotationOrder): New rotation order.

        Returns:
            bool: True if successful.

        """

        self._ro = value.clone()

        return True

    @property
    def localXfo(self):
        """Gets local transform of this Object3D

        Returns:
            Xfo: Local Xfo of the object.

        """

        globalXfo = self.globalXfo

        parent = self.getParent()
        if not isinstance(parent, SceneItem):
            return globalXfo

        parentXfo = parent.globalXfo

        return parentXfo.inverse().multiply(globalXfo)

    @property
    def globalXfo(self):
        """Gets global transform of this Object3D

        Returns:
            Xfo: Global Xfo

        """

        for source in self.getSources():
            if isinstance(source, Object3D):
                continue
            if isinstance(source, Constraint):
                return source.compute()
            if isinstance(source, Operator):
                source.evaluate()
                break

        return self._xfo

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
        nameFormat = None
        for typeName in nameTemplate['formats'].keys():
            if typeName in typeNameHierarchy:
                nameFormat = nameTemplate['formats'][typeName]
                break

        if nameFormat is None:
            nameFormat = nameTemplate['formats']['default']

        objectType = None
        for eachType in typeNameHierarchy:
            if eachType in nameTemplate['types'].keys():
                objectType = eachType
                break

        if objectType is None:
            objectType = 'default'

        # Generate a name by concatenating the resolved tokens together.
        builtName = ""
        skipSep = False
        for token in nameFormat:

            if token is 'sep':
                if not skipSep:
                    builtName += nameTemplate['separator']

            elif token is 'location':
                if self.isTypeOf('Component'):
                    location = self.getLocation()
                elif self.getComponent() is None:
                    location = None
                else:
                    component = self.getComponent()
                    if component is None:
                        raise ValueError("object [%s] does not have a component." % self.getName())
                    location = component.getLocation()

                altLocation = self.getMetaDataItem("altLocation")
                if altLocation is not None and altLocation in nameTemplate['locations']:
                    location = altLocation

                if location not in nameTemplate['locations']:
                    msg = "Invalid location on '{}'. Location: {}. Valid locations: {}"
                    msg = msg.format(self.getPath(), location, nameTemplate['locations'])
                    raise ValueError(msg)

                builtName += location

            elif token is 'type':

                if objectType == 'Locator' and self.testFlag('inputObject'):
                    objectType = 'ComponentInput'
                elif objectType == 'Locator' and self.testFlag('outputObject'):
                    objectType = 'ComponentOutput'

                altType = self.getMetaDataItem("altType")
                if altType is not None and nameTemplate['types'].get(altType, None) is not None:
                    objectType = altType

                builtName += nameTemplate['types'][objectType]

            elif token is 'name':
                builtName += self.getName()

            elif token is 'component':
                if self.getComponent() is None:
                    skipSep = True
                    continue
                builtName += self.getComponent().getName()

            elif token is 'container':
                if self.getContainer() is None:
                    skipSep = True
                    continue
                builtName += self.getContainer().getName()

            else:
                raise ValueError("Unresolvabled token '" + token +
                                 "' used on: " + self.getPath())

        return builtName

    def setName(self, name):
        """Sets the name of the object with a string.

        Args:
            name (str): The new name for the item.

        Returns:
            bool: True if successful.

        """

        # check for name collision and adjust the name if they exist
        if self.getParent() is not None:
            # Increment name if it already exists
            initName = name
            suffix = 1
            collision = True
            while collision:
                child = self.getParent().getChildByDecoratedName(name + self.getNameDecoration())
                collision = child is not None and child is not self
                if not collision:
                    break

                result = re.split(r"(\d+)$", initName, 1)
                if len(result) > 1:
                    initName = result[0]
                    suffix = int(result[1])

                name = initName + str(suffix).zfill(2)
                suffix += 1

        super(Object3D, self).setName(name)

        return True

    # ==================
    # Hierarchy Methods
    # ==================
    def getContainer(self):
        """Returns the Container the object belongs to.

        Returns:
            Object: Container.

        """

        parent = self.getParent()
        while (parent is not None and 'Container' not in
               parent.getTypeHierarchyNames()):
            parent = parent.getParent()

        return parent

    def getLayer(self):
        """Returns the Layer the object belongs to.

        Returns:
            Object: Layer this object belongs to.

        """

        parent = self.getParent()
        while (parent is not None and not parent.isTypeOf('Layer')):
            parent = parent.getParent()

        return parent

    # ==============
    # Child Methods
    # ==============
    def hasChild(self, child):
        """Checks the supplied item is a child

        Args:
            child (Object): Object to check if is is a child of this object.

        """

        for i, eachChild in enumerate(self.getChildren()):
            if eachChild == child:
                return True

        return False

    def _checkChildIndex(self, index):
        """Checks the supplied index is valid.

        Args:
            index (int): Child index to check.

        """

        if index > len(self.getChildren()):
            raise IndexError("'" + str(index) +
                             "' is out of the range of the 'children' array.")

        return True

    def addChild(self, child):
        """Adds a child to this object.

        Note:
            We allow for duplicate child names as long as the types differ.

        Args:
            child (Object): Object that will be a child of this object.

        Returns:
            bool: True if successful.

        """
        SceneItem.setParent(child, self)

        if child.getParent() is not None:
            parent = child.getParent()
            if child in parent.getChildren():
                parent.getChildren().remove(child)

        child.setName(child.getName())

        self.getChildren().append(child)

        # Assign the child the same component.
        if self._component is not None:
            child.setComponent(self._component)

        return True


    def setParent(self, parent):
        """Sets the parent of this object.

        Arguments:
        parent (Object): Object that is the parent of this one.

        Returns:
            bool: True if successful.

        """
        if parent:
            parent.addChild(self)
        else:
            if self._parent is not None:
                parent.removeChild(self)
            SceneItem.setParent(self, None)

        return True

    def removeChildByIndex(self, index):
        """Removes a child from this object by index.

        Args:
            index (int): Index of child to remove.

        Returns:
            bool: True if successful.

        """

        if self._checkChildIndex(index) is not True:
            return False

        self.removeChild(self.getChildren()[index])

        return True

    def removeChildByName(self, name):
        """Removes a child from this object by name.

        Args:
            name (str): Name of child to remove.

        Returns:
            bool: True if successful.

        """

        removeIndex = None

        for i, eachChild in enumerate(self.getChildren()):
            if eachChild.getName() == name:
                removeIndex = i

        if removeIndex is None:
            raise ValueError("'" + name +
                             "' is not a valid child of this object.")

        self.removeChildByIndex(removeIndex)

        return True

    def removeChild(self, child):
        """Removed the child as an child item of this object.

        Returns:
            bool: True if successful.

        """

        try:
            self._children.remove(child)
        except:
            names = []
            for c in self._children:
                names.append(c.getName())
            raise Exception("Object '" + self.getPath() +
                            "' does not have child:" + child.getPath() +
                            ". it does have:" + str(names))

        SceneItem.setParent(child, None)

        # Un-assign the child the component.
        if self._component is not None:
            child.setComponent(None)

        return True

    def getDescendents(self, nodeList=None, classType=None, inheritedClass=False):
        """Gets the children of this object.

        Args:
            nodeList: (list): optional list to append children to
            classType (str): Name of the type of class to limit the search to
            inheritedClass (bool): Match nodes that is a sub-class of type.

        Returns:
            list: Child objects.

        """

        if nodeList is None:
            nodeList = []

        for child in self._children:
                if classType is not None:
                    if inheritedClass is not None and child.isTypeOf(classType):
                        nodeList.append(child)
                    elif child.getTypeName() == classType:
                        nodeList.append(child)

                else:
                    nodeList.append(child)

                child.getDescendents(classType=classType,
                                     nodeList=nodeList,
                                     inheritedClass=inheritedClass)

        return nodeList

    def getChildren(self):
        """Gets the children of this object.

        Returns:
            list: Child objects.

        """

        return self._children

    def getNumChildren(self):
        """Returns the number of children this object has.

        Returns:
            int: Number of children of this object.

        """

        return len(self.getChildren())

    def getChildByIndex(self, index):
        """Returns the child object at specified index.

        Args:
            index (int): Index of the child to find.

        Returns:
            Object: Child object at specified index.

        """

        if self._checkChildIndex(index) is not True:
            return False

        return self.getChildren()[index]

    def getChildByName(self, name):
        """Returns the child object with the specified name.

        Args:
            name (str): Name of the child to return.

        Returns:
            Object: Object if found.

        """

        for eachChild in self.getChildren():
            if eachChild.getName() == name:
                return eachChild

        return None

    def getChildByDecoratedName(self, decoratedName):
        """Returns the child object with the specified name.

        Args:
            decoratedName (str): Decorated name of the child to find.

        Returns:
            Object: Object if found.

        """

        for eachChild in self.getChildren():
            if eachChild.getDecoratedName() == decoratedName:
                return eachChild

        return None

    def getChildrenByType(self, childType):
        """Returns all children that are of the specified type.

        Args:
            childType (str): Type of children to find.

        Returns:
            list: Array of child objects of the specified type.

        """

        childrenOfType = []
        for eachChild in self.getChildren():
            if eachChild.isTypeOf(childType):
                childrenOfType.append(eachChild)

        return childrenOfType

    # ========================
    # Attribute Group Methods
    # ========================
    def _checkAttributeGroupIndex(self, index):
        """Checks the supplied index is valid.

        Args:
            index (int): Attribute index to check.

        Returns:
            bool: True if successful.

        """

        if index > len(self._attributeGroups):
            raise IndexError("'" + str(index) +
                             "' is out of the range of 'attributeGroups' array.")

        return True

    def addAttributeGroup(self, attributeGroup):
        """Adds an attributeGroup to this object.

        Args:
            attributeGroup (Object): Attribute Group object to add to this
                object.

        Returns:
            bool: True if successful.

        """

        if attributeGroup.getName() in [x.getName() for x in self._attributeGroups]:
            raise IndexError("Child with " + attributeGroup.getName() +
                             " already exists as a attributeGroup.")

        self._attributeGroups.append(attributeGroup)
        attributeGroup.setParent(self)

        return True

    def removeAttributeGroupByIndex(self, index):
        """Removes attribute at specified index.

        Args:
            index (int): Index of attribute to remove.

        Returns:
            bool: True if successful.

        """

        if self._checkAttributeGroupIndex(index) is not True:
            return False

        del self._attributeGroups[index]

        return True

    def removeAttributeGroupByName(self, name):
        """Removes the attribute with the specified name.

        Args:
            name (str): Name of the attribute to remove.

        Returns:
            bool: True if successful.

        """

        removeIndex = None

        for i, eachAttributeGroup in enumerate(self._attributeGroups):
            if eachAttributeGroup.getName() == name:
                removeIndex = i

        if removeIndex is None:
            return False

        self.removeAttributeGroupByIndex(removeIndex)

        return True

    def getNumAttributeGroups(self):
        """Returns the number of attributeGroups as an integer.

        Returns:
            int: Number of attributeGroups on this object.

        """

        return len(self._attributeGroups)

    def getAttributeGroupByIndex(self, index):
        """Returns the attribute at the specified index.

        Args:
            index (int): Index of the attribute to return.

        Returns:
            AttributeGroup: Attribute Group at the specified index.

        """

        if self._checkAttributeGroupIndex(index) is not True:
            return False

        return self._attributeGroups[index]

    def getAttributeGroupByName(self, name):
        """Return the attribute group with the specified name.

        Args:
            name (str): Name of the attribute group to return.

        Returns:
            Attribute: Attribute with the specified name.

        """

        for eachAttributeGroup in self._attributeGroups:
            if eachAttributeGroup.getName() == name:
                return eachAttributeGroup

        return None

    # ===================
    # Constraint Methods
    # ===================
    def checkConstraintIndex(self, index):
        """Checks the supplied index is valid.

        Args:
            index (int): Constraint index to check.

        Returns:
            bool: True if successful.

        """

        if index > len(self._constraints):
            raise IndexError("'" + str(index) +
                             "' is out of the range of 'constraints' array.")

        return True

    def constrainTo(self, constrainers, constraintType="Pose", maintainOffset=False, name=None):
        """Adds an constraint to this object.

        Args:
            constrainers (Object or Object list): Constraint object to add to
                this object or objects.
            constraintType (str): String name of the constraint type.
            maintainOffset (bool): Sets the constraint to maintain offset when
                creating the constraint.
            name (str): Name of the constraint. If set to None, a name is
                automatically generated.

        Returns:
            string: Constraint object

        """

        if name is None:
            constraintName = ""
            if hasattr(constrainers, '__iter__'):
                constraintName = '_'.join([self.getName(), 'To', constrainers[0].getName(), constraintType + 'Constraint'])
            else:
                constraintName = '_'.join([self.getName(), 'To', constrainers.getName(), constraintType + 'Constraint'])
        else:
            constraintName = name

        constraint = None
        if constraintType == "Orientation":
            constraint = OrientationConstraint(constraintName)
        elif constraintType == "Pose":
            constraint = PoseConstraint(constraintName)
        elif constraintType == "Position":
            constraint = PositionConstraint(constraintName)
        elif constraintType == "Scale":
            constraint = ScaleConstraint(constraintName)
        else:
            raise ValueError("'" + constraintType +
                "' is not a valid constraint type. Valid types are Orientation, Pose, Position, or Scale")

        # Accept a single object or a list of objects
        if hasattr(constrainers, '__iter__'):
            pass
        else:
            constrainers = [constrainers]

        for constrainer in constrainers:
            constraint.addConstrainer(constrainer)

        constraint.setMaintainOffset(maintainOffset)

        self.addConstraint(constraint)

        return constraint

    def addConstraint(self, constraint):
        """Adds an constraint to this object.

        Args:
            constraint (Object): Constraint object to add to this object.

        Returns:
            bool: True if successful.

        """

        if constraint.getName() in [x.getName() for x in self._constraints]:
            raise IndexError("Constraint with name '" + constraint.getName() +
                             "'' already exists as a constraint.")

        for x in self._constraints:
            if x.isTypeOf(constraint.getTypeName()):
                raise IndexError("Constraint with type '" + constraint.getTypeName() +
                                 "'' already exists on object.")

        self._constraints.append(constraint)

        constraint.setParent(self)
        constraint.setConstrainee(self)

        return True

    def removeConstraintByIndex(self, index):
        """Removes constraint at specified index.

        Args:
            index (int): Index of constraint to remove.

        Returns:
            bool: True if successful.

        """

        if self.checkConstraintIndex(index) is not True:
            return False

        sourceIndex = self._sources.index(self._constraints[index])
        del self._sources[sourceIndex]
        del self._constraints[index]

        return True

    def removeConstraintByName(self, name):
        """Removes the constraint with the specified name.

        Args:
            name (str): Name of the constraint to remove.

        Returns:
            bool: True if successful.

        """

        removeIndex = None

        for i, eachConstraint in enumerate(self._constraints):
            if eachConstraint.getName() == name:
                removeIndex = i

        if removeIndex is None:
            return False

        self.removeConstraintByIndex(removeIndex)

        return True

    def removeAllConstraints(self):
        """Removes all of the constraints for this object.

        Returns:
            bool: True if successful.

        """

        while len(self._constraints) > 0:
            self.removeConstraintByIndex(0)

        return True

    def getNumConstraints(self):
        """Returns the number of constraints as an integer.

        Returns:
            int: Number of constraints on this object.

        """

        return len(self._constraints)

    def getConstraintByIndex(self, index):
        """Returns the constraint at the specified index.

        Args:
            index (int): Index of the constraint to return.

        Returns:
            Constraint: Constraint at the specified index.

        """

        if self.checkConstraintIndex(index) is not True:
            return False

        return self._constraints[index]

    def getConstraintByName(self, name):
        """Return the constraint group with the specified name.

        Args:
            name (str): Name of the constraint group to return.

        Returns:
            Attribute: Attribute with the specified name.

        """

        for eachConstraint in self._constraints:
            if eachConstraint.getName() == name:
                return eachConstraint

        return None

    # ===================
    # Visibility Methods
    # ===================
    def getVisibilityAttr(self):
        """Returns the Visibility attribute object.

        Returns:
            BoolAttribute: Attribute that holds the value of the visibility.

        """

        return self._visibility

    def getVisibility(self):
        """Returns the visibility status of the scene item.

        Returns:
            bool: Visible or not.

        """

        return self._visibility.getValue()

    def setVisibility(self, value):
        """Sets the visibility of the scene object.

        Args:
            value (bool): value of the visibility of the object.

        Returns:
            bool: True if successful.

        """

        self._visibility.setValue(value)

        return True

    def getShapeVisibilityAttr(self):
        """Returns the Shape Visibility attribute object.

        Returns:
            BoolAttribute: Attribute that holds the value of the shape
                visibility.

        """

        return self._shapeVisibility

    def getShapeVisibility(self):
        """Returns the shape visibility status of the scene item.

        Returns:
            bool: Visible or not.

        """

        return self._shapeVisibility.getValue()

    def setShapeVisibility(self, value):
        """Sets the shape visibility of the scene object.

        Args:
            value (bool): Value of the visibility of the object.

        Returns:
            bool: True if successful.

        """

        self._shapeVisibility.setValue(value)

        return True

    # ================
    # Display Methods
    # ================
    def setColor(self, color):
        """Sets the color of this object.

        Args:
            color (str, Color): Name of the color from the Config or a Color() object.

        Returns:
            bool: True if successful.

        """

        assert type(color).__name__ in ('str', 'Color'), self.getPath() + \
            ".setColor(), 'color' argument type is not of type 'str' or 'Color'."

        self._color = color

        return True

    def getColor(self):
        """Returns the color of the object.

        Returns:
            str: Color of the object.

        """

        return self._color

    # ==========================
    # Parameter Locking Methods
    # ==========================
    def lockRotation(self, x=False, y=False, z=False):
        """Sets flags for locking rotation parameters.

        Args:
            x (bool): Lock x axis.
            y (bool): Lock y axis.
            z (bool): Lock z axis.

        Returns:
            bool: True if successful.

        """

        if x is True:
            self.setFlag("lockXRotation")

        if y is True:
            self.setFlag("lockYRotation")

        if z is True:
            self.setFlag("lockZRotation")

        return True

    def lockScale(self, x=False, y=False, z=False):
        """Sets flags for locking scale parameters.

        Args:
            x (bool): Lock x axis.
            y (bool): Lock y axis.
            z (bool): Lock z axis.

        Returns:
            bool: True if successful.

        """

        if x is True:
            self.setFlag("lockXScale")

        if y is True:
            self.setFlag("lockYScale")

        if z is True:
            self.setFlag("lockZScale")

        return True

    def lockTranslation(self, x=False, y=False, z=False):
        """Sets flags for locking translation parameters.

        Args:
            x (bool): Lock x axis.
            y (bool): Lock x axis.
            z (bool): Lock x axis.

        Returns:
            bool: True if successful.

        """

        if x is True:
            self.setFlag("lockXTranslation")

        if y is True:
            self.setFlag("lockYTranslation")

        if z is True:
            self.setFlag("lockZTranslation")

        return True

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

        classHierarchy = self.getTypeHierarchyNames()

        jsonData = {
            '__typeHierarchy__': classHierarchy,
            'name': self.getName(),
            'parent': None,
            'children': [],
            'flags': self._flags,
            'attributeGroups': [],
            'constraints': [],
            'xfo': self.xfo.jsonEncode(),
        }

        if self.getParent() is not None:
            jsonData['parent'] = self.getParent().getName()

        if self.getColor() is not None:
            if type(self.getColor()) is tuple:
                jsonData['color'] = self.getColor()
            elif type(self.getColor()):
                jsonData['color'] = self.getColor()

        jsonData['visibility'] = self.getVisibilityAttr().jsonEncode(saver)
        jsonData['shapeVisibility'] = self.getShapeVisibilityAttr().jsonEncode(saver)

        for child in self.getChildren():
            jsonData['children'].append(child.jsonEncode(saver))

        for attrGroup in self._attributeGroups:
            jsonData['attributeGroups'].append(attrGroup.jsonEncode(saver))

        for constr in self._constraints:
            jsonData['constraints'].append(constr.jsonEncode(saver))

        return jsonData

    def jsonDecode(self, loader, jsonData):
        """Returns the color of the object..

        Args:
            loader (Object): Loader object.
            jsonData (Dict): JSON object structure.

        Returns:
            bool: True if successful.

        """

        self._flags = jsonData['flags']
        self.xfo = Xfo()
        self.xfo.jsonDecode(jsonData['xfo'], decodeValue)

        if 'color' in jsonData and jsonData['color'] is not None:
            self.color.jsonDecode(jsonData['color'], decodeValue)

        self._visibility = loader.construct(jsonData['visibility'])
        self._shapeVisibility = loader.construct(jsonData['shapeVisibility'])

        for child in jsonData['children']:
            self.addChild(loader.construct(child))

        for attrGroup in jsonData['attributeGroups']:
            # There is one default attribute group assigned to each scene item.
            # Load data into the existing item instead of constructing a new
            # one.
            if attrGroup['name'] == '':
                loader.registerItem(self._attributeGroups[0])
                self._attributeGroups[0].jsonDecode(loader, attrGroup)
            else:
                self.addAttributeGroup(loader.construct(attrGroup))

        for constr in jsonData['constraints']:
            self.addConstraint(loader.construct(constr))

        return True
