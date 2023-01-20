#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

global Node

def hierarchy(File, listTiers):
    """ récupère la hierarchie d'un fichier ELAN ou d'un Template """
    independent_tiers = File.getIndepTiers()
    for i in independent_tiers:
        """if i.type.stereotype == "Symbolic_Association":
            stereotype = "SA"
        elif i.type.stereotype == "Symbolic_Subdivision":
            stereotype = "SS"
        else:
            stereotype = "none"
        """
        serialized = {
            "nom": i.nom,
            "type": i.type.nom,
            "position": 0,
            "stereotype": "none",   #stereotype,
            "nb_anns": len(i.anns),
            "parent": "",
            "enfants": []
        }

        getchildrenHierarchy(i, 1, serialized)
        listTiers.append(serialized)


def getchildrenHierarchy(tier, node, parent):
    """ Récupère tous les enfants d'une tier indépendante
        Si il existe des petits-enfants, ils seront récupèrés par récurrence et ainsi de suite
    :param class tier  : le tier independant dont on va récupérer le enfants
    :param int node    : correspond à la position hiérarchique de l'enfant
    :param list parent : les informations du parent y sont stockés
    """
    global Node
    Node = node
    for depTier in tier.children:
        print(depTier.nom)
        if depTier.type.stereotype == "Symbolic_Association":
            stereotype = "SA"
        elif depTier.type.stereotype == "Symbolic_Subdivision":
            stereotype = "SS"
        else:
            stereotype = "none"
        serialized = {
            "nom": depTier.nom,
            "type": depTier.type.nom,
            "position": Node,
            "stereotype": stereotype,
            "nb_anns": len(depTier.anns),
            "parent": parent["nom"],
            "enfants": []
        }
        Node = Node + 1
        getchildrenHierarchy(depTier, Node, serialized)
        parent["enfants"].append(serialized)
    Node = Node - 1

def recuperationHierarchy(newFile, pathName):
    """ Récuperation hiérarchique d'un fichier ELAN """

    #global newFile
    #global pathName
    # global dirJson

    listTiers = []
    hierarchy(newFile, listTiers)
    newFile.addJson(json.dumps(listTiers))

    inf = "{}".format(os.path.splitext(os.path.basename(pathName))[0])
    dataw = json.loads(json.dumps(listTiers))

    objFile = list()
    for d in dataw:
        objets_internes(d, objFile)

    for o in objFile:
        inf = "{}\n {} {} ({}:{}) {}".format(
            inf,
            int(o["position"]) * "   ",
            o["nom"],
            o["stereotype"],
            o["type"],
            o["nb_anns"]
        )
    inf = "{}\n\n".format(inf)
    return inf

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