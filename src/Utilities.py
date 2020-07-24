import os
import shutil
from Exceptions import ParameterError
from XMLInterface import XMLInterface

current_version = "AutoTester V1.1.2"
tests_folder = './Tests'
golden_images_folder = 'GoldenImage'
configuration_file = 'ConnectionsConfig.xml'
config_file = XMLInterface(configuration_file)
gdt_interface_lib_dir = './lib/GdtInterfaceLib/bin/Debug/'
gdt_interface_lib_path = './lib/GdtInterfaceLib/bin/Debug/GdtInterfaceLib'
gdt_interface_connection = 'OFP_SR1', 'OFP_SR2'
host_socket_tx_conf = ('127.0.0.1', 36981)
host_socket_rx_conf = ('127.0.0.1', 36982)
host_screenshot_path = 'J:/host_screenshot.tga'
projects = {
            "ATR": {
                "gdt_project": "ATR.gdt",
                "gdt_project_name": "ATR_Run_Project"
            },
            "Phoenix": {
                "gdt_project": "PHX.gdt",
                "gdt_project_name": "PHX_Run_Project"
            },
            "ClearVision": {
                "gdt_project": "ClearVision.gdt",
                "gdt_project_name": "ClearVision_Run_Project"
            }

        }


class Utilities:
    @staticmethod
    def remove_folder(folder: str) -> None:
        if os.path.exists(folder):
            shutil.rmtree(folder)

        else:
            raise ParameterError('folder', 'The folder do not exist.')

    @staticmethod
    def validity_to_bool(validity: str) -> bool:
        if validity.lower() == 'valid':
            return True

        elif validity.lower() == 'invalid':
            return False
        else:
            raise ParameterError('validity', 'The value is not \'valid\' nor \'invalid\'.')

    @staticmethod
    def validity_or_number_to_bool(validity) -> bool:
        if validity == 1:
            return True
        elif validity == 0:
            return False
        elif validity.lower() == 'valid' or validity == "1":
            return True

        elif validity.lower() == 'invalid' or validity == "0":
            return False
        else:
            raise ParameterError('validity', 'The value is not \'valid\' nor \'invalid\'.')

    @staticmethod
    def bool_to_validity(bool_value: bool) -> str:
        if bool_value is True:
            return 'Valid'

        elif bool_value is False:
            return 'Invalid'
        else:
            raise ParameterError('bool_value', 'The value is not True nor False.')

    @staticmethod
    def bool_to_affirmative(bool_value: bool) -> str:
        if bool_value is True:
            return 'Yes'

        elif bool_value is False:
            return 'No'

        else:
            raise ParameterError('bool_value', 'The value is not True nor False.')

    @staticmethod
    def get_current_version() -> str:
        return current_version

    @staticmethod
    def get_tests_folder() -> str:
        return tests_folder

    @staticmethod
    def get_svn_path_attach() -> str:
        if "TESTPATH" in config_file.svn_path:
            return config_file.svn_path['TESTPATH']
        else:
            return ""

    @staticmethod
    def get_svn_path_result() -> str:
        if "RESULTPATH" in config_file.svn_path:
            return config_file.svn_path['RESULTPATH']
        else:
            return ""

    @staticmethod
    def get_svn_path_result_ci() -> str:
        if "CIPATH" in config_file.svn_path:
            return config_file.svn_path['CIPATH']
        else:
            return ""

    @staticmethod
    def get_svn_user() -> str:
        if "USERNAME" in config_file.svn_user:
            return config_file.svn_user['USERNAME']
        else:
            return ""

    @staticmethod
    def get_svn_password() -> str:
        if "PASSWORD" in config_file.svn_user:
            return config_file.svn_user['PASSWORD']
        else:
            return ""

    @staticmethod
    def get_configuration_file() -> str:
        return configuration_file

    @staticmethod
    def get_gdt_interface_lib_dir() -> str:
        return gdt_interface_lib_dir

    @staticmethod
    def get_gdt_interface_lib_path() -> str:
        return gdt_interface_lib_path

    @staticmethod
    def get_gdt_interface_connection() -> str:
        return gdt_interface_connection

    @staticmethod
    def get_host_socket_rx_conf():
        return host_socket_rx_conf

    @staticmethod
    def get_host_socket_tx_conf():
        return host_socket_tx_conf

    @staticmethod
    def get_host_screenshot_path() -> str:
        return host_screenshot_path

    @staticmethod
    def get_config_file():
        return config_file

    @staticmethod
    def get_projects_data():
        return projects

    @staticmethod
    def get_current_project():
        if "PROJECT" in config_file.general:
            return config_file.general["PROJECT"]
        else:
            return ""

    @staticmethod
    def set_current_project(project):
        config_file.set_general_data("PROJECT", project)

    @staticmethod
    def is_using_dark_mode():
        if "DARK_MODE" in config_file.general:
            if config_file.general["DARK_MODE"] == "True":
                return True
            else:
                return False
        else:
            return True

    @staticmethod
    def set_dark_mode(dark_mode: bool):
        config_file.set_general_data("DARK_MODE", dark_mode)
