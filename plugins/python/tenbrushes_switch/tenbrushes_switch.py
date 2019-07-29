# This script is licensed CC 0 1.0, so that you can learn from it.

# ------ CC 0 1.0 ---------------

# The person who associated a work with this deed has dedicated the
# work to the public domain by waiving all of his or her rights to the
# work worldwide under copyright law, including all related and
# neighboring rights, to the extent allowed by law.

# You can copy, modify, distribute and perform the work, even for
# commercial purposes, all without asking permission.

# https://creativecommons.org/publicdomain/zero/1.0/legalcode

import krita
from . import uitenbrushes


class TenBrushesExtension(krita.Extension):

    def __init__(self, parent):
        super(TenBrushesExtension, self).__init__(parent)

        self.actions = []
        self.buttons = []
        self.selectedPresets = []
        # Indicates whether we want to activate the previous-selected brush
        # on the second press of the shortcut
        self.activatePrev = True
        self.oldPreset = None
        self.brush_index = 0

    def setup(self):
        self.readSettings()

    def createActions(self, window):
        action = window.createAction("ten_brushes_switch", i18n("Ten Brushes Switch"))
        action.setToolTip(i18n("Assign ten brush presets to ten shortcuts. (switchable extension)"))
        action.triggered.connect(self.initialize)
        self.loadActions(window)

    def initialize(self):
        self.uitenbrushes = uitenbrushes.UITenBrushes()
        self.uitenbrushes.initialize(self)

    def readSettings(self):
        self.selectedPresets = Application.readSetting(
            "", "tenbrushesSwitch", "").split(',')
        setting = Application.readSetting(
            "", "tenbrushesSwitchActivatePrev2ndPress", "True")
        # we should not get anything other than 'True' and 'False'
        self.activatePrev = setting == 'True'

    def writeSettings(self):
        presets = []

        for index, button in enumerate(self.buttons):
            self.actions[index].preset = button.preset
            presets.append(button.preset)
        Application.writeSetting("", "tenbrushesSwitch", ','.join(map(str, presets)))
        Application.writeSetting("", "tenbrushesSwitchActivatePrev2ndPress",
                                 str(self.activatePrev))

    def loadActions(self, window):
        allPresets = Application.resources("preset")

        for index, item in enumerate(['1', '2', '3', '4', '5',
                                      '6', '7', '8', '9', '0']):
            action = window.createAction(
                "activate_preset_" + item,
                str(i18n("Activate Brush Preset {num}")).format(num=item), "")
            action.triggered.connect(self.activatePreset)

            if (index < len(self.selectedPresets)
                    and self.selectedPresets[index] in allPresets):
                action.preset = self.selectedPresets[index]
            else:
                action.preset = None

            self.actions.append(action)
        
        # Add next preset switch action
        action = window.createAction(
            "activate_next_preset",
            i18n("Activate Next Brush Preset"))
        action.triggered.connect(self.switchToNextPreset)
        self.actions.append(action)

        # Add previous preset switch action
        action = window.createAction(
            "activate_previous_preset",
            i18n("Activate Previous Brush Preset"))
        action.triggered.connect(self.switchToPrevPreset)
        self.actions.append(action)

    def activatePreset(self):
        allPresets = Application.resources("preset")
        window = Application.activeWindow()
        if (window and len(window.views()) > 0
                and self.sender().preset in allPresets):
            currentPreset = window.views()[0].currentBrushPreset()
            if (self.activatePrev
                    and self.sender().preset == currentPreset.name()):
                window.views()[0].activateResource(self.oldPreset)
            else:
                self.oldPreset = window.views()[0].currentBrushPreset()
                window.views()[0].activateResource(
                    allPresets[self.sender().preset])
    
    def switchPreset(self, step):
        allPresets = Application.resources("preset")
        window = Application.activeWindow()
        presets_size = len(self.selectedPresets)
        
        # Set the index to the selected one if the current brush preset is in selected presets
        self.brush_index = 0
        currentPreset = window.views()[0].currentBrushPreset()
        for i in range(0, presets_size - 1):
            if (self.selectedPresets[i] == currentPreset.name()):
                self.brush_index = i
        
        for i in range(0, presets_size - 1):
            self.brush_index = (self.brush_index + step) % presets_size

            preset = self.selectedPresets[self.brush_index]
            if not (preset in allPresets):
                continue
            
            if (window and len(window.views()) > 0):
                window.views()[0].activateResource(allPresets[preset])
            break
    
    def switchToNextPreset(self):
        self.switchPreset(1)
    
    def switchToPrevPreset(self):
        self.switchPreset(-1)
