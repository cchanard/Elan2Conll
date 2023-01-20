#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from collections import deque
from os.path import basename
from xml.dom.minidom import *
import wx
from elan.fic import Fic, Template, Tier, Type, Annotation
from outils import createWrite as CW, hierarchy, validation, elanTools

from lxml import etree
from lxml.etree import SubElement

global newFile
global newTemplate
global pathName
global dirNew
global linkTemplate
global preAl

listFic = []
TS = {}
preAl = []

pathDirectory = ""
tierBool = False
typeBool = False

class App(wx.App):
    def OnInit(self):
        self.frame = ToolsFrame(None, title=u'ELAN Tools')
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        return True

class ToolsFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="", pos=(10, 50), size=(1000, 1000), style=wx.DEFAULT_FRAME_STYLE,
                 name="ToolsFrame"):
        super(ToolsFrame, self).__init__(parent, id, title, pos, size, style, name)
        self.topPanel = wx.Panel(self)
        panel0 = wx.Panel(self.topPanel, -1)
        titre = wx.StaticText(panel0, pos=(0, 15), label="ELAN TOOLS")
        font = titre.GetFont()
        font.PointSize += 10
        font = font.Bold()
        titre.SetFont(font)

        """-----------------------------------------------------------------------------------------------------------
                                                        Panel commun 
        ------------------------------------------------------------------------------------------------------------"""
        self.comPanel = wx.Panel(self.topPanel, -1)
        self.textCom1 = wx.TextCtrl(self.comPanel)
        self.textCom2 = wx.TextCtrl(self.comPanel)
        self.checkCom2 = wx.CheckBox(self.comPanel, label="Token = Mot")
        self.buttonCom = wx.Button(self.comPanel, label="Go")
        self.buttonCom.SetBackgroundColour(wx.Colour(200, 200, 100))

        self.hb2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hb2.Add(self.textCom2, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)
        self.hb2.Add(self.checkCom2, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)
        self.hb2.Add(self.buttonCom, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)

        self.vb1 = wx.BoxSizer(wx.VERTICAL)
        self.vb1.Add(self.textCom1, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)
        self.vb1.Add(self.hb2, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)

        self.comPanel.SetSizer(self.vb1)
        self.comPanel.Hide()

        # panel checkbox, Button
        self.comPanel2 = wx.Panel(self.topPanel, -1)
        self.checkCom3 = wx.CheckBox(self.comPanel2, label="add DR tiers")
        self.buttonCom3 = wx.Button(self.comPanel2, label="Go")
        self.buttonCom3.SetBackgroundColour(wx.Colour(200, 200, 100))
        self.hb3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hb3.Add(self.buttonCom3, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)
        self.hb3.Add(self.checkCom3, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)
        # self.vb2 = wx.BoxSizer(wx.VERTICAL)
        # self.vb2.Add(self.hb3, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)
        self.comPanel2.SetSizer(self.hb3)
        self.comPanel2.Hide()

        """-----------------------------------------------------------------------------------------------------------
                                                            Panel Voc List
        ------------------------------------------------------------------------------------------------------------"""

        self.vocListPanel = wx.Panel(self.topPanel, -1)

        choices = ["Alphabetical", "Numerical"]
        self.radioBox = wx.RadioBox(self.vocListPanel, label="Sorting Choice", pos=(80, 10), choices=choices,
                                    majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.vb7 = wx.BoxSizer(wx.VERTICAL)
        self.hb8 = wx.BoxSizer(wx.HORIZONTAL)

        """-----------------------------------------------------------------------------------------------------------
                            Panel console et consoleTemplate 
        ------------------------------------------------------------------------------------------------------------"""

        self.consolePanel = wx.Panel(self.topPanel, -1)
        self.txtAlign = wx.BoxSizer(wx.HORIZONTAL)
        self.console = wx.TextCtrl(self.consolePanel, size=(450, 400), style=wx.TE_MULTILINE)
        self.consoleTemplate = wx.TextCtrl(self.consolePanel, size=(450, 400), style=wx.TE_MULTILINE)
        self.txtAlign.Add(self.console, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)
        self.txtAlign.Add(self.consoleTemplate, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)
        self.consolePanel.SetSizer(self.txtAlign)

        self.consolePanel2 = wx.Panel(self.topPanel, -1)
        self.txtAlign2 = wx.BoxSizer(wx.HORIZONTAL)
        self.consoleTraitement = wx.TextCtrl(self.consolePanel2, size=(450, 400), style=wx.TE_MULTILINE)
        self.txtAlign2.Add(self.consoleTraitement, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 1)
        self.consolePanel2.SetSizer(self.txtAlign2)

        """-----------------------------------------------------------------------------------------------------------
                            Mise en forme avec mainSizer 
        ------------------------------------------------------------------------------------------------------------"""

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(panel0, 0, wx.EXPAND | wx.ALL, border=10)
        self.mainSizer.Add(self.comPanel, 0, wx.EXPAND | wx.ALL, border=10)
        self.mainSizer.Add(self.comPanel2, 0, wx.EXPAND | wx.ALL, border=10)

        self.mainSizer.Add(self.consolePanel, 0, wx.EXPAND | wx.ALL, border=10)
        self.mainSizer.Add(self.consolePanel2, 0, wx.EXPAND | wx.ALL, border=10)
        self.topPanel.SetSizer(self.mainSizer)

        self.listMenu = []

        # create a menu bar
        self.makeMenuBar()

        disableMenu(self.listMenu)
        self.consoleTemplate.Hide()


    def makeMenuBar(self):
        fileMenu = wx.Menu()
        openItem = fileMenu.Append(-1, "Open file\tCtrl-O",
                                   "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        elanDirectoryItem = fileMenu.Append(-1, "Open ELAN Directory\tCtrl-D",
                                            "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        openItemTemplate = fileMenu.Append(-1, "Open Template\tCtrl-T",
                                           "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        saveAsItem = fileMenu.Append(-1, "&Save as new Elan File\tCtrl-S", "Save as")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        """  Menu Aide """
        alignHelpItem = helpMenu.Append(wx.ID_ANY, "Help on Align", "Align help")
        hierarchyHelpItem = helpMenu.Append(wx.ID_ANY, "Help on Hierarchy", "Hierarchy help")
        validateHelpItem = helpMenu.Append(wx.ID_ANY, "Help on Validate", "Validate help")
        changeLabelHelpItem = helpMenu.Append(wx.ID_ANY, "Help on Change Label", "Change label help")
        createLabelHelpItem = helpMenu.Append(wx.ID_ANY, "Help on Create Conll", "Create Conll help")


        """ Items du menu Commande """
        commandMenu = wx.Menu()
        alignItem = commandMenu.Append(wx.ID_ANY, "Align", "align boundaries")
        hierarchyItem = commandMenu.Append(wx.ID_ANY, "Show Hierarchy")
        refItem = commandMenu.Append(wx.ID_ANY, "&Change Label", "Annotation Value for ref")
        self.validateItem = commandMenu.Append(wx.ID_ANY, "Validate")
        eaf2ConnlUItem = commandMenu.Append(wx.ID_ANY, "Convert ELAN to ConnlU")
        self.listMenu.append(commandMenu)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(commandMenu, "&Command")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnOpen, openItem)
        self.Bind(wx.EVT_MENU, self.OpenELANDirectory, elanDirectoryItem)
        self.Bind(wx.EVT_MENU, self.OnOpenTemplate, openItemTemplate)
        self.Bind(wx.EVT_MENU, self.LabelRef, refItem)
        self.Bind(wx.EVT_MENU, self.OnEaf2ConllU, eaf2ConnlUItem)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, saveAsItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)

        """ Items du menu Help """
        self.Bind(wx.EVT_MENU, lambda evt, temp='alignHelp': self.OnHelp(evt, temp), alignHelpItem)
        self.Bind(wx.EVT_MENU, lambda evt, temp='hierarchyHelp': self.OnHelp(evt, temp), hierarchyHelpItem)
        self.Bind(wx.EVT_MENU, lambda evt, temp='validateHelp': self.OnHelp(evt, temp), validateHelpItem)
        self.Bind(wx.EVT_MENU, lambda evt, temp='changeLabel': self.OnHelp(evt, temp), changeLabelHelpItem)
        self.Bind(wx.EVT_MENU, lambda evt, temp='conllHelp': self.OnHelp(evt, temp), createLabelHelpItem)

        """ Items du menu Command """
        self.Bind(wx.EVT_MENU, self.OnAlign, alignItem)
        self.Bind(wx.EVT_MENU, self.OnHierarchy, hierarchyItem)
        self.Bind(wx.EVT_MENU, self.OnValidate, self.validateItem)

    def OnHelp(self, event, label):
        source = "ressources" + os.sep + "aide" + os.sep + label + ".txt"
        with open(source, encoding='utf-8', mode='r') as f:
            message = f.read()
        wx.MessageBox(message, label, wx.OK | wx.ICON_INFORMATION)

    def OnHelpAlign(self, event):
        with open("ressources" + os.sep + "aide" + os.sep + "alignHelp.txt", "r") as f:
            message = f.read()
        wx.MessageBox(message, "About Align", wx.OK | wx.ICON_INFORMATION)

    def OnEaf2ConllU(self, event):
        global listFic
        #listFic=("D:\\1_Developpement\\Python\\ElanToSud\\BEJ_MV_NARR_02_FARMER.eaf")
        self.ClearHelp(event)
        self.textCom1.Clear()
        self.textCom2.Clear()
        self.buttonCom.SetLabelText('create Conll')
        self.buttonCom.Bind(wx.EVT_BUTTON, self.EvtSelectTiers)
        self.textCom1.AppendText("Mft ref tx mot mb ge ps ft")
        self.textCom2.AppendText(". ! ?")
        self.comPanel.Show()
        self.mainSizer.Fit(self.topPanel)

    def LabelRef(self, event):
        global listFic
        elanTools.LabelRef(listFic)

    def OnAlign(self, event):
        self.ClearHelp(event)
        self.textCom1.Clear()
        self.textCom2.Clear()
        self.buttonCom.SetLabelText('Align')
        self.buttonCom.Bind(wx.EVT_BUTTON, self.EvtSelectTiers)
        self.textCom1.AppendText("mot@SP1")
        self.textCom2.AppendText("rp@SP1, qt@SP1")
        self.comPanel.Show()
        self.mainSizer.Fit(self.topPanel)

    def OnSaveAs(self, event):
        """ Sauvegarde des fichiers ELAN modifiés """
        global pathName
        global dirNew
        try:
            for fic in listFic:
                dirNew = CW.CreateDirNew(os.path.dirname(fic.nom))
                ext = ""
                nom = os.path.splitext(os.path.basename(fic.nom))[0] + ext + '.EAF'

                path = dirNew + "/" + nom
                tree = fic.getTree()

                with open(path, "w") as f:
                    tree.write(path, encoding="UTF-8", xml_declaration=True)
        except IOError:
            wx.LogError("Cannot save current data in file '%s'." % pathName)


    def help(self):
        choice = self.choice.GetStringSelection()

        lien = "ressources" + os.sep + "aide" + os.sep + choice + ".txt"
        with open(lien, "r") as f:
            test = f.read()
        wx.MessageBox(test, "About",
                      wx.OK | wx.ICON_INFORMATION)

    def ClearHelp(self, event):
        # self.panelHelp.Hide()
        self.mainSizer.Fit(self.topPanel)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnOpenTemplate(self, event):
        """ Ouverture d'un template """
        global newTemplate
        global pathName
        global dirJson
        global TS

        listTiers = []
        data = []

        self.consoleTemplate.Show()
        # self.console.Clear()
        self.ClearHelp(event)

        with wx.FileDialog(self, "Open Template", wildcard="ELAN files (*.etf)|*.etf|XML files (*.xml)|*.xml)",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathName = fileDialog.GetPath()

            try:
                with open(pathName, 'r', encoding='utf8') as file:
                    tree = etree.parse(pathName)
                    dom = parse(file)
                    newTemplate = Template(pathName)
                    newTemplate.setTree(tree)

                    elanTools.readTypes(newTemplate, dom)
                    elanTools.readTiers(newTemplate, dom, TS)
                    hierarchy.hierarchy(newTemplate, listTiers)

                    self.consoleTemplate.Clear()
                    # self.console.Clear()
                    self.consoleTemplate.AppendText(os.path.splitext(os.path.basename(pathName))[0] + "\n")
                    newTemplate.json = json.dumps(listTiers)
                    dataw = json.loads(newTemplate.json)
                    objTemplate = list()
                    for d in dataw:
                        objets_internes(d, objTemplate)

                    for o in objTemplate:
                        self.consoleTemplate.AppendText(
                            "\n" + int(o['position']) * '   ' + o['nom'] + " (" + o["stereotype"] + ":"
                            + o['type'] + ")")

                    self.consoleTemplate.AppendText("\n\nTemplate load successfully")
                    self.validateItem.Enable(True)

            except IOError:
                wx.LogError("Cannot open template '%s'." % newTemplate)

    def OnOpen(self, event):
        # Ouverture d'un fichier ELAN
        global pathName
        global listFic
        listFic = []

        self.ClearHelp(event)
        self.console.Clear()
        # enableMenu(self.listMenu)

        with wx.FileDialog(self, "Open file",
                           wildcard="ELAN files (*.eaf;*.EAF)|*.eaf;*.EAF|XML files (*.xml)|*.xml|Flex files (*.flextext)|*.flextext|Toolbox files (*.txt)|*.txt|Wav files (*.wav)|*.wav|Elan parse files (*.eafp)|*.eafp|Toolbox parse files (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathName = fileDialog.GetPath()
            print(pathName)
            # listFic.append(pathName)
            self.console.AppendText("\n" + pathName)
            if pathName.endswith(('.eaf', '.EAF')):
                self.lectureTypesTiers()

    def OpenELANDirectory(self, event):
        # liste les fichiers ELAN d'un répertoire
        global pathName
        global pathDirectory
        global listFic
        global newFile
        listFic = []
        listLiens = []

        self.ClearHelp(event)
        self.console.Clear()
        self.comPanel.Hide()
        self.comPanel2.Hide()

        enableMenu(self.listMenu)
        self.validateItem.Enable(False)

        with wx.DirDialog(None, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathDirectory = dirDialog.GetPath()
            listDirectory = os.listdir(pathDirectory)
            test = ""

            # liste des fichiers ELAN du repertoire
            for f in listDirectory:
                if f.endswith((".eaf",".EAF")):
                    listLiens.append(pathDirectory + os.sep + f)
                    print(f)

            for nom in listLiens:
                pathName = nom
                self.lectureTypesTiers()
                hierarchy.recuperationHierarchy(newFile, pathName)
            # self.console.Clear()
            self.console.AppendText("\n" + pathDirectory + "\n")

    def lectureTypesTiers(self):
        """ Récupère les types et tiers d'un fichier ELAN
        Crée une instance Fic (newFile) et initialise les type et les tiers
        """
        global newFile
        global pathName
        global listFic
        global TS

        try:
            with open(pathName, 'r', encoding='utf8') as file:
                tree = etree.parse(pathName)
                dom = parse(file)
                newFile = Fic(pathName)
                self.readFile(dom)
                #print(newFile.nom)
                self.console.AppendText("\n" + newFile.nom)

                if pathName.endswith((".eaf",".EAF")):
                    console = elanTools.readTypes(newFile, dom)
                    self.console.AppendText(console)

                    console = elanTools.readTiers(newFile, dom, TS)
                    self.console.AppendText(console)
                    enableMenu(self.listMenu)
                    self.validateItem.Enable(False)
                else:
                    disableMenu(self.listMenu)

                newFile.setTree(tree)
                listFic.append(newFile)

        except IOError:
            wx.LogError("Cannot open file '%s'." % newFile)

    def OnAbout(self, event):
        wx.MessageBox("Written by C. Chanard And B. Yildiz April 2020\nchristian.chanard@cnrs.fr", "About ELAN-Tools",
                      wx.OK | wx.ICON_INFORMATION)

    def OnFocus(self, event):
        t = event.GetEventObject()
        t.SetValue("")

    def OnValidate(self, event):
        """ Valide ou non la structure d'un fichier ELAN par rapport à un template (à ouvrir avant) """
        print('OnValidate')
        global listFic
        global newTemplate
        self.consoleTraitement.AppendText("Validation :\n")
        for fic in listFic:
            if fic.json == '':
                # si la commande Hierarchy n'a pas été préalablement demandée
                hierarchy.recuperationHierarchy(newFile, pathName)
            console = validation.validate(fic, newTemplate)
            self.consoleTraitement.AppendText(console)

    def OnHierarchy(self, event):
        global newFile
        global pathName
        information = hierarchy.recuperationHierarchy(newFile, pathName)
        self.console.AppendText(information)

    def EvtHelp(self, event):
        self.helpPanel.Hide()
        self.mainSizer.Fit(self.topPanel)
        self.help()

    def EvtSelectTiers(self, event):
        global listFic
        global delayBool
        global preAl
        self.comPanel.Hide()
        self.comPanel2.Hide()
        self.mainSizer.Fit(self.topPanel)
        bouton = event.GetEventObject().GetLabelText()
        if bouton == 'Align':
            fromAlign = self.textCom1.GetValue()
            print("-" + fromAlign + "-")
            t2 = self.textCom2.GetValue()
            print("t2=" + t2)
            print("-" + fromAlign + "-")
            for fic in listFic:
                console = elanTools.Align(fic, preAl, fromAlign, t2)
                self.console.AppendText(console)
        if bouton == 'create Conll':
            tiers = self.textCom1.GetValue()
            tiers = tiers.replace(",", "")
            tiers = ' '.join(tiers.split())
            # ponctuations séparés par espace
            punctuation = self.textCom2.GetValue()
            punctuation = punctuation.replace(",", "").replace('?', '\?').replace('.', '\\.')
            punctuation = '|'.join(punctuation.split())
            motSeg = self.checkCom2.IsChecked()
            for fic in listFic:
                message = elanTools.Elan2ConllU(fic, tiers, punctuation, motSeg)
                self.consoleTraitement.AppendText("\n\n" + message)


    def doSaveData(self, file):
        pass

    def readFile(self, dom):
        global TS
        ts = []
        timeSlots = dom.getElementsByTagName("TIME_SLOT")
        for TimeSlot in timeSlots:
            slotVal = TimeSlot.getAttribute("TIME_VALUE")
            slotId = TimeSlot.getAttribute("TIME_SLOT_ID")
            TS[slotId] = slotVal
            #print(slotId + " = " + str(slotVal))
        newFile.timeslot = TS
        #print(TS)

class WindowPopup(wx.PopupWindow):
    # pas utilisée
    def __init__(self, parent, style):
        wx.PopupWindow.__init__(self, parent, style)
        p = wx.Panel(self)
        vb1 = wx.BoxSizer(wx.VERTICAL)
        hb2 = wx.BoxSizer(wx.HORIZONTAL)
        t1 = wx.TextCtrl(p, size=(200, 20))
        t1.SetHint("mots@SP1")
        t2 = wx.TextCtrl(p, size=(200, 20))
        t2.SetHint("Tiers à aligner")
        b2 = wx.Button(p, label="Btn1")
        hb2.Add(t2, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        hb2.Add(b2, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

        vb1.Add(t1, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        vb1.Add(hb2, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 0)
        # vb1.Add(b1, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        # self.vb1.Fit(self)
        # self.t2.SetFocus()"""
        p.SetSizer(vb1)
        self.Layout()
        self.Show(True)


def objets_internes(objet_actuel: dict, objets: list):
    """ Ajoute les objets internes à un objet dans une liste, par récurrence.
    Note : la variable "objets" est modifiée par référence, donc on y ajoute
    progressivement des valeurs.
    :param obj objet_actuel : objet dans lequel on cherche des objets internes.
    :param list  objets     : liste dans laquelle on va ajouter les objets internes trouvés.
    """

    # Ajoute le dernier objet à la liste (sans les enfants)
    objets.append({cle: valeur for cle, valeur in objet_actuel.items() if cle != 'enfants'})

    # Condition de sortie : pas d'enfants
    if not 'enfants' in objet_actuel.keys() or not objet_actuel['enfants']:
        return

    for enfant in objet_actuel['enfants']:
        # Rappelle la méthode avec l'enfant comme objet actuel
        objets_internes(enfant, objets)

def disableMenu(menus: list):
    for menu in menus:
        for item in menu.GetMenuItems():
            item.Enable(False)


def enableMenu(menus: list):
    for menu in menus:
        for item in menu.GetMenuItems():
            item.Enable(True)


def enableItem(menus: list, Item):
    for menu in menus:
        for item in menu.GetMenuItems():
            if item.GetItemLabelText() == Item:
                item.Enable(True)


def disableItem(menus: list, Item):
    for menu in menus:
        for item in menu.GetMenuItems():
            if item.GetItemLabelText() == Item:
                item.Disable(False)


if __name__ == "__main__":
    app = App(False)
    app.MainLoop()


class AboutFrame(wx.Frame):
    title = "About this program"

    def __init__(self):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title=self.title)
