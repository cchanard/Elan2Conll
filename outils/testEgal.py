#!/usr/bin/env python3
annot= "Masta"



gl = annot.split("\\")
if len(gl) > 1:
    print('\\')
    glose = gl[0].strip(' .')
    etiq = gl[1].strip(' .')
elif annot.islower() or annot.istitle() and '-' not in annot and '=' not in annot:
    print('lower, title')
    glose = annot.strip(' .')
    etiq = ''
elif annot == '.' or annot == '?' or annot == '/' or annot == '//' or annot == '!' or annot == '<' or annot == '>':
    print('punct')
    glose = ''
    etiq = 'PUNCT'
else:  # etiquette morph
    print ('autre')
    glose = ''
    etiq = annot.strip(' .')

print('glose='+glose)
if etiq.isupper()  and etiq != 'PUNCT':
    print('etiq='+etiq)

if glose.istitle() and not '-' in glose:
    misc = "ProperName= " + glose + '|'
print("misc="+misc)