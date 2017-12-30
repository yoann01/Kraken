"""Kraken - objects.Attributes.BoolAttribute module.

Classes:
BoolAttribute - Base Attribute.

"""

from kraken.core.objects.attributes.attribute import Attribute
from kraken.core.kraken_system import ks


class BoolAttribute(Attribute):
    """Boolean Attribute. Implemented value type checking and limiting."""

    def __init__(self, name, value=False, parent=None, metaData=None):
        super(BoolAttribute, self).__init__(name, value=value, parent=parent, metaData=metaData)
        assert type(value) is bool, "Value is not of type 'bool'."


    def setValue(self, value):
        """Sets the value of the attribute..

        Args:
            value (bool): Value to set the attribute to.

        Returns:
            bool: True if successful.

        """

        if type(value) is not bool:
            raise TypeError("Value is not of type 'bool'.")

        super(BoolAttribute, self).setValue(value)

        return True


    def getRTVal(self):
        """Returns and RTVal object for this attribute.

        Returns:
            RTVal: RTVal object of the attribute.

        """

        return ks.rtVal('Boolean', self._value)


    def getDataType(self):
        """Returns the name of the data type for this attribute.

        Note:
            This is a localized method specific to the Boolean Attribute.

        Returns:
            str: String name of the attribute type.

        """

        return 'Boolean'
