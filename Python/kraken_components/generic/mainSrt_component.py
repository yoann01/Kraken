from kraken.core.maths import Vec3, Vec3, Euler, Quat, Xfo

from kraken.core.objects.components.base_example_component import BaseExampleComponent

from kraken.core.objects.attributes.attribute_group import AttributeGroup
from kraken.core.objects.attributes.scalar_attribute import ScalarAttribute
from kraken.core.objects.attributes.bool_attribute import BoolAttribute

from kraken.core.objects.constraints.pose_constraint import PoseConstraint

from kraken.core.objects.component_group import ComponentGroup
from kraken.core.objects.hierarchy_group import HierarchyGroup
from kraken.core.objects.locator import Locator
from kraken.core.objects.joint import Joint
from kraken.core.objects.ctrlSpace import CtrlSpace
from kraken.core.objects.control import Control

from kraken.core.objects.operators.kl_operator import KLOperator

from kraken.core.profiler import Profiler
from kraken.helpers.utility_methods import logHierarchy


class MainSrtComponent(BaseExampleComponent):
    """MainSrt Component Base"""

    def __init__(self, name='mainSrtBase', parent=None):
        super(MainSrtComponent, self).__init__(name, parent)


        # ===========
        # Declare IO
        # ===========
        # Declare Inputs Xfos

        # Declare Output Xfos
        self.srtOutputTgt = self.createOutput('srt', dataType='Xfo', parent=self.outputHrcGrp).getTarget()
        self.offsetOutputTgt = self.createOutput('offset', dataType='Xfo', parent=self.outputHrcGrp).getTarget()

        # Declare Input Attrs
        self.drawDebugInputAttr = self.createInput('drawDebug', dataType='Boolean', value=False, parent=self.cmpInputAttrGrp).getTarget()

        # Declare Output Attrs
        self.rigScaleOutputAttr = self.createOutput('rigScale', dataType='Float', value=1.0, parent=self.cmpOutputAttrGrp).getTarget()


class MainSrtComponentGuide(MainSrtComponent):
    """MainSrt Component Guide"""

    def __init__(self, name='mainSrt', parent=None):

        Profiler.getInstance().push("Construct MainSrt Guide Component:" + name)
        super(MainSrtComponentGuide, self).__init__(name, parent)

        # =========
        # Attributes
        # =========
        # Add Component Params to IK control
        guideSettingsAttrGrp = AttributeGroup("GuideSettings", parent=self)

        self.mainSrtSizeInputAttr = ScalarAttribute('mainSrtSize', value=5.0, minValue=1.0, maxValue=50.0, parent=guideSettingsAttrGrp)
        self.mainSrtSizeInputAttr.setValueChangeCallback(self.resizeMainSrtCtrl)

        # =========
        # Controls
        # =========

        # Guide Controls
        self.mainSrtCtrl = Control('mainSrt', parent=self.ctrlCmpGrp, shape="circle")

        data = {
                "location": 'M',
                "mainSrtSize": self.mainSrtSizeInputAttr.getValue(),
                "mainSrtXfo": Xfo(tr=Vec3(0.0, 0.0, 0.0))
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
        data = super(MainSrtComponentGuide, self).saveData()

        data["mainSrtSize"] = self.mainSrtSizeInputAttr.getValue()
        data["mainSrtXfo"] = self.mainSrtCtrl.xfo

        return data


    def loadData(self, data):
        """Load a saved guide representation from persisted data.

        Arguments:
        data -- object, The JSON data object.

        Return:
        True if successful.

        """

        super(MainSrtComponentGuide, self).loadData( data )

        self.mainSrtSizeInputAttr.setValue(data["mainSrtSize"])
        self.mainSrtCtrl.xfo = data["mainSrtXfo"]

        scaleValue = data["mainSrtSize"]
        self.mainSrtCtrl.setShape('circle')
        self.mainSrtCtrl.scalePoints(Vec3(scaleValue, 1.0, scaleValue))

        return True


    def getRigBuildData(self):
        """Returns the Guide data used by the Rig Component to define the layout of the final rig.

        Return:
        The JSON rig data object.

        """

        data = super(MainSrtComponentGuide, self).getRigBuildData()

        data["mainSrtSize"] = self.mainSrtSizeInputAttr.getValue()
        data["mainSrtXfo"] = self.mainSrtCtrl.xfo

        return data

    # ==========
    # Callbacks
    # ==========
    def resizeMainSrtCtrl(self, newSize):
        self.mainSrtCtrl.setShape('circle')
        self.mainSrtCtrl.scalePoints(Vec3(newSize, 1.0, newSize))

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

        return MainSrtComponentRig


class MainSrtComponentRig(MainSrtComponent):
    """MainSrt Component Rig"""

    def __init__(self, name='mainSrt', parent=None):

        Profiler.getInstance().push("Construct MainSrt Rig Component:" + name)
        super(MainSrtComponentRig, self).__init__(name, parent)


        # =========
        # Controls
        # =========
        # Add Controls
        self.mainSRTCtrlSpace = CtrlSpace('SRT', parent=self.ctrlCmpGrp)
        self.mainSRTCtrl = Control('SRT', shape='circle', parent=self.mainSRTCtrlSpace)
        self.mainSRTCtrl.lockScale(x=True, y=True, z=True)

        self.offsetCtrlSpace = CtrlSpace('Offset', parent=self.mainSRTCtrl)
        self.offsetCtrl = Control('Offset', shape='circle', parent=self.offsetCtrlSpace)
        self.offsetCtrl.setColor("orange")
        self.offsetCtrl.lockScale(x=True, y=True, z=True)

        # Add Component Params to Main control
        mainSrtSettingsAttrGrp = AttributeGroup('DisplayInfo_MainSrtSettings', parent=self.mainSRTCtrl)
        self.rigScaleAttr = ScalarAttribute('rigScale', value=1.0, parent=mainSrtSettingsAttrGrp, minValue=0.1, maxValue=100.0)

        self.rigScaleOutputAttr.connect(self.rigScaleAttr)

        # ==========
        # Deformers
        # ==========


        # ==============
        # Constrain I/O
        # ==============
        # Constrain inputs

        # Constrain outputs
        self.srtOutputToSrtCtrlConstraint = PoseConstraint('_'.join([self.srtOutputTgt.getName(), 'To', self.mainSRTCtrl.getName()]))
        self.srtOutputToSrtCtrlConstraint.addConstrainer(self.mainSRTCtrl)
        self.srtOutputTgt.addConstraint(self.srtOutputToSrtCtrlConstraint)

        self.offsetToSrtCtrlConstraint = PoseConstraint('_'.join([self.offsetOutputTgt.getName(), 'To', self.mainSRTCtrl.getName()]))
        self.offsetToSrtCtrlConstraint.addConstrainer(self.offsetCtrl)
        self.offsetOutputTgt.addConstraint(self.offsetToSrtCtrlConstraint)


        # ===============
        # Add Canvas Ops
        # ===============
        # Add Rig Scale Canvas Op
        self.rigScaleOp = KLOperator('rigScale', 'RigScaleSolver', 'Kraken')
        self.addOperator(self.rigScaleOp)

        # Add Att Inputs
        self.rigScaleOp.setInput('drawDebug', self.drawDebugInputAttr)
        self.rigScaleOp.setInput('rigScale', self.rigScaleOutputAttr)

        # Add Xfo Inputs

        # Add Xfo Outputs
        self.rigScaleOp.setOutput('target', self.mainSRTCtrlSpace)


        Profiler.getInstance().pop()


    def loadData(self, data=None):
        """Load a saved guide representation from persisted data.

        Arguments:
        data -- object, The JSON data object.

        Return:
        True if successful.

        """

        super(MainSrtComponentRig, self).loadData( data )

        # ================
        # Resize Controls
        # ================
        self.mainSRTCtrl.scalePoints(Vec3(data["mainSrtSize"], 1.0, data["mainSrtSize"]))
        self.offsetCtrl.scalePoints(Vec3(data["mainSrtSize"] - 0.5, 1.0, data["mainSrtSize"] - 0.5))

        # =======================
        # Set Control Transforms
        # =======================
        self.mainSRTCtrlSpace.xfo = data["mainSrtXfo"]
        self.mainSRTCtrl.xfo = data["mainSrtXfo"]
        self.offsetCtrlSpace.xfo = data["mainSrtXfo"]
        self.offsetCtrl.xfo = data["mainSrtXfo"]

        # ============
        # Set IO Xfos
        # ============
        self.srtOutputTgt = data["mainSrtXfo"]
        self.offsetOutputTgt = data["mainSrtXfo"]

        # Evaluate Constraints
        self.srtOutputToSrtCtrlConstraint.evaluate()
        self.offsetToSrtCtrlConstraint.evaluate()

        # Evaluate Operators
        self.rigScaleOp.evaluate()


from kraken.core.kraken_system import KrakenSystem
ks = KrakenSystem.getInstance()
ks.registerComponent(MainSrtComponentGuide)
ks.registerComponent(MainSrtComponentRig)
