[[_TOC_]]
# ELAN2Conll
## Installation
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
pip install -r requirements.txt
```
## Conversion d'Elan à ConllU
- Au lancement du script `Elan2Conll.py`, une interface graphique s'ouvre, intitulée **ELAN Tools**
- Pour charger un fichier ou un dossier de fichiers ELAN : `File > Open File (or ELAN Directory)`
- Le ou les fichiers sont analysés et la hiérarchie des tiers est affichée
- Pour lancer la conversion : `Command > Convert ELAN to ConllU`. Deux champs texte s'affichent. 
  - Le premier est une liste de noms de tiers par défaut (*Mft ref tx mot mb ge ps ft*). Il faut la modifier afin qu'elle reflète la hiérarchie des tiers des fichiers que l'on vient de télécharger. **/!\ ATTENTION** : Pour la première tier (*Mft*), c'est celle qui correspond au découpage le plus large, dans certains fichiers il s'agit en fait de la tier *ft*. Dans ce cas, il faut remplacer *Mft* par *ft*. 
  - Le deuxième champ texte est la liste des marqueurs de "fin de phrase" par défaut. On le remplacera par le délimiteur utilisé (par ex: §)
  - Un checkbox permet de préciser si le token doit être le mot ou le morphème (par défaut)
- Si tout se déroule bien, le ou les fichiers ConllU sont créés dans un répertoire `new` au même niveau que le fichier ou le répertoire de fichiers ELAN.





