import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets, QtCore
from functools import partial
from TestClass import TestClass
from PKLGenerator import PKLGenerator
from Utilities import Utilities
from Exceptions import TestError
from SVNInterface import SVNInterface

folder = Utilities.get_tests_folder()
projects = Utilities.get_projects_data()


# GUI classes
class TestMenu(QDialog):
    def __init__(self, _local, parent=None):
        super(TestMenu, self).__init__(parent)

        self.local = _local

        size_object = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.setGeometry((size_object.width() / 2) - 450, (size_object.height() / 2) - 250, 1000, 500)

        self.originalPalette = QApplication.palette()
        self.setWindowIcon(QtGui.QIcon('./lib/style/fvicon.ico'))
        self.setWindowTitle(Utilities.get_current_version())
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        if Utilities.is_using_dark_mode():
            dark_theme_file = "./lib/style/dark_theme/style.qss"
            with open(dark_theme_file, "r") as fh:
                self.setStyleSheet(fh.read())
            self.dark_style = True

        self.stepid = 0
        #self.parent = parent
        ##############################
        side_layout = QGroupBox("Test Information:")
        self.progressBar = QProgressBar()
        self.steps = 20
        self.svn_download = False

        self.testProgress = QLabel("Test Progress:")
        self.progressBar.setRange(0, self.steps)
        self.progressBar.setValue(0)
        self.progressBar.setToolTip('This progress bar shows the test status')

        self.currentStatus = QLabel("Overall test status:")

        self.currentStatusIMG = QLabel("Setup")
        self.currentStatusIMG.setStyleSheet('color: yellow')

        self.updateCurrentStatus("NORUN")

        self.consoleText = QLabel("Test Output:")
        self.consoleOutput = QTextBrowser()
        # self.textEdit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.testProgress)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.currentStatus)
        layout.addWidget(self.currentStatusIMG)
        layout.addWidget(self.consoleText)
        layout.addWidget(self.consoleOutput)
        layout.addStretch(1)
        side_layout.setLayout(layout)

        ##############################
        self.text = QLabel("Test List:")

        self.testlist = list()
        if self.local:  # Read Tests folder and create a list
            read_dir = os.listdir(folder)
            for file in read_dir:
                if os.path.exists(folder + "/" + file + "/"):
                    self.testlist.append(file)
        else:  # Read from SVN folders with TEST_ prefix and create a list
            self.svn_download = True
            test_list = SVNInterface("").list()

            for test in test_list:
                self.testlist.append(test[:len(test)-1])  # Remove '/' from test name

        self.testList = QListWidget()
        self.testList.addItems(self.testlist)

        self.resultList = QTextBrowser()
        self.resultList.hide()

        self.runScenario = QLabel("Start from scenario:")
        self.runScenarioBox = QSpinBox()
        self.runScenarioBox.setRange(0, 999)

        mid_layout = QVBoxLayout()
        mid_layout.addWidget(self.text)
        mid_layout.addWidget(self.testList)
        mid_layout.addWidget(self.resultList)
        mid_layout.addWidget(self.runScenario)
        mid_layout.addWidget(self.runScenarioBox)
        mid_layout.addStretch(1)

        ##############################
        if self.local is False:
            self.uploadSVNCheckBox = QCheckBox("&Upload results to SVN")
            self.uploadSVNCheckBox.setChecked(False)
            self.uploadSVNCheckBox.setToolTip(
                'This checkbox is used if you want to upload test resutls back to the SVN')
        else:
            self.uploadSVNCheckBox = QCheckBox("&Manually run test")
            # disabled feature
            self.uploadSVNCheckBox.setEnabled(True)
            self.uploadSVNCheckBox.setToolTip('This feature will come in the future')
        self.uploadSVNCheckBox.toggled.connect(self.check_result_path)

        self.host_env_button = QCheckBox("&PC environment")
        if Utilities.get_config_file().connections["OFP_SR1"]["TARGET_IP"] == "127.0.0.1":
            self.host_env_button.setChecked(True)
        self.host_env_button.toggled.connect(self.auto_configure_ip)

        self.instrumented_button = QCheckBox("Instrumented")

        self.pauseButton = QPushButton("Pause")
        self.pauseButton.setFixedHeight(30)
        # self.pauseButton.setDefault(False)
        self.pauseButton.setEnabled(False)
        self.pauseButton.setCheckable(True)
        self.pauseButton.toggle()

        self.runButton = QPushButton("Run")
        self.runButton.setFixedHeight(30)
        self.runButton.setDefault(True)

        self.backButton = QPushButton("Back")
        self.backButton.setFixedHeight(30)
        self.backButton.setDefault(True)

        # self.exitButton = QPushButton("Exit")
        # self.exitButton.setDefault(True)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.uploadSVNCheckBox)
        bottom_layout.addWidget(self.host_env_button)
        bottom_layout.addWidget(self.instrumented_button)
        mid_layout.addLayout(bottom_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.pauseButton)
        buttons_layout.addWidget(self.runButton)
        buttons_layout.addWidget(self.backButton)
        mid_layout.addLayout(buttons_layout)
        # bottom_layout.addWidget(self.exitButton)

        ##############################


        ##############################
        self.pauseButton.clicked.connect(self.pause_test)
        self.runButton.clicked.connect(self.runTest)
        # self.exitButton.clicked.connect(self.parent.close_application)
        self.backButton.clicked.connect(self.back_test)

        main_layout = QGridLayout()
        main_layout.addLayout(mid_layout, 4, 0, 1, 2)
        main_layout.addWidget(side_layout, 4, 2)
        # main_layout.addLayout(bottom_layout, 5, 2, 1, 2)
        self.setLayout(main_layout)

        ##############################

    def onUpdateText(self, text, color=""):
        cursor = self.consoleOutput.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        scrollbar = self.consoleOutput.verticalScrollBar()
        current_scroll = scrollbar.value()
        current_maximum = scrollbar.maximum()
        if color != '':
            text = text.replace('\n', '<br>')
            cursor.insertHtml('''<b><span style="color: {};">{}</span></b><br>'''.format(color, text))
        else:
            cursor.insertText(text + "\n")
        if current_scroll == current_maximum:
            scrollbar.setValue(scrollbar.maximum())

    def updateCurrentStatus(self, status):
        if status == "FAILED":
            self.currentStatusIMG.setText("FAILED")
            self.currentStatusIMG.setStyleSheet('color: red')
        elif status == "PASSED":
            self.currentStatusIMG.setText("PASSED")
            self.currentStatusIMG.setStyleSheet('color: green')
        elif status == "PRECONDITION":
            self.currentStatusIMG.setText("PRECONDITIONING")
            self.currentStatusIMG.setStyleSheet('color: yellow')
        elif status == "NORUN":
            self.currentStatusIMG.setText("No Run")
            self.currentStatusIMG.setStyleSheet('color: Blue')

    def getCurrentStatus(self):
        return self.currentStatusIMG.text()

    def updateScenario(self, status, scenario_id, tab=False):

        cursor = self.resultList.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        scrollbar = self.resultList.verticalScrollBar()
        current_scroll = scrollbar.value()
        current_maximum = scrollbar.maximum()

        if tab:
            tab = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        else:
            tab = ""

        if status == "PASSED":
            color = "#7fc97f"
        elif status == "FAILED":
            color = "#FA0000"
        else:
            color = "#FAFAFA"

        if scenario_id != -1:
            scenario = f"Scenario {scenario_id}..."
        else:
            scenario = ""

        cursor.insertHtml(f'<b><span style="color: {color};font-size:10pt">{tab}{scenario} {status}</span></b><br>')

        if current_scroll == current_maximum:
            scrollbar.setValue(scrollbar.maximum())

        # self.resultList.insertText(scenario)

    def runTest(self):
        _testname = self.testlist[self.testList.currentRow()]
        svn_results = self.uploadSVNCheckBox.isChecked()
        _host_env = self.host_env_button.isChecked()
        instrumented = self.instrumented_button.isChecked()

        testname = _testname

        try:
            self.test = TestClass(testname, self.svn_download, svn_results,
                                  _executed=False, _host_env=_host_env, _menu=self, _ci=False, _instrumented=instrumented)
        except TestError as error:
            self.onUpdateText(error.message, "red")
            return None

        self.testList.setEnabled(False)
        self.runButton.setEnabled(False)
        self.backButton.setEnabled(False)
        self.uploadSVNCheckBox.setEnabled(False)
        self.host_env_button.setEnabled(False)
        self.instrumented_button.setEnabled(False)

        # self.runScenarioBox.setEnabled(False)

        self.testList.hide()
        self.resultList.show()

        self.runScenario.hide()
        self.runScenarioBox.hide()

        self.pauseButton.setEnabled(True)

        # for items in range(0, len(self.testlist)):
        # self.testList.takeItem(0)
        self.text.setText("Scenarios Result:")

        self.test.localRun = self.local

        self.test.startfrom = self.runScenarioBox.value()
        if self.local:
            text_print = f'Starting local test run for {self.test.test_name}, manual run: {self.test.SVNResults}, ' \
                         f'host env: {self.test.host_env}, instrumented: {self.test.instrumented}\n\n\n'
            self.test.consoleprint(text_print)
            # self.hide()

            self.test.run_test()
        else:
            testfolder = "%s/%s" % (folder, self.test.test_name)
            answer = QMessageBox.Yes
            if os.path.exists(testfolder):
                answer = QMessageBox.critical(self, Utilities.get_current_version(),
                                              "Test folder already exists!!!\n\nDo you want to override test data?",
                                              QMessageBox.Yes | QMessageBox.No)

            if answer == QMessageBox.Yes:
                print('Starting test run for %s, upload to svn:%s\n\n\n' % (self.test.test_name, self.test.SVNResults))
                self.onUpdateText(
                    'Starting test run for %s, upload to svn:%s\n\n\n' % (self.test.test_name, self.test.SVNResults))
                # self.hide()
                self.test.run_test()
            else:
                QMessageBox.information(self, Utilities.get_current_version(),
                                        "Test run was cancelled.\nUse local run if you dont want to override test data.",
                                        QMessageBox.Ok)
                pass

    def pause_test(self):
        paused = self.pauseButton.isChecked()
        if paused:
            self.pauseButton.setText("Pause")
        else:
            self.pauseButton.setText("Resume")

    def popup(self, title, text, style=0):
        if style == 0:  # Yes/No
            answer = QMessageBox.information(self, title, text, QMessageBox.Yes | QMessageBox.No)
        if style == 1:  # Ok
            answer = QMessageBox.information(self, title, text, QMessageBox.Ok)
        if style == 3:  # input
            answer = QMessageBox.information(self, title, text, QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.No:
                text, ok_pressed = QInputDialog.getText(self, title, "What actually happened:", QLineEdit.Normal, "")
                if ok_pressed and text != '':
                    return answer, text
            else:
                return answer
        return answer

    def back_test(self):
        self.destroy()
        self.menu = TestPath()
        self.menu.show()
        self.svn_download = False

    def closeEvent(self, event):
        choice = QMessageBox.question(self, Utilities.get_current_version(), "Are you sure you want to exit?",
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            if hasattr(self, 'test'):
                self.test.clear_injections()
            sys.exit(0)
        else:
            event.ignore()

    def auto_configure_ip(self):
        checked = self.host_env_button.isChecked()
        config_file = Utilities.get_config_file()
        if checked:
            config_file.set_connection_value("OFP_SR1", "TARGET_IP", "127.0.0.1")
            config_file.set_connection_value("OFP_SR1", "ENDIANITY_TYPE", "0")
            QMessageBox.information(self, Utilities.get_current_version(), "AutoTester is now configured to PC!"
                                    , QMessageBox.Ok)
        else:
            config_file.set_connection_value("OFP_SR1", "TARGET_IP", "192.168.0.101")
            config_file.set_connection_value("OFP_SR1", "ENDIANITY_TYPE", "1")
            QMessageBox.information(self, Utilities.get_current_version(), "AutoTester is now configured to target!"
                                    ,QMessageBox.Ok)
        config_file.save()

    def check_result_path(self):
        if self.uploadSVNCheckBox.isChecked() and Utilities.get_svn_path_result() == "":
            self.uploadSVNCheckBox.setChecked(False)
            return QMessageBox.question(self, Utilities.get_current_version(), "SVN result path was not configured!!\nPlease configure via settings!!", QMessageBox.Ok)


class PklCreator(QDialog):
    def __init__(self, parent=None):
        super(PklCreator, self).__init__(parent)

        self.parent = parent

        ##############################

        self.text = QLabel("Test List:")

        self.testlist = list()
        read_dir = os.listdir(folder)
        for file in read_dir:
            if os.path.exists(folder + "/" + file + "/"):
                self.testlist.append(file)
        self.testList = QListWidget()
        self.testList.addItems(self.testlist)

        mid_layout = QVBoxLayout()
        mid_layout.addWidget(self.text)
        mid_layout.addWidget(self.testList)
        mid_layout.addStretch(1)
        ##############################
        self.generateButton = QPushButton("Show Generator")
        self.generateButton.setDefault(True)

        self.generateButton.clicked.connect(self.generate)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.generateButton)

        ##############################

        main_layout = QGridLayout()
        main_layout.addLayout(mid_layout, 4, 0, 1, 2)
        main_layout.addLayout(bottom_layout, 5, 0, 1, 2)

        self.setLayout(main_layout)

        ##############################
        self.setWindowTitle(Utilities.get_current_version())
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def generate(self):
        _testname = self.testlist[self.testList.currentRow()]
        self.hide()
        try:
            menu = PklCreator2(_testname, self)
            menu.show()
        except StopIteration:
            self.show()


class PklCreator2(QDialog):
    def __init__(self, _testname, parent=None):
        super(PklCreator2, self).__init__(parent)

        self.setWindowTitle(Utilities.get_current_version())
        self.originalPalette = QApplication.palette()
        self.setWindowIcon(QtGui.QIcon('./lib/style/fvicon.ico'))

        QApplication.setStyle(QStyleFactory.create('Fusion'))

        self.setFixedWidth(700)
        self.setFixedHeight(400)

        self.testname = _testname

        # =======================================================
        self.table = QTableWidget()

        self.table.setColumnCount(3)
        self.table.verticalHeader().hide()
        #self.table.horizontalHeader().hide()
        self.table.setHorizontalHeaderLabels(["Name", "RDP_X", "RDP_Y"])

        self.golden_img_folder = f'{folder}/{self.testname}/GoldenImage'

        if os.path.exists(self.golden_img_folder) is False:
            QMessageBox.critical(self, Utilities.get_current_version(),
                                 "GoldenImage folder was not found!", QMessageBox.Ok)
            raise StopIteration

        images = os.listdir(self.golden_img_folder)
        self.table.setRowCount(len(images))
        row = 0
        for file in images:
            if ".png" in file:
                check_box_item = QTableWidgetItem(file)
                check_box_item.setToolTip(file)
                check_box_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                check_box_item.setCheckState(QtCore.Qt.Unchecked)
                self.table.setItem(row, 0, check_box_item)
                row += 1
        self.table.setRowCount(row)

        images_group = QGroupBox("Generator")
        images_group.setFixedHeight(300)
        images_group.setFixedWidth(350)
        images_layout = QVBoxLayout()
        images_layout.addWidget(self.table)
        images_group.setLayout(images_layout)

        # =======================================================
        self.generate_button = QPushButton(" &Generate")
        self.generate_button.setFixedWidth(60)
        self.generate_button.clicked.connect(self.generate_pkl)

        self.show_button = QPushButton(" &Show PKL")
        self.show_button.setFixedWidth(60)
        self.show_button.clicked.connect(self.show_pkl)
        # =======================================================
        preview_group = QGroupBox("Preview")
        preview_group.setFixedHeight(300)
        preview_group.setFixedWidth(350)
        preview_layout = QVBoxLayout()

        self.pkl_list = QListWidget()
        for file in images:
            if ".pkl" in file:
                self.pkl_list.addItem(file)
        preview_layout.addWidget(self.pkl_list)
        preview_group.setLayout(preview_layout)
        """
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        for file in images:
            if ".pkl" in file:
                dic_pattern = load_obj(f'{self.golden_img_folder}/{file}')
                img_result = Image.new(size=dic_pattern['Size'], mode='RGBA')
                draw = ImageDraw.Draw(img_result)
                for pixel in dic_pattern['Data']:
                    int_x = pixel['X']
                    int_y = pixel['Y']
                    tpl_rgba = pixel['RGBA']

                    draw.point((int_x, int_y), tpl_rgba)

                image_q = ImageQt(img_result)
                #self.image_name = QLabel(file)
                #preview_layout.addWidget(self.image_name)
                self.imageLabel2 = QLabel()
                self.imageLabel2.setPixmap(QPixmap.fromImage(image_q))
                preview_layout.addWidget(self.imageLabel2)

        preview_group.setLayout(preview_layout)"""
        # =======================================================

        main_layout = QGridLayout()
        main_layout.addWidget(images_group, 0, 0)
        main_layout.addWidget(preview_group, 0, 1)
        main_layout.addWidget(self.generate_button, 1, 0)
        main_layout.addWidget(self.show_button, 1, 1)
        self.setLayout(main_layout)

        self.show()

    def show_pkl(self):
        pkl_name = self.pkl_list.item(self.pkl_list.currentRow())
        if pkl_name is None:
            return QMessageBox.critical(self, Utilities.get_current_version(),
                                        "You did not choose any file to show.", QMessageBox.Ok)
        pkl_path = f"{self.golden_img_folder}/{pkl_name.text()}"
        PKLGenerator.show(pkl_path)

    def generate_pkl(self):
        count = 0
        # Remove pkl list
        for items in range(0, len(self.pkl_list)):
            self.pkl_list.takeItem(0)
        for row in range(0, self.table.rowCount()):
            item = self.table.item(row, 0)
            rdp_x = self.table.item(row, 1)
            rdp_y = self.table.item(row, 2)
            if rdp_x is None:
                rdp_x = 0
            else:
                rdp_x = rdp_x.text()
            if rdp_y is None:
                rdp_y = 0
            else:
                rdp_y = rdp_y.text()
            if item.checkState() == QtCore.Qt.Checked:
                count += 1
                file_name = item.text()
                png = "%s\\%s" % (self.golden_img_folder, file_name)
                pkl = "%s\\%s.pkl" % (self.golden_img_folder, file_name[0:file_name.rindex('.')])
                if os.path.isfile(pkl):
                    os.remove(pkl)
                PKLGenerator.generate(png, 255, 0, 0, 255, float(rdp_x), float(rdp_y), pkl, False)
                print(f"generate: {file_name}, rdp_x: {rdp_x}, rdp_y: {rdp_y}")
        if count == 0:
            QMessageBox.critical(self, Utilities.get_current_version(),
                                 "You did not choose any file to generate.", QMessageBox.Ok)
        else:
            # Create pkl list again
            images = os.listdir(self.golden_img_folder)
            for file in images:
                if ".pkl" in file:
                    self.pkl_list.addItem(file)
            QMessageBox.information(self, Utilities.get_current_version(), f"Successfully generated {count} PKL files.",
                                    QMessageBox.Ok)


class TestSettings(QDialog):
    def __init__(self, parent=None):
        super(TestSettings, self).__init__(parent)

        self.parent = parent

        OFP_SR = [None, None]
        self.settingsText = [None, None]
        self.ip = [None, None]
        self.port = [None, None]
        self.local = [None, None]
        self.localText = [None, None]
        self.portText = [None, None]
        self.ipText = [None, None]

        ##############################
        self.config_file = Utilities.get_config_file()
        connections_dict = self.config_file.connections
        for xid in range(0, len(OFP_SR)):
            OFP_SR[xid] = QGroupBox()
            snowrunner = "OFP_SR%s" % (xid + 1)
            self.settingsText[xid] = QLabel("%s:" % (snowrunner))

            self.ip[xid] = QLineEdit(connections_dict[snowrunner]["TARGET_IP"])
            self.port[xid] = QLineEdit(connections_dict[snowrunner]["TARGET_PORT"])
            self.local[xid] = QLineEdit(connections_dict[snowrunner]["LOCAL_PORT"])

            self.ipText[xid] = QLabel("IP:")
            self.portText[xid] = QLabel("Target Port:")
            self.localText[xid] = QLabel("Local Port:")

            layout = QVBoxLayout()
            layout.addWidget(self.settingsText[xid])
            layout.addWidget(self.ipText[xid])
            layout.addWidget(self.ip[xid])
            layout.addWidget(self.portText[xid])
            layout.addWidget(self.port[xid])
            layout.addWidget(self.localText[xid])
            layout.addWidget(self.local[xid])

            OFP_SR[xid].setLayout(layout)

        svn_path_group = QGroupBox()
        self.svn_path = QLineEdit(Utilities.get_svn_path_attach())
        self.svn_result_path = QLineEdit(Utilities.get_svn_path_result())

        layout = QVBoxLayout()
        layout.addWidget(QLabel("SVN Test's Path:"))
        layout.addWidget(self.svn_path)
        layout.addWidget(QLabel("SVN Result's Path:"))
        layout.addWidget(self.svn_result_path)
        svn_path_group.setLayout(layout)

        general_group = QGroupBox()
        self.project_text = QLabel("Project configuration:")

        self.projects = list()
        for project in projects:
            self.projects.append(project)

        self.project_list = QComboBox()
        self.project_list.addItems(self.projects)
        self.project_list.setCurrentText(Utilities.get_current_project())

        layout = QVBoxLayout()
        self.dark_mode_checkbox = QCheckBox()

        layout.addWidget(self.project_text)
        layout.addWidget(self.project_list)

        dark_mode_text = QLabel("Dark mode:")
        layout.addWidget(dark_mode_text)
        layout.addWidget(self.dark_mode_checkbox)
        self.dark_mode_checkbox.setChecked(Utilities.is_using_dark_mode())

        general_group.setLayout(layout)

        ##############################
        self.saveButton = QPushButton("Save")
        self.saveButton.setDefault(True)

        self.backButton = QPushButton("Exit")
        self.backButton.setDefault(True)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.saveButton)
        bottom_layout.addWidget(self.backButton)

        ##############################

        self.saveButton.clicked.connect(self.save_settings)
        self.backButton.clicked.connect(self.backTest)

        main_layout = QGridLayout()
        main_layout.addWidget(OFP_SR[0], 4, 0)
        main_layout.addWidget(OFP_SR[1], 4, 1)
        main_layout.addWidget(svn_path_group, 5, 0)
        main_layout.addWidget(general_group, 5, 1)
        main_layout.addLayout(bottom_layout, 7, 0, 1, 2)

        self.setLayout(main_layout)

        ##############################
        self.setWindowTitle(Utilities.get_current_version())
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def backTest(self):
        self.hide()
        self.parent.show()

    def save_settings(self):

        # project configuration
        chosen_project = self.project_list.currentText()
        current_project_path = self.config_file.connections["OFP_SR1"]["GDT_CLUSTER_FILE"]
        new_project_path = current_project_path[:current_project_path.rfind("/") + 1] + projects[chosen_project]["gdt_project"]

        Utilities.set_current_project(chosen_project)
        self.parent.current_project.setText(f"Project: {chosen_project}")

        # OFP configurations
        for xid in range(0, len(self.ip)):
            ip = self.ip[xid].text()
            port = self.port[xid].text()
            local = self.local[xid].text()
            self.config_file.set_connection_value(f"OFP_SR{xid+1}", "TARGET_IP", ip)
            self.config_file.set_connection_value(f"OFP_SR{xid+1}", "TARGET_PORT", port)
            self.config_file.set_connection_value(f"OFP_SR{xid+1}", "LOCAL_PORT", local)
            self.config_file.set_connection_value(f"OFP_SR{xid+1}", "GDT_CLUSTER_FILE", new_project_path)
            self.config_file.set_connection_value(f"OFP_SR{xid+1}", "GDT_PROJECT_NAME", projects[chosen_project]["gdt_project_name"])

        # SVN path's
        self.config_file.set_svn_data("TESTPATH", self.svn_path.displayText())
        self.config_file.set_svn_data("RESULTPATH", self.svn_result_path.displayText())

        # Dark/white mode
        dark_mode = self.dark_mode_checkbox.isChecked()
        Utilities.set_dark_mode(dark_mode)
        if dark_mode:
            dark_theme_file = "./lib/style/dark_theme/style.qss"
            with open(dark_theme_file, "r") as fh:
                self.parent.setStyleSheet(fh.read())
        else:
            self.parent.setStyleSheet("")

        # Save config file and close settings window
        self.config_file.save()
        self.hide()
        self.parent.show()


class TestPath(QMainWindow):
    def __init__(self, parent=None):
        super(TestPath, self).__init__(parent)

        self.originalPalette = QApplication.palette()
        self.setWindowIcon(QtGui.QIcon('./lib/style/fvicon.ico'))
        self.setWindowTitle(Utilities.get_current_version())
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        size_object = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.setGeometry((size_object.width() / 2) - 200, (size_object.height() / 2) - 50, 300, 150)

        self.status_bar = self.statusBar()

        self.current_project = QLabel(f"Project: {Utilities.get_current_project()}")
        self.status_bar.addWidget(self.current_project)

        mainMenu = self.menuBar()

        if Utilities.is_using_dark_mode():
            dark_theme_file = "./lib/style/dark_theme/style.qss"
            with open(dark_theme_file, "r") as fh:
                self.setStyleSheet(fh.read())
            self.dark_style = True

        file_menu = mainMenu.addMenu('&File')

        generator_action = QAction('&PKL Generator', self)
        generator_action.setShortcut('CTRL+G')
        generator_action.setStatusTip('GoldenImage Generator')
        generator_action.triggered.connect(self.generator)
        file_menu.addAction(generator_action)

        settings_action = QAction('&Settings', self)
        settings_action.setShortcut('CTRL+S')
        settings_action.setStatusTip('Settings')
        settings_action.triggered.connect(self.settings)
        file_menu.addAction(settings_action)

        about_action = QAction('&About', self)
        about_action.setStatusTip('About')
        about_action.triggered.connect(self.about)
        file_menu.addAction(about_action)

        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('CTRL+Q')
        exit_action.setStatusTip('Exit program')
        exit_action.triggered.connect(partial(self.closeEvent, QtGui.QCloseEvent))
        file_menu.addAction(exit_action)

        self.testPath = QLabel("Choose your test Path:", self)
        self.testPath.setGeometry(0, 0, 400, 25)
        self.testPath.move(80, 30)

        self.svnButton = QPushButton("SVN", self)
        self.svnButton.setGeometry(0, 0, 60, 30)
        self.svnButton.move(75, 60)
        self.svnButton.clicked.connect(partial(self.show_tests, False))
        self.svnButton.setToolTip(Utilities.get_svn_path_attach())
        # TODO: Login window if svn_user == N/A

        self.localButton = QPushButton("Local", self)
        self.localButton.setGeometry(0, 0, 60, 30)
        self.localButton.move(150, 60)
        self.localButton.clicked.connect(partial(self.show_tests, True))
        self.localButton.setToolTip(folder)

        self.exitButton = QPushButton("Exit", self)
        self.exitButton.setGeometry(0, 0, 60, 30)
        self.exitButton.move(115, 95)
        self.exitButton.clicked.connect(partial(self.closeEvent, QtGui.QCloseEvent))

        self.show()

    def show_tests(self, local=False):
        self.local = local
        if not local and Utilities.get_svn_path_attach() == "":
            return QMessageBox.question(self, Utilities.get_current_version(), "SVN path was not configured!!\nPlease configure via settings!!", QMessageBox.Ok)
        self.destroy()
        self.menu = TestMenu(local)
        self.menu.show()

    def closeEvent(self, event):
        choice = QMessageBox.question(self, Utilities.get_current_version(), "Are you sure you want to exit?",
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit(0)
        else:
            event.ignore()

    def settings(self):
        # self.hide()
        self.menu = TestSettings(self)
        self.menu.show()

    def generator(self):
        # self.hide()
        self.menu = PklCreator(self)
        self.menu.show()

    def about(self):
        info_text = "%s\n\nThis program was created for Elbit Aerospace Solutions\nby Emil Shain\n" \
                    "All Rights Reserved.©" %Utilities.get_current_version()
        QMessageBox.information(self, Utilities.get_current_version(), info_text, QMessageBox.Ok)


def run_with_gui():
    app = QApplication(sys.argv)
    menu = TestPath()
    menu.show()

    def exception_hook(exctype, value, traceback):
        if menu is not None:
            menu.menu.onUpdateText("\n\nERROR WHILE RUNNING\n%s, %s,%s" % (exctype, value, traceback))

        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook

    sys.exit(app.exec_())
