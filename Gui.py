from mainWidget import Ui_MainWidget
from interfacesWidget import Ui_InterfacesWidget
from mainWindow import Ui_MainWindow

#from utils import getPacketInfoDict
from utils import *
from PyQt5 import QtCore, QtGui, QtWidgets
from scapy.all import *
import threading
import globals

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.setupUi(self)
		self.interfacesWidget = InterfacesWidget()
		self.mainWidget= MainWidget()
		self.parentWidget = QtWidgets.QStackedWidget(self)
		self.parentWidget.addWidget(self.mainWidget)
		self.parentWidget.addWidget(self.interfacesWidget)
		self.setCentralWidget(self.parentWidget)
		self.parentWidget.setCurrentWidget(self.interfacesWidget)
		self.actionSave_Packet.triggered.connect(self.savePacket)
		self.actionOpen_Packet.triggered.connect(self.openPacket)
		self.actionQuit.triggered.connect(self.Quit)
		

	def savePacket(self):
		name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
		wrpcap(name[0] + ".pcap", self.mainWidget.getPacketList())

	def openPacket(self):
		name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
		self.mainWidget.clearPacketList()
		selectedPackets = rdpcap(name[0])
		self.mainWidget.addListOfPackets(selectedPackets)
		self.parentWidget.setCurrentWidget(self.mainWidget)

	def Quit(self):
		buttonReply = QtWidgets.QMessageBox.question(self, 'Unsaved packets...', "Do you want to stop the capture and save the captured packets before quitting?", QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
		if buttonReply == QtWidgets.QMessageBox.Save:
			print('Yes clicked.')
			globals.stop = True
			name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
			wrpcap(name[0] + ".pcap", self.mainWidget.getPacketList())
			sys.exit()
		elif buttonReply == QtWidgets.QMessageBox.Discard:
			print('No clicked.')
			globals.stop = True
			sys.exit()
		else:
			pass
		#msg = QtWidgets.QMessageBox(self, "Unsaved packets...", "Do you want to stop the capture and save the captured packets before quitting?", QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
		#if(msg == QtWidgets.QMessageBox.Save):
			#closeEvent()
			#savePacket()
			#sys.exit()
		#elif(msg == QtWidgets.QMessageBox.Discard):
			#closeEvent()
			#sys.exit()
		#else:
			#pass

	def closeEvent(self, event):
		globals.stop = True

	def connectStart(self, fn):
		self.actionStart.triggered.connect(fn)

	def connectStop(self, fn):
		self.actionStop.triggered.connect(fn)

	def connectRestart(self, fn):
		self.actionRestart.triggered.connect(fn)

	def addInterfaces(self, interfacesList):
		self.interfacesWidget.addInterfaces(interfacesList)

	def getCurrentInterface(self):
		try:
			self.currentInterface = self.interfacesWidget.currentInterface()
			return self.interfacesWidget.currentInterface()
		except(RuntimeError):
			return self.currentInterface

	def addPacketToList(self, packetDict, packet):
		self.mainWidget.addPacketToList(packetDict, packet)

	def clearPacketsList(self):
		self.mainWidget.clearPacketList()

	def setWidget(self, w):
		if (w == "Main"):
			self.parentWidget.setCurrentWidget(self.mainWidget)
		else:
			self.parentWidget.setCurrentWidget(self.interfacesWidget)

class InterfacesWidget(QtWidgets.QWidget, Ui_InterfacesWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		self.setupUi(self)
	def addInterfaces(self, interfacesList):
		for i in interfacesList:
			self.interfacesList.addItem(i)
	def currentInterface(self):
		return self.interfacesList.currentText()

class MainWidget(QtWidgets.QWidget, Ui_MainWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		self.setupUi(self)
		self.countPacket = 0
		self.packetList = []
		self.packetTable.itemClicked.connect(self.rowClicked)
		self.hexView.setStyleSheet("font: 9pt Consolas")
		self.packetTable.setStyleSheet("font: 9pt Consolas")
		self.packetTable.horizontalHeader().setStretchLastSection(True)
		self.filterButton.clicked.connect(self.filterFunction)

	def clearPacketList(self):
		self.packetTable.setRowCount(0)
		self.packetList = []
		self.countPacket = 0

	def addListOfPackets(self, packetList):
		for packet in packetList:
			packet.show()
			self.addPacketToList(getPacketInfoDict(packet), packet)


	def getPacketList(self):
		return self.packetList

	def rowClicked(self):
		rowNum = self.packetTable.currentRow()
		hexItem = QtWidgets.QListWidgetItem()
		hexItem.setText(hexdump3(self.packetList[rowNum],True))
		self.hexView.clear()
		self.hexView.addItem(hexItem)

	def filterFunction(self):
		pass

	def addPacketToList(self, packetDict, originalPacket):
		self.packetTable.setRowCount(self.packetTable.rowCount() + 1)
		time = QtWidgets.QTableWidgetItem()
		src = QtWidgets.QTableWidgetItem()
		dst = QtWidgets.QTableWidgetItem()
		protocol = QtWidgets.QTableWidgetItem()
		length = QtWidgets.QTableWidgetItem()
		info = QtWidgets.QTableWidgetItem()

		# Set flags for each Widget
		time.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
		src.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
		dst.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
		length.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
		protocol.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
		info.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)

		time.setText(originalPacket.sprintf("%.time%"))
		protocol.setText( packetDict["proto"])

		if (packetDict["proto"] == "UDP" or packetDict["proto"] == "TCP" or packetDict["proto"] == "HTTP"):
			src.setText( packetDict["srcIP"])
			dst.setText( packetDict["dstIP"])
			length.setText( str(packetDict["len"]))
			info.setText( packetDict["srcPort"] + " -> " + packetDict["dstPort"])
		else:
			src.setText( packetDict["srcMac"])
			dst.setText( packetDict["dstMac"])
		
		self.packetTable.setItem(self.countPacket, 1, time)
		self.packetTable.setItem(self.countPacket, 2, src)
		self.packetTable.setItem(self.countPacket, 3, dst)
		self.packetTable.setItem(self.countPacket, 4, protocol)
		self.packetTable.setItem(self.countPacket, 5, length)
		self.packetTable.setItem(self.countPacket, 6, info)
		for i in range(self.packetTable.rowCount() + 2):
			self.packetTable.setRowHeight(i, 20)

		self.packetList.append(originalPacket) # add packet to packet list 
		self.countPacket += 1 # increment packet count
