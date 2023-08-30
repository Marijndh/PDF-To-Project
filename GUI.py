import os
import subprocess
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QLabel, QListWidget, QPushButton, QDialog, \
    QDialogButtonBox, QVBoxLayout, QLineEdit, QMessageBox, QApplication


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("PDF-To-Project")

        self.running_main = False
        self.run_main_again = False
        self.send_email = ''

        self.setFixedSize(800, 450)
        self.layout = QGridLayout()
        self.setStyleSheet("background-color: rgb(3, 38, 94);")

        self.search = QWidget()
        layout = QVBoxLayout(self.search)
        layout.setContentsMargins(0, 0, 0, 0)

        searching_for = QLabel("Bezig met: ")
        searching_for.setFixedSize(300, 140)
        searching_for.setStyleSheet(
            "border-top: 0px; border-bottom: 0px;  font-size: 30px;  margin-top: 100px; text-align: center;")
        searching_for.setAlignment(Qt.AlignCenter)

        self.dots = QLabel("")
        self.dots.setStyleSheet(
            "border-top: 0px; border-bottom: 0px;  font-size: 50px; text-align: center; margin-bottom: 20px;")
        self.dots.setFixedSize(300, 70)
        self.dots.setAlignment(Qt.AlignCenter)

        self.search_text = QLabel("")
        self.search_text.setStyleSheet(
            "border-top: 0px; border-bottom: 0px; font-size: 12px; margin-bottom: 100px; text-align: center;")
        self.search_text.setFixedSize(300, 125)
        self.search_text.setAlignment(Qt.AlignCenter)

        layout.addWidget(searching_for)
        layout.addWidget(self.dots)
        layout.addWidget(self.search_text)

        self.email_titel = QLabel("*Nog geen email titel kunnen vinden*")
        self.found_objects = QListWidget()
        self.ClearFoundObject()
        self.recent_logs = QListWidget()
        self.recent_logs.itemDoubleClicked.connect(self.LogsDoubleClick)
        self.AddLogs()
        self.again = QPushButton("Opnieuw")
        self.again.clicked.connect(self.ButtonClick)

        self.email_titel.setFixedSize(790, 35)
        self.search.setFixedSize(300, 350)
        self.found_objects.setFixedSize(300, 350)
        self.recent_logs.setFixedSize(150, 350)
        self.again.setFixedSize(140, 30)

        self.email_titel.setStyleSheet(
            "margin-left: 5px; margin-right: 10px; font-size: 20px; font-weight: bold; color: rgb(102, 154, 237);")
        self.search.setStyleSheet(
            "margin-left: 15px; background-color: rgb(102, 154, 237);")
        self.found_objects.setStyleSheet(
            "margin-right: 10px; background-color: rgb(102, 154, 237); ")
        self.recent_logs.setStyleSheet(
            "margin-right: 5px; background-color: rgb(102, 154, 237);")
        self.again.setStyleSheet(
            "margin-left: 5px; font-size: 12px; background-color: rgb(102, 154, 237);")

        self.layout.addWidget(self.email_titel, 0, 0)
        self.layout.addWidget(self.search, 1, 0)
        self.layout.addWidget(self.found_objects, 1, 1)
        self.layout.addWidget(self.recent_logs, 1, 2)
        self.layout.addWidget(self.again, 3, 2)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        sys.exit()

    def ClearFoundObject(self):
        self.found_objects.clear()
        self.found_objects.addItem('Status van programma: ')
        self.found_objects.item(0).setFont(QFont('Arial', 10, 100))

    def ButtonClick(self):
        self.run_main_again = True

    def LogsDoubleClick(self):
        if not self.running_main:
            if self.recent_logs.selectedItems() is not None:
                x = self.recent_logs.selectedItems()[0]
                CREATE_NO_WINDOW = 0x08000000
                subprocess.Popen(f"notepad.exe Logs/{x.text()}", creationflags=CREATE_NO_WINDOW)

                answer = self.AskQuestion("Wil je deze log-file mailen? Y/N")
                if answer.upper() == 'Y':
                    self.send_email = x.text()

    def SetRunningMain(self, running):
        self.running_main = running

    def AddLogs(self):
        self.recent_logs.clear()
        self.recent_logs.addItem('Recente log-files: ')
        self.recent_logs.item(0).setFont(QFont('Arial', 10, 100))
        log_list = os.listdir("Logs")
        log_list.reverse()
        for x in log_list:
            self.recent_logs.addItem(x)
        QApplication.processEvents()

    def SetTitel(self, titel):
        self.email_titel.setText(titel)
        QApplication.processEvents()

    def AddStatusLabel(self, text):
        self.found_objects.addItem(text)
        QApplication.processEvents()

    def Alert(self, text):
        button = QMessageBox.critical(
            QMainWindow(),
            " ",
            text,
            buttons=QMessageBox.Ok,
            defaultButton=QMessageBox.Ok,
        )
        QApplication.processEvents()

    def AskQuestion(self, question):
        dlg = QDialog(self)
        dlg.setStyleSheet("background-color: white;")
        dlg.setWindowTitle(" ")
        dlg.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dlg.buttonBox.accepted.connect(dlg.accept)
        dlg.layout = QVBoxLayout()
        label = QLabel(question)
        label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        dlg.layout.addWidget(label)
        answer = QLineEdit()
        answer.setStyleSheet("font-size: 12px; background-color: white; color: black;")
        dlg.layout.addWidget(answer)
        dlg.layout.addWidget(dlg.buttonBox)
        dlg.setLayout(dlg.layout)
        dlg.show()
        if dlg.exec():
            return answer.text()
        else:
            self.AskQuestion(question)
        QApplication.processEvents()

    def Searching_For(self, search):
        if len(self.dots.text()) > 9:
            self.dots.setText('.')
        else:
            self.dots.setText(self.dots.text() + '.')
        self.search_text.setText(search)
        QApplication.processEvents()
