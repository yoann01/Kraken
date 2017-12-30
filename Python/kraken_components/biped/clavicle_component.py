from kraken.core.maths import *

from kraken.core.objects.components.base_example_component import BaseExampleComponent

from kraken.core.objects.attributes.attribute_group import AttributeGroup
from kraken.core.objects.attributes.bool_attribute import BoolAttribute

from kraken.core.objects.constraints.pose_constraint import PoseConstraint

from kraken.core.objects.component_group import ComponentGroup
from kraken.core.objects.joint import Joint
from kraken.core.objects.ctrlSpace import CtrlSpace
from kraken.core.objects.control import Control

from kraken.core.objects.operators.kl_operator import KLOperator

from kraken.core.profiler import Profiler


class ClavicleComponent(BaseExampleComponent):
    """Clavicle Component Base"""

    def __init__(self, name='clavicle', parent=None, *args, **kwargs):
        super(ClavicleComponent, self).__init__(name, parent, *args, **kwargs)

        # ===========
        # Declare IO
        # ===========
        # Declare Inputs Xfos
        self.globalSRTInputTgt = self.createInput('globalSRT', dataType='Xfo', parent=self.inputHrcGrp).getTarget()
        self.spineEndInputTgt = self.createInput('spineEnd', dataType='Xfo', parent=self.inputHrcGrp).getTarget()

        # Declare Output Xfos
        self.clavicleOutputTgt = self.createOutput('clavicle', dataType='Xfo', parent=self.outputHrcGrp).getTarget()
        self.clavicleEndOutputTgt = self.createOutput('clavicleEnd', dataType='Xfo', parent=self.outputHrcGrp).getTarget()

        # Declare Input Attrs
        self.drawDebugInputAttr = self.createInput('drawDebug', dataType='Boolean', value=False, parent=self.cmpInputAttrGrp).getTarget()
        self.rigScaleInputAttr = self.createInput('rigScale', dataType='Float', value=1.0, parent=self.cmpInputAttrGrp).getTarget()
        self.rightSideInputAttr = self.createInput('rightSide', dataType='Boolean', value=self.getLocation() is 'R', parent=self.cmpInputAttrGrp).getTarget()

        # Declare Output Attrs



class ClavicleComponentGuide(ClavicleComponent):
    """Clavicle Component Guide"""

    def __init__(self, name='clavicle', parent=None, *args, **kwargs):

        Profiler.getInstance().push("Construct Clavicle Guide Component:" + name)
        super(ClavicleComponentGuide, self).__init__(name, parent, *args, **kwargs)


        # =========
        # Controls
        # =========
        # Guide Controls
        guideSettingsAttrGrp = AttributeGroup("GuideSettings", parent=self)

        self.clavicleCtrl = Control('clavicle', parent=self.ctrlCmpGrp, shape="circle")
        self.clavicleCtrl.scalePoints(Vec3(0.75, 0.75, 0.75))
        self.clavicleCtrl.rotatePoints(0.0, 0.0, 90.0)

        self.clavicleGuideSettingsAttrGrp = AttributeGroup("Settings", parent=self.clavicleCtrl)
        self.handDebugInputAttr = BoolAttribute('drawDebug', value=False, parent=self.clavicleGuideSettingsAttrGrp)

        self.drawDebugInputAttr.connect(self.handDebugInputAttr)

        self.clavicleUpVCtrl = Control('clavicleUpV', parent=self.clavicleCtrl, shape="triangle")
        self.clavicleUpVCtrl.setColor('red')
        self.clavicleUpVCtrl.rotatePoints(-90.0, 0.0, 0.0)
        self.clavicleUpVCtrl.rotatePoints(0.0, 90.0, 0.0)
        self.clavicleUpVCtrl.scalePoints(Vec3(0.5, 0.5, 0.5))

        self.clavicleEndCtrl = Control('clavicleEnd', parent=self.ctrlCmpGrp, shape="cube")
        self.clavicleEndCtrl.scalePoints(Vec3(0.25, 0.25, 0.25))

        self.default_data = {
            "name": name,
            "location": "L",
            "clavicleXfo": Xfo(Vec3(0.15, 15.5, -0.5)),
            "clavicleUpVXfo": Xfo(Vec3(0.15, 16.5, -0.5)),
            "clavicleEndXfo": Xfo(Vec3(2.25, 15.5, -0.75))
        }

        self.loadData(self.default_data)

        Profiler.getInstance().pop()


    # =============
    # Data Methods
    # =============
    def saveData(self):
        """Save the data for the component to be persisted.

        Return:
        The JSON data object

        """

        data = super(ClavicleComponentGuide, self).saveData()

        data['clavicleXfo'] = self.clavicleCtrl.xfo
        data['clavicleUpVXfo'] = self.clavicleUpVCtrl.xfo
        data['clavicleEndXfo'] = self.clavicleEndCtrl.xfo

        return data


    def loadData(self, data):
        """Load a saved guide representation from persisted data.

        Arguments:
        data -- object, The JSON data object.

        Return:
        True if successful.

        """

        super(ClavicleComponentGuide, self).loadData( data )

        self.clavicleCtrl.xfo = data['clavicleXfo']
        self.clavicleUpVCtrl.xfo = data['clavicleUpVXfo']
        self.clavicleEndCtrl.xfo = data['clavicleEndXfo']

        return True


    def getRigBuildData(self):
        """Returns the Guide data used by the Rig Component to define the layout of the final rig..

        Return:
        The JSON rig data object.

        """

        data = super(ClavicleComponentGuide, self).getRigBuildData()


        # Values
        claviclePosition = self.clavicleCtrl.xfo.tr
        clavicleUpV = self.clavicleUpVCtrl.xfo.tr
        clavicleEndPosition = self.clavicleEndCtrl.xfo.tr

        # Calculate Clavicle Xfo
        clavicleXfo = Xfo()
        clavicleOri = Quat()
        clavicleOri.setFromDirectionAndUpvector((clavicleEndPosition - claviclePosition).unit(),
                                                (clavicleUpV - claviclePosition).unit())

        xAlignOffset = Quat()
        xAlignOffset.setFromAxisAndAngle(Vec3(0, 1, 0), Math_degToRad(-90))

        clavicleXfo.ori = clavicleOri * xAlignOffset
        clavicleXfo.tr = claviclePosition

        clavicleLen = claviclePosition.subtract(clavicleEndPosition).length()

        data['clavicleXfo'] = clavicleXfo
        data['clavicleLen'] = clavicleLen

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

        return ClavicleComponentRig


class ClavicleComponentRig(ClavicleComponent):
    """Clavicle Component"""

    def __init__(self, name='Clavicle', parent=None):

        Profiler.getInstance().push("Construct Clavicle Rig Component:" + name)
        super(ClavicleComponentRig, self).__init__(name, parent)


        # =========
        # Controls
        # =========
        # Clavicle
        self.clavicleCtrlSpace = CtrlSpace('clavicle', parent=self.ctrlCmpGrp)
        self.clavicleCtrl = Control('clavicle', parent=self.clavicleCtrlSpace, shape="cube")
        self.clavicleCtrl.alignOnXAxis()
        self.clavicleCtrl.lockTranslation(True, True, True)
        self.clavicleCtrl.lockScale(True, True, True)


        # ==========
        # Deformers
        # ==========
        self.deformersLayer = self.getOrCreateLayer('deformers')
        self.defCmpGrp = ComponentGroup(self.getName(), self, parent=self.deformersLayer)
        self.addItem('defCmpGrp', self.defCmpGrp)

        self.clavicleDef = Joint('clavicle', parent=self.defCmpGrp)
        self.clavicleDef.setComponent(self)


        # ==============
        # Constrain I/O
        # ==============
        # Constraint inputs
        self.clavicleInputConstraint = PoseConstraint('_'.join([self.clavicleCtrl.getName(), 'To', self.spineEndInputTgt.getName()]))
        self.clavicleInputConstraint.setMaintainOffset(True)
        self.clavicleInputConstraint.addConstrainer(self.spineEndInputTgt)
        self.clavicleCtrlSpace.addConstraint(self.clavicleInputConstraint)

        # Constraint outputs
        self.clavicleConstraint = PoseConstraint('_'.join([self.clavicleOutputTgt.getName(), 'To', self.clavicleCtrl.getName()]))
        self.clavicleConstraint.addConstrainer(self.clavicleCtrl)
        self.clavicleOutputTgt.addConstraint(self.clavicleConstraint)

        self.clavicleEndConstraint = PoseConstraint('_'.join([self.clavicleEndOutputTgt.getName(), 'To', self.clavicleCtrl.getName()]))
        self.clavicleEndConstraint.setMaintainOffset(True)
        self.clavicleEndConstraint.addConstrainer(self.clavicleCtrl)
        self.clavicleEndOutputTgt.addConstraint(self.clavicleEndConstraint)


        # ===============
        # Add Canavs Ops
        # ===============
        # Add Deformer Canvas Op
        self.clavicleDefOp = KLOperator('defConstraint', 'PoseConstraintSolver', 'Kraken')
        self.addOperator(self.clavicleDefOp)

        # Add Att Inputs
        self.clavicleDefOp.setInput('drawDebug', self.drawDebugInputAttr)
        self.clavicleDefOp.setInput('rigScale', self.rigScaleInputAttr)

        # Add Xfo Inputs
        self.clavicleDefOp.setInput('constrainer', self.clavicleOutputTgt)

        # Add Xfo Outputs
        self.clavicleDefOp.setOutput('constrainee', self.clavicleDef)

        Profiler.getInstance().pop()


    def loadData(self, data=None):
        """Load a saved guide representation from persisted data.

        Arguments:
        data -- object, The JSON data object.

        Return:
        True if successful.

        """

        super(ClavicleComponentRig, self).loadData( data )

        clavicleXfo = data.get('clavicleXfo')
        clavicleLen = data.get('clavicleLen')

        clavicleLenVec = Vec3(clavicleLen, 0.75, 0.75)

        self.clavicleCtrlSpace.xfo = clavicleXfo
        self.clavicleCtrl.xfo = clavicleXfo
        self.clavicleCtrl.scalePoints(clavicleLenVec)

        if data['location'] == "R":
            self.clavicleCtrl.translatePoints(Vec3(0.0, 0.0, -1.0))
        else:
            self.clavicleCtrl.translatePoints(Vec3(0.0, 0.0, 1.0))


        # Set IO Xfos
        self.spineEndInputTgt.xfo = clavicleXfo
        self.clavicleEndOutputTgt.xfo = clavicleXfo
        self.clavicleEndOutputTgt.xfo.tr = clavicleXfo.transformVector(Vec3(clavicleLen, 0.0, 0.0))
        self.clavicleOutputTgt.xfo = clavicleXfo

        # Eval Constraints
        self.clavicleInputConstraint.evaluate()
        self.clavicleConstraint.evaluate()
        self.clavicleEndConstraint.evaluate()

        # Eval Operators
        self.clavicleDefOp.evaluate()


from kraken.core.kraken_system import KrakenSystem
ks = KrakenSystem.getInstance()
ks.registerComponent(ClavicleComponentGuide)
ks.registerComponent(ClavicleComponentRig)