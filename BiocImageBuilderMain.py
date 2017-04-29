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
        # GUI
        # stylesheet
        self.setStyleSheet("QPushButton{"
                             "    background-color: #1588c5;"
                             "    color: white;"
                             "    height: 25px;"
                             "    border: 1px solid #1a8ac6;"
                             "    border-radius: 2px;}"
                             "QPushButton:pressed {"
                             "    background-color: #0077cc;"
                             "    border-style: inset;"
                             "}"
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
        self.lblFormTitle = QtWidgets.QLabel(self.frameTitle)
        self.lblFormTitle.setGeometry(QtCore.QRect(66, 11, 300, 30))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.lblFormTitle.setFont(font)
        self.lblFormTitle.setStyleSheet("color: white;")
        self.lblFormTitle.setObjectName("lblFormTitle")
        self.lblIcon = QtWidgets.QLabel(self.frameTitle)
        self.lblIcon.setGeometry(QtCore.QRect(14, 15, 41, 31))
        self.lblIcon.setText("")
        self.lblIcon.setPixmap(QtGui.QPixmap("icons/builder_icon.png"))
        self.lblIcon.setScaledContents(True)
        self.lblIcon.setObjectName("lblIcon")
        self.lblDockerVersion = QtWidgets.QLabel(self.frameTitle)
        self.lblDockerVersion.setGeometry(QtCore.QRect(71, 37, 300, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lblDockerVersion.setFont(font)
        self.lblDockerVersion.setStyleSheet("color: white;")
        self.lblDockerVersion.setObjectName("lblDockerVersion")
        self.vlayoutBase.addWidget(self.frameTitle)
        self.frameSubtitle = QtWidgets.QFrame(self)
        self.frameSubtitle.setEnabled(True)
        self.frameSubtitle.setMinimumSize(QtCore.QSize(0, 45))
        self.frameSubtitle.setMaximumSize(QtCore.QSize(16777215, 45))
        self.frameSubtitle.setStyleSheet("QFrame#frameSubtitle\n"
                                         "{background: #1998de; }")
        self.frameSubtitle.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameSubtitle.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frameSubtitle.setObjectName("frameSubtitle")
        self.lblSubtitle = QtWidgets.QLabel(self.frameSubtitle)
        self.lblSubtitle.setGeometry(QtCore.QRect(15, 7, 301, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lblSubtitle.setFont(font)
        self.lblSubtitle.setStyleSheet("color: white")
        self.lblSubtitle.setObjectName("lblSubtitle")
        self.vlayoutBase.addWidget(self.frameSubtitle)
        self.mainContent = QtWidgets.QWidget(self)
        self.mainContent.setObjectName("mainContent")
        self.hlayout_mainArea = QtWidgets.QHBoxLayout(self.mainContent)
        self.hlayout_mainArea.setContentsMargins(8, 8, 8, 8)
        self.hlayout_mainArea.setSpacing(2)
        self.hlayout_mainArea.setObjectName("hlayout_mainArea")
        self.vlayout_content = QtWidgets.QVBoxLayout()
        self.vlayout_content.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.vlayout_content.setSpacing(2)
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
        self.pbrBuildPrgoress.setProperty("value", 24)
        self.pbrBuildPrgoress.setObjectName("pbrBuildPrgoress")
        self.vlayout_content.addWidget(self.pbrBuildPrgoress)
        self.hlayout_buttons = QtWidgets.QHBoxLayout()
        self.hlayout_buttons.setObjectName("hlayout_buttons")
        self.btnOpen = QtWidgets.QPushButton(self.mainContent)
        self.btnOpen.setMinimumSize(QtCore.QSize(75, 0))
        self.btnOpen.setMaximumSize(QtCore.QSize(75, 16777215))
        self.btnOpen.setObjectName("btnOpen")
        self.hlayout_buttons.addWidget(self.btnOpen)
        self.btnSave = QtWidgets.QPushButton(self.mainContent)
        self.btnSave.setMinimumSize(QtCore.QSize(75, 0))
        self.btnSave.setMaximumSize(QtCore.QSize(75, 16777215))
        self.btnSave.setObjectName("btnSave")
        self.hlayout_buttons.addWidget(self.btnSave)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hlayout_buttons.addItem(spacerItem)
        self.btnBuild = QtWidgets.QPushButton(self.mainContent)
        self.btnBuild.setMinimumSize(QtCore.QSize(90, 0))
        self.btnBuild.setMaximumSize(QtCore.QSize(90, 16777215))
        self.btnBuild.setObjectName("btnBuild")
        self.hlayout_buttons.addWidget(self.btnBuild)
        self.vlayout_content.addLayout(self.hlayout_buttons)

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

        # events
        self.btnSelectScriptFile.clicked.connect(self.OnChooseScriptFile)
        self.btnBuild.clicked.connect(self.OnBuildClicked)
        self.btnGetPackageList.clicked.connect(self.OnGetPakageListClicked)
        self.cboBaseImage.currentIndexChanged.connect(self.OnBaseImageSelectChanged)
        self.edtPackageName.textChanged.connect(self.OnPackageNameChanged)
        self.model_package.itemChanged.connect(self.OnPackageListSelectedChanged)

        self.InitializeUI()
        #self.test_log()

        self.show()

    def retranslateUi(self, Widget):
        _translate = QtCore.QCoreApplication.translate
        Widget.setWindowTitle(_translate("Widget", "Bioconductor Docker Image Builder"))
        self.lblFormTitle.setText(_translate("Widget", " Bioconductor Docker Image Builder"))
        self.lblSubtitle.setText(_translate("Widget", "Customize your own bioconductor image"))
        self.lblName.setText(_translate("Widget", "Image Name: "))
        self.lblBaseImage.setText(_translate("Widget", "Select base image:"))
        self.lblRScript.setText(_translate("Widget", "Select R script:"))
        self.btnSelectScriptFile.setText(_translate("Widget", " ☰ "))
        self.lblDockerfile.setText(_translate("Widget", "Builder detail: "))
        self.btnBuild.setText(_translate("Form", "Build"))
        self.lblDockerVersion.setText(_translate("Form", "Docker Engine: {0}"))
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

        self.SelectedBiocPackage = []
        self.lblDockerVersion.setText(strDockerInfo)
        #self.dockerClient.images()

        # scan docker files
        self.cboBaseImage.addItem("From scratch", "-SCRATCH-")
        self.dockerfile_dir = os.path.join(os.path.split(os.path.realpath(sys.argv[0]))[0], 'DockerFiles')
        dockerfiles = [x for x in fnmatch.filter(os.listdir(self.dockerfile_dir), '*.Dockerfile')]
        for f in dockerfiles:
            filename, _ = os.path.splitext(os.path.basename(f))
            self.cboBaseImage.addItem(filename, os.path.join(self.dockerfile_dir, f))




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
        self.txtDockerfile.setDocument(self.documentFromDockerfile(dockerfile))


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




    @pyqtSlot()
    def OnBuildClicked(self):
        dockerfile_example = '''
#xenial image
FROM docker/whalesay:latest
RUN apt-get -y update && apt-get install -y fortunes
CMD /usr/games/fortune -a | cowsay'''

        dockerfile = '''
#xenial image
FROM ubuntu:16.04

#tools to manage repositories
RUN apt-get update && apt-get install -y software-properties-common wget texinfo texlive texlive-fonts-extra

#To get R's blas and lapack must compile from source NOT from deb
RUN wget https://cran.r-project.org/src/base/R-latest.tar.gz
RUN tar -xzvf R-latest.tar.gz

#install stuff for compilation of R

RUN apt-get install -y build-essential gfortran xorg-dev gcc-multilib gobjc++ libblas-dev liblzma-dev gobjc++ libreadline-dev aptitude \
 libbz2-dev libpcre3-dev libcurl4-openssl-dev

#configure and compile
RUN cd R-* && ./configure
RUN cd R-* && make -j 8
RUN cd R-* && make prefix=/ install

#need to install in xxx for libraries to be in the right place

#install components of bioconductor for networkBMA
RUN Rscript -e "source('https://bioconductor.org/biocLite.R');biocLite(c('stats','utils','BMA','Rcpp','RcppArmadillo','RcppEigen','BH','leaps','BiocParallel','Rgraphviz'),ask=FALSE)"

CMD ["/bin/bash"]'''

        imagename = self.edtImageName.text();
        self.txtOutput.append("Start building image [{0}]....".format(imagename))
        # Call docker API to build image using thread
        self.buildimage_thread = DockerThread_BuildImage(self.dockerClient, imagename, dockerfile)
        self.buildimage_thread.build_process.connect(self.ThreadEvent_OnImageBuilding)
        self.buildimage_thread.build_complete.connect(self.ThreadEvent_OnImageBuildComplete)
        self.buildimage_thread.start()


    def ThreadEvent_OnImageBuilding(self, message):
        ESC = r'\x1b'
        CSI = ESC + r'\['
        OSC = ESC + r'\]'
        CMD = '[@-~]'
        ST = ESC + r'\\'
        BEL = r'\x07'
        pattern = '(' + CSI + '.*?' + CMD + '|' + OSC + '.*?' + '(' + ST + '|' + BEL + ')' + ')'
        self.txtDockerfile.append(re.sub(pattern, '', message))

    def ThreadEvent_OnImageBuildComplete(self):
        pass


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

