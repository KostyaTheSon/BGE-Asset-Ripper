import bpy
import os
import struct
import numpy as np
from PIL import Image
import pydub
import pyogg
import pefile
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class BGEAssetRipper(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("BGE Asset Ripper")
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()

        self.exeFileLabel = QLabel("Select BGE executable file:")
        layout.addWidget(self.exeFileLabel)

        self.exeFileButton = QPushButton("Browse...")
        self.exeFileButton.clicked.connect(self.selectExeFile)
        layout.addWidget(self.exeFileButton)

        self.extractButton = QPushButton("Extract Assets")
        self.extractButton.clicked.connect(self.extractAssets)
        layout.addWidget(self.extractButton)

        self.statusLabel = QLabel("")
        layout.addWidget(self.statusLabel)

        self.setLayout(layout)

    def selectExeFile(self):
        # Open file dialog to select BGE executable file
        exeFile, _ = QFileDialog.getOpenFileName(self, "Select BGE executable file", "", "Executable files (*.exe)")
        if exeFile:
            self.exeFileLabel.setText(f"Selected file: {exeFile}")

    def extractAssets(self):
        # Extract assets from BGE executable file
        exeFile = self.exeFileLabel.text().split(": ")[1]
        blenderFile = extractBlenderFile(exeFile)
        if blenderFile:
            extractAssets(blenderFile)
            self.statusLabel.setText("Assets extracted successfully!")

def extractBlenderFile(exeFile):
    # Extract Blender file from BGE executable file
    with open(exeFile, 'rb') as f:
        data = f.read()
        offset = data.find(b'BLENDER')
        if offset != -1:
            blenderFile = data[offset:]
            with open('blender_file.blend', 'wb') as bf:
                bf.write(blenderFile)
            return 'blender_file.blend'
        else:
            return None

def extractAssets(blenderFile):
    # Extract assets from Blender file using bpy
    bpy.context.window_manager.load_factory_settings_factory('BLENDER')
    with bpy.data.libraries.load(blenderFile) as (data_from, data_to):
        for block in data_from.blocks:
            if block.code == bpy.types.Image:
                image_data = block.data
                image = Image.frombytes('RGBA', (block.width, block.height), image_data)
                image.save(f'image_{block.name}.png')
            elif block.code == bpy.types.Sound:
                audio_data = block.data
                audio = pydub.AudioSegment(audio_data, frame_rate=44100, sample_width=2, channels=2)
                audio.export(f'audio_{block.name}.ogg', format='ogg')

if __name__ == '__main__':
    app = QApplication([])
    window = BGEAssetRipper()
    window.show()
    app.exec_()
