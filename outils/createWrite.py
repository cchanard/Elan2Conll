import json
import os


def CreateDirJson(path):
    """ Créer un répertoire stockant les json hierarchique """
    dirJson = path + "/json"
    if not os.path.exists(dirJson):
        try:
            os.mkdir(dirJson)
        except IOError as e:
            print(e.errno)
    return dirJson


def CreateDirNew(path):
    """ Créer un répertoire stockant les fichiers ELAN corrigés """
    dirNew = path + "\\new"
    if not os.path.exists(dirNew):
        try:
            os.mkdir(dirNew)
        except IOError as e:
            print(e.errno)
    return dirNew


def WriteJson(listTiers, File, pathName):
    """ Ecrit le json hierarchique d'un fichier ELAN """
    data = []
    dirJson = CreateDirJson(os.path.dirname(pathName))
    nom = os.path.splitext(os.path.basename(pathName))[0] + '.json'

    with open(dirJson + "\\" + nom, "w") as f:
        for information in listTiers:
            data.append(information)
        f.write(json.dumps(data, indent=4))
    File.addJsonLink(dirJson + "\\" + nom)
