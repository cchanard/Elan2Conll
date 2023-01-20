#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re
import xml.etree.ElementTree as ET

def get_udtags(lem, pos, gloss, all_glosses):
	""" Convert a tuple of (lemma, part-of-speech, gloss) to a UD part-of-speech
	    tag and a list of morphological features """
	tags = ['X', []]
# FIXME maybe, it's better to make a table and read it?
	if lem in [',', '.', '!', '"', ';', ':', '(', ')', '?', '-']:
		return ['PUNCT',[]]
#	print(lem, pos, gloss, all_glosses, file=sys.stderr)
#	part of speech tags
	if pos == 'adj':
		tags[0] = 'ADJ'
	if pos == 'adv':
		tags[0] = 'ADV'
	if pos == 'adv.p':
		tags[0]='ADV'
	if pos == 'adv.ex':
		tags[0] = 'ADV'
	if pos == 'num':
		tags[0] = 'NUM'
	if pos == 'n':
		tags[0] = 'NOUN'
	if pos == 'n.prop':
		tags[0] = 'PROPN'
	if pos == 'v':
		tags[0] = 'VERB'
	if pos == 'vq':
		tags[0] ='VERB'
	if pos == 'ptcp':
		tags[0] ='VERB'
	if pos == 'pers':
		tags[0] = 'PRON'
		tags[1].append('PronType=Prs')
	if pos == 'prn':
		tags[0] = 'PRON'
	if pos == 'pm':
		tags[0] = 'AUX'
	if pos == 'conj' and lem in ["bàri", "jàa", "jàga", "kélen", "kòni", "nká", "nk'", "ô", "ôo", "wô", "tàrí", "tɛ̀rí", "wà", "wáa", "w'", "wálà", "wàlámà", "wàlímà", "wáli", "wó","àni"]:
		tags[0] = 'CCONJ'
	if pos == 'conj' and lem in ["bárì", "bárìsá", "bárì sá", "báwò", "bɛ́ɛ", "bína", "bíɲa", "dàma", "dɔ́rɔn", "jànkó", "jàngó", "kàsɔrɔ", "kàtugu", "kàtuguni", "kɔ́ntɛ̀", "mînkɛ́", "mînkɛ́ni", "ní", "n'ó tɛ́","n'",  "nóntɛ́", "nɔ́ntɛ", "sá", "sábu", "sáabu", "sábi", "sábula", "sàfɛ", "sánì", "sánni", "sán'", "sánn'", "sànkó", "sàngó", "tɛ́sɛ", "tílen", "wálasa", "wáasa", "wálisa", "yáa", "yála", "yálasa", "yáasa", "yála", "yálisa", "jáasa", "yànni", "yànn'", "yàli"]:
		tags[0] = 'SCONJ'
	if pos == 'part' and lem in ["dé", "dún", "dɔ́rɔn"]:
		tags[0] = 'DET'
	if pos == 'cop':
		tags[0] = 'VERB'
	if pos == 'intj':
		tags[0] = 'INTJ'
	if pos == 'onomat':
		tags[0] = 'INTJ'
	if pos == 'pp':
		tags[0] = 'ADP'
	if pos == 'dtm':
		tags[0] = 'DET'
	if pos == 'prt':
		tags[0] = 'PART'
#	then glosses
	if gloss == 'ABR':
		tags[1].append('Abbr=Yes')
	if gloss == 'REL':
		tags[1].append('PronType=Rel')
	if gloss == 'PFV.TR':
		tags[1].append('Aspect=Perf')
		tags[1].append('Valency=2')
		tags[1].append('Polarity=Pos')
	if gloss == 'SBJV':
		tags[1].append('Mood=Sub')
		tags[1].append('Polarity=Pos')
	if gloss == 'REFL':
		tags[1].append('Reflexive=Yes')
	if gloss == 'RECP':
		tags[1].append('PronType=Rcp')
	if gloss == 'EQU':
		tags[1].append('Polarity=Pos')
	if gloss == 'QUAL.NEG':
		tags[1].append('Polarity=Neg')
	if gloss == 'QUAL.AFF':
		tags[1].append('Polarity=Pos')
	if gloss == 'PST':
		tags[1].append('Tense=Past')
	if gloss == 'PROH':
		tags[1].append('Polarity=Neg')
		tags[1].append('Mood=Imp')
	if gloss == 'PROG.NEG':
		tags[1].append('Polarity=Neg')
		tags[1].append('Aspect=Prog')
	if gloss == 'PROG.AFF':
		tags[1].append('Polarity=Pos')
		tags[1].append('Aspect=Prog')
	if gloss == 'PFV.EMPH':
		tags[1].append('Polarity=Pos')
		tags[1].append('Aspect=Perf')
	if gloss == 'PFV.NEG':
		tags[1].append('Polarity=Neg')
		tags[1].append('Aspect=Perf')
	if gloss == 'IPFV.NEG':
		tags[1].append('Polarity=Neg')
		tags[1].append('Aspect=Imp')
	if gloss == 'IPFV.AFF':
		tags[1].append('Polarity=Pos')
		tags[1].append('Aspect=Imp')
	if gloss == 'INFR.NEG':
		tags[1].append('Evident=Infer')
		tags[1].append('Aspect=Perf')
		tags[1].append('Polarity=Neg')
	if gloss == 'INFR':
		tags[1].append('Evident=Infer')
		tags[1].append('Aspect=Perf')
		tags[1].append('Polarity=Pos')
	if gloss == 'IMP':
		tags[1].append('Mood=Imp')
		tags[1].append('Polarity=Pos')
	if gloss == 'FUT.NEG':
		tags[1].append('Polarity=Neg')
		tags[1].append('Tense=Fut')
	if gloss == 'FUT':
		tags[1].append('Tense=Fut')
		tags[1].append('Polarity=Pos')
	if gloss == 'CERT':
		tags[1].append('Tense=Fut')
		tags[1].append('Polarity=Pos')
	if gloss == 'BE':
		tags[1].append('Polarity=Pos')
	if gloss == 'COP.NEG':
		tags[1].append('Polarity=Neg')
	if gloss == 'COND.NEG':
		tags[1].append('Mood=Cnd')
		tags[1].append('Polarity=Neg')
	if gloss == 'COND.AFF':
		tags[1].append('Mood=Cnd')
		tags[1].append('Polarity=Pos')
	if gloss == 'PST':
		tags[1].append('Tense=Past')
	if gloss == 'DEM':
		tags[1].append('PronType=Dem')
		tags[1].append('Definite=Def')
	if gloss == '3SG.EMPH':
		tags[1].append('Number=Sing')
		tags[1].append('Person=3')
		tags[1].append('PronType=Emp')
	if gloss == '2SG.EMPH':
		tags[1].append('Number=Sing')
		tags[1].append('Person=2')
		tags[1].append('PronType=Emp')
	if gloss == '2PL.EMPH':
		tags[1].append('Number=Plur')
		tags[1].append('Person=2')
		tags[1].append('PronType=Emp')
	if gloss == '1SG.EMPH':
		tags[1].append('Number=Sing')
		tags[1].append('Person=1')
		tags[1].append('PronType=Emp')
	if gloss == '1PL.EMPH':
		tags[1].append('Number=Plur')
		tags[1].append('Person=1')
		tags[1].append('PronType=Emp')
	if gloss == '3SG':
		tags[1].append('Number=Sing')
		tags[1].append('Person=3')
	if gloss == '3PL':
		tags[1].append('Number=Plur')
		tags[1].append('Person=3')
	if gloss == '2SG':
		tags[1].append('Number=Sing')
		tags[1].append('Person=2')
	if gloss == '1SG':
		tags[1].append('Number=Sing')
		tags[1].append('Person=1')
	if gloss == '2PL':
		tags[1].append('Number=Plur')
		tags[1].append('Person=2')
	if gloss == '1PL':
		tags[1].append('Number=Plur')
		tags[1].append('Person=1')
#	now mrph
	if 'DEF' in all_glosses:
		tags[1].append('Definite=Def')
	if 'PFV.INTR' in all_glosses:
		tags[1].append('Aspect=Perf')
		tags[1].append('Valency=1')
		tags[1].append('Polarity=Pos')
	if 'PROG' in all_glosses:
		tags[1].append('Aspect=Prog')
	if 'PL2' in all_glosses:
		tags[1].append('Number=Plur')
	if 'OPT2' in all_glosses:
		tags[1].append('Mood=Subj')
		tags[1].append('Polarity=Pos')
	if 'PL' in all_glosses:
		tags[1].append('Number=Plur')
	if 'ART' in all_glosses:
		tags[1].append('Definite=Def')
	if 'PTCP.PRIV' in all_glosses:
		tags[1].append('VerbForm=Part')
	if 'PTCP.RES' in all_glosses:
		tags[1].append('VerbForm=Part')
		tags[1].append('Aspect=Perf')
	if 'PTCP.POT' in all_glosses:
		tags[1].append('VerbForm=Part')
		tags[1].append('Tense=Fut')
	if 'PTCP.PROG' in all_glosses:
		tags[1].append('VerbForm=Part')
		tags[1].append('Aspect=Prog')
	if 'NMLZ' in all_glosses:
		tags[1].append('VerbForm=Vnoun')
	if 'ADJ' in all_glosses:
		tags[1].append('AdjType=Attr')
	if 'ORD' in all_glosses:
		tags[1].append('NumType=Ord')
	if 'CARDINAL' in all_glosses:
		tags[1].append('NumType=Card')
	if 'CAUS' in all_glosses:
		tags[1].append('Voice=Cau')
	if tags[1] == []:
		tags[1] = ['_']
#now two ni
	if lem == "ní́" and 'et' in gloss:
		tags[0] = 'CCONJ'
	if lem == "n'" and 'et' in gloss:
		tags[0] = 'CCONJ'
	if lem == "ní" and 'si' in gloss:
		tags[0] = 'SCONJ'
	if lem == "n'" and 'si' in gloss:
		tags[0] = 'SCONJ'
#	print(tags,file=sys.stderr)

	return tags
def get_val(token, tip, attr):
	""" Return the value of a specific kind of subelement"""
	# .//span[@class="lemma"]
	# .//sub[@class="ps"]
	val = token.findall('.//'+tip+'[@class="'+attr+'"]')
	vals = []
	for v in val:
		vals.append(v.text)
	if len(val) > 0:
		return (val[0].text, vals)
	# FIXME why we return twice the same value? return (vals[0], vals[1:])
	else:
		return ('_', [])

# Load the HTML file
tree = ET.parse(sys.argv[1])
root = tree.getroot()

# Set the token count to 0
count_tok = 0

# Set the document ID to the name of the file
doc_id = sys.argv[1]
# Set the sentence ID to 1
sent_id = 1

def clean_str(s):
	o = s
	o = o.replace('&#65279;', '')
	o = o.replace('﻿', '')
	o = o.replace('\n', ' ')
	o = re.sub('  *', ' ', o)
	return o

# For each of the sentences in the file
for sent in root.findall('.//span[@class="sent"]'):
	# If the sentence has some kind of HTML tag in, skip it.
	# Print out the sentence ID and the original text as a comment
	txt = clean_str(sent.text).strip()
	if txt == '':
		sent_id = sent_id + 1
		continue
	#print('@@', ' '.join([repr(x) +'/'+ str(ord(x)) for x in txt]))
	print('# sent_id = %s:%d' % (doc_id, sent_id))
	print('# text = %s' % (txt))
	tok_id = 1
	# Find all the tokens in the sentence
	tokens = sent.findall(".//span")
	for token in tokens:
		morf = ''
		# What kind of token are we looking at?
		klass = token.attrib["class"]
		# If the token is not punctuation or a word then skip it.
		if klass != 'c' and klass != 'w':
			continue
		# The word form is the contents of the span
		w = clean_str(token.text).strip()
		#print('@@', w, ' '.join([repr(x) +'/'+ str(ord(x)) for x in w]))
		if w == '':
			continue
		# Get the language-specific part-of-speech tag and the gloss
		(xpos, ps) = get_val(token, 'sub', 'ps');
		(gloss, glosses)  = get_val(token, 'sub', 'gloss');
		# If the type of token is punctuation, then the lemma is the
		# same as the surface form
		if klass == 'c':
			lem = w
			gloss = w
		else:
			(lem, lemmes)  = get_val(token, 'span', 'lemma')
			(m, mg) = get_val(token, 'sub', 'gloss')
			morf = morf + ','.join(mg)
		# Get the universal part of speech and list of features
		(upos, feats) = get_udtags(lem, xpos, gloss, glosses);
		# Print out the token line
		if morf.strip() == '' or morf == gloss:
			print('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (tok_id, w, lem, upos, xpos, '|'.join(feats), '_', '_', '_','Gloss='+gloss))
		else:
			print('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (tok_id, w, lem, upos, xpos, '|'.join(feats), '_', '_', '_','Gloss='+gloss+ '|Morf=' + morf))
		# Increment the token id by 1
		tok_id = tok_id + 1
		count_tok = count_tok + 1
	print('')
	sent_id = sent_id + 1

# Print out the number of sentences and tokens as debugging information
print(sent_id, count_tok, file=sys.stderr)
