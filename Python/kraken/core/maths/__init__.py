"""Kraken - math module."""

from math_object import MathObject
from vec2 import Vec2
from vec3 import Vec3
from vec4 import Vec4
from quat import Quat
from euler import Euler
from xfo import Xfo
from mat33 import Mat33
from mat44 import Mat44
from rotation_order import RotationOrder
from color import Color
from constants import DEG_TO_RAD, RAD_TO_DEG, PI


def Math_radToDeg(val):
    """Converts radians to degrees.

    Args:
        val (float): value to convert to degrees.

    Returns:
        float: Value in degrees.

    """

    return val * RAD_TO_DEG

def Math_degToRad(val):
    """Converts degrees to radians.

    Args:
        val (float): value to convert to radians.

    Returns:
        float: Value in radians.

    """

    return val * DEG_TO_RAD


def decodeValue(jsonData):
    """Returns a constructed math value based on the provided json data.

    Args:
        jsondata (dict): The JSON data to use to decode into a Math value.

    Returns:
        object: The constructed math value

    """

    if type(jsonData) is not dict:
        return jsonData

    if '__mathObjectClass__' not in jsonData:
        raise Exception("Invalid JSON data for constructing value:" + str(jsonData))

    if jsonData['__mathObjectClass__'] == 'Vec2':
        val = Vec2()
        val.jsonDecode(jsonData, decodeValue)
    elif jsonData['__mathObjectClass__'] == 'Vec3':
        val = Vec3()
        val.jsonDecode(jsonData, decodeValue)
    elif jsonData['__mathObjectClass__'] == 'Vec4':
        val = Vec4()
        val.jsonDecode(jsonData, decodeValue)
    elif jsonData['__mathObjectClass__'] == 'Euler':
        val = Euler()
        val.jsonDecode(jsonData, decodeValue)
    elif jsonData['__mathObjectClass__'] == 'Quat':
        val = Quat()
        val.jsonDecode(jsonData, decodeValue)
    elif jsonData['__mathObjectClass__'] == 'Xfo':
        val = Xfo()
        val.jsonDecode(jsonData, decodeValue)
    elif jsonData['__mathObjectClass__'] == 'Mat33':
        val = Mat33()
        val.jsonDecode(jsonData, decodeValue)
    elif jsonData['__mathObjectClass__'] == 'Mat44':
        val = Mat44()
        val.jsonDecode(jsonData, decodeValue)
    else:
        raise Exception("Unsupported Math type:" + jsonData['__mathObjectClass__'])

    return val
