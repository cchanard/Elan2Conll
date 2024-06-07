- [ELAN2Conll](#elan2conll)
  * [Installation](#installation)
    + [Versions python](#versions-python)
    + [Création d'un environnement virtuel](#cr-ation-d-un-environnement-virtuel)
    + [Activation de l'environnement](#activation-de-l-environnement)
    + [Installation des packages](#installation-des-packages)
    + [Lancement de l'interface graphique](#lancement-de-l-interface-graphique)
  * [Conversion d'Elan à ConllU](#conversion-d-elan---conllu)
  * [Transformation d'un fichier Elan annoté par morphème en un fichier Elan annoté au niveau du mot (cf fichier Gbaya de Paulette)](#transformation-d-un-fichier-elan-annot--par-morph-me-en-un-fichier-elan-annot--au-niveau-du-mot--cf-fichier-gbaya-de-paulette-)
  * [Conversion Toolbox to Elan](#conversion-toolbox-to-elan)
    + [Associer un fichier son au fichier d'annotations Elan](#associer-un-fichier-son-au-fichier-d-annotations-elan)

# ELAN2Conll
## Installation
Le logiciel fonctionne sous windows et linux à condtion de pouvoir installer WxPython sur votre distribution Linux.

### Versions python
Le logiciel a été testé avec les versions 3.7.5 et 3.8.8 de Python.

### Création d'un environnement virtuel
```shell
python -m venv elan2conllenv
```
### Activation de l'environnement
- sous Windows avec PowerShell
```
\elan2conllenv\Script\Activate.ps1
```
- sous Linux
```shell
source activate
```
### Installation des packages
Une fois l'environnement activé, on peut installer les packages nécessaires :

```shell
# sous windows
pip install -r requirements.txt
# Pour Linux, il faudra trouver la wheel adaptée à votre distribution, par exemple :
pip install -U \
    -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04 \
    wxPython
```

### Lancement de l'interface graphique
```
python Elan2Conll.py
```

## Conversion d'Elan à ConllU
- Au lancement du script `Elan2Conll.py`, une interface graphique s'ouvre, intitulée **ELAN Tools**
- Pour **charger un fichier ou un dossier** de fichiers ELAN : `File > Open File (or ELAN Directory)`
- Le ou les fichiers sont analysés et la hiérarchie des tiers est affichée
- Pour **lancer la conversion** : `Command > Convert ELAN to ConllU`. Deux champs texte s'affichent :
  - Le premier est une **liste de noms de tiers par défaut** (`Mft ref tx mot mb ge ps ft`). Il faut la modifier afin qu'elle reflète la hiérarchie des tiers des fichiers que l'on vient de télécharger. **/!\ ATTENTION** : Pour la première tier (*Mft*), c'est celle qui contient le délimiteur de fin de phrase (cela permet de regrouper plusieurs ref en une phrase dans conll). Dans certains fichiers il s'agit en fait de la tier *ft*, avec le point par exemple comme fin de phrase. Dans ce cas, il faut remplacer *Mft* par *ft*. 

	Si un fichier dénommé **listeTiers.txt** se trouve dans le répertoire du ou des fichiers ELAN à convertir, la liste des tiers qu'il contiendra viendra se substituer à la liste par défaut. Cette liste ne devra pas contenir de @SPx, le script se charge de traiter tous les locuteurs (attention, s'il y a plusieurs locuteurs, le fichier ELAN devra contenir la même liste des champs pour chaque locuteur)
  - Le deuxième champ texte est la **liste des marqueurs de "fin de phrase" par défaut**. On le remplacera par le délimiteur utilisé (par ex: §).
      - Un checkbox permet de préciser si le token doit être le **mot ou le morphème** (par défaut)
- Si tout se déroule bien, le ou les fichiers ConllU sont créés dans un répertoire `new` au même niveau que le fichier ou le répertoire de fichiers ELAN.

## Transformation d'un fichier Elan annoté par morphème en un fichier Elan annoté au niveau du mot (cf fichier Gbaya de Paulette)
À partir d'un fichier Toolbox d'origine, lorsque l'on fait la transformation en Conll, on obtient un découpage en morphème (token = morph).

Si l'on veut un fichier Conll dans lequel les tokens sont des mots ou des concaténations de morphèmes, il faut procéder comme suit :

- Cette procédure suppose qu'on a les tiers *mot, mb, ps*. 
- Dans Elan, `Acteur > Copier Acteur > Sélectionner *mb* > Cocher "copier les acteurs dépendants" > Suivant > Sélectionner *mot* (car on veut concaténer tous les morphèmes d'un mot sous le mot) > Suivant > Choisir un type "Symbolic Association" > Terminer`
- Les tiers `mb, ge, rx et ps` sont copiés sous mot avec une extension *-cp*.
- Clic droit sur `mb@sp` et supprimer mb (et ses enfants).
- Renommer les SP-cp en SP en faisant `acteur > modifier les attributs d'acteur`.
- Relancer elan2conll : `File > Open File > Command > Convert Elan2Conll et cocher la case "Token=mot"`.
- Quand on **NE COCHE PAS** l'option `Token=mot`, on obtient des tokens qui sont la concaténation des morphèmes.

**ToDo** : vérifier quel fichier est plus utile dans Arborator.

## Conversion Flex to ElanCorpA
- **Locuteurs** : il faut remplacer tous les préfixes **X_** (ex: A_, B_) par **@SPn** (avec n un chiffre). On peut le faire par chercher-remplacer avec une expression régulière.
- Il faut que la **hiérarchie des tiers** du fichier Flex soit conforme à celle des fichiers ElanCorpA (voir [documentation ELAN-CorpA](https://llacan.cnrs.fr/res_ELAN-CorpA.php))

## Conversion Toolbox to Elan
- En général, la ligne de texte (`\tx` ou `\t`) toolbox correspond à la ligne mot dans Elan. Pas vraiment de ligne phrase et de ligne mot.
- Si on veut ajouter une ligne `mot` (sur le modèle d'Elan-corpA), on duplique la ligne `\tx` (ou \t) dans Toolbox (expression régulière) et on l'appelle `\mot`.
- `Fichier > Importer > Toolbox > choisir le fichier > Set Field Markers (définition à la main des champs)`
  - t : association > change
  - mot : parent = t, subdivition > add
  - m : parent = mot, subdivision > change
  - vérifier les autres 
- Store markers (fichier .mkr) > close
- Cocher : *all markers are unicode*
- Une fois le fichier importé dans Elan, pour avoir la représentation hiérarchique et non plate des tiers : `clic droit sur la partie gauche(avec la liste de tiers) > Sort tiers (trier par acteur) > Sort by hierarchy`
- Si dans la tier `\tx`, les mots sont séparés par plusieurs espaces, il faut normaliser : `Rechercher > 2 espaces ou plus dans \t à remplacer par un seul espace`.
- Nettoyer les mots éventuellement en supprimant les guillemets, points... avec "Rechercher"




