from kraken.core.maths import Vec3

from kraken.core.objects.components.base_example_component import BaseExampleComponent

from kraken.core.objects.attributes.attribute_group import AttributeGroup
from kraken.core.objects.attributes.bool_attribute import BoolAttribute
from kraken.core.objects.attributes.integer_attribute import IntegerAttribute
from kraken.core.objects.attributes.scalar_attribute import ScalarAttribute
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


class SpineComponent(BaseExampleComponent):
    """Spine Component"""

    def __init__(self, name="spineBase", parent=None, *args, **kwargs):
        super(SpineComponent, self).__init__(name, parent, *args, **kwargs)

        # ===========
        # Declare IO
        # ===========
        # Declare Inputs Xfos
        self.globalSRTInputTgt = self.createInput('globalSRT', dataType='Xfo', parent=self.inputHrcGrp).getTarget()

        # Declare Output Xfos
        self.spineCogOutputTgt = self.createOutput('cog', dataType='Xfo', parent=self.outputHrcGrp).getTarget()
        self.spineBaseOutputTgt = self.createOutput('spineBase', dataType='Xfo', parent=self.outputHrcGrp).getTarget()
        self.pelvisOutputTgt = self.createOutput('pelvis', dataType='Xfo', parent=self.outputHrcGrp).getTarget()
        self.spineEndOutputTgt = self.createOutput('spineEnd', dataType='Xfo', parent=self.outputHrcGrp).getTarget()

        self.spineVertebraeOutput = self.createOutput('spineVertebrae', dataType='Xfo[]')

        # Declare Input Attrs
        self.drawDebugInputAttr = self.createInput('drawDebug', dataType='Boolean', value=False, parent=self.cmpInputAttrGrp).getTarget()
        self.rigScaleInputAttr = self.createInput('rigScale', dataType='Float', value=1.0, parent=self.cmpInputAttrGrp).getTarget()
        self.lengthInputAttr = self.createInput('length', dataType='Float', value=1.0, parent=self.cmpInputAttrGrp).getTarget()

        # Declare Output Attrs


class SpineComponentGuide(SpineComponent):
    """Spine Component Guide"""

    def __init__(self, name='spine', parent=None, *args, **kwargs):

        Profiler.getInstance().push("Construct Spine Guide Component:" + name)
        super(SpineComponentGuide, self).__init__(name, parent, *args, **kwargs)

        # =========
        # Controls
        # ========
        guideSettingsAttrGrp = AttributeGroup("GuideSettings", parent=self)
        self.numDeformersAttr = IntegerAttribute('numDeformers', value=1, minValue=0, maxValue=20, parent=guideSettingsAttrGrp)

        # Guide Controls
        self.cog = Control('cogPosition', parent=self.ctrlCmpGrp, shape="sphere")
        self.cog.scalePoints(Vec3(1.2, 1.2, 1.2))
        self.cog.setColor('red')

        self.spine01Ctrl = Control('spine01Position', parent=self.ctrlCmpGrp, shape='sphere')
        self.spine02Ctrl = Control('spine02Position', parent=self.ctrlCmpGrp, shape='sphere')
        self.spine03Ctrl = Control('spine03Position', parent=self.ctrlCmpGrp, shape='sphere')
        self.spine04Ctrl = Control('spine04Position', parent=self.ctrlCmpGrp, shape='sphere')

        data = {
            'name': name,
            'location': 'M',
            'cogPosition': Vec3(0.0, 11.1351, -0.1382),
            'spine01Position': Vec3(0.0, 11.1351, -0.1382),
            'spine02Position': Vec3(0.0, 11.8013, -0.1995),
            'spine03Position': Vec3(0.0, 12.4496, -0.3649),
            'spine04Position': Vec3(0.0, 13.1051, -0.4821),
            'numDeformers': 6
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

        data = super(SpineComponentGuide, self).saveData()

        data['cogPosition'] = self.cog.xfo.tr
        data['spine01Position'] = self.spine01Ctrl.xfo.tr
        data['spine02Position'] = self.spine02Ctrl.xfo.tr
        data['spine03Position'] = self.spine03Ctrl.xfo.tr
        data['spine04Position'] = self.spine04Ctrl.xfo.tr
        data['numDeformers'] = self.numDeformersAttr.getValue()

        return data


    def loadData(self, data):
        """Load a saved guide representation from persisted data.

        Arguments:
        data -- object, The JSON data object.

        Return:
        True if successful.

        """

        super(SpineComponentGuide, self).loadData( data )

        self.cog.xfo.tr = data["cogPosition"]
        self.spine01Ctrl.xfo.tr = data["spine01Position"]
        self.spine02Ctrl.xfo.tr = data["spine02Position"]
        self.spine03Ctrl.xfo.tr = data["spine03Position"]
        self.spine04Ctrl.xfo.tr = data["spine04Position"]
        self.numDeformersAttr.setValue(data["numDeformers"])

        return True


    def getRigBuildData(self):
        """Returns the Guide data used by the Rig Component to define the layout of the final rig.

        Return:
        The JSON rig data object.

        """

        data = super(SpineComponentGuide, self).getRigBuildData()

        data['cogPosition'] = self.cog.xfo.tr
        data['spine01Position'] = self.spine01Ctrl.xfo.tr
        data['spine02Position'] = self.spine02Ctrl.xfo.tr
        data['spine03Position'] = self.spine03Ctrl.xfo.tr
        data['spine04Position'] = self.spine04Ctrl.xfo.tr
        data['numDeformers'] = self.numDeformersAttr.getValue()

        return data


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

        return SpineComponentRig


class SpineComponentRig(SpineComponent):
    """Spine Component"""

    def __init__(self, name="spine", parent=None):

        Profiler.getInstance().push("Construct Spine Rig Component:" + name)
        super(SpineComponentRig, self).__init__(name, parent)


        # =========
        # Controls
        # =========
        # COG
        self.cogCtrlSpace = CtrlSpace('cog', parent=self.ctrlCmpGrp)
        self.cogCtrl = Control('cog', parent=self.cogCtrlSpace, shape="circle")
        self.cogCtrl.scalePoints(Vec3(6.0, 6.0, 6.0))
        self.cogCtrl.setColor("orange")
        self.cogCtrl.lockScale(True, True, True)

        # Spine01
        self.spine01CtrlSpace = CtrlSpace('spine01', parent=self.cogCtrl)
        self.spine01Ctrl = Control('spine01', parent=self.spine01CtrlSpace, shape="circle")
        self.spine01Ctrl.scalePoints(Vec3(4.0, 4.0, 4.0))
        self.spine01Ctrl.lockScale(True, True, True)

        # Spine02
        self.spine02CtrlSpace = CtrlSpace('spine02', parent=self.spine01Ctrl)
        self.spine02Ctrl = Control('spine02', parent=self.spine02CtrlSpace, shape="circle")
        self.spine02Ctrl.scalePoints(Vec3(4.5, 4.5, 4.5))
        self.spine02Ctrl.lockScale(True, True, True)
        self.spine02Ctrl.setColor("blue")


        # Spine04
        self.spine04CtrlSpace = CtrlSpace('spine04', parent=self.cogCtrl)
        self.spine04Ctrl = Control('spine04', parent=self.spine04CtrlSpace, shape="circle")
        self.spine04Ctrl.scalePoints(Vec3(6.0, 6.0, 6.0))
        self.spine04Ctrl.lockScale(True, True, True)

        # Spine03
        self.spine03CtrlSpace = CtrlSpace('spine03', parent=self.spine04Ctrl)
        self.spine03Ctrl = Control('spine03', parent=self.spine03CtrlSpace, shape="circle")
        self.spine03Ctrl.scalePoints(Vec3(4.5, 4.5, 4.5))
        self.spine03Ctrl.lockScale(True, True, True)
        self.spine03Ctrl.setColor("blue")

        # Pelvis
        self.pelvisCtrlSpace = CtrlSpace('pelvis', parent=self.spine01Ctrl)
        self.pelvisCtrl = Control('pelvis', parent=self.pelvisCtrlSpace, shape="cube")
        self.pelvisCtrl.alignOnYAxis(negative=True)
        self.pelvisCtrl.scalePoints(Vec3(4.0, 0.375, 3.75))
        self.pelvisCtrl.translatePoints(Vec3(0.0, -0.5, -0.25))
        self.pelvisCtrl.lockTranslation(True, True, True)
        self.pelvisCtrl.lockScale(True, True, True)
        self.pelvisCtrl.setColor("dodgerblue")


        # ==========
        # Deformers
        # ==========
        deformersLayer = self.getOrCreateLayer('deformers')
        self.defCmpGrp = ComponentGroup(self.getName(), self, parent=deformersLayer)
        self.addItem('defCmpGrp', self.defCmpGrp)
        self.deformerJoints = []
        self.spineOutputs = []
        self.setNumDeformers(1)

        pelvisDef = Joint('pelvis', parent=self.defCmpGrp)
        pelvisDef.setComponent(self)

        # =====================
        # Create Component I/O
        # =====================
        # Setup component Xfo I/O's
        self.spineVertebraeOutput.setTarget(self.spineOutputs)


        # ==============
        # Constrain I/O
        # ==============
        # Constraint inputs
        self.spineSrtInputConstraint = PoseConstraint('_'.join([self.cogCtrlSpace.getName(), 'To', self.globalSRTInputTgt.getName()]))
        self.spineSrtInputConstraint.addConstrainer(self.globalSRTInputTgt)
        self.spineSrtInputConstraint.setMaintainOffset(True)
        self.cogCtrlSpace.addConstraint(self.spineSrtInputConstraint)

        # Constraint outputs
        self.spineCogOutputConstraint = PoseConstraint('_'.join([self.spineCogOutputTgt.getName(), 'To', self.cogCtrl.getName()]))
        self.spineCogOutputConstraint.addConstrainer(self.cogCtrl)
        self.spineCogOutputTgt.addConstraint(self.spineCogOutputConstraint)

        self.spineBaseOutputConstraint = PoseConstraint('_'.join([self.spineBaseOutputTgt.getName(), 'To', 'spineBase']))
        self.spineBaseOutputConstraint.addConstrainer(self.spineOutputs[0])
        self.spineBaseOutputTgt.addConstraint(self.spineBaseOutputConstraint)

        self.pelvisOutputConstraint = PoseConstraint('_'.join([self.pelvisOutputTgt.getName(), 'To', self.pelvisCtrl.getName()]))
        self.pelvisOutputConstraint.addConstrainer(self.pelvisCtrl)
        self.pelvisOutputTgt.addConstraint(self.pelvisOutputConstraint)

        self.spineEndOutputConstraint = PoseConstraint('_'.join([self.spineEndOutputTgt.getName(), 'To', 'spineEnd']))
        self.spineEndOutputConstraint.addConstrainer(self.spineOutputs[0])
        self.spineEndOutputTgt.addConstraint(self.spineEndOutputConstraint)


        # ===============
        # Add Canvas Ops
        # ===============
        # Add Spine Canvas Op
        self.bezierSpineKLOp = KLOperator('spine', 'BezierSpineSolver', 'Kraken')
        self.addOperator(self.bezierSpineKLOp)

        # Add Att Inputs
        self.bezierSpineKLOp.setInput('drawDebug', self.drawDebugInputAttr)
        self.bezierSpineKLOp.setInput('rigScale', self.rigScaleInputAttr)
        self.bezierSpineKLOp.setInput('length', self.lengthInputAttr)

        # Add Xfo Inputs
        self.bezierSpineKLOp.setInput('base', self.spine01Ctrl)
        self.bezierSpineKLOp.setInput('baseHandle', self.spine02Ctrl)
        self.bezierSpineKLOp.setInput('tipHandle', self.spine03Ctrl)
        self.bezierSpineKLOp.setInput('tip', self.spine04Ctrl)

        # Add Xfo Outputs
        self.bezierSpineKLOp.setOutput('outputs', self.spineOutputs)

        # Add Deformer Canvas Op
        self.deformersToOutputsKLOp = KLOperator('defConstraint', 'MultiPoseConstraintSolver', 'Kraken')
        self.addOperator(self.deformersToOutputsKLOp)

        # Add Att Inputs
        self.deformersToOutputsKLOp.setInput('drawDebug', self.drawDebugInputAttr)
        self.deformersToOutputsKLOp.setInput('rigScale', self.rigScaleInputAttr)

        # Add Xfo Outputs
        self.deformersToOutputsKLOp.setInput('constrainers', self.spineOutputs)

        # Add Xfo Outputs
        self.deformersToOutputsKLOp.setOutput('constrainees', self.deformerJoints)

        # Add Pelvis Canvas Op
        self.pelvisDefKLOp = KLOperator('pelvisDefConstraint', 'PoseConstraintSolver', 'Kraken')
        self.addOperator(self.pelvisDefKLOp)

        # Add Att Inputs
        self.pelvisDefKLOp.setInput('drawDebug', self.drawDebugInputAttr)
        self.pelvisDefKLOp.setInput('rigScale', self.rigScaleInputAttr)

        # Add Xfo Inputs
        self.pelvisDefKLOp.setInput('constrainer', self.pelvisOutputTgt)

        # Add Xfo Outputs
        self.pelvisDefKLOp.setOutput('constrainee', pelvisDef)


        Profiler.getInstance().pop()


    def setNumDeformers(self, numDeformers):

        # Add new deformers and outputs
        for i in xrange(len(self.spineOutputs), numDeformers):
            name = 'spine' + str(i + 1).zfill(2)
            spineOutput = ComponentOutput(name, parent=self.outputHrcGrp)
            self.spineOutputs.append(spineOutput)

        for i in xrange(len(self.deformerJoints), numDeformers):
            name = 'spine' + str(i + 1).zfill(2)
            spineDef = Joint(name, parent=self.defCmpGrp)
            spineDef.setComponent(self)
            self.deformerJoints.append(spineDef)

        return True


    def loadData(self, data=None):
        """Load a saved guide representation from persisted data.

        Arguments:
        data -- object, The JSON data object.

        Return:
        True if successful.

        """

        super(SpineComponentRig, self).loadData( data )

        cogPosition = data['cogPosition']
        spine01Position = data['spine01Position']
        spine02Position = data['spine02Position']
        spine03Position = data['spine03Position']
        spine04Position = data['spine04Position']
        numDeformers = data['numDeformers']

        self.cogCtrlSpace.xfo.tr = cogPosition
        self.cogCtrl.xfo.tr = cogPosition

        self.pelvisCtrlSpace.xfo.tr = cogPosition
        self.pelvisCtrl.xfo.tr = cogPosition

        self.spine01CtrlSpace.xfo.tr = spine01Position
        self.spine01Ctrl.xfo.tr = spine01Position

        self.spine02CtrlSpace.xfo.tr = spine02Position
        self.spine02Ctrl.xfo.tr = spine02Position

        self.spine03CtrlSpace.xfo.tr = spine03Position
        self.spine03Ctrl.xfo.tr = spine03Position

        self.spine04CtrlSpace.xfo.tr = spine04Position
        self.spine04Ctrl.xfo.tr = spine04Position

        length = spine01Position.distanceTo(spine02Position) + spine02Position.distanceTo(spine03Position) + spine03Position.distanceTo(spine04Position)
        self.lengthInputAttr.setMax(length * 3.0)
        self.lengthInputAttr.setValue(length)

        # Update number of deformers and outputs
        self.setNumDeformers(numDeformers)

        # Updating constraint to use the updated last output.
        self.spineEndOutputConstraint.setConstrainer(self.spineOutputs[-1], index=0)

        # ============
        # Set IO Xfos
        # ============

        # Evaluate Constraints
        self.spineSrtInputConstraint.evaluate()
        self.spineCogOutputConstraint.evaluate()
        self.spineBaseOutputConstraint.evaluate()
        self.pelvisOutputConstraint.evaluate()
        self.spineEndOutputConstraint.evaluate()

        # Evaluate Operators
        self.bezierSpineKLOp.evaluate()
        self.deformersToOutputsKLOp.evaluate()
        self.pelvisDefKLOp.evaluate()



from kraken.core.kraken_system import KrakenSystem
ks = KrakenSystem.getInstance()
ks.registerComponent(SpineComponentGuide)
ks.registerComponent(SpineComponentRig)
