from lxml.etree import SubElement


class Fic:
    """ Class contenant les données nécessaires au traitement d'un fichier ELAN
    :param str nom          : nom du fichier ELAN
    :param list tiers       : liste des tiers du fichier ELAN
    :param list types       : liste des types du fichier ELAN
    :param list anns        : liste des annotations du fichier ELAN
    :param str jsonLink     : nom du fichier json hierarchique du fichier ELAN
    :param str json         : json hierarchique du fichier ELAN
    :param ElementTree tree : arborescence du fichier
    :param int speaker      : nombre de participants
    :paraml boolean preAl   : alignement à la tier mot (par exemple) de tiers indep
    """

    def __init__(self, nom):
        self.nom = nom
        self.tiers = []  # classe Tier
        self.types = []  # classe Type
        self.anns = []  # classe Annotation
        self.timeslot = {}  # TIME_SLOT_ID => TIME_VALUE
        self.json = ""
        self.tree = ""
        self.speaker = 0
        self.preAl = False
        self.template = False

    def setTree(self, tree):
        self.tree = tree

    def getTree(self):
        return self.tree

    def addTier(self, tier):
        self.tiers.append(tier)

    def getTierList(self):
        return self.tiers

    def getTierNameList(selfself):
        tList = []
        for Tier in selfself.tiers:
            tList.append(Tier.nom)
        return tList

    def getTier(self, id):
        # retourne l'instance de la Tier id
        for Tier in self.tiers:
            if Tier.nom == id:
                return Tier
        return None

    def setTier(self, identifier, newTier):
        for tier in self.tiers:
            if tier.nom == identifier:
                tier = newTier

    def getTiersOfType(self, type):
        tiersOfType = []
        for tier in self.tiers:
            if tier.type.nom == type and tier not in tiersOfType:
                tiersOfType.append(tier)
        return tiersOfType

    def getAssocTier(self):
        # retourne la liste des tiers de type Association
        assocTier = []
        for Tier in self.tiers:
            if Tier.type.stereotype == "Symbolic_Association":
                assocTier.append(Tier)
        return assocTier

    def getSubdivTier(self):
        # retourne la liste des tiers de type Subdivision
        subdivTier = []
        for Tier in self.tiers:
            if Tier.type.stereotype == "Symbolic_Subdivision":
                subdivTier.append(Tier)
        return subdivTier

    def getIndepTiers(self):
        # retourne la liste des tiers indépendantes
        indepTiers = []
        for tier in self.tiers:
            if tier.type.stereotype == "":
                indepTiers.append(tier)
        return indepTiers

    def getDepTiers(self):
        # retourne la liste des tiers dépendantes
        depTiers = []
        for tier in self.tiers:
            if tier.type.stereotype != "":
                depTiers.append(tier)
        return depTiers

    def addType(self, type):
        self.types.append(type)

    def getType(self, id):
        # retourne l'instance du Type id
        for Type in self.types:
            if Type.nom == id:
                return Type
        return None

    def addAnn(self, annId):
        # ajoute une Annotation dans la liste des annotations
        self.anns.append(annId)

    def getAnnIds(self):
        return self.anns

    def getAnn(self, annId):
        # retourne l'Annotation d'identifiant annId
        for Ann in self.anns:
            if Ann.id == annId:
                return Ann
        return None

    def getAnnRef(self, annRef):
        # retourne l'Annotation parente d'identifiant annRef
        for Ann in self.anns:
            if Ann.id == annRef:
                return Ann
        return None

    def getAnnsChildren(self, TierParent, TierChild):
        # retourne les ann d'une tier enfant
        tierNames = []
        for tier in self.tiers:
            tierNames.append(tier.nom)
        ANN = {}
        if TierParent in tierNames and TierChild in tierNames:
            parentAnns = self.getTier(TierParent).anns
            childAnns = self.getTier(TierChild).anns
            for annP in parentAnns:
                tmp = []
                for annC in childAnns:
                    if annC.ref == annP.id:
                        tmp.append(annC)
                ANN[annP.id] = tmp
        return ANN

    def getAnnChildren(self, ann, TierChild):
        # retourne les ann enfants (de la tier enfant) d'une annotation parent
        # print(TierChild)
        childAnns = self.getTier(TierChild).anns
        ANN = []
        for annC in childAnns:
            if annC.ref == ann:
                ANN.append(annC)
        return (ANN)

    def getIndepParent(self, tier):
        parent = tier.parent
        while parent.type.stereotype != '':
            parent = parent.parent
        return (parent)

    def getAnnotation(self, id):
        tiers = self.tiers
        for tier in tiers:
            anns = tier.anns
            for ann in anns:
                if ann.id == id:
                    return ann
        return False

    def preAlign(self, tnl):
        """
        :param tnl: liste des tiers à traiter
        :return: affecte directement les attributs start et end des instances d'annotations
        """
        # mftSP, refSP, txSP, motSP, mbSP, geSP, psSP, ftSP = tnl
        print("preAlign")
        print(tnl)
        # creation des frontières symboliques des tiers dépendantes
        # tiers enfants en association avec des tiers de référence (ref > tx par exemple)
        print("pré-traitement Align")
        indepTiers = self.getIndepTiers()
        print("indep=" + str(len(indepTiers)))
        for oneTier in indepTiers:
            if oneTier.nom in tnl:
                Type = oneTier.type
                print("type=" + Type.nom + " " + Type.stereotype)
                for childTier in oneTier.children:  # print("child="+childTier.nom)
                    if childTier.type.stereotype == "Symbolic_Association" and childTier.nom in tnl:
                        for Ann in childTier.anns:
                            # AnnRef = newFile.getAnn(Ann.ref)
                            AnnRef = oneTier.getAnnotation(Ann.ref)
                            # print(AnnRef.id + " " + AnnRef.start + " - " + AnnRef.end)
                            Ann.start = AnnRef.start
                            Ann.end = AnnRef.end

        # tiers enfants en association à d'autres tiers
        depTiers = self.getDepTiers()
        subdivTiers = self.getSubdivTier()
        assocTiers = self.getAssocTier()
        for oneTier in depTiers:
            if oneTier.nom in tnl:
                for childTier in oneTier.children:
                    if childTier.nom in tnl:
                        if childTier.type.stereotype == "Symbolic_Association" and len(childTier.anns) > 0:
                            # association
                            print("-------" + oneTier.nom + " Assoc " + childTier.nom)
                            # self.console.AppendText("\n-------" + oneTier.nom + " Assoc " + childTier.nom)
                            for Ann in childTier.anns:
                                # if Ann.tier == oneTier.nom:
                                AnnRef = self.getAnnRef(Ann.ref)
                                ## print(AnnRef.id + " " + "annStart "+AnnRef.start)
                                Ann.start = AnnRef.start
                                Ann.end = AnnRef.end
                        if childTier.type.stereotype == "Symbolic_Subdivision":
                            # subdivision
                            print("-------" + oneTier.nom + " Subdiv " + childTier.nom)
                            # self.console.AppendText("\n\n-------" + oneTier.nom + " Subdiv " + childTier.nom)
                            # print("-----"+childTier.nom + " " + str(len(childTier.anns)))

                            # dictionnaire du nombre de sibling d'un même parent
                            Sibling = {}
                            for Ann1 in childTier.anns:
                                if Ann1.ref in Sibling:
                                    Sibling[Ann1.ref] = Sibling[Ann1.ref] + 1
                                else:
                                    Sibling[Ann1.ref] = 1
                            i = 0
                            annsChildren = childTier.anns
                            while i < len(annsChildren):
                                Ann2 = annsChildren[i]
                                AnnRef = self.getAnnRef(Ann2.ref)
                                # print("======= " + AnnRef.id + " " + AnnRef.start + " - " + AnnRef.end)
                                start = int(AnnRef.start)
                                end = int(AnnRef.end)
                                Start = start
                                nbSibling = Sibling[Ann2.ref]
                                # print(nbSibling)
                                if nbSibling == 1:
                                    # subdivision 1 seul enfant
                                    Ann2.start = str(Start)
                                    Ann2.end = str(end)
                                    # print(str(i + nbSibling) + " " + Ann2.id + "  " + Ann2.start + " - " + Ann2.end)
                                    # self.console.AppendText("\n" + str(i + nbSibling) + " " + Ann.id + "  " + str(Ann.start) + " - " + Ann.end)
                                    i = i + 1
                                else:
                                    # subdivision de la durée du parent entre les enfants
                                    dur = round((end - start) / nbSibling)  # CC 23/12
                                    Start = start
                                    for j in range(nbSibling - 1):
                                        k = i + j
                                        Ann3 = annsChildren[k]
                                        Ann3.start = str(Start)  # .split('.')[0] # CC 23/12
                                        Ann3.end = str(Start + dur)  # .split('.')[0]
                                        # print(str(k) + " " + Ann3.id + "  " + Ann3.start + " - " + Ann3.end)
                                        Start = Start + dur
                                    # dernier item : End = end
                                    i = i + nbSibling - 1
                                    Ann = childTier.anns[i]
                                    Ann.start = str(Start)  # .split('.')[0]
                                    Ann.end = str(end)
                                    # print(str(i) + " " + " " + Ann.id + "  " + Ann.start + " - " + Ann.end)
                                    i = i + 1
        self.preAl = True

    def addJsonLink(self, jsonLink):
        self.jsonLink = jsonLink

    def addJson(self, json):
        self.json = json

    def getJsonLink(self):
        return self.jsonLink

    def getJson(self):
        return self.json

    def getSpeaker(self):
        return self.speaker

    def setSpeaker(self, speaker):
        self.speaker = speaker

    def getTimeSlots(self):
        return self.timeslot


class Template(Fic):
    """ class héritant de Fic représentant un template .etf
    :param str nom : nom du fichier template .etf
    """

    def __init__(self, nom):
        Fic.__init__(self, nom)


class Tier:
    """ Class contenant les données sur une tier
    :param str nom : nom de la tier
    :param str parentId : nom de la tier parent
    :param Tier parent : Tier parent de la tier
    :param parent Type : Type de la tier
    :param str acteur : participant
    :param list anns : liste des Annotations
    :param list children : liste des Tier enfants de la tier
    """

    def __init__(self, nom, parentId, parent, type, acteur, anns):
        self.nom = nom
        self.parentId = parentId
        self.parent = parent
        self.type = type
        self.acteur = acteur
        self.anns = anns
        self.children = []

    def getAnnotation(self, ref):
        # retourne l'Annotation d'identifiant ref de la tier
        for ann in self.anns:
            if ann.id == ref:
                return ann
        return False

    def addChild(self, Tier):
        self.children.append(Tier)

    def setParent(self, Parent):
        self.parent = Parent

    def getAnnsDep(self, annId):
        annsDep = []
        for Ann in self.anns:
            if Ann.ref == annId:
                annsDep.append(Ann)
        return annsDep

    def createElementTier(self, top, tierName, tierType, parentName):
        subElement = SubElement(top, 'TIER')
        subElement.set("DEFAULT_LOCALE", "en")
        subElement.set("LINGUISTIC_TYPE_REF", tierType)
        subElement.set("TIER_ID", tierName)
        if parentName > "":
            subElement.set("PARENT_REF", parentName)
        return subElement

    def createElementRefAnnotation(self, Anns, Tier):
        for ann in Anns:
            annot = SubElement(Tier, "ANNOTATION")
            alAnnot = SubElement(annot, "REF_ANNOTATION")
            alAnnot.set("ANNOTATION_ID", ann.id)
            alAnnot.set("ANNOTATION_REF", ann.ref)
            annVal = SubElement(alAnnot, "ANNOTATION_VALUE")
            annVal.text = ann.value

    def createElementSubAnnotation(self, Anns, Tier):
        annPrev = ""
        annRef = ""
        for ann in Anns:
            annot = SubElement(Tier, "ANNOTATION")
            alAnnot = SubElement(annot, "REF_ANNOTATION")
            alAnnot.set("ANNOTATION_ID", ann.id)
            alAnnot.set("ANNOTATION_REF", ann.ref)
            if ann.ref != annRef:
                annPrev = ann.id
                annRef = ann.ref
            else:
                alAnnot.set("PREVIOUS_ANNOTATION", annPrev)
                annPrev = ann.id
            annVal = SubElement(alAnnot, "ANNOTATION_VALUE")
            annVal.text = ann.value


class Type:
    """ Class contenant les données sur un type
    :param str nom        : nom du type
    :param str align      : type d'alignement (true/false)
    :param str stereotype : stereotype du type
    :param list types     : liste de types
    """

    def __init__(self, nom, align, const):
        self.nom = nom
        self.align = align
        self.stereotype = const
        self.types = []


class Annotation:
    """ Class contenant les données sur une annotation
        :param str id : id de l'annotation
        :param str value : valeur de l'annotation
        :param int ts1   : étiquette de timecode de début
        :param int ts2   : étiquette de timecode de fin
        :param str start : valeur du timecode de début de l'annotation
        :param str end   : valeur du timecode de fin de l'annotation
        :param str ref   : id de l'annotation parente
        :param str tierName : tier à laquelle appartient l'annotation
        :param int nAnn  : numéro d'ordre de l'annotation dans la tier
    """

    def __init__(self, annId, annRef, ts1, ts2, annStart, annEnd, annValue, tierName, nAnn):
        self.id = annId
        self.value = annValue
        self.start = annStart
        self.end = annEnd
        self.ts1 = ts1
        self.ts2 = ts2
        self.ref = annRef
        self.tier = tierName
        self.nAnn = nAnn

    def getSlot(self):
        ts = {}
        ts[self.ts1] = self.start
        ts[self.ts2] = self.end
        return (ts)
