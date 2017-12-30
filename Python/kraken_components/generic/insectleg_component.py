import math

from kraken.core.maths import Vec3
from kraken.core.maths.xfo import Xfo
from kraken.core.maths.xfo import xfoFromDirAndUpV

from kraken.core.objects.components.base_example_component import BaseExampleComponent

from kraken.core.objects.attributes.attribute_group import AttributeGroup
from kraken.core.objects.attributes.scalar_attribute import ScalarAttribute
from kraken.core.objects.attributes.integer_attribute import IntegerAttribute
from kraken.core.objects.attributes.bool_attribute import BoolAttribute
from kraken.core.objects.attributes.string_attribute import StringAttribute

from kraken.core.objects.constraints.pose_constraint import PoseConstraint

from kraken.core.objects.component_group import ComponentGroup
from kraken.core.objects.components.component_output import ComponentOutput
from kraken.core.objects.hierarchy_group import HierarchyGroup
from kraken.core.objects.locator import Locator
from kraken.core.objects.joint import Joint
from kraken.core.objects.ctrlSpace import CtrlSpace
from kraken.core.objects.layer import Layer
from kraken.core.objects.control import Control

from kraken.core.objects.operators.kl_operator import KLOperator

from kraken.core.profiler import Profiler
from kraken.helpers.utility_methods import logHierarchy

from kraken.log import getLogger


logger = getLogger('kraken')


class InsectLegComponent(BaseExampleComponent):
    """Insect Leg Base"""

    def __init__(self, name='InsectLegBase', parent=None):

        super(InsectLegComponent, self).__init__(name, parent)

        # ===========
        # Declare IO
        # ===========
        # Declare Inputs Xfos
        self.rootInputTgt = self.createInput('rootInput', dataType='Xfo', parent=self.inputHrcGrp).getTarget()

        # Declare Output Xfos
        self.boneOutputs = self.createOutput('boneOutputs', dataType='Xfo[]')

        self.legEndXfoOutputTgt = self.createOutput('legEndXfoOutput', dataType='Xfo', parent=self.outputHrcGrp).getTarget()
        self.legEndPosOutputTgt = self.createOutput('legEndPosOutput', dataType='Xfo', parent=self.outputHrcGrp).getTarget()

        # Declare Input Attrs
        self.drawDebugInputAttr = self.createInput('drawDebug', dataType='Boolean', value=False, parent=self.cmpInputAttrGrp).getTarget()
        self.rigScaleInputAttr = self.createInput('rigScale', dataType='Float', value=1.0, parent=self.cmpInputAttrGrp).getTarget()
        self.tipBoneLenInputAttr = self.createInput('tipBoneLen', dataType='Float', value=1.0, parent=self.cmpInputAttrGrp).getTarget()

        # Declare Output Attrs


class InsectLegComponentGuide(InsectLegComponent):
    """InsectLeg Component Guide"""

    def __init__(self, name='InsectLeg', parent=None):

        Profiler.getInstance().push("Construct InsectLeg Guide Component:" + name)
        super(InsectLegComponentGuide, self).__init__(name, parent)

        # =========
        # Controls
        # =========
        guideSettingsAttrGrp = AttributeGroup("GuideSettings", parent=self)
        self.numJoints = IntegerAttribute('numJoints', value=5, minValue=2, maxValue=20, parent=guideSettingsAttrGrp)
        self.numJoints.setValueChangeCallback(self.updateNumLegControls)

        self.jointCtrls = []

        numJoints = self.numJoints.getValue()
        jointPositions = self.generateGuidePositions(numJoints)

        for i in xrange(numJoints):
            self.jointCtrls.append(Control('leg' + str(i + 1).zfill(2), parent=self.ctrlCmpGrp, shape="sphere"))

        jointXfos = []
        for i in xrange(numJoints):
            jointXfos.append(Xfo(jointPositions[i]))

        data = {
           "location": "L",
           "jointPositions": jointXfos,
           "numJoints": self.numJoints.getValue()
          }

        self.loadData(data)

        Profiler.getInstance().pop()


    # =============
    # Data Methods
    # =============
    def saveData(self):
        """Save the data for the component to be persisted.

        Return:
        The JSON data object

        """

        data = super(InsectLegComponentGuide, self).saveData()

        jointPositions = []
        for i in xrange(len(self.jointCtrls)):
            jointPositions.append(self.jointCtrls[i].xfo)

        data['jointPositions'] = jointPositions

        return data


    def loadData(self, data):
        """Load a saved guide representation from persisted data.

        Arguments:
        data -- object, The JSON data object.

        Return:
        True if successful.

        """

        super(InsectLegComponentGuide, self).loadData(data)

        for i in xrange(len(data['jointPositions'])):
            self.jointCtrls[i].xfo = data['jointPositions'][i]

        return True


    def getRigBuildData(self):
        """Returns the Guide data used by the Rig Component to define the layout of the final rig..

        Return:
        The JSON rig data object.

        """

        data = super(InsectLegComponentGuide, self).getRigBuildData()

        numJoints = self.numJoints.getValue()

        # Calculate FW
        toFirst = self.jointCtrls[0].xfo.tr.subtract(self.jointCtrls[1].xfo.tr).unit()
        toTip = self.jointCtrls[0].xfo.tr.subtract(self.jointCtrls[-1].xfo.tr).unit()
        fw = toTip.cross(toFirst).unit()

        # Calculate Xfos
        boneXfos = []
        boneLengths = []
        for i in xrange(numJoints):
            boneVec = self.jointCtrls[i + 1].xfo.tr.subtract(self.jointCtrls[i].xfo.tr)
            boneLengths.append(boneVec.length())
            bone1Normal = fw.cross(boneVec).unit()
            bone1ZAxis = boneVec.cross(bone1Normal).unit()

            xfo = Xfo()
            xfo.setFromVectors(boneVec.unit(), bone1Normal, bone1ZAxis, self.jointCtrls[i].xfo.tr)

            boneXfos.append(xfo)

        data['boneXfos'] = boneXfos
        data['endXfo'] = self.jointCtrls[-1].xfo
        data['boneLengths'] = boneLengths

        return data

    # ==========
    # Callbacks
    # ==========
    def updateNumLegControls(self, numJoints):
        """Generate the guide controls for the variable outputes array.

        Arguments:
        numJoints -- object, The number of joints in the chain.

        Return:
        True if successful.

        """

        if numJoints == 0:
            raise IndexError("'numJoints' must be > 0")

        if numJoints + 1 > len(self.jointCtrls):
            for i in xrange(len(self.jointCtrls), numJoints + 1):
                newCtrl = Control('leg' + str(i + 1).zfill(2), parent=self.ctrlCmpGrp, shape="sphere")
                self.jointCtrls.append(newCtrl)

        elif numJoints + 1 < len(self.jointCtrls):
            numExtraCtrls = len(self.jointCtrls) - (numJoints + 1)
            for i in xrange(numExtraCtrls):
                extraCtrl = self.jointCtrls.pop()
                self.ctrlCmpGrp.removeChild(extraCtrl)

        # Reset the control positions based on new number of joints
        jointPositions = self.generateGuidePositions(numJoints)
        for i in xrange(len(self.jointCtrls)):
            self.jointCtrls[i].xfo.tr = jointPositions[i]

        return True

    def generateGuidePositions(self, numJoints):
        """Generates the positions for the guide controls based on the number
        of joints.

        Args:
            numJoints (int): Number of joints to generate a transform for.

        Returns:
            list: Guide control positions.

        """

        halfPi = math.pi / 2.0
        step = halfPi / numJoints

        xValues = []
        yValues = []
        for i in xrange(numJoints + 1):
            xValues.append(math.cos((i * step) + halfPi) * -10)
            yValues.append(math.sin((i * step) + halfPi) * 10)

        guidePositions = []
        for i in xrange(numJoints + 1):
            guidePositions.append(Vec3(xValues[i], yValues[i], 0.0))

        return guidePositions


    # ==============
    # Class Methods
    # ==============
    @classmethod
    def getComponentType(cls):
        """Enables introspection of the class prior to construction to determine if it is a guide component.

        Return:
        The true if this component is a guide component.

        """

        return 'Guide'

    @classmethod
    def getRigComponentClass(cls):
        """Returns the corresponding rig component class for this guide component class

        Return:
        The rig component class.

        """

        return InsectLegComponentRig


class InsectLegComponentRig(InsectLegComponent):
    """Insect Leg Rig"""

    def __init__(self, name='InsectLeg', parent=None):

        Profiler.getInstance().push("Construct InsectLeg Rig Component:" + name)
        super(InsectLegComponentRig, self).__init__(name, parent)


        # =========
        # Controls
        # =========

        # Chain Base
        self.chainBase = Locator('ChainBase', parent=self.ctrlCmpGrp)
        self.chainBase.setShapeVisibility(False)

        # FK
        self.fkCtrlSpaces = []
        self.fkCtrls = []
        self.setNumControls(4)

        # IK Control
        self.legIKCtrlSpace = CtrlSpace('IK', parent=self.ctrlCmpGrp)
        self.legIKCtrl = Control('IK', parent=self.legIKCtrlSpace, shape="pin")

        if self.getLocation() == 'R':
            self.legIKCtrl.rotatePoints(0, 90, 0)
            self.legIKCtrl.translatePoints(Vec3(-1.0, 0.0, 0.0))
        else:
            self.legIKCtrl.rotatePoints(0, -90, 0)
            self.legIKCtrl.translatePoints(Vec3(1.0, 0.0, 0.0))

        # Add Component Params to IK control
        legSettingsAttrGrp = AttributeGroup("DisplayInfo_LegSettings", parent=self.legIKCtrl)
        legdrawDebugInputAttr = BoolAttribute('drawDebug', value=False, parent=legSettingsAttrGrp)
        legUseInitPoseInputAttr = BoolAttribute('useInitPose', value=True, parent=legSettingsAttrGrp)
        self.rootIndexInputAttr = IntegerAttribute('rootIndex', value=0, parent=legSettingsAttrGrp)
        legFkikInputAttr = ScalarAttribute('fkik', value=1.0, minValue=0.0, maxValue=1.0, parent=legSettingsAttrGrp)

        # Connect IO to controls
        self.drawDebugInputAttr.connect(legdrawDebugInputAttr)

        # UpV
        self.legUpVCtrlSpace = CtrlSpace('UpV', parent=self.ctrlCmpGrp)
        self.legUpVCtrl = Control('UpV', parent=self.legUpVCtrlSpace, shape="triangle")
        self.legUpVCtrl.alignOnZAxis()
        self.legUpVCtrl.rotatePoints(0, 90, 0)


        # ==========
        # Deformers
        # ==========
        deformersLayer = self.getOrCreateLayer('deformers')
        self.defCmpGrp = ComponentGroup(self.getName(), self, parent=deformersLayer)
        self.addItem('defCmpGrp', self.defCmpGrp)
        self.deformerJoints = []
        self.boneOutputsTgt = []
        self.setNumDeformers(4)

        # =====================
        # Create Component I/O
        # =====================

        # Set IO Targets
        self.boneOutputs.setTarget(self.boneOutputsTgt)


        # ==============
        # Constrain I/O
        # ==============
        # Constraint inputs
        legRootInputConstraint = PoseConstraint('_'.join([self.fkCtrlSpaces[0].getName(), 'To', self.rootInputTgt.getName()]))
        legRootInputConstraint.setMaintainOffset(True)
        legRootInputConstraint.addConstrainer(self.rootInputTgt)
        self.fkCtrlSpaces[0].addConstraint(legRootInputConstraint)


        chainBaseInputConstraint = PoseConstraint('_'.join([self.chainBase.getName(), 'To', self.rootInputTgt.getName()]))
        chainBaseInputConstraint.setMaintainOffset(True)
        chainBaseInputConstraint.addConstrainer(self.rootInputTgt)
        self.chainBase.addConstraint(chainBaseInputConstraint)

        # ===============
        # Add Canvas Ops
        # ===============
        # Add Canvas Op
        self.nBoneSolverKLOp = KLOperator('leg', 'NBoneIKSolver', 'Kraken')
        self.addOperator(self.nBoneSolverKLOp)

        # # Add Att Inputs
        self.nBoneSolverKLOp.setInput('drawDebug', self.drawDebugInputAttr)
        self.nBoneSolverKLOp.setInput('rigScale', self.rigScaleInputAttr)
        self.nBoneSolverKLOp.setInput('useInitPose', legUseInitPoseInputAttr)
        self.nBoneSolverKLOp.setInput('ikblend', legFkikInputAttr)
        self.nBoneSolverKLOp.setInput('rootIndex', self.rootIndexInputAttr)
        self.nBoneSolverKLOp.setInput('tipBoneLen', self.tipBoneLenInputAttr)

        # Add Xfo Inputs
        self.nBoneSolverKLOp.setInput('chainBase', self.chainBase)
        self.nBoneSolverKLOp.setInput('ikgoal', self.legIKCtrl)
        self.nBoneSolverKLOp.setInput('upVector', self.legUpVCtrl)

        self.nBoneSolverKLOp.setInput('fkcontrols', self.fkCtrls)

        # Add Xfo Outputs
        self.nBoneSolverKLOp.setOutput('pose', self.boneOutputsTgt)

        self.nBoneSolverKLOp.setOutput('legEnd', self.legEndPosOutputTgt)

        # Add Deformer Canvas Op
        self.outputsToDeformersKLOp = KLOperator('defConstraint', 'MultiPoseConstraintSolver', 'Kraken')
        self.addOperator(self.outputsToDeformersKLOp)

        # Add Att Inputs
        self.outputsToDeformersKLOp.setInput('drawDebug', self.drawDebugInputAttr)
        self.outputsToDeformersKLOp.setInput('rigScale', self.rigScaleInputAttr)

        # Add Xfo Inputs
        self.outputsToDeformersKLOp.setInput('constrainers', self.boneOutputsTgt)

        # Add Xfo Outputs
        self.outputsToDeformersKLOp.setOutput('constrainees', self.deformerJoints)

        Profiler.getInstance().pop()


    def setNumControls(self, numControls):

        # Add new control spaces and controls
        for i in xrange(len(self.fkCtrlSpaces), numControls):
            if i==0:
                parent = self.ctrlCmpGrp
            else:
                parent = self.fkCtrls[i - 1]

            boneName = 'bone' + str(i + 1).zfill(2) + 'FK'
            fkCtrlSpace = CtrlSpace(boneName, parent=parent)

            fkCtrl = Control(boneName, parent=fkCtrlSpace, shape="cube")
            fkCtrl.alignOnXAxis()
            fkCtrl.lockScale(x=True, y=True, z=True)
            fkCtrl.lockTranslation(x=True, y=True, z=True)

            self.fkCtrlSpaces.append(fkCtrlSpace)
            self.fkCtrls.append(fkCtrl)


    def setNumDeformers(self, numDeformers):

        # Add new deformers and outputs
        for i in xrange(len(self.boneOutputsTgt), numDeformers):
            name = 'bone' + str(i + 1).zfill(2)
            legOutput = ComponentOutput(name, parent=self.outputHrcGrp)
            self.boneOutputsTgt.append(legOutput)

        for i in xrange(len(self.deformerJoints), numDeformers):
            name = 'bone' + str(i + 1).zfill(2)
            boneDef = Joint(name, parent=self.defCmpGrp)
            boneDef.setComponent(self)
            self.deformerJoints.append(boneDef)

        return True


    def calculateUpVXfo(self, boneXfos, endXfo):
        """Calculates the transform for the UpV control.

        Args:
            boneXfos (list): Bone transforms.
            endXfo (Xfo): Transform for the end of the chain.

        Returns:
            Xfo: Up Vector transform.

        """


        # Calculate FW
        toFirst = boneXfos[1].tr.subtract(boneXfos[0].tr).unit()
        toTip = endXfo.tr.subtract(boneXfos[0].tr).unit()
        fw = toTip.cross(toFirst).unit()

        chainNormal = fw.cross(toTip).unit()
        chainZAxis = toTip.cross(chainNormal).unit()

        chainXfo = Xfo()
        chainXfo.setFromVectors(toTip.unit(), chainNormal, chainZAxis, boneXfos[0].tr)

        rootToTip = endXfo.tr.subtract(boneXfos[0].tr).length()

        upVXfo = Xfo()
        upVXfo.tr = chainXfo.transformVector(Vec3(rootToTip / 2.0, rootToTip / 2.0, 0.0))

        return upVXfo


    def loadData(self, data=None):
        """Load a saved guide representation from persisted data.

        Arguments:
        data -- object, The JSON data object.

        Return:
        True if successful.

        """

        super(InsectLegComponentRig, self).loadData( data )

        boneXfos = data['boneXfos']
        boneLengths = data['boneLengths']
        numJoints = data['numJoints']
        endXfo = data['endXfo']

        # Add extra controls and outputs
        self.setNumControls(numJoints)
        self.setNumDeformers(numJoints)

        # Scale controls based on bone lengths
        for i, each in enumerate(self.fkCtrlSpaces):
            self.fkCtrlSpaces[i].xfo = boneXfos[i]
            self.fkCtrls[i].xfo = boneXfos[i]
            self.fkCtrls[i].scalePoints(Vec3(boneLengths[i], 1.75, 1.75))

        self.chainBase.xfo = boneXfos[0]

        self.legIKCtrlSpace.xfo = endXfo
        self.legIKCtrl.xfo = endXfo

        upVXfo = self.calculateUpVXfo(boneXfos, endXfo)
        self.legUpVCtrlSpace.xfo = upVXfo
        self.legUpVCtrl.xfo = upVXfo

        # Set max on the rootIndex attribute
        self.rootIndexInputAttr.setMax(len(boneXfos))

        # ============
        # Set IO Xfos
        # ============
        self.rootInputTgt.xfo = boneXfos[0]

        for i in xrange(len(boneLengths)):
            self.boneOutputsTgt[i].xfo = boneXfos[i]

        self.legEndXfoOutputTgt.xfo = endXfo
        self.legEndPosOutputTgt.xfo = endXfo

        # =============
        # Set IO Attrs
        # =============
        tipBoneLen = boneLengths[len(boneLengths) - 1]
        self.tipBoneLenInputAttr.setMax(tipBoneLen * 2.0)
        self.tipBoneLenInputAttr.setValue(tipBoneLen)

        # ====================
        # Evaluate Splice Ops
        # ====================
        # evaluate the nbone op so that all the output transforms are updated.
        self.nBoneSolverKLOp.evaluate()
        self.outputsToDeformersKLOp.evaluate()


from kraken.core.kraken_system import KrakenSystem
ks = KrakenSystem.getInstance()
ks.registerComponent(InsectLegComponentGuide)
ks.registerComponent(InsectLegComponentRig)
