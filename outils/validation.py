#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from outils import validation, hierarchy

def presence_SS_SA(objFile: list):
    """ Teste la présence des stereotypes : Symbolic_Association et Symbolic_Subdivision
    :param liste objFile : liste contenant tous les objets du fichier Elan à tester
    """
    SA = False
    SS = False
    for o in objFile:
        if SA and SS:
            break
        elif o["stereotype"] == "SA":
            SA = True
        elif o["stereotype"] == "SS":
            SS = True
    if SA and SS:
        return True
    else:
        return False

def presence_tiers(objFile: list, objTemplate: list):
    """ Teste la présence des tiers d'un fichier Elan en fonction des tiers d'un Template référence
    :param list objFile : liste contenant tous les objets du fichier Elan à tester
    :param list objTemplate : liste contenant tout les objets du Template de référence
    """

    tiersTemplate = []
    results = []

    for o in objTemplate:
        tiersTemplate.append(o["nom"].split("@")[0])

    for o in objFile:
        if o["nom"].split("@")[0] in tiersTemplate:
            tiersTemplate.remove(o["nom"].split("@")[0])

    if len(tiersTemplate) == 0:
        results.append(True)
        return results
    else:
        results.append(False)
        results.append(tiersTemplate)
        return results

def presence_types(objFile: list, objTemplate: list):
    """ Teste la présence des types d'un un fichier Elan en fonction des types d'un Template référence
     en incluant les stereotypes de ces derniers
    :param list objFile     : liste contenant tout les objets du fichier Elan à tester
    :param list objTemplate : liste contenant tout les objets du Template de référence
    """
    typeTemplate = []
    results = []
    for o in objTemplate:
        t = [o["type"], o["stereotype"]]
        typeTemplate.append(t)

    for o in objFile:
        test = [o["type"], o["stereotype"]]
        if test in typeTemplate:
            typeTemplate.remove(test)

    if len(typeTemplate) == 0:
        results.append(True)
        return results
    else:
        results.append(False)
        results.append(typeTemplate)
        return results

def test_hierarchie(objFile: list, objTemplate: list):
    """ Teste la hierarchie d'un fichier Elan en fonction d'un Template de référence
    :param list objFile     : liste contenant tout les objets du fichier Elan à tester
    :param list objTemplate : liste contenant tout les objets du Template de référence
    """
    results = []
    test_Template = []

    if len(objFile) < len(objTemplate):
        results.append(False)
        return results

    for o in objTemplate:
        temp = [o['stereotype'], o['position'], o['parent'].split("@")[0]]
        test_Template.append(temp)

    for o in objFile:
        temp = [o['stereotype'], o['position'], o['parent'].split("@")[0]]
        if temp in test_Template:
            test_Template.remove(temp)

    if len(test_Template) == 0:
        results.append(True)
        return results
    else:
        results.append(False)
        results.append(test_Template)
        return results

def validate(fic, newTemplate):
    dataTemplate = json.loads(newTemplate.json)
    dataFile = json.loads(fic.json)

    objFile = list()
    objTemplate = list()

    console = fic.nom + "\n"
    console = console + fic.nom + "\n"

    for o in dataFile:
        hierarchy.objets_internes(o, objFile)

    for o in dataTemplate:
        hierarchy.objets_internes(o, objTemplate)

    if not validation.presence_SS_SA(objFile):
        console = console + "SA and SS are missingK\n"
        console = console + "SA and SS are missingK\n"

    test = validation.presence_tiers(objFile, objTemplate)

    if test[0]:
        console = console + "tiers are OK"
        console = console + "tiers are OK"
    else:
        console = console + "tiers are missing:"
        console = console + "tiers are missing:"
        for s in test[1]:
            console = console + "   - " + s

    test = validation.presence_types(objFile, objTemplate)

    if test[0]:
        console = console + "\ntypes are OK"
    else:
        console = console + "\ntypes are missing:"
        for s in test[1]:
            console = console + "   - " + s[0] + ":" + s[1]

    test = validation.test_hierarchie(objFile, objTemplate)

    if test[0]:
        console = console + "\nHierarchy is ok\n\n"
    else:
        if len(test) == 1:
            console = console + "\nNot enough tiers to test hierarchy\n\n"
        else:
            console = console + "\nMissing in hierarchy : "
            for i in test[1]:
                console = console + "  - " + i[0] + " " + str(i[1]) + " " + i[2]
            console = console + "\n\n"
    return(console)