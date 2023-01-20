#!/usr/bin/env python3


import os
import re
from elan.fic import Tier, Annotation, Type
import collections
from xml.dom.minidom import *
from lxml import etree
from outils import createWrite as CW


def findLastId(tree):
    # return last Id (axxax) of a tree
    annRefs = tree.findall('//REF_ANNOTATION')
    refId = []
    for annRef in annRefs:
        ref = annRef.get('ANNOTATION_ID')
        num = re.match("([a-z]+)([0-9]+),ref")
        if num.group(0) == 'ann':  # id provenant du script CopyTier
            continue
        refId.append(int(num.group(1)))
    lastId = max(refId)
    print(refId)
    print(max(refId))
    return int(lastId)


def getAllRefId(tree):
    annRefs = tree.findall('//REF_ANNOTATION')
    refId = []
    for annRef in annRefs:
        ref = annRef.get('ANNOTATION_ID')
        if ref not in refId:
            refId.append(ref)
    refId.sort()
    return refId

def Elan2ConllU(fic, tierNames, Punct, MotSeg):
    """
        converti une liste de fichiers ELAN en fichiers Conll, enregistrés dans un ss-dossier new
        :param listFic = liste des fichiers à traiter
        :param tierNames = liste des tiers. la première est la tier qui contient la traduction libre avec le délimiteur
         d'unités maximales (phrases). Peut être ft si pas de Mft. Puis dans l'ordre :
         reférence, texte, mots, gloses, pos et éventuellement Graid
        :param Punct = délimiteurs d'unités maximales (peut être simplement . ou ; . ou // ...)
        :return = message pour l'affichage sur la console
    """
    # MotSeg = True      # token = mots => MSeg
    # MotSeg = False      # token = morphemes => pas de MSeg
    Symb = ['.', '?', '?//', '?//]', '/', '//', '//]', '//+', '//=', '!', '!//', '!//]', '<', '>', '>+', '[', ']',
            "&//", '{', '}', '|a', '|r', '|c', '||']  # CC 220203
    tierNameListe = tierNames.split()
    print('Elan2ConllU')
    print(tierNameListe)
    print("punct=" + Punct)
    # tierTypeList = (mft, ref, tx, mot, mb, ge, ps, ft)     # print(str(tList)[1:-1])
    message = ''
    print(fic.nom)
    ficAudio = fic.nom.split('\\')[-1][:-3] + "WAV"  # par défaut = nom du fichier
    LNG = ficAudio.split('_')[0]
    # liste des tiers existantes
    tierNameList = fic.getTierNameList()  # print(str(tierNameList)[1:-1])

    # extrait les speakers
    SP = []
    for name in tierNameList:
        if len(name.split('@')) > 1 and name.split('@')[1].strip() not in SP:
            SP.append(name.split('@')[1].strip())
    print(SP)
    errorList = []
    AnnTx = {}
    AnnFt = {}
    REF = []  # liste des (id et valeur) des ref
    tierNameListSP = {}
    MFT = []
    fin = False
    haveGraid = False

    for sp in SP:
        tnl = []
        # vérifie que toutes les tiers demandées existent avec les différents SP
        for t in tierNameListe:
            if t.strip() + "@" + sp not in tierNameList:
                errorList.append(t + "@" + sp)
            else:
                tnl.append(t.strip() + "@" + sp)
        if len(errorList) > 0:
            print('le(s) tier(s) ' + str(errorList)[1:-1] + ' manque(nt) dans le fichier' + fic.nom)
            console = "!!! Le(s) tier(s) " + str(errorList)[1:-1] + " manque(nt) \ndans le fichier" + fic.nom
            fin = True
            break

        print(str(tierNameList)[1:-1])
        tierNameListSP[sp] = tnl
        if len(tnl) == 8:  # 13/03/22
            mftSP, refSP, txSP, motSP, mbSP, geSP, psSP, ftSP = tnl
        else:  # 13/03/22  si tier GRAID à la fin des tiers
            haveGraid = True
            mftSP, refSP, txSP, motSP, mbSP, geSP, psSP, ftSP, GraidSP = tnl

        # affecte des index temporels symboliques aux annotations dépendantes
        # au préalable, fait coïncider les frontières de mFt avec les frontières des mots
        # si mFt de type indépendant => Martine
        # #if not fic.preAl:      // 18/02/22
        fic.preAlign(tnl)

        # les unités maximales provenant de la tier mft. Punct = fin d'une unité
        mftAnns = fic.getTier(mftSP).anns  # print(len(mftAnns))
        txAnns = fic.getTier(txSP).anns  # print(len(txAnns))
        ftAnns = fic.getTier(ftSP).anns  # print(len(ftAnns))

        if len(mftAnns) > 0 and len(txAnns) > 0:
            txtMft = ''     # texte des Mft concaténés   # 17/08/2022 plus utilisé
            #txtMFT = []     # 17/08/2022 plus utilisé
            Start = []      # liste de liste des start des unités Max
            End = []        # liste de liste des end des unités Max
            stop = False    # unité précédente est terminale
            start = mftAnns[0].start
            for mftAnn in mftAnns:  # print(mftAnn.value)
                end = mftAnn.end
                if re.search(Punct, mftAnn.value) is not None:
                    if stop:  # si précédent == délimiteur
                        start = mftAnn.start
                    else:  # si précédent != délimiteur
                        stop = True
                    #txtMft = txtMft + ' ' + mftAnn.value  # concatène les textes de Mft # 17/08/2022 plus utilisé
                    #MFT.append((txtMft.strip(), start, end))  # ces start et end ne sont plus utilisés en sortie = faux après tri
                    Start.append(start)
                    End.append(end)
                    #txtMFT.append(txtMft)
                    #txtMft = ''
                else:
                    if stop:
                        stop = False
                        start = mftAnn.start
                    #txtMft = txtMft + ' ' + mftAnn.value  # print('mft'); print(len(MFT))

            # les ref correspondants aux Start et End des unités max
            print(Start)
            refAnns = fic.getTier(refSP).anns
            # print('ref'); print(len(refAnns))
            annRef = []
            if len(refAnns) > 0:
                Ref = []  # liste des (id et valeur) des ref
                for i in range(len(Start)):  # print(Start[i] + " - " + End[i])
                    annRef = []
                    for refAnn in refAnns:
                        # print(refAnn.start + ' - ' + refAnn.end)
                        if int(refAnn.start) >= int(Start[i]):
                            if int(refAnn.end) <= int(End[i]):
                                #annRef.append((refAnn.id, refAnn.value.replace('.', '_'), txtMFT[i], sp, Start[i], End[i]))
                                annRef.append((refAnn.id, refAnn.value.replace('.', '_'), sp, Start[i], End[i]))
                            else:
                                if len(annRef) > 0:  # ==0 => problème d'alignement
                                    Ref.append(annRef)
                                break
            if len(annRef) > 0:
                Ref.append(annRef)  # un dernier pour la route ! avec ce SP
            REF.append(Ref)
            # dico des id ref vers id tx pour Tx pour établir en sortie la portée des unités Max en terme de ref
            for txAnn in txAnns:
                AnnTx[txAnn.ref] = txAnn.id
            for ftAnn in ftAnns:
                AnnFt[ftAnn.ref] = ftAnn.id
        #print('REF');
        #print(REF)
    # fin des SP
    if fin == True:
        return (console)

    # tri par valeur de ref = ordre tenant compte des tours de parole (après fonction Label)
    ordRef = {}
    for Ref in REF:
        for r in Ref:
            # if len(r) > 0 :                                  # pallier problème d'alignement
            ordRef[r[len(r) - 1][1].split('_')[-1]] = r  # num extrait du label de l'annotation ref
    ordRef = dict(sorted(ordRef.items()))
    REF = []
    for key, value in ordRef.items():
        REF.append(value)
    #print('REF');
    #print(REF)

    # les tx correspondants aux ref
    TXtx = []   # liste de liste des tx concaténés des unités Max
    FTtx = []   # liste de liste des ft concaténés des unités Max
    TXannIds = []  # liste de liste des annId des tx des unités Max

    for Ref in REF:     # pour chaque unité max
        txt = ''
        ft = ''
        TxannId = []  # liste des tx d'une unité Max

        for refIdValue in Ref:  # ensemble des ref d'une unité max : { refAnn.id, refAnn.value, sp, Start[i], End[i] }
            refId = refIdValue[0]
            if refId in AnnTx:
                annTx = fic.getAnn(AnnTx[refId])  # annotation du tx correspondant au ref
                if annTx is not None:
                    txt = txt + ' ' + annTx.value
                    TxannId.append(AnnTx[refId])

                if refId in AnnFt:
                    annFt = fic.getAnn(AnnFt[refId])  # annotation du ft correspondant au ref
                    if annFt is not None:
                        ft = ft + ' ' + annFt.value
        TXtx.append(re.sub(' {2,}', ' ', txt))
        TXannIds.append(TxannId)
        FTtx.append(re.sub(' {2,}', ' ', ft))
        # print('TXtx'); print(re.sub(' {2,}', ' ',txt))

    # les ft correspondants aux ref
    print('free translation')
    ftAnns = []
    for sp, tierNamelist in tierNameListSP.items():
        for tierName in tierNamelist:
            if tierName.startswith('ft'):
                tier = fic.getTier(tierName)
                for anns in tier.anns:
                    ftAnns.append(anns)
    AnnFt = {}
    FT = []
    for ftAnn in ftAnns:
        AnnFt[ftAnn.ref] = ftAnn.id
    for Ref in REF:
        ft = ''
        for refIdValue in Ref:
            refId = refIdValue[0]
            if refId in AnnFt:
                annFt = fic.getAnn(AnnFt[refId])
                if annFt is not None:
                    ft = ft + ' ' + annFt.value
        FT.append(ft)

    # récupère les annotations enfants des tiers parents (dictionnaire) pour chaque SP
    annsTxMot = {}
    annsMotMorph = {}
    annsMorphGe = {}
    annsMorphPs = {}
    annsMorphGraid = {}
    for sp in SP:
        if len(tierNameListSP[sp]) == 8:
            mftSP, refSP, txSP, motSP, mbSP, geSP, psSP, ftSP = tierNameListSP[sp]
        else:  # tier Graid à la fin => Sonja
            mftSP, refSP, txSP, motSP, mbSP, geSP, psSP, ftSP, GraidSP = tierNameListSP[sp]
        anns = fic.getAnnsChildren(txSP, motSP)
        if len(anns) > 0:
            if annsTxMot is None:
                annsTxMot = anns
            else:
                annsTxMot.update(anns)

            annsMb = fic.getAnnsChildren(motSP, mbSP)
            if annsMotMorph is None:
                annsMotMorph = annsMb
            else:
                annsMotMorph.update(annsMb)

            annsGe = fic.getAnnsChildren(mbSP, geSP)
            if annsMorphGe is None:
                annsMorphGe = annsGe
            else:
                annsMorphGe.update(annsGe)

            annsPs = fic.getAnnsChildren(mbSP, psSP)
            if annsMorphPs is None:
                annsMorphPs = annsPs
            else:
                annsMorphPs.update(annsPs)

            if haveGraid:
                annsGraid = fic.getAnnsChildren(mbSP, GraidSP)
                if annsMorphGraid is None:
                    annsMorphGraid = annsGraid
                else:
                    annsMorphGraid.update(annsGraid)

    # les mots correspondant au tx
    MOTanns = []
    TXmots = []
    for Mtx in TXannIds:  # chaque groupe de tx
        nMot = 0
        txMot = ""
        annMot = []
        for idTx in Mtx:  # chaque phrase du groupe
            motsId = annsTxMot[idTx]
            for m in range(len(motsId)):
                nMot = nMot + 1
                valMot = motsId[m].value.replace("|","$")
                if valMot != '':  # 11/03/22 ne tient pas compte des mots vides
                    txMot = txMot + ' ' + valMot
                    annMot.append((motsId[m].id, str(nMot), valMot))  # valMot 16/02/22))
        MOTanns.append(annMot)
        TXmots.append(txMot.strip())
        # print('TXmots'); print(len(TXmots))

    # les morphèmes, gloses, pos associés aux mots
    MORPH = []
    GE = []
    GE2 = []
    LEMME = []
    PS = []
    TXMorph = []
    GLOSE = []
    GRAID = []
    for annsMot in MOTanns:  # ensemble des mots d'une phrase max
        morphTxt = ''
        morphs = []
        morphAnns = []
        lemme = []
        for idMot, nMot, valMot in annsMot:  # chaque mot d'une phrase  //valMot 16/02/22
            morphsId = annsMotMorph[idMot]  # liste des morphId du mot
            if len(morphsId) > 0:  # si pas de morphème enfant : ignorer mot
                for m in range(len(morphsId)):
                    tc1 = morphsId[m].start
                    tc2 = morphsId[m].end
                    valMorph = morphsId[m].value.replace("|","$")
                    lem = re.search('( |^)([^-=]+)( |$)', valMorph)
                    if lem and (lem.group(2).islower() or lem.group(2).istitle()):
                        lemme.append(lem.group(2))
                    # elif morphsId[m].value.islower():
                    #    lemme.append(morphsId[m].value)
                    else:
                        lemme.append('')
                    morphTxt = morphTxt + valMorph + ' '
                    morphs.append((valMorph, tc1, tc2, nMot, valMot))  # valMot 16/02/22
                    morphAnns.append(morphsId[m].id.replace(" ", ""))  # liste des morphID de la phrase max
        MORPH.append(morphs)  # print('morph'); print(len(MORPH))
        TXMorph.append(morphTxt)
        LEMME.append(lemme)
        # les gloses des morphèmes
        ges = []
        gloss = []
        for idMorph in morphAnns:  # chaque morph de la phrase
            if idMorph in annsMorphGe:
                ann = fic.getAnnotation(idMorph)
                if ann.value in Symb:
                    ges.append(ann.value.replace("|","$"))
                    gloss.append('')
                else:
                    if len(annsMorphGe[idMorph]) > 0:
                        gl = re.search('( |^)([^-=]+)( |$)', annsMorphGe[idMorph][0].value)
                        if gl and gl.group(2).islower():
                            gloss.append(gl.group(2))
                        elif annsMorphGe[idMorph][0].value.islower():
                            gloss.append(annsMorphGe[idMorph][0].value)
                        else:
                            gloss.append(annsMorphGe[idMorph][0].value)
                            # gloss.append('')
                        ges.append(annsMorphGe[idMorph][0].value.strip(' .'))
                    else:  # pas de glose
                        ges.append('')
                        gloss.append('')
            else:
                ges.append('')
                gloss.append('')
        GE.append(ges)
        GLOSE.append(gloss)         #print(GLOSE)

        # les catégories
        pss = []
        for idMorph in morphAnns:
            if idMorph in annsMorphPs:  # corrigé annsMorphGe 11/03/22
                ann = fic.getAnnotation(idMorph)
                if ann.value in Symb:
                    pss.append(ann.value)
                else:
                    if len(annsMorphPs[idMorph]) > 0:
                        pss.append(annsMorphPs[idMorph][0].value.strip(' .-='))
                    else:  # pas de ps
                        pss.append('')
            else:
                pss.append('')
        PS.append(pss)  # print('pos'); print(PS[1]); print(TXMorph); exit()

        # les GRAID
        graids = []
        for idMorph in morphAnns:
            if idMorph in annsMorphGraid:
                ann = fic.getAnnotation(idMorph)
                if ann.value in Symb:
                    graids.append(ann.value)
                else:
                    if len(annsMorphGraid[idMorph]) > 0:
                        graids.append(annsMorphGraid[idMorph][0].value.strip(' .-='))
                    else:  # pas de ps
                        graids.append('')
            else:
                graids.append('')
        GRAID.append(graids)  # print('pos'); print(PS[1]); print(TXMorph); exit()

    """print("MORPH")
    print(MORPH)
    print("GLOSE")
    print(GLOSE)
    print("LEMME")
    print("PS")
    print(PS)
    print("GRAID")
    print(GRAID)
    # print(LEMME)
    """

    # Enregistre conll
    out = ''
    for t in range(len(TXtx)):
        # refAnn.id, refAnn.value.replace('.', '_'), sp, Start[i], End[i]
        refNum = REF[t][0][1] + '-' + REF[t][len(REF[t]) - 1][1].split('_')[-1]
        # txtMft = REF[t][0][2]  # 17/08/2022 plus utilisé
        sp = REF[t][0][2]
        start = REF[t][0][3]  # start de la première phrase du groupe
        end = REF[t][len(REF[t]) - 1][4]  # end de la dernière phrase du groupe

        out = out + "# sent_id = " + refNum + "\n"
        out = out + "# speaker_id = " + sp + "\n"
        out = out + "# sound_url = https://corporan.huma-num.fr/Archives/media/" + LNG + "/WAV/" + ficAudio + '\n'
        out = out + "# sent_timecode = " + start + ", " + end + '\n'
        # out = out + "# text = " + TXtx[t] + "\n"               # liste des ann.value de la tier mot
        out = out + "# phonetic_text = " + ''.join(TXMorph[t]) + "\n"  # liste des ann.value de la tier morph
        out = out + "# text = " + TXmots[t] + "\n"
        #out = out + "# text_en = " + FT[t] + "\n"
        out = out + "# text_en = " + FTtx[t] + "\n"  # 17/08/2022 pour traiter cas où Mft = tx
        #out = out + "# text_en = " + txtMft.strip('§') + "\n"  # 17/08/2022 plus utilisé
        for m in range(len(MORPH[t])):
            if MotSeg:  # 16/02/22 => Natalia
                MSeg = "|MSeg=" + MORPH[t][m][0].replace(' ', '')
            else:
                MSeg = ''
            lemme = LEMME[t][m]
            if GLOSE[t][m] != '':  # valeur du lemme
                # Mglose = "|MGloss=" + GLOSE[t][m].strip()
                gloss = "|Gloss=" + GLOSE[t][m].strip()
            else:
                # Mglose = ''
                gloss = ""
            misc = "AlignBegin=" + MORPH[t][m][1] + "|AlignEnd=" + MORPH[t][m][2] + "|nWord=" + MORPH[t][m][3]
            # misc = misc + gloss        # on utilise plutôt Etiq_Glose(GE)
            misc = misc + MSeg
            glose, etiq, TypeToken, Position = Etiq_Glose(GE[t][m])
            pos = PS[t][m].replace('.', '].[')
            # pos = pos.replace('-', '].[')
            # pos = '[' + pos.replace('=', '].[') + ']'.replace("|","$")
            pos = '[' + pos.replace("|", "$") + ']'
            graid = GRAID[t][m]
            # misc = misc + Mglose
            if glose.islower():     # mot
                misc = misc + "|GE=" + glose.replace("|", "$")
                gloss = "|Gloss=" + glose
            elif glose != '':       # étiquette
                misc = misc + "|GE=" + '[' + glose.replace('.', '].[').replace("|", "$") + ']'
                # misc = misc + "|MGloss=" + glose.replace("|", "$") + ']'
                # glose = "Gloss=" + glose
            # TokenType
            if TypeToken:
                misc = misc + "|TypeToken=" + TypeToken
            if Position:
                misc = misc + "|Position=" + Position
            if etiq != '':  # and etiq.isupper():                   # étiquette gramm. dans glose
                # misc = misc + "|GE=" + etiq #+ '[' + etiq.replace('.', '].[') + ']'
                misc = misc + '|RX=' + pos.upper()
            elif (PS[t][m] != '' and PS[t][m] not in Symb):  # pas d'étiquette gram. dans glose'
                misc = misc + '|RX=' + pos.upper()
            if (graid != '' and graid not in Symb):  # pas d'étiquette gram. dans glose'
                graid = '[' + graid.replace(':', ']:[') + ']'
                misc = misc + '|GRAID=' + graid

            misc = misc.replace('[-', '-[').replace('[=', '=[').replace('-]', ']-').replace('=]', ']=')
            # out = out + str(m+1) + "\t" + MORPH[t][m][0] + "\t_\t_\t" + PS[t][m] + "\t" + glose + etiq + "\t_\t_\t_\t" + misc + '\n'
            # out = out + str(m+1) + "\t" + MORPH[t][m][0] + "\t_\t" + PS[t][m].upper() + "\t_\tGloss=" + GE[t][m].replace("|","$") + "\t_\t_\t_\t" + misc + '\n'
            if MotSeg:
                token = MORPH[t][m][4]
            else:
                token = MORPH[t][m][0]
            """out = out + str(m + 1) + "\t" + token + "\t" + lemme + "\t" + PS[t][m].upper() + "\t_\tMGloss=" + GE[t][
                m].replace("|", "$") + "\t_\t_\t_\t" + misc + '\n'"""
            out = out + str(m + 1) + "\t" + token + "\t" + lemme + "\t" + PS[t][m].upper() + "\t_\tGloss=" + GE[t][
                m] + "\t_\t_\t_\t" + misc + '\n'

        out = out + '\n'
    print(out)
    ficName = os.path.basename(fic.nom)
    dirNew = CW.CreateDirNew(os.path.dirname(fic.nom))
    ficOut = dirNew + os.sep + ficName[0:-4] + ".conll"
    f = open(ficOut, "w", encoding='utf8')
    f.write(out)
    f.close()
    message = message + "Fichier " + ficName[0:-4] + ".conll \nengistré dans le dossier " + dirNew
    print(message)
    return (message)


def Etiq_Glose(annot):
    PUNCT = ['.', '?', '?//', '?//]', '/', '//', '//]', '//+', '//=', '!', '!//', '!//]', '<', '>', '>+', '[', ']',
             "&//", '{', '}', '|a', '|r', '|c', '||']  # CC 220203
    sep = ["-", "=", "_"]
    glose, etiq, TypeToken, Position = "", "", "", ""
    gl = annot.split("\\")
    if len(gl) > 1:
        glose = gl[0]  # .strip(' .-=')
        etiq = gl[1]  # .strip(' .-=')
        TypeToken = "stem"
    # elif annot[0:].isupper and annot[1:].islower() and '-' not in annot and '=' not in annot:     # nom propre
    # glose = annot.strip(' .-=')
    # TypeToken = "Stem"
    elif annot[0:].islower:
        glose = annot.strip(' .-=')
    elif annot in PUNCT:
        TypeToken = "PUNCT"
    elif annot != "":  # etiquette morph
        if annot[0:1] == "-":
            TypeToken = "DerAff"
            Position = "Post"
        elif annot[-1] == "-":
            TypeToken = "DerAff"
            Position = "Pre"
        elif annot[0:1] == "-" and annot[-1] == "-":
            TypeToken = "InfAff"
        elif annot[0:1] == "=":
            TypeToken = "Clitic"
            Position = "Post"
        elif annot[-1] == "=":
            TypeToken = "Clitic"
            Position = "Pre"
        elif annot[0:1] not in sep and annot[-1] not in sep:  # pas affixe
            TypeToken = "Stem"
        etiq = annot  # .strip(' .-=')
    if etiq != '':
        etiq = etiq.replace('.', '].[')
        etiq = etiq.replace('-', '].[')
        etiq = '[' + etiq.replace('=', '].[') + ']'
    return (glose, etiq, TypeToken, Position)


def LabelRef(listFic):
    """ Change les ANNOTATION_VALUE pour la tier ref sur la base du nom du fichier """
    print("AnnotationRef\n\n")
    for fic in listFic:
        nomFic = os.path.splitext(os.path.basename(fic.nom))[0]
        cpt = 1
        tree = fic.getTree()
        # rechercher toutes les tiers de type 'ref'
        refTiers = fic.getTiersOfType('ref')
        print(len(refTiers))
        refAnnStart = []
        for tier in refTiers:
            if (tier.nom.startswith('ref')):
                print(tier.nom)
                for ann in tier.anns:
                    refAnnStart.append(([int(ann.start)], ann.id))
        # trier par start
        refAnnStart = sorted(refAnnStart, key=lambda id: id[0])
        print(refAnnStart)

        # affecter les label et number
        cpt = 1
        for start, id in refAnnStart:
            path = "/ANNOTATION_DOCUMENT/TIER/ANNOTATION/ALIGNABLE_ANNOTATION[@ANNOTATION_ID='" + id + "']/ANNOTATION_VALUE"  # print(path)
            for alignable in tree.xpath(path):
                label = nomFic + '_' + "{:03d}".format(cpt)  # print(label)
                alignable.text = label
                cpt = cpt + 1
        print('Enregistrer les fichiers par : File Save As')


def readTypes(newFile, dom):
    """ Crée la liste des Type de l'instance Fic (newFile) """
    console = "\nListe des types"
    types = dom.getElementsByTagName('LINGUISTIC_TYPE')
    Types = []
    for type in types:
        typeId = type.getAttribute('LINGUISTIC_TYPE_ID')
        align = type.getAttribute('TIME_ALIGNABLE')
        stereotype = type.getAttribute('CONSTRAINTS')
        newType = Type(typeId, align, stereotype)
        Types.append(newType)
        if type.getAttribute('TIME_ALIGNABLE') == 'true':
            console = console + "\n" + typeId + " = independant"
            print("independant = " + typeId)
        else:
            print("dependant = " + typeId)
            console = console + "\n" + typeId + " = dependant"
    newFile.types = Types
    console = console + "\nnombre de types = " + str(len(newFile.types))
    return (console)


def readTiers(newFile, dom, TS):
    """ Crée la liste des Tiers de l'instance Fic (newFile)
        Crée la liste des Annotation de chaque Tier
    """
    AnnIds = {}  # CC 030521  liste des id d'annotation
    AnnIdRefs = {}  # CC 030521 liste des idRef
    refId = True  # CC 030521 liste des idRef
    console = "\n\nHiérarchie des Tiers"
    tiers = dom.getElementsByTagName('TIER')
    for tier in tiers:
        parentTier = None
        type = tier.getAttribute('LINGUISTIC_TYPE_REF')
        Type = newFile.getType(type)
        tierName = tier.getAttribute('TIER_ID')
        acteur = tier.getAttribute('PARTICIPANT')
        parentName = tier.getAttribute('PARENT_REF')
        console = console + "\n" + tierName + "\t<\t" + parentName
        print(tierName + "\t<\t" + parentName)

        # Initialisation des éléments des tier alignables
        alAnns = tier.getElementsByTagName('ALIGNABLE_ANNOTATION')
        if alAnns:
            Ann = []
            nAnn = 1
            for a in range(len(alAnns)):
                id = alAnns[a].getAttribute('ANNOTATION_ID')
                if id not in AnnIds:
                    AnnIds[id] = 1
                else:
                    AnnIds[id] = AnnIds[id] + 1
                # ts1[id] = alAnns[a].getAttribute('TIME_SLOT_REF1')
                # ts2[id] = alAnns[a].getAttribute('TIME_SLOT_REF2')
                ts1 = alAnns[a].getAttribute('TIME_SLOT_REF1')
                ts2 = alAnns[a].getAttribute('TIME_SLOT_REF2')
                if ts1 not in TS:
                    print("   !!! " + ts1 + " is not a valid timeslot")
                    console = console + "\n!!! " + ts1 + " is not a valid timeslot"
                    break
                if ts2 not in TS:
                    print("   !!! " + ts2 + " is not a valid timeslot")
                    console = console + "\n!!! " + ts2 + " is not a valid timeslot"
                    break
                annots = alAnns[a].getElementsByTagName('ANNOTATION_VALUE')
                if annots[0].firstChild is not None:
                    valeur = annots[0].firstChild.nodeValue
                else:
                    valeur = ""
                # nouvelle instance d'annotation
                # newAnn = Annotation(id, "", ts1[id], ts2[id], TS[ts1[id]], TS[ts2[id]], valeur[id], tierName, str(nAnn))
                newAnn = Annotation(id, "", ts1, ts2, TS[ts1], TS[ts2], valeur, tierName, str(nAnn))
                # print("id= " + id + " " + valeur + " " + str(TS[ts1]) + " " + str(TS[ts2]))
                Ann.append(newAnn)
                newFile.anns.append(newAnn)
                nAnn = nAnn + 1
        else:
            # initialisation  des tier dépendantes
            depAnns = tier.getElementsByTagName('REF_ANNOTATION')
            Ann = []
            nAnn = 1
            for a in range(len(depAnns)):
                id = depAnns[a].getAttribute('ANNOTATION_ID')
                ref = depAnns[a].getAttribute('ANNOTATION_REF')
                if id not in AnnIds:
                    AnnIds[id] = 1
                else:
                    AnnIds[id] = AnnIds[id] + 1
                if ref not in AnnIdRefs:
                    AnnIdRefs[ref] = 1
                else:
                    AnnIdRefs[ref] = AnnIdRefs[ref] + 1
                annots = depAnns[a].getElementsByTagName('ANNOTATION_VALUE')
                if annots[0].firstChild is not None:
                    valeur = annots[0].firstChild.nodeValue
                else:
                    valeur = ""
                # nouvelle instance d'annotation
                newAnn = Annotation(id, ref, "", "", "", "", valeur, tierName, str(nAnn))
                Ann.append(newAnn)
                # ajout de l'ann dans la liste des ann de la classe Fic
                newFile.anns.append(newAnn)
                nAnn = nAnn + 1
        # crée l'instance Tier
        newTier = Tier(tierName, parentName, parentTier, Type, acteur, Ann)
        newFile.addTier(newTier)

    # attribution du parent de chaque enfant
    for tier in newFile.getDepTiers():
        parentTier = newFile.getTier(tier.parentId)
        tier.setParent(parentTier)
        print(tier.nom + "\t<\t" + parentTier.nom)
        newFile.setTier(tier.nom, tier)  # met à jour dans Fic

    # recherche des enfants de chaque tier
    for tier in newFile.tiers:
        parentTier = tier.parent
        if parentTier is not None:
            print("parent=" + parentTier.nom)
            parentTier.addChild(tier)
            newFile.setTier(parentTier.nom, parentTier)  # met à jour dans Fic

    # controle annRef pointe vers un annId existant dans la tier parent  // 040521
    for tier in newFile.getDepTiers():
        parentTier = tier.parent
        annsParent = parentTier.anns
        print(tier.nom + "\t<\t" + parentTier.nom)
        for ann in tier.anns:
            if newFile.getAnnRef(ann.ref) not in annsParent:
                print("  !!! the annRef " + ann.ref + " is not a valid annId or is missing")
                console = console + "\n!!! the annRef " + ann.ref + " is not a valid annId or is missing"
                refId = False
                print(annsParent)
                break
    if refId:
        print("Id references OK")
        console = console + "\nRefIds : OK"
    console = console + "\nnombre de tiers = " + str(len(newFile.tiers)) + "\n\n"
    print(console)
    return console


def Align(fic, preAl, fromAlign, t2):
    """ recherche les TimeCode des tier alignable et vérifie si les frontières correspondent entre elles
    Si une frontière d'une tier est à une distance différente de epsilon de la frontière d'une autre tier,
     => faire en sorte qu'elles soient identiques
     """
    epsilon = 50
    toAlign = t2.split(",")
    console = "\n\nAlign : "
    # pré-traitement pour affecter aux annotations des index temoporels
    # if not fic in preAl:
    fic.preAlign()
    # preAl.append(fic)
    console = console + "\nAlignement du fichier " + fic.nom
    tree = fic.getTree()
    M = fic.getTier(fromAlign)
    Start = [];
    End = [];
    Value = []
    Id = []
    for a in range(0, len(M.anns) - 1):
        Start.append(M.anns[a].start)
        End.append(M.anns[a].end)
        Value.append(M.anns[a].value)
        # print(" start=" + M.anns[a].start + " end=" + M.anns[a].end)
    print(Value, Start, End)
    # traitement des tier à aligner
    print("toAlign= " + str(len(toAlign)))
    for T in toAlign:
        print("Align " + T)
        RP = fic.getTier(T.strip())
        print("-------" + RP.nom + "-------" + str(len(RP.anns)))
        console = console + "\nAlignement de " + RP.nom + " sur la tier des mots"
        for a in range(len(RP.anns)):
            start = RP.anns[a].start
            end = RP.anns[a].end
            nAnn = RP.anns[a].nAnn
            # print("st=" + start + " fin=" + end)
            annId = RP.anns[a].id
            ts1 = RP.anns[a].ts1
            ts2 = RP.anns[a].ts2

            for s in range(len(Start)):
                if abs(int(start) - int(Start[s])) < epsilon and abs(int(start) - int(Start[s])) > 1:
                    # print(annId + " startRP > " + ts1 + " " + start + " Mot " + Start[s])
                    # remplacement de la valeur du TS1 de RP
                    path = "/ANNOTATION_DOCUMENT/TIME_ORDER/TIME_SLOT[@TIME_SLOT_ID='" + ts1 + "']"

                    for Ts1 in tree.xpath(path):
                        """point = Start[s].index('.')
                        if point > 2:
                            debut = Start[s][0:point]"""
                        debut = Start[s]
                        print("ts1=" + Ts1.get("TIME_VALUE") + " replaced by " + debut)
                        console = console + "\n" + RP.nom + "-" + nAnn + " start= " + Ts1.get(
                            "TIME_VALUE") + " replaced by " + debut
                        Ts1.set('TIME_VALUE', debut)
            for s in range(len(End)):
                if abs(int(end) - int(End[s])) < epsilon and abs(int(end) - int(End[s])) > 1:
                    # print(annId + " endRP > " + ts2 + " " + end + " Mot " + End[s])
                    # remplacement de la valeur du TS2 de RP
                    path = "/ANNOTATION_DOCUMENT/TIME_ORDER/TIME_SLOT[@TIME_SLOT_ID='" + ts2 + "']"
                    for Ts2 in tree.xpath(path):
                        """point = End[s].index('.')
                        if point > 2:
                            fin = End[s][0:point]"""
                        fin = End[s]
                        print("ts2=" + Ts2.get("TIME_VALUE") + " replaced by " + fin)
                        console = console + "\n" + RP.nom + "-" + nAnn + " end=" + Ts2.get(
                            "TIME_VALUE") + " replaced by " + fin
                        Ts2.set('TIME_VALUE', fin)

    dirNew = CW.CreateDirNew(os.path.dirname(fic.nom))
    nom = os.path.splitext(os.path.basename(fic.nom))[0] + '_align' + '.eaf'
    path = dirNew + "\\" + nom
    tree = fic.getTree()
    with open(path, "w") as f:
        tree.write(path, encoding="UTF-8", xml_declaration=True)
    console = console + "\n\n"
    return (console)
