import sys
import os
import clr
from clr import System

from Utilities import Utilities
from Exceptions import ParameterError, GDTConnectionError
from enum import Enum

clr.AddReference(Utilities.get_gdt_interface_lib_path())
from GdtInterface import GdtClient


class GDTInterface:
    class GDTInterfaceDataType(Enum):
        FLAG = 0
        STRING = 1
        NUMBER = 2
        DOUBLE = 3

    def __init__(self, connection: str):
        self.connection = connection
        self.is_connected = False
        try:
            self.gdt_client = GdtClient(Utilities.get_configuration_file(), self.connection)
        except:
            raise ParameterError('configuration_file or connection', f'Either the configuration file path ({Utilities.get_configuration_file()}) or the required connection ({self.connection}) is not valid.')

    def connect(self):
        current_path = os.getcwd()
        try:
            os.chdir(Utilities.get_gdt_interface_lib_dir())
            self.is_connected = self.gdt_client.Connect(True, 10)
        except:
            raise GDTConnectionError('Connection failed. Please check the configuration file and ensure that the application is running on target.')
        finally:
            os.chdir(current_path)

    def __del__(self):
        current_path = os.getcwd()
        try:
            if self.is_connected is True:
                os.chdir(Utilities.get_gdt_interface_lib_dir())
                self.gdt_client.Disconnet()
                self.is_connected = False
            else:
                raise GDTConnectionError('GDT Interface is not connected yet.')
        except:
            pass
        finally:
            os.chdir(current_path)

    def disconnect(self):
        current_path = os.getcwd()
        try:
            if self.is_connected is True:
                os.chdir(Utilities.get_gdt_interface_lib_dir())
                self.gdt_client.Disconnet()
                self.is_connected = False
            else:
                raise GDTConnectionError('GDT Interface is not connected yet.')
        except:
            pass
        finally:
            os.chdir(current_path)

    def write_data_item(self, data_item_type: GDTInterfaceDataType, data_item_name: str, value, validity, override) -> bool:
        if self.is_connected is True:
            # Necessary for CLR function parameters compatibility.
            nullable_validity = System.Nullable[System.Boolean](validity)
            nullable_override = System.Nullable[System.Boolean](override)

            try:
                clr_data_item_type = self.__convert_local_type_to_clr_type(data_item_type)
                is_injected = self.gdt_client.WriteDataItem(clr_data_item_type, data_item_name, value, nullable_validity, nullable_override)

            except:
                raise ParameterError('data_item_type, data_item_name or value', f'Either the data item type ({data_item_type}), the data item name ({data_item_name}) or the value ({value}) is not valid.')

            return is_injected

        else:
            raise GDTConnectionError('GDT Interface is not connected yet.')

    def inject_data_item(self, data_item_type: GDTInterfaceDataType, data_item_name: str, value) -> bool:
        if self.is_connected is True:
            try:
                clr_data_item_type = self.__convert_local_type_to_clr_type(data_item_type)
                is_injected = self.gdt_client.WriteDataItemValue(clr_data_item_type, data_item_name, value)

            except:
                raise ParameterError('data_item_type, data_item_name or value', f'Either the data item type ({data_item_type}), the data item name ({data_item_name}) or the value ({value}) is not valid.')

            return is_injected

        else:
            raise GDTConnectionError('GDT Interface is not connected yet.')

    def inject_data_item_validity(self, data_item_type: GDTInterfaceDataType, data_item_name: str, validity: bool) -> bool:
        if self.is_connected is True:
            try:
                clr_data_item_type = self.__convert_local_type_to_clr_type(data_item_type)
                is_injected = self.gdt_client.WriteDataItemValidity(clr_data_item_type, data_item_name, validity)

            except:
                raise ParameterError('data_item_type, data_item_name or validity', f'Either the data item type ({data_item_type}), the data item name ({data_item_name}) or the validity ({validity}) is not valid.')

            return is_injected

        else:
            raise GDTConnectionError('GDT Interface is not connected yet.')

    def inject_data_item_override(self, data_item_type: GDTInterfaceDataType, data_item_name: str, override: bool) -> bool:
        if self.is_connected is True:
            try:
                clr_data_item_type = self.__convert_local_type_to_clr_type(data_item_type)
                is_injected = self.gdt_client.SetDataItemOverride(clr_data_item_type, data_item_name, override)

            except:
                raise ParameterError('data_item_type, data_item_name or override', f'Either the data item type ({data_item_type}), the data item name ({data_item_name}) or the override ({override}) is not valid.')

            return is_injected

        else:
            raise GDTConnectionError('GDT Interface is not connected yet.')

    def read_data_item(self, data_item_type: GDTInterfaceDataType, data_item_name: str):
        if self.is_connected is True:
            try:
                clr_data_item_type = self.__convert_local_type_to_clr_type(data_item_type)
                value_read = self.gdt_client.ReadDataItem(clr_data_item_type, data_item_name, None, True, True, 0)

            except:
                raise ParameterError('data_item_type or data_item_name',
                                     f'Either the data item type ({data_item_type}) or the data item name ({data_item_name}) is not valid.')

            ret_dict = {
                "value": value_read[1],
                "validity": value_read[2],
                "override": value_read[3]
            }

            return ret_dict

        else:
            raise GDTConnectionError('GDT Interface is not connected yet.')

    def inject_struct(self, struct_name: str, struct_field: str, value) -> bool:
        current_path = os.getcwd()
        if self.is_connected is True:
            try:
                os.chdir(Utilities.get_gdt_interface_lib_dir())
                is_injected = self.gdt_client.WriteStructField(struct_name, struct_field, value)
                return is_injected
            except:
                raise ParameterError('struct_name, struct_field or value', f'Either the struct name ({struct_name}), the struct field ({struct_field}) or the value ({value}) is not valid.')
            finally:
                os.chdir(current_path)
        else:
            raise GDTConnectionError('GDT Interface is not connected yet.')

    def read_struct(self, struct_name: str, struct_field: str):
        current_path = os.getcwd()
        if self.is_connected is True:
            try:
                os.chdir(Utilities.get_gdt_interface_lib_dir())
                struct = self.gdt_client.ReadStruct(struct_name, None, 50)
                if struct is None:
                    raise StopIteration

                field_value = struct.TryGetValue(struct_field, None)
                if field_value[0] is False:
                    raise StopIteration

                return field_value[1].Value
            except:
                raise ParameterError('struct_name or struct_field', f'Either the struct name ({struct_name}) or the struct field ({struct_field}) is not valid.')
            finally:
                os.chdir(current_path)
        else:
            raise GDTConnectionError('GDT Interface is not connected yet.')

    def read_buffer(self, buffer_name: str, buffer_field: str, element_field: str):
        current_path = os.getcwd()
        if self.is_connected is True:
            try:
                os.chdir(Utilities.get_gdt_interface_lib_dir())
                return self.gdt_client.ReadBufferElement(buffer_name, buffer_field, element_field, None, True, 50)
            except System.Collections.Generic.KeyNotFoundException:
                raise ParameterError('buffer_name or buffer_field', f'Either the buffer name ({buffer_name}) or the buffer field ({buffer_field}) is not valid.')
            finally:
                os.chdir(current_path)
        else:
            raise GDTConnectionError('GDT Interface is not connected yet.')

    def __convert_local_type_to_clr_type(self, local_type: GDTInterfaceDataType) -> GdtClient.BufferType:
        translation_dict = {
            GDTInterface.GDTInterfaceDataType.FLAG: GdtClient.BufferType.FLAG,
            GDTInterface.GDTInterfaceDataType.STRING: GdtClient.BufferType.STRING,
            GDTInterface.GDTInterfaceDataType.NUMBER: GdtClient.BufferType.NUMBER,
            GDTInterface.GDTInterfaceDataType.DOUBLE: GdtClient.BufferType.DOUBLE
        }

        return translation_dict[local_type]
