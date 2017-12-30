from kraken.core.maths import Vec3, Quat, Xfo

from kraken.core.objects.rig import Rig

from kraken_components.generic.mainSrt_component import MainSrtComponentRig
from kraken_components.biped.head_component import HeadComponentRig
from kraken_components.biped.clavicle_component import ClavicleComponentGuide, ClavicleComponentRig
from kraken_components.biped.arm_component import ArmComponentGuide, ArmComponentRig
from kraken_components.biped.leg_component import LegComponentGuide, LegComponentRig
from kraken_components.biped.spine_component import SpineComponentRig
from kraken_components.biped.neck_component import NeckComponentGuide, NeckComponentRig

from kraken.core.profiler import Profiler


class BobRig(Rig):
    """Simple biped test rig.

    This example shows how to create a simple scripted biped rig that loads data
    onto component rig classes and also onto guide classes. It also demonstrates
    how to make connections between components.

    """

    def __init__(self, name):

        Profiler.getInstance().push("Construct BobRig:" + name)
        super(BobRig, self).__init__(name)

        # Add Components
        mainSrtComponent = MainSrtComponentRig("mainSrt", self)

        spineComponent = SpineComponentRig("spine", self)
        spineComponent.loadData(data={
            'cogPosition': Vec3(0.0, 11.1351, -0.1382),
            'spine01Position': Vec3(0.0, 11.1351, -0.1382),
            'spine02Position': Vec3(0.0, 11.8013, -0.1995),
            'spine03Position': Vec3(0.0, 12.4496, -0.3649),
            'spine04Position': Vec3(0.0, 13.1051, -0.4821),
            'numDeformers': 4
        })

        neckComponentGuide = NeckComponentGuide("neck")
        neckComponentGuide.loadData({
            "location": "M",
            "neckXfo": Xfo(ori=Quat(Vec3(-0.371748030186, -0.601501047611, 0.371748059988), 0.601500988007), tr=Vec3(0.0, 16.0, -0.75), sc=Vec3(1.00000011921, 1.0, 1.00000011921)),
            "neckMidXfo": Xfo(ori=Quat(Vec3(-0.371748030186, -0.601501047611, 0.371748059988), 0.601500988007), tr=Vec3(0.0, 16.5, -0.5), sc=Vec3(1.00000011921, 1.0, 1.00000011921)),
            "neckEndXfo": Xfo(ori=Quat(Vec3(-0.371748030186, -0.601501047611, 0.371748059988), 0.601500988007), tr=Vec3(0.0, 17.0, -0.25), sc=Vec3(1.0, 1.0, 1.0)),
            "neckCrvData": neckComponentGuide.neckCtrlShape.getCurveData(),
            "neckMidCrvData": neckComponentGuide.neckMidCtrlShape.getCurveData()
        })

        neckComponent = NeckComponentRig("neck", self)
        neckComponent.loadData(neckComponentGuide.getRigBuildData())

        headComponent = HeadComponentRig("head", self)
        headComponent.loadData(data={
            "headXfo": Xfo(Vec3(0.0, 17.5, -0.5)),
            "headCrvData": headComponent.headCtrl.getCurveData(),
            "eyeLeftXfo": Xfo(tr=Vec3(0.375, 18.5, 0.5), ori=Quat(Vec3(-0.0, -0.707106769085, -0.0), 0.707106769085)),
            "eyeLeftCrvData": headComponent.eyeLeftCtrl.getCurveData(),
            "eyeRightXfo": Xfo(tr=Vec3(-0.375, 18.5, 0.5), ori=Quat(Vec3(-0.0, -0.707106769085, -0.0), 0.707106769085)),
            "eyeRightCrvData": headComponent.eyeRightCtrl.getCurveData(),
            "jawXfo": Xfo(Vec3(0.0, 17.875, -0.275)),
            "jawCrvData": headComponent.jawCtrl.getCurveData()
        })

        clavicleLeftComponentGuide = ClavicleComponentGuide("clavicle")
        clavicleLeftComponentGuide.loadData({
            "location": "L",
            "clavicleXfo": Xfo(Vec3(0.1322, 15.403, -0.5723)),
            "clavicleUpVXfo": Xfo(Vec3(0.0, 1.0, 0.0)),
            "clavicleEndXfo": Xfo(Vec3(2.27, 15.295, -0.753))
        })

        clavicleLeftComponent = ClavicleComponentRig("clavicle", self)
        clavicleLeftComponent.loadData(data=clavicleLeftComponentGuide.getRigBuildData())

        clavicleRightComponentGuide = ClavicleComponentGuide("clavicle")
        clavicleRightComponentGuide.loadData({
            "location": "R",
            "clavicleXfo": Xfo(Vec3(-0.1322, 15.403, -0.5723)),
            "clavicleUpVXfo": Xfo(Vec3(0.0, 1.0, 0.0)),
            "clavicleEndXfo": Xfo(Vec3(-2.27, 15.295, -0.753))
        })

        clavicleRightComponent = ClavicleComponentRig("clavicle", self)
        clavicleRightComponent.loadData(data=clavicleRightComponentGuide.getRigBuildData())

        armLeftComponentGuide = ArmComponentGuide("arm")
        armLeftComponentGuide.loadData({
            "location": "L",
            "bicepXfo": Xfo(Vec3(2.27, 15.295, -0.753)),
            "forearmXfo": Xfo(Vec3(5.039, 13.56, -0.859)),
            "wristXfo": Xfo(Vec3(7.1886, 12.2819, 0.4906)),
            "handXfo": Xfo(tr=Vec3(7.1886, 12.2819, 0.4906),
                           ori=Quat(Vec3(-0.0865, -0.2301, -0.2623), 0.9331)),
            "bicepFKCtrlSize": 1.75,
            "forearmFKCtrlSize": 1.5
        })

        armLeftComponent = ArmComponentRig("arm", self)
        armLeftComponent.loadData(data=armLeftComponentGuide.getRigBuildData())

        armRightComponentGuide = ArmComponentGuide("arm")
        armRightComponentGuide.loadData({
            "location": "R",
            "bicepXfo": Xfo(Vec3(-2.27, 15.295, -0.753)),
            "forearmXfo": Xfo(Vec3(-5.039, 13.56, -0.859)),
            "wristXfo": Xfo(Vec3(-7.1886, 12.2819, 0.4906)),
            "handXfo": Xfo(tr=Vec3(-7.1886, 12.2819, 0.4906),
                           ori=Quat(Vec3(-0.2301, -0.0865, -0.9331), 0.2623)),
            "bicepFKCtrlSize": 1.75,
            "forearmFKCtrlSize": 1.5
        })

        armRightComponent = ArmComponentRig("arm", self)
        armRightComponent.loadData(data=armRightComponentGuide.getRigBuildData())

        legLeftComponentGuide = LegComponentGuide("leg")
        legLeftComponentGuide.loadData({
            "name": "Leg",
            "location": "L",
            "femurXfo": Xfo(Vec3(0.9811, 9.769, -0.4572)),
            "kneeXfo": Xfo(Vec3(1.4488, 5.4418, -0.5348)),
            "ankleXfo": Xfo(Vec3(1.841, 1.1516, -1.237)),
            "toeXfo": Xfo(Vec3(1.85, 0.4, 0.25)),
            "toeTipXfo": Xfo(Vec3(1.85, 0.4, 1.5))
        })

        legLeftComponent = LegComponentRig("leg", self)
        legLeftComponent.loadData(data=legLeftComponentGuide.getRigBuildData())

        legRightComponentGuide = LegComponentGuide("leg")
        legRightComponentGuide.loadData({
            "name": "Leg",
            "location": "R",
            "femurXfo": Xfo(Vec3(-0.9811, 9.769, -0.4572)),
            "kneeXfo": Xfo(Vec3(-1.4488, 5.4418, -0.5348)),
            "ankleXfo": Xfo(Vec3(-1.85, 1.1516, -1.237)),
            "toeXfo": Xfo(Vec3(-1.85, 0.4, 0.25)),
            "toeTipXfo": Xfo(Vec3(-1.85, 0.4, 1.5))
        })

        legRightComponent = LegComponentRig("leg", self)
        legRightComponent.loadData(data=legRightComponentGuide.getRigBuildData())

        # ============
        # Connections
        # ============
        # Spine to Main SRT
        mainSrtRigScaleOutput = mainSrtComponent.getOutputByName('rigScale')
        mainSrtOffsetOutput = mainSrtComponent.getOutputByName('offset')

        spineGlobalSrtInput = spineComponent.getInputByName('globalSRT')
        spineGlobalSrtInput.setConnection(mainSrtOffsetOutput)

        spineRigScaleInput = spineComponent.getInputByName('rigScale')
        spineRigScaleInput.setConnection(mainSrtRigScaleOutput)

        # Neck to Main SRT
        neckGlobalSrtInput = neckComponent.getInputByName('globalSRT')
        neckGlobalSrtInput.setConnection(mainSrtOffsetOutput)

        # Neck to Spine
        spineEndOutput = spineComponent.getOutputByName('spineEnd')

        neckSpineEndInput = neckComponent.getInputByName('neckBase')
        neckSpineEndInput.setConnection(spineEndOutput)

        # Head to Main SRT
        headGlobalSrtInput = headComponent.getInputByName('globalSRT')
        headGlobalSrtInput.setConnection(mainSrtOffsetOutput)

        headBaseInput = headComponent.getInputByName('worldRef')
        headBaseInput.setConnection(mainSrtOffsetOutput)

        # Head to Neck
        neckEndOutput = neckComponent.getOutputByName('neckEnd')

        headBaseInput = headComponent.getInputByName('neckRef')
        headBaseInput.setConnection(neckEndOutput)


        # Clavicle to Spine
        spineEndOutput = spineComponent.getOutputByName('spineEnd')
        clavicleLeftSpineEndInput = clavicleLeftComponent.getInputByName('spineEnd')
        clavicleLeftSpineEndInput.setConnection(spineEndOutput)
        clavicleRightSpineEndInput = clavicleRightComponent.getInputByName('spineEnd')
        clavicleRightSpineEndInput.setConnection(spineEndOutput)

        # Arm to Global SRT
        mainSrtOffsetOutput = mainSrtComponent.getOutputByName('offset')
        armLeftGlobalSRTInput = armLeftComponent.getInputByName('globalSRT')
        armLeftGlobalSRTInput.setConnection(mainSrtOffsetOutput)

        armLeftRigScaleInput = armLeftComponent.getInputByName('rigScale')
        armLeftRigScaleInput.setConnection(mainSrtRigScaleOutput)

        armRightGlobalSRTInput = armRightComponent.getInputByName('globalSRT')
        armRightGlobalSRTInput.setConnection(mainSrtOffsetOutput)

        armRightRigScaleInput = armRightComponent.getInputByName('rigScale')
        armRightRigScaleInput.setConnection(mainSrtRigScaleOutput)

        # Arm To Clavicle Connections
        clavicleLeftEndOutput = clavicleLeftComponent.getOutputByName('clavicleEnd')
        armLeftClavicleEndInput = armLeftComponent.getInputByName('root')
        armLeftClavicleEndInput.setConnection(clavicleLeftEndOutput)
        clavicleRightEndOutput = clavicleRightComponent.getOutputByName('clavicleEnd')
        armRightClavicleEndInput = armRightComponent.getInputByName('root')
        armRightClavicleEndInput.setConnection(clavicleRightEndOutput)

        # Leg to Global SRT
        mainSrtOffsetOutput = mainSrtComponent.getOutputByName('offset')
        legLeftGlobalSRTInput = legLeftComponent.getInputByName('globalSRT')
        legLeftGlobalSRTInput.setConnection(mainSrtOffsetOutput)

        legLeftRigScaleInput = legLeftComponent.getInputByName('rigScale')
        legLeftRigScaleInput.setConnection(mainSrtRigScaleOutput)

        legRightGlobalSRTInput = legRightComponent.getInputByName('globalSRT')
        legRightGlobalSRTInput.setConnection(mainSrtOffsetOutput)

        legRightRigScaleInput = legRightComponent.getInputByName('rigScale')
        legRightRigScaleInput.setConnection(mainSrtRigScaleOutput)

        # Leg To Pelvis Connections
        spinePelvisOutput = spineComponent.getOutputByName('pelvis')
        legLeftPelvisInput = legLeftComponent.getInputByName('pelvisInput')
        legLeftPelvisInput.setConnection(spinePelvisOutput)
        legRightPelvisInput = legRightComponent.getInputByName('pelvisInput')
        legRightPelvisInput.setConnection(spinePelvisOutput)

        Profiler.getInstance().pop()
