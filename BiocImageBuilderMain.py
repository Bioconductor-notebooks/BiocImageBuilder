import sys, os, fnmatch
import re, ast
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QStandardItem, QTextDocument, QFont

from DockerClient import DockerClient, DockerThread_BuildImage
from UIDockerfileEditor import DockerSyntaxHighlighter

class UIDockerBuilder(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.FLAG_in_bundle = False
        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
            self.FLAG_in_bundle =True

        #print(self.base_dir)

        # GUI
        # stylesheet
        self.setStyleSheet(
            "QPushButton{background-color: #1588c5; color: white; height: 25px; border: 1px solid #1a8ac6; border-radius: 2px;}"
            "QPushButton:pressed { background-color: #158805; border-style: inset;}"
            "QPushButton:disabled{ background-color: gray; }"
            #"QPushButton:flat {border: none;}"
            "QPushButton:hover{background-color: #1588f5; }"
                           #"QComboBox{"
                           #"      border: 1px solid gray; border-radius: 3px; padding: 1px 1px 1px 3px;"
                           #"      min-width: 6em;"
                           #"}"
                           #"QSplitter::handle:horizontal { width: 2px; border: 1px solid green; border-radius: 1px; padding: 2px;}"
                           )
        # creat controls
        self.vlayoutBase = QtWidgets.QVBoxLayout()
        self.vlayoutBase.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.vlayoutBase.setContentsMargins(0, 0, 0, 0)
        self.vlayoutBase.setSpacing(0)
        self.vlayoutBase.setObjectName("vlayoutBase")
        # Title area
        self.frameTitle = QtWidgets.QFrame(self)
        self.frameTitle.setMinimumSize(QtCore.QSize(0, 65))
        self.frameTitle.setMaximumSize(QtCore.QSize(16777215, 65))
        self.frameTitle.setStyleSheet("QFrame#frameTitle{\n"
                                      "    background: #1588c5;\n"
                                      "    color: #1588c5\n"
                                      "}")
        self.frameTitle.setFrameShape(QtWidgets.QFrame.Box)
        self.frameTitle.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frameTitle.setObjectName("frameTitle")
        self.lblFormTitle = QtWidgets.QLabel()
        self.lblFormTitle.setFixedSize(QtCore.QSize(300,30))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.lblFormTitle.setFont(font)
        self.lblFormTitle.setStyleSheet("color: white;")
        self.lblFormTitle.setObjectName("lblFormTitle")
        self.lblIcon = QtWidgets.QLabel()
        self.lblIcon.setFixedSize(QtCore.QSize(41, 31))
        self.lblIcon.setText("")
        self.lblIcon.setPixmap(QtGui.QPixmap(os.path.join(self.base_dir,"icons/builder_icon.png")))
        self.lblIcon.setScaledContents(True)
        self.lblIcon.setObjectName("lblIcon")
        self.lblDockerVersion = QtWidgets.QLabel()
        self.lblDockerVersion.setFixedSize(QtCore.QSize(550, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lblDockerVersion.setFont(font)
        self.lblDockerVersion.setStyleSheet("color: white;")
        self.lblDockerVersion.setObjectName("lblDockerVersion")
        self.lblBuiding = QtWidgets.QLabel()
        self.lblBuiding.setFixedSize(QtCore.QSize(550, 16))
        self.lblBuiding.setFont(font)
        self.lblBuiding.setStyleSheet("color: white;")
        self.lblBuiding.setObjectName("lblBuilding")
        self.lblBuiding.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.lblBuiding.setAlignment(Qt.AlignVCenter|Qt.AlignRight)
        self.lblBuidingStep = QtWidgets.QLabel()
        self.lblBuidingStep.setFixedSize(QtCore.QSize(300, 16))
        self.lblBuidingStep.setFont(font)
        self.lblBuidingStep.setStyleSheet("color: white;")
        self.lblBuidingStep.setObjectName("lblBuidingStep")
        self.lblBuidingStep.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        # grid layout for title area
        self.glayout_title = QtWidgets.QGridLayout(self.frameTitle)
        self.glayout_title.addWidget(self.lblIcon, 0, 0, 2, 0) # rowspan=2
        self.glayout_title.addWidget(self.lblFormTitle, 0, 1, Qt.AlignLeft | Qt.AlignTop)
        self.glayout_title.addWidget(self.lblBuidingStep, 0, 2, Qt.AlignRight | Qt.AlignTop)
        self.glayout_title.addWidget(self.lblDockerVersion, 1, 1, Qt.AlignLeft | Qt.AlignBottom)
        self.glayout_title.addWidget(self.lblBuiding, 1, 2, Qt.AlignRight | Qt.AlignBottom)
        self.glayout_title.setColumnMinimumWidth(0, 41)
        self.frameTitle.setLayout(self.glayout_title)

        self.vlayoutBase.addWidget(self.frameTitle)
        self.frameSubtitle = QtWidgets.QFrame(self)
        self.frameSubtitle.setEnabled(True)
        self.frameSubtitle.setMinimumSize(QtCore.QSize(0, 35))
        self.frameSubtitle.setMaximumSize(QtCore.QSize(16777215, 35))
        self.frameSubtitle.setStyleSheet("QFrame#frameSubtitle\n"
                                         "{background: #1998de; }")
        self.frameSubtitle.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameSubtitle.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frameSubtitle.setObjectName("frameSubtitle")
        self.lblSubtitle = QtWidgets.QLabel(self.frameSubtitle)
        self.lblSubtitle.setGeometry(QtCore.QRect(15, 2, 301, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lblSubtitle.setFont(font)
        self.lblSubtitle.setStyleSheet("color: white")
        self.lblSubtitle.setObjectName("lblSubtitle")
        self.vlayoutBase.addWidget(self.frameSubtitle)
        # Left of main area
        self.mainContent = QtWidgets.QWidget(self)
        self.mainContent.setObjectName("mainContent")
        self.hlayout_mainArea = QtWidgets.QHBoxLayout(self.mainContent)
        self.hlayout_mainArea.setContentsMargins(8, 8, 8, 8)
        self.hlayout_mainArea.setSpacing(2)
        self.hlayout_mainArea.setObjectName("hlayout_mainArea")
        self.vlayout_content = QtWidgets.QVBoxLayout()
        self.vlayout_content.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.vlayout_content.setSpacing(5)
        self.vlayout_content.setContentsMargins(1, 1, 1, 1)
        self.vlayout_content.setObjectName("vlayout_content")
        self.lblName = QtWidgets.QLabel(self.mainContent)
        self.lblName.setMinimumSize(QtCore.QSize(0, 25))
        self.lblName.setMaximumSize(QtCore.QSize(16777215, 25))
        self.lblName.setObjectName("lblName")
        self.vlayout_content.addWidget(self.lblName)
        self.edtImageName = QtWidgets.QLineEdit(self.mainContent)
        self.edtImageName.setObjectName("edtImageName")
        self.vlayout_content.addWidget(self.edtImageName)
        self.lblBaseImage = QtWidgets.QLabel(self.mainContent)
        self.lblBaseImage.setMinimumSize(QtCore.QSize(0, 25))
        self.lblBaseImage.setMaximumSize(QtCore.QSize(16777215, 25))
        self.lblBaseImage.setObjectName("lblBaseImage")
        self.vlayout_content.addWidget(self.lblBaseImage)
        self.cboBaseImage = QtWidgets.QComboBox(self.mainContent)
        self.cboBaseImage.setMinimumSize(QtCore.QSize(0, 30))
        self.cboBaseImage.setMaximumSize(QtCore.QSize(16777215, 30))
        self.cboBaseImage.setObjectName("cboBaseImage")
        self.vlayout_content.addWidget(self.cboBaseImage)
        self.lblRScript = QtWidgets.QLabel(self.mainContent)
        self.lblRScript.setMinimumSize(QtCore.QSize(0, 25))
        self.lblRScript.setMaximumSize(QtCore.QSize(16777215, 25))
        self.lblRScript.setObjectName("lblRScript")
        self.vlayout_content.addWidget(self.lblRScript)
        self.hlayout_RScript = QtWidgets.QHBoxLayout()
        self.hlayout_RScript.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.hlayout_RScript.setContentsMargins(0, -1, -1, -1)
        self.hlayout_RScript.setSpacing(1)
        self.hlayout_RScript.setObjectName("horizontalLayout")
        self.edtRScript = QtWidgets.QLineEdit(self.mainContent)
        self.edtRScript.setObjectName("edtRScript")
        self.edtRScript.setReadOnly(True)
        self.hlayout_RScript.addWidget(self.edtRScript)
        self.btnSelectScriptFile = QtWidgets.QPushButton(self.mainContent)
        self.btnSelectScriptFile.setMinimumSize(QtCore.QSize(24, 24))
        self.btnSelectScriptFile.setMaximumSize(QtCore.QSize(24, 24))
        self.btnSelectScriptFile.setObjectName("btnSelectScriptFile")
        self.hlayout_RScript.addWidget(self.btnSelectScriptFile)
        self.vlayout_content.addLayout(self.hlayout_RScript)
        self.lblDockerfile = QtWidgets.QLabel(self.mainContent)
        self.lblDockerfile.setObjectName("lblDockerfile")
        self.vlayout_content.addWidget(self.lblDockerfile)
        self.txtDockerfile = QtWidgets.QPlainTextEdit(self.mainContent)
        self.txtDockerfile.setObjectName("txtDockerfile")
        #self.txtDockerfile.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)      ### text wrap
        self.vlayout_content.addWidget(self.txtDockerfile)
        self.pbrBuildPrgoress = QtWidgets.QProgressBar(self.mainContent)
        self.pbrBuildPrgoress.setProperty("value", 0)
        self.pbrBuildPrgoress.setVisible(False)
        self.pbrBuildPrgoress.setObjectName("pbrBuildPrgoress")
        self.vlayout_content.addWidget(self.pbrBuildPrgoress)
        # buttons area
        self.hlayout_buttons = QtWidgets.QHBoxLayout()
        self.hlayout_buttons.setObjectName("hlayout_buttons")
        self.hlayout_buttons.setSpacing(5)
        self.btnOpen = QtWidgets.QPushButton(self.mainContent)
        self.btnOpen.setFixedSize(QtCore.QSize(75, 30))
        self.btnOpen.setObjectName("btnOpen")
        self.btnSave = QtWidgets.QPushButton(self.mainContent)
        self.btnSave.setFixedSize(QtCore.QSize(75, 30))
        self.btnSave.setObjectName("btnSave")
        self.btnBuild = QtWidgets.QPushButton(self.mainContent)
        self.btnBuild.setFixedSize(QtCore.QSize(90, 30))
        self.btnBuild.setObjectName("btnBuild")
        self.hlayout_buttons.addWidget(self.btnOpen)
        self.hlayout_buttons.addWidget(self.btnSave)
        self.hlayout_buttons.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.hlayout_buttons.addWidget(self.btnBuild)
        self.vlayout_content.addLayout(self.hlayout_buttons)
        # Right bioconductor packages aera
        self.vlayout_packages = QtWidgets.QVBoxLayout()
        self.vlayout_packages.setSpacing(3)
        self.vlayout_packages.setObjectName("vlayout_packages")
        self.vlayout_packages.setContentsMargins(1, 1, 1, 1)
        self.linePackageHeader = QtWidgets.QFrame(self.mainContent)
        self.linePackageHeader.setFrameShape(QtWidgets.QFrame.HLine)
        self.linePackageHeader.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.linePackageHeader.setObjectName("linePackageHeader")
        self.vlayout_packages.addWidget(self.linePackageHeader)
        self.lblInfoTitle = QtWidgets.QLabel(self.mainContent)
        self.lblInfoTitle.setMinimumSize(QtCore.QSize(0, 25))
        self.lblInfoTitle.setMaximumSize(QtCore.QSize(16777215, 25))
        self.lblInfoTitle.setStyleSheet(
            "background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(235, 235, 235, 255), stop:1 rgba(217, 217, 217, 255));\n"
            "padding-left: 3px;")
        self.lblInfoTitle.setObjectName("lblInfoTitle")
        self.vlayout_packages.addWidget(self.lblInfoTitle)
        self.hlayout_list_search = QtWidgets.QHBoxLayout()
        self.hlayout_list_search.setObjectName("hlayout_list_search")
        self.btnGetPackageList = QtWidgets.QPushButton(self.mainContent)
        self.btnGetPackageList.setMinimumSize(QtCore.QSize(75, 0))
        self.btnGetPackageList.setObjectName("btnGetPackageList")
        self.hlayout_list_search.addWidget(self.btnGetPackageList)
        self.lblSearchPackage = QtWidgets.QLabel(self.mainContent)
        self.lblSearchPackage.setObjectName("lblSearchPackage")
        self.hlayout_list_search.addWidget(self.lblSearchPackage)
        self.edtPackageName = QtWidgets.QLineEdit(self.mainContent)
        self.edtPackageName.setClearButtonEnabled(True)
        self.edtPackageName.setObjectName("edtPackageName")
        self.hlayout_list_search.addWidget(self.edtPackageName)
        self.vlayout_packages.addLayout(self.hlayout_list_search)
        self.lstPackages = QtWidgets.QTableView(self.mainContent)
        self.lstPackages.setObjectName("lstPackages")
        self.lstPackages.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.lstPackages.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.lstPackages.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.lstPackages.verticalHeader().setVisible(False)
        self.vlayout_packages.addWidget(self.lstPackages)
        # main window horizontal splitter
        container_mainLeft = QtWidgets.QWidget()
        container_mainRight = QtWidgets.QWidget()
        container_mainLeft.setLayout(self.vlayout_content)
        container_mainRight.setLayout(self.vlayout_packages)
        self.splitter_main = QtWidgets.QSplitter()
        self.splitter_main.addWidget(container_mainLeft)
        self.splitter_main.addWidget(container_mainRight)
        self.splitter_main.setOrientation(Qt.Horizontal)
        self.splitter_main.setSizes([200,150])
        self.hlayout_mainArea.addWidget(self.splitter_main)

        self.vlayoutBase.addWidget(self.mainContent)

        self.setLayout(self.vlayoutBase)
        self.layout().setContentsMargins(0,0,0,0)
        self.setMinimumSize(900, 700)

        # initialize UI components
        self.retranslateUi(self)
        self.model_package = QtGui.QStandardItemModel(self.lstPackages)
        self.model_package.setColumnCount(2)
        headerNames = ['Package Name', 'Detail']
        self.model_package.setHorizontalHeaderLabels(headerNames)
        self.package_list_proxy = QtCore.QSortFilterProxyModel(self)
        self.package_list_proxy.setSourceModel(self.model_package)
        self.defaultFont = "Helvetica Neue" if sys.platform == "darwin" else "Courier"

        # create UI events
        self.btnSelectScriptFile.clicked.connect(self.OnChooseScriptFile)
        self.btnBuild.clicked.connect(self.OnBuildClicked)
        self.btnGetPackageList.clicked.connect(self.OnGetPakageListClicked)
        self.btnOpen.clicked.connect(self.OnLoadDockerfile)
        self.btnSave.clicked.connect(self.OnSaveDockerfile)
        self.cboBaseImage.currentIndexChanged.connect(self.OnBaseImageSelectChanged)
        self.edtPackageName.textChanged.connect(self.OnPackageNameChanged)
        self.model_package.itemChanged.connect(self.OnPackageListSelectedChanged)

        self.InitializeUI()
        self.show()

    def retranslateUi(self, Widget):
        _translate = QtCore.QCoreApplication.translate
        Widget.setWindowTitle(_translate("Widget", "Bioconductor Docker Image Builder"))
        self.lblFormTitle.setText(_translate("Widget", "Bioconductor Docker Image Builder"))
        self.lblSubtitle.setText(_translate("Widget", "Customize your own bioconductor image"))
        self.lblName.setText(_translate("Widget", "Image Name: "))
        self.lblBaseImage.setText(_translate("Widget", "Select base image:"))
        self.lblRScript.setText(_translate("Widget", "Select R script:"))
        self.btnSelectScriptFile.setText(_translate("Widget", " ☰ "))
        self.lblDockerfile.setText(_translate("Widget", "Builder detail: "))
        self.btnBuild.setText(_translate("Form", "Build"))
        self.lblDockerVersion.setText(_translate("Form", "Docker Engine: {0}"))
        #self.lblBuiding.setText(_translate("Form", 'Ready'))
        self.lblDockerfile.setText(_translate("Form", "Docker file:"))
        self.btnOpen.setText(_translate("Form", "Open"))
        self.btnSave.setText(_translate("Form", "Save"))
        self.btnBuild.setText(_translate("Form", "Build"))
        self.lblInfoTitle.setText(_translate("Form", "Bioconductor R packages"))
        self.btnGetPackageList.setText(_translate("Form", "Get List"))
        self.lblSearchPackage.setText(_translate("Form", "Search: "))

    def InitializeUI(self):
        # Init Docker Engine
        self.dockerInitialized = False
        self.dockerClient = None
        strDockerInfo = ""
        try:
            self.dockerClient = DockerClient('unix:///var/run/docker.sock', 'local')
            strDockerInfo = self.lblDockerVersion.text().format(self.dockerClient.version()['Version'])
            self.dockerInitialized = True
        except:
            e = sys.exc_info()[0]
            print (e)
            strDockerInfo = "No Docker Engine installed OR missing docker-py"
            self.btnBuild.setEnabled(False)

        self.SelectedBiocPackage = []
        self.lblDockerVersion.setText(strDockerInfo)
        #self.dockerClient.images()

        # scan docker files
        self.cboBaseImage.addItem("From scratch", "-SCRATCH-")
        self.dockerfile_dir = os.path.join(self.base_dir, 'DockerFiles')
        dockerfiles = [x for x in fnmatch.filter(os.listdir(self.dockerfile_dir), '*.Dockerfile')]
        for f in dockerfiles:
            filename, _ = os.path.splitext(os.path.basename(f))
            self.cboBaseImage.addItem(filename, os.path.join(self.dockerfile_dir, f))

        self.building_log_file = os.path.join(self.base_dir, 'building.log')


    @pyqtSlot()
    def OnChooseScriptFile(self):
        start_file = os.path.expanduser("~/")
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open R Script File', start_file)
        if not filename:
            return

        self.edtRScript.setText(filename)

    def OnBaseImageSelectChanged(self, index):
        dockerfile = self.cboBaseImage.itemData(index)
        self.documentFromDockerfile(dockerfile)


    def documentFromDockerfile(self, filename):
        doc = QTextDocument(self)
        doc.setDocumentLayout(QtWidgets.QPlainTextDocumentLayout(doc))
        if filename == "-SCRATCH-":
            doc.setPlainText("")
        else:
            with open(filename, 'r') as f:
                doc.setPlainText(f.read())
        doc.setDefaultFont(QFont(self.defaultFont))
        doc.highlighter = DockerSyntaxHighlighter(doc)
        #doc.modificationChanged[bool].connect(self.onModificationChanged)
        doc.setModified(False)
        self._cachedDocument = doc
        self.txtDockerfile.setDocument(doc)

        # parser bioc package list from docker file
        # self.SelectedBiocPackage = []
        # rawText = doc.toPlainText()
        # self.model_package.clear()
        #
        # if rawText.find("biocLite(") >= 0:
        #     packages = rawText.split("biocLite(")[1].split("\n")[0].split(")")[0]
        #     if packages.find("c(") >= 0:
        #         packages = packages.split("c(")[1]
        #
        #     l = ast.literal_eval(packages)
        #     self.SelectedBiocPackage = [i.strip() for i in l]
        #     #print (self.SelectedBiocPackage)
        return self._cachedDocument

    @pyqtSlot()
    def OnGetPakageListClicked(self):
        service_getpackage = BiocPackageList()
        packageList = service_getpackage.GetList()

        for pkg in packageList:
            itemName = QStandardItem(pkg['Name'])
            itemName.setCheckable(True)
            #if itemName in self.SelectedBiocPackage:
            #    itemName.setCheckState(Qt.Checked)
            itemTitle = QStandardItem(pkg['Title'])
            self.model_package.appendRow([itemName, itemTitle])

        # Apply the model to the list view
        self.lstPackages.setModel(self.package_list_proxy)
        self.lstPackages.resizeColumnsToContents()


    @pyqtSlot(str)
    def OnPackageNameChanged(self, text):
        search = QtCore.QRegExp(text,QtCore.Qt.CaseInsensitive,QtCore.QRegExp.RegExp)
        self.package_list_proxy.setFilterRegExp(search)

    def _move_editor_cursor(self, start, end):
        cursor = self.txtDockerfile.textCursor()
        cursor.setPosition(start)
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end - start)
        self.txtDockerfile.setTextCursor(cursor)

    def _find_bioclite(self, query, text):
        pattern = re.compile(query)
        return pattern.search(text, 0) if query != "" else None

    def _update_bioc_package_in_dockerfile(self, previous_package):
        base_bioclite = "RUN Rscript -e \"source('https://bioconductor.org/biocLite.R');biocLite(c({0}),ask=FALSE)\"\n"
        previous = ','.join("'{0}'".format(w) for w in previous_package)
        current = ','.join("'{0}'".format(w) for w in self.SelectedBiocPackage)

        # no package selected, delete
        delete_mode = previous_package and not self.SelectedBiocPackage
        if delete_mode: current = ''

        plainText = self.txtDockerfile.toPlainText()

        matched = self._find_bioclite(previous, plainText)

        if matched:
            self._move_editor_cursor(matched.start(), matched.end())
            if delete_mode:
                cursor = self.txtDockerfile.textCursor()
                cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
                self.txtDockerfile.setTextCursor(cursor)
        else:
            # try locate "CMD"
            matched_cmd = self._find_bioclite("CMD", plainText)
            if matched_cmd:
                self._move_editor_cursor(matched_cmd.start(), matched_cmd.end())
                cursor = self.txtDockerfile.textCursor()
                cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                self.txtDockerfile.setTextCursor(cursor)
            else:
                self.txtDockerfile.moveCursor(QtGui.QTextCursor.End)

        cursor = self.txtDockerfile.textCursor()
        if matched and cursor.hasSelection():
            cursor.insertText(current)
        else:
            cursor.insertText(base_bioclite.format(current))
        self.txtDockerfile.setTextCursor(cursor)


    def OnPackageListSelectedChanged(self, item):
        package_name = item.text()
        previous_package = self.SelectedBiocPackage.copy()
        if not item.checkState():self.SelectedBiocPackage.remove(package_name)
        else: self.SelectedBiocPackage.append(package_name)

        self._update_bioc_package_in_dockerfile(previous_package)

    def OnSaveDockerfile(self):
        filename = self.cboBaseImage.currentData()
        if filename == "-SCRATCH-":
            filename = os.path.expanduser("~/")

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Dockerfile',
            filename,
            'Docker files (*.*)'
        )

        if filename:
            f = open(filename, 'w')
            f.write(self.txtDockerfile.toPlainText())
            f.close()

    def OnLoadDockerfile(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open Dockerfile',
            os.path.expanduser("~/"),
            'Docker files (*)'
        )
        if filename:
            itemName = '... ' + os.path.join(os.path.basename(os.path.dirname(filename)), os.path.basename(filename))
            index = self.cboBaseImage.findData(filename)
            if index >= 0:
                self.cboBaseImage.setCurrentIndex(index)
            else:
                self.cboBaseImage.addItem(itemName, filename)
                self.cboBaseImage.setCurrentIndex(self.cboBaseImage.findData(filename))

    def _set_building_text(self, labelCtrl, text):
        metrics = QtGui.QFontMetrics(labelCtrl.font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, labelCtrl.width())
        labelCtrl.setText(elidedText)

    def _enableUIElements(self, enabled=False):
        self.edtImageName.setEnabled(enabled)
        self.btnSelectScriptFile.setEnabled(enabled)
        self.txtDockerfile.setReadOnly(not enabled)
        self.lstPackages.setEnabled(enabled)
        self.edtPackageName.setEnabled(enabled)
        self.btnOpen.setEnabled(enabled)
        self.btnSave.setEnabled(enabled)
        self.btnGetPackageList.setEnabled(enabled)
        self.btnBuild.setEnabled(self.dockerInitialized and enabled)
        self.cboBaseImage.setEnabled(enabled)

    def _building_message_processor(self, message):
        # write to log file
        if not self.FLAG_in_bundle:
            with open(self.building_log_file, 'a') as f:
                f.write(message)

        # eliminate blank lines
        message = [s for s in message.splitlines() if s.strip()]
        if not message:
            return
        #message = ''.join(message)
        message = message[0]
        self._set_building_text(self.lblBuiding, message)

        endOfBuiding = False
        # extract step progress
        #   example: 'Step 10/10 : FROM ubuntu:16.04'
        step_pattern = re.compile(r'Step \d+\/\d+')
        if step_pattern.search(message):
            progress = message.split(' : ')[0].split(' ')[1].split('/')
            progress = [int(x) for x in progress]
            if progress[0] == 1: self.pbrBuildPrgoress.setMaximum(progress[1])

            self.pbrBuildPrgoress.setValue(progress[0])
            self._set_building_text(self.lblBuidingStep, message)

            endOfBuiding = progress[0] == progress[1]

        successful = message.find("Successfully built") >= 0

        if endOfBuiding or successful:
            self._set_building_text(self.lblBuidingStep, '')
            self._enableUIElements(True)
            self.pbrBuildPrgoress.setVisible(False)

    @pyqtSlot()
    def OnBuildClicked(self):
        imagename = self.edtImageName.text()
        if not imagename:
            msg = QtWidgets.QMessageBox()
            msg.setText('No Image Name')
            msg.setInformativeText("No Image Name\n\nPlease specify a image name")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec()
            self.edtImageName.setFocus()
            return

        # verify image name
        pattern = re.compile("^(?:(?=[^:\/]{1,253})(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(?:\.(?!-)[a-zA-Z0-9-]{1,63}(?<!-))*(?::[0-9]{1,5})?/)?((?![._-])(?:[a-z0-9._-]*)(?<![._-])(?:/(?![._-])[a-z0-9._-]*(?<![._-]))*)(?::(?![.-])[a-zA-Z0-9_.-]{1,128})?$")
        if not pattern.search(imagename):
            msg = QtWidgets.QMessageBox()
            msg.setText('Image Name Invalid')
            msg.setInformativeText("Typical image name:\n    registry/image-name[:version] \n\n"
                        "For example: \n    biodepot/bwb:latest")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec()
            self.edtImageName.setFocus()
            return

        self._enableUIElements(False)
        self.pbrBuildPrgoress.setVisible(True)
        dockerfile = self.txtDockerfile.toPlainText()

        self._set_building_text(self.lblBuidingStep, "Start building")
        # Call docker API to build image using thread
        self.buildimage_thread = DockerThread_BuildImage(self.dockerClient, imagename, dockerfile)
        self.buildimage_thread.build_process.connect(self.ThreadEvent_OnImageBuilding)
        self.buildimage_thread.build_complete.connect(self.ThreadEvent_OnImageBuildComplete)
        self.buildimage_thread.start()


    def ThreadEvent_OnImageBuilding(self, message):
        # filter message, eliminate terminal colors
        ESC = r'\x1b'
        CSI = ESC + r'\['
        OSC = ESC + r'\]'
        CMD = '[@-~]'
        ST = ESC + r'\\'
        BEL = r'\x07'
        pattern = '(' + CSI + '.*?' + CMD + '|' + OSC + '.*?' + '(' + ST + '|' + BEL + ')' + ')'
        plainMessage = re.sub(pattern, '', message)
        self._building_message_processor(plainMessage)

    def ThreadEvent_OnImageBuildComplete(self):
        self._set_building_text(self.lblBuidingStep, '')
        self._enableUIElements(True)
        self.pbrBuildPrgoress.setVisible(False)


import requests, json
class BiocPackageList:
    #fetch_url = "http://bioconductor.org/packages/release/BiocViews.html#___Software"
    package_json_url = "http://bioconductor.org/packages/json/3.5/bioc/packages.js"
    #{"Name": "a4", "Title": "Automated Affymetrix Array Analysis Umbrella Package"}

    def GetList(self):
        package_list = []
        try:
            rawhtml = requests.get(self.package_json_url)
            jsonValue = '{%s}' % (rawhtml.text.split('{', 1)[1].rsplit('}', 1)[0],)
            packages = json.loads(jsonValue)
            for item in packages['content']:
                package_list.append({"Name": item[0], "Title": item[2]})
        except:
            pass

        return package_list

def main(argv=sys.argv):

    app = QtWidgets.QApplication(list(argv))

    mainWindow = UIDockerBuilder()

    sys.exit(app.exec_())
    return 0


if __name__=="__main__":
    sys.exit(main())

