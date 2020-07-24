import xml.etree.ElementTree as ET
import xml.dom.minidom
from Exceptions import ParameterError


class XMLInterface:
    def __init__(self, file):
        self.configuration_file = file
        tree = ET.parse(self.configuration_file)
        self.root = tree.getroot()
        self.svn_path = self.load_svn_paths()
        self.connections = self.load_connections()
        self.svn_user = self.load_user_password()
        self.general = self.load_general_data()

    def load_svn_paths(self):
        svn_path = dict()
        for svn in self.root.findall("./SVN"):
            for value in svn:
                svn_path[value.tag] = value.text
        return svn_path

    def load_connections(self):
        connections = dict()
        for connection in self.root.findall("./CONNECTIONS/"):
            connections[connection.tag] = dict()
            for ofp_sr in connection:
                connections[connection.tag][ofp_sr.tag] = ofp_sr.text
        return connections

    def load_user_password(self):
        user_data = dict()
        for svn in self.root.findall("./SVNUSER"):
            for value in svn:
                if value.text is None:
                    user_data[value.tag] = "N/A"
                else:
                    user_data[value.tag] = value.text
        return user_data

    def load_general_data(self):
        general_data = dict()
        for svn in self.root.findall("./GENERAL"):
            for value in svn:
                if value.text is None:
                    general_data[value.tag] = "N/A"
                else:
                    general_data[value.tag] = value.text
        return general_data

    def set_general_data(self, attribute, data):
        self.general[attribute] = str(data)

    def set_svn_data(self, attribute, data):
        self.svn_path[attribute] = str(data)

    def set_connection_value(self, snow_runner: str, attribute: str, value: str):
        if snow_runner not in self.connections:
            raise ParameterError(self.configuration_file, f"{snow_runner} was not found in the xml!!")
        if attribute not in self.connections[snow_runner]:
            raise ParameterError(self.configuration_file, f"{attribute} was not found in {snow_runner}!!")
        self.connections[snow_runner][attribute] = value

    def save(self):
        root = ET.Element("root")
        connections = ET.SubElement(root, "CONNECTIONS")

        # Save connections dictionary
        for key, value in self.connections.items():
            ofp_sr = ET.SubElement(connections, key)
            for tag, text in value.items():
                ET.SubElement(ofp_sr, tag).text = text

        # Save svn dictionary
        svn = ET.SubElement(root, "SVN")
        for tag, text in self.svn_path.items():
            ET.SubElement(svn, tag).text = text

        # Save svn user&password
        svn = ET.SubElement(root, "SVNUSER")
        for tag, text in self.svn_user.items():
            ET.SubElement(svn, tag).text = text

        # Save general settings
        svn = ET.SubElement(root, "GENERAL")
        for tag, text in self.general.items():
            ET.SubElement(svn, tag).text = text

        # Save xml
        tree = ET.ElementTree(root)
        tree.write(self.configuration_file)

        # Beautify xml
        pretty_xml = xml.dom.minidom.parse(self.configuration_file).toprettyxml()
        with open(self.configuration_file, "w") as f:
            f.write(pretty_xml)
