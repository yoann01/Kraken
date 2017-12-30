"""Kraken - builders module.

Classes:
Builder -- Base builder object to build objects in DCC.

"""

import os
import logging

from kraken.log import getLogger

from kraken.core.kraken_system import KrakenSystem
from kraken.core.configs.config import Config
from kraken.core.profiler import Profiler

from kraken.core.objects.scene_item import SceneItem
from kraken.core.objects.object_3d import Object3D
from kraken.core.traverser import Traverser

logger = getLogger('kraken')
logger.setLevel(logging.INFO)


class Builder(object):
    """Core Builder class for building objects.

    Note:
        Sub-class for each DCC in it's plugin directory.

    This builder traverses the graph and determines the the build order. Once
    the build order has been determined, the builder iterates through the list
    and builds each object type. Each object type has it's own method for users
    to re-implement for each application.

    Attributes:
        _buildPhase_3DObjectsAttributes (type): Description.
        _buildPhase_AttributeConnections (type): Description.
        _buildPhase_ConstraintsOperators (type): Description.

    """

    _buildPhase_3DObjectsAttributes = 0
    _buildPhase_AttributeConnections = 1
    _buildPhase_ConstraintsOperators = 2
    _buildPhase_lockAttributes = 3
    _buildPhase_lockTransformAttrs = 4

    def __init__(self, debugMode=False):
        super(Builder, self).__init__()
        self._buildElements = []
        self._sceneItemsById = {}

        self.config = Config.getInstance()

        self._debugMode = debugMode

    # ====================
    # Object registration
    # ====================
    def _registerSceneItemPair(self, kSceneItem, dccSceneItem):
        """Registers a pairing between the kraken scene item and the dcc scene item
        for querying later.

        Args:
            kSceneItem (object): kraken scene item that you want to pair.
            dccSceneItem (object): dcc scene item that you want to pair.

        Returns:
            bool: True if successful.

        """

        pairing = {
            "src": kSceneItem,
            "tgt": dccSceneItem
        }

        self._buildElements.append(pairing)

        return True

    def deleteBuildElements(self):
        """Clear out all dcc built elements from the scene if exist."""

        return None

    def getDCCSceneItem(self, kSceneItem):
        """Given a kSceneItem, returns the built dcc scene item.

        Args:
            kSceneItem (object): kSceneItem to base the search.

        Returns:
            object: The DCC Scene Item that corresponds to the given scene item

        """

        if isinstance(kSceneItem, SceneItem):
            for builtElement in self._buildElements:
                if builtElement['src'] == kSceneItem:
                    return builtElement['tgt']

        return None

    def getDCCSceneItemPairs(self):
        """Returns all of the built dcc scene item pairs.

        Returns:
            array: An array of dicts with 'src' and 'tgt' key value pairs

        """

        return self._buildElements

    # ========================
    # SceneItem Build Methods
    # ========================
    def buildContainer(self, kContainer, buildName):
        """Builds a container / namespace object.

        Args:
            kContainer (object): kContainer that represents a container to be
                built.
            buildName (string): The name to use on the built object.

        Returns:
            object: DCC Scene Item that is created.

        """

        logger.info("buildContainer: " + kContainer.getPath() + " as: " +
                    buildName)

        return self.buildLocator(kContainer, buildName)

    def buildLayer(self, kSceneItem, buildName):
        """Builds a layer object.

        Args:
            kSceneItem (object): kSceneItem that represents a layer to be built.
            buildName (string): The name to use on the built object.

        Returns:
            object: DCC Scene Item that is created.

        """

        logger.info("buildLayer: " + kSceneItem.getPath() + " as: " + buildName)

        return None

    def buildHierarchyGroup(self, kSceneItem, buildName):
        """Builds a hierarchy group object.

        Args:
            kSceneItem (object): kSceneItem that represents a group to be built.
            buildName (string): The name to use on the built object.

        Returns:
            object: DCC Scene Item that is created.

        """


        logger.info("buildHierarchyGroup: " + kSceneItem.getPath() + " as: " +
                    buildName)

        return None

    def buildGroup(self, kSceneItem, buildName):
        """Builds a group object.

        Args:
            kSceneItem (object): kSceneItem that represents a group to be built.
            buildName (string): The name to use on the built object.

        Returns:
            object: DCC Scene Item that is created.

        """

        logger.info("buildGroup: " + kSceneItem.getPath() + " as: " +
                    buildName)

        return None

    def buildJoint(self, kSceneItem, buildName):
        """Builds a joint object.

        Args:
            kSceneItem (object): kSceneItem that represents a joint to be built.
            buildName (string): The name to use on the built object.

        Returns:
            object: DCC Scene Item that is created.

        """

        logger.info("buildJoint: " + kSceneItem.getPath() + " as: " +
                    buildName)

        return None

    def buildLocator(self, kSceneItem, buildName):
        """Builds a locator / null object.

        Args:
            kSceneItem (object): kSceneItem that represents a locator / null to be built.
            buildName (string): The name to use on the built object.

        Returns:
            object: DCC Scene Item that is created.

        """


        logger.info("buildLocator: " + kSceneItem.getPath() + " as: " +
                    buildName)

        return None

    def buildCurve(self, kSceneItem, buildName):
        """Builds a Curve object.

        Args:
            kSceneItem (object): kSceneItem that represents a curve to be built.
            buildName (string): The name to use on the built object.

        Returns:
            object: DCC Scene Item that is created.

        """

        logger.info("buildCurve: " + kSceneItem.getPath() + " as: " +
                    buildName)

        return None

    def buildControl(self, kSceneItem, buildName):
        """Builds a Control object.

        Args:
            kSceneItem (object): kSceneItem that represents a control to be built.
            buildName (string): The name to use on the built object.

        Returns:
            object: DCC Scene Item that is created.

        """

        logger.info("buildControl:" + kSceneItem.getPath() + " as: " +
                    buildName)

        return None

    # ========================
    # Attribute Build Methods
    # ========================
    def buildBoolAttribute(self, kAttribute):
        """Builds a Bool attribute.

        Args:
            kAttribute (object): kAttribute that represents a string attribute to be built.

        Returns:
            object: True if successful.

        """

        logger.info("buildBoolAttribute: " + kAttribute.getPath())

        return True

    def buildScalarAttribute(self, kAttribute):
        """Builds a Float attribute.

        Args:
            kAttribute (object): kAttribute that represents a string attribute to be built.

        Returns:
            bool: True if successful.

        """


        logger.info("buildScalarAttribute: " + kAttribute.getPath())

        return True

    def buildIntegerAttribute(self, kAttribute):
        """Builds a Integer attribute.

        Args:
            kAttribute (object): kAttribute that represents a string attribute to be built.

        Returns:
            bool: True if successful.

        """


        logger.info("buildIntegerAttribute: " + kAttribute.getPath())

        return True

    def buildStringAttribute(self, kAttribute):
        """Builds a String attribute.

        Args:
            kAttribute (object): kAttribute that represents a string attribute to be built.

        Returns:
            bool: True if successful.

        """

        logger.info("buildStringAttribute: " + kAttribute.getPath())

        return True

    def buildAttributeGroup(self, kAttributeGroup):
        """Builds attribute groups on the DCC object.

        Args:
            kAttributeGroup (SceneObject): kraken object to build the attribute group on.

        Returns:
            bool: True if successful.

        """

        logger.info("buildAttributeGroup: " + kAttributeGroup.getPath())

        return True

    def connectAttribute(self, kAttribute):
        """Connects the driver attribute to this one.

        Args:
            kAttribute (object): attribute to connect.

        Returns:
            bool: True if successful.

        """


        logger.info("connectAttribute: " + kAttribute.getPath())

        return True

    # =========================
    # Constraint Build Methods
    # =========================
    def buildOrientationConstraint(self, kConstraint, buildName):
        """Builds an orientation constraint represented by the kConstraint.

        Args:
            kConstraint (object): kraken constraint object to build.

        Returns:
            object: DCC Scene Item that was created.

        """

        logger.info("buildOrientationConstraint: " + kConstraint.getPath() +
                    " to: " + kConstraint.getConstrainee().getPath())

        dccSceneItem = None  # Add constraint object here.
        self._registerSceneItemPair(kConstraint, dccSceneItem)

        return dccSceneItem

    def buildPoseConstraint(self, kConstraint, buildName):
        """Builds an pose constraint represented by the kConstraint.

        Args:
            kConstraint (object): kraken constraint object to build.

        Returns:
            bool: True if successful.

        """

        logger.info("buildPoseConstraint: " + kConstraint.getPath() + " to: " +
                    kConstraint.getConstrainee().getPath())

        dccSceneItem = None  # Add constraint object here.
        self._registerSceneItemPair(kConstraint, dccSceneItem)

        return dccSceneItem

    def buildPositionConstraint(self, kConstraint, buildName):
        """Builds an position constraint represented by the kConstraint.

        Args:
            kConstraint (object): kraken constraint object to build.

        Returns:
            bool: True if successful.

        """

        logger.info("buildPositionConstraint:" + kConstraint.getPath() +
                    " to: " + kConstraint.getConstrainee().getPath())

        dccSceneItem = None  # Add constraint object here.
        self._registerSceneItemPair(kConstraint, dccSceneItem)

        return dccSceneItem

    def buildScaleConstraint(self, kConstraint, buildName):
        """Builds an scale constraint represented by the kConstraint.

        Args:
            kConstraint (object): kraken constraint object to build.

        Returns:
            bool: True if successful.

        """

        logger.info("buildScaleConstraint: " + kConstraint.getPath() +
                    " to: " + kConstraint.getConstrainee().getPath())

        dccSceneItem = None  # Add constraint object here.
        self._registerSceneItemPair(kConstraint, dccSceneItem)

        return dccSceneItem


    # =========================
    # Operator Builder Methods
    # =========================
    def buildKLOperator(self, kKLOperator, buildName):
        """Builds Splice Operators on the components.

        Note:
            Implement in DCC Plugins.

        Args:
            kOperator (object): kraken operator that represents a KL operator.

        Returns:
            bool: True if successful.

        """

        logger.info("buildKLOperator:" + kKLOperator.getPath() + " as: " +
                    buildName)

        return True

    def buildCanvasOperator(self, kOperator, buildName):
        """Builds Splice Operators on the components.

        Note:
            Implement in DCC Plugins.

        Args:
            kOperator (object): kraken operator that represents a Canvas
                operator.

        Returns:
            bool: True if successful.

        """

        logger.info("buildCanvasOperator: " + kOperator.getPath() + " as: " +
                    buildName)

        return True

    # =====================
    # Build Object Methods
    # =====================
    def __buildSceneItem(self, kObject, phase):
        """Builds the DCC sceneitem for the supplied kObject.

        Args:
            kObject (object): kraken object to build.
            phase (type): Description.

        Returns:
            object: DCC object that was created.

        """

        dccSceneItem = None

        buildName = kObject.getName()
        if hasattr(kObject, 'getBuildName'):
            buildName = kObject.getBuildName()

        logger.debug("building(" + str(phase) + "): " + kObject.getPath() +
                     " as: " + buildName + " type: " + kObject.getTypeName())

        # Build Object
        if kObject.isTypeOf("Rig"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildContainer(kObject, buildName)

        elif kObject.isTypeOf("Layer"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildLayer(kObject, buildName)

        elif kObject.isTypeOf("Component"):
            return None

        elif kObject.isTypeOf("ComponentGroup"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildGroup(kObject, buildName)

        elif kObject.isTypeOf("HierarchyGroup"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildHierarchyGroup(kObject, buildName)

        elif kObject.isTypeOf("CtrlSpace"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildGroup(kObject, buildName)

        elif kObject.isTypeOf("Transform"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildGroup(kObject, buildName)

        elif kObject.isTypeOf("Locator"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildLocator(kObject, buildName)

        elif kObject.isTypeOf("Joint"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildJoint(kObject, buildName)

        elif kObject.isTypeOf("Control"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildControl(kObject, buildName)

        elif kObject.isTypeOf("Curve"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildCurve(kObject, buildName)

        elif kObject.isTypeOf('AttributeGroup'):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildAttributeGroup(kObject)

        elif kObject.isTypeOf("BoolAttribute"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildBoolAttribute(kObject)
            elif phase == self._buildPhase_AttributeConnections:
                self.connectAttribute(kObject)

        elif kObject.isTypeOf("ScalarAttribute"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildScalarAttribute(kObject)
            elif phase == self._buildPhase_AttributeConnections:
                self.connectAttribute(kObject)

        elif kObject.isTypeOf("IntegerAttribute"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildIntegerAttribute(kObject)
            elif phase == self._buildPhase_AttributeConnections:
                self.connectAttribute(kObject)

        elif kObject.isTypeOf("StringAttribute"):
            if phase == self._buildPhase_3DObjectsAttributes:
                dccSceneItem = self.buildStringAttribute(kObject)
            elif phase == self._buildPhase_AttributeConnections:
                self.connectAttribute(kObject)

        elif kObject.isTypeOf("OrientationConstraint"):
            if phase == self._buildPhase_ConstraintsOperators:
                dccSceneItem = self.buildOrientationConstraint(kObject, buildName)

        elif kObject.isTypeOf("PoseConstraint"):
            if phase == self._buildPhase_ConstraintsOperators:
                dccSceneItem = self.buildPoseConstraint(kObject, buildName)

        elif kObject.isTypeOf("PositionConstraint"):
            if phase == self._buildPhase_ConstraintsOperators:
                dccSceneItem = self.buildPositionConstraint(kObject, buildName)

        elif kObject.isTypeOf("ScaleConstraint"):
            if phase == self._buildPhase_ConstraintsOperators:
                dccSceneItem = self.buildScaleConstraint(kObject, buildName)

        elif kObject.isTypeOf("KLOperator"):
            if phase == self._buildPhase_ConstraintsOperators:
                dccSceneItem = self.buildKLOperator(kObject, buildName)

        elif kObject.isTypeOf("CanvasOperator"):
            if phase == self._buildPhase_ConstraintsOperators:
                dccSceneItem = self.buildCanvasOperator(kObject, buildName)

        # Important Note: The order of these tests is important.
        # New classes should be added above the classes they are derrived from.
        # No new types should be added below SceneItem here.
        elif kObject.isTypeOf("SceneItem"):
            if phase == 0:
                dccSceneItem = self.buildLocator(kObject, buildName)

        else:
            raise NotImplementedError(kObject.getName() +
                                      ' has an unsupported type: ' +
                                      str(type(kObject)))

        if dccSceneItem is not None:
            self._sceneItemsById[kObject.getId()] = dccSceneItem
        else:
            dccSceneItem = self._sceneItemsById.get(kObject.getId(), None)

        if dccSceneItem is not None and isinstance(kObject, Object3D) and \
            phase == self._buildPhase_ConstraintsOperators:

            self.setTransform(kObject)
            self.setVisibility(kObject)
            self.setObjectColor(kObject)

        if dccSceneItem is not None and kObject.isTypeOf("Attribute") is True and \
            phase == self._buildPhase_lockAttributes:

            self.lockAttribute(kObject)

        if dccSceneItem is not None and isinstance(kObject, Object3D) and \
            phase == self._buildPhase_lockTransformAttrs:

            self.lockTransformAttrs(kObject)

        return dccSceneItem

    def __buildSceneItemList(self, kObjects, phase):
        """Builds the provided list of objects.

        Args:
            kObjects (list): Objects to be built.
            phase (int): Description.

        Returns:
            Type: True if successful.

        """

        for kObject in kObjects:
            self.__buildSceneItem(kObject, phase)


    def build(self, kSceneItem):
        """Builds a rig object.

        We have to re-order component children by walking the graph to ensure
        that inputs objects are in place for the dependent components.

        Args:
            kSceneItem (sceneitem): The item to be built.

        Returns:
            object: DCC Scene Item that is created.

        """

        Profiler.getInstance().push("build:" + kSceneItem.getName())

        traverser = Traverser('Children')
        traverser.addRootItem(kSceneItem)

        rootItems = traverser.traverse(
            discoverCallback=traverser.discoverChildren,
            discoveredItemsFirst=False)

        traverser = Traverser('Build')
        for rootItem in rootItems:
            traverser.addRootItem(rootItem)
        traverser.traverse()

        try:
            self._preBuild(kSceneItem)

            objects3d = traverser.getItemsOfType('Object3D')
            attributeGroups = traverser.getItemsOfType(['AttributeGroup'])
            attributes = traverser.getItemsOfType(['Attribute'])

            # build all 3D objects and attributes
            self.__buildSceneItemList(objects3d,
                                      self._buildPhase_3DObjectsAttributes)

            self.__buildSceneItemList(attributeGroups,
                                      self._buildPhase_3DObjectsAttributes)

            self.__buildSceneItemList(attributes,
                                      self._buildPhase_3DObjectsAttributes)

            # connect all attributes
            self.__buildSceneItemList(attributes,
                                      self._buildPhase_AttributeConnections)

            # build all additional connections
            self.__buildSceneItemList(traverser.items,
                                      self._buildPhase_ConstraintsOperators)

            # lock parameters
            self.__buildSceneItemList(attributes,
                                      self._buildPhase_lockAttributes)

            # lock parameters
            self.__buildSceneItemList(traverser.items,
                                      self._buildPhase_lockTransformAttrs)

        finally:
            self._postBuild(kSceneItem)

            # Clear Config when finished.
            self.config.clearInstance()

        Profiler.getInstance().pop()

        return self.getDCCSceneItem(kSceneItem)

    # ==================
    # Attribute Methods
    # ==================
    def lockAttribute(self, kAttribute):
        """Locks attributes.

        Args:
            kAttribute (object): kraken attributes to lock.

        Returns:
            bool: True if successful.

        """

        return True

    def lockTransformAttrs(self, kSceneItem):
        """Locks the transform attributes on an object.

        Args:
            kSceneItem (object): kraken object to lock the SRT attributes on.

        Returns:
            Type: True if successful.

        """

        return True


    # ===================
    # Visibility Methods
    # ===================
    def setVisibility(self, kSceneItem):
        """Sets the visibility of the object after its been created.

        Args:
            kSceneItem (object): kraken object to set the visibility on.

        Returns:
            bool: True if successful.

        """

        return True

    # ================
    # Display Methods
    # ================
    def getBuildColor(self, kSceneItem):
        """Gets the build color for the object.

        Args:
            kSceneItem (object): kraken object to get the color for.

        Returns:
            str: color to set on the object.

        """

        config = self.getConfig()
        colors = config.getColors()
        colorMap = config.getColorMap()
        typeNames = kSceneItem.getTypeHierarchyNames()
        component = kSceneItem.getComponent()
        objectColor = kSceneItem.getColor()

        buildColor = None
        if objectColor is not None:

            if type(objectColor) is str:
                if objectColor not in colors:
                    buildColor = colorMap['Default']

                    warning = "Invalid color '{}' on '{}', default color '{}' will be used."
                    logger.warn(warning.format(objectColor, kSceneItem.getPath(), buildColor))

                else:
                    buildColor = objectColor

            elif type(objectColor).__name__ == "Color":
                buildColor = objectColor
            else:
                raise TypeError("Invalid type for object color: '" + type(objectColor).__name__ + "'")

        else:
            #  Find the first color mapping that matches a type in the object
            #  hierarchy.
            for typeName in typeNames:
                if typeName in colorMap.keys():
                    if component is None:
                        buildColor = colorMap[typeName]['default']
                    else:
                        componentLocation = component.getLocation()
                        buildColor = colorMap[typeName][componentLocation]
                    break

        return buildColor

    def setObjectColor(self, kSceneItem):
        """Sets the color on the dccSceneItem.

        Args:
            kSceneItem (object): kraken object to set the color on.

        Returns:
            bool: True if successful.

        """

        return True

    # ==================
    # Transform Methods
    # ==================
    def setTransform(self, kSceneItem):
        """Translates the transform to Softimage transform.

        Args:
            kSceneItem (object): object to set the transform on.

        Returns:
            bool: True if successful.

        """

        return True

    # ===============
    # Config Methods
    # ===============
    def getConfig(self):
        """Gets the current config for the builder.

        Returns:
            object: config.

        """

        return self.config

    def setConfig(self, config):
        """Sets the builder's config.

        Args:
            config (Config): the config to use for this builder.

        Returns:
            bool: True if successful.

        """

        self.config = config

        return True

    # ==============
    # Build Methods
    # ==============
    def _preBuild(self, kSceneItem):
        """Protected Pre-Build method.

        Args:
            kSceneItem (object): kraken kSceneItem object to build.

        Returns:
            bool: True if successful.

        """

        return True

    def _postBuild(self, kSceneItem):
        """Protected Post-Build method.

        Args:
            kSceneItem (object): kraken kSceneItem object to run post-build
                operations on.

        Returns:
            bool: True if successful.

        """

        if os.environ.get('KRAKEN_DCC', None) is not None:
            self.logOrphanedGraphItems(kSceneItem)

            invalidOps = []
            self.checkEvaluatedOps(kSceneItem, invalidOps)

            if len(invalidOps) > 0:
                logger.warn("Non-evaluated Operators:")
                logger.warn('\n'.join([x.getTypeName() + ': ' + x.getPath() + ' --  ('+x.getBuildName()+')' for x in invalidOps]))

            invalidConstraints = []
            self.checkEvaluatedConstraints(kSceneItem, invalidConstraints)

            if len(invalidConstraints) > 0:
                logger.warn("Non-evaluated Constraints:")
                logger.warn('\n'.join([x.getTypeName() + ': ' + x.getPath() + ' --  ('+x.getBuildName()+')' for x in invalidConstraints]))

        return True

    def logOrphanedGraphItems(self, kSceneItem):
        """Logs any objects that were left out from the build process.

        Args:
            kSceneItem (object): kraken kSceneItem object to recursively iterate
                on to find objects that weren't built.

        Returns:
            Type: True if successful.

        """

        def iterChildren(item, orphanedObjects):

            for each in item.getChildren():
                if each.getName() in ('implicitAttrGrp', 'visibility', 'ShapeVisibility'):
                    continue

                if each.isTypeOf('Component'):
                    continue

                if self.getDCCSceneItem(each) is None:
                    orphanedObjects.append(each)

                iterChildren(each, orphanedObjects)

        orphanedObjects = []
        iterChildren(kSceneItem, orphanedObjects)

        if len(orphanedObjects) > 0:
            logger.warn("Orphaned objects found:")
            logger.warn('\n'.join([x.getTypeName() + ': ' + x.getPath() for x in orphanedObjects]))

    def checkEvaluatedOps(self, kSceneItem, invalidOps):
        """Recursively checks for operators that haven't been evaluated.

        Args:
            kSceneItem (Object3D): Object to recursively check for invalid ops.
            invalidOps (list): List invalid operators will be appended to.

        Returns:
            bool: True if successful.

        """

        if kSceneItem.isTypeOf('Component'):
            for op in kSceneItem.getOperators():
                if op.testFlag('HAS_EVALUATED') is False:
                    invalidOps.append(op)

        for each in kSceneItem.getChildren():
            self.checkEvaluatedOps(each, invalidOps)

    def checkEvaluatedConstraints(self, kSceneItem, invalidConstraints):
        """Recursively checks for constraints that haven't been evaluated.
        Don't include leaf nodes or nodes that are simply parents as these don't
        need to be evaluated in the python graph, they can wait for the DCC

        Args:
            kSceneItem (Object3D): Object to recursively check for invalid ops.
            invalidConstraints (list): List invalid constraints will be appended to.

        Returns:
            bool: True if successful.

        """

        if kSceneItem.isTypeOf('Object3D'):
            for i in xrange(kSceneItem.getNumConstraints()):
                constraint = kSceneItem.getConstraintByIndex(i)
                if constraint.testFlag('HAS_EVALUATED') is False:
                    constrainee = constraint.getConstrainee()
                    depends = [obj for obj in constrainee.getDepends()
                            if obj.isTypeOf("Object3D") and obj not in constrainee.getChildren()
                            ]

                    if depends and constrainee.getTypeName() != 'ComponentInput':
                        invalidConstraints.append(constraint)

        for each in kSceneItem.getChildren():
            self.checkEvaluatedConstraints(each, invalidConstraints)