import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import pickle
from collections import Iterable
from nltk.tag import ClassifierBasedTagger
from nltk.chunk import ChunkParserI
from nltk.chunk import conlltags2tree, tree2conlltags

GLOBAL_INDEX = 0

# init the stemmer
stemmer = StemmerFactory().create_stemmer()

def features(tokens, index, history):
	global GLOBAL_INDEX

	if(index == 0):
		GLOBAL_INDEX += 1
		print "kalimat ke- ", GLOBAL_INDEX

	"""
	`tokens`  = a POS-tagged sentence [(w1, t1), ...]
	`index`   = the index of the token we want to extract features for
	`history` = the previous predicted IOB tags
	"""

	# Pad the sequence with placeholders
	tokens = [('[START2]', '[START2]'), ('[START1]', '[START1]')] + list(tokens) + [('[END1]', '[END1]'), ('[END2]', '[END2]')]
	history = ['[START2]', '[START1]'] + list(history)

	# shift the index with 2, to accommodate the padding
	index += 2

	word, pos = tokens[index]
	prevword, prevpos = tokens[index - 1]
	prevprevword, prevprevpos = tokens[index - 2]
	nextword, nextpos = tokens[index + 1]
	nextnextword, nextnextpos = tokens[index + 2]
	previob = history[index - 1]
	contains_dash = '-' in word
	contains_dot = '.' in word
	allascii = all([True for c in word if c in string.ascii_lowercase])

	allcaps = word == word.capitalize()
	capitalized = word[0] in string.ascii_uppercase

	prevallcaps = prevword == prevword.capitalize()
	prevcapitalized = prevword[0] in string.ascii_uppercase

	nextallcaps = prevword == prevword.capitalize()
	nextcapitalized = prevword[0] in string.ascii_uppercase

	return {
		'word': word,
		'lemma': stemmer.stem(word),
		'pos': pos,
		'all-ascii': allascii,

		'next-word': nextword,
		'next-lemma': stemmer.stem(nextword),
		'next-pos': nextpos,

		'next-next-word': nextnextword,
		'nextnextpos': nextnextpos,

		'prev-word': prevword,
		'prev-lemma': stemmer.stem(prevword),
		'prev-pos': prevpos,

		'prev-prev-word': prevprevword,
		'prev-prev-pos': prevprevpos,

		'prev-iob': previob,

		'contains-dash': contains_dash,
		'contains-dot': contains_dot,

		'all-caps': allcaps,
		'capitalized': capitalized,

		'prev-all-caps': prevallcaps,
		'prev-capitalized': prevcapitalized,

		'next-all-caps': nextallcaps,
		'next-capitalized': nextcapitalized,
	}

class NamedEntityChunker(ChunkParserI):
	def __init__(self, train_sents, **kwargs):
		assert isinstance(train_sents, Iterable)
 
		self.feature_detector = features
		self.tagger = ClassifierBasedTagger(
			train=train_sents,
			feature_detector=features,
			**kwargs)
 
	def parse(self, tagged_sent):
		chunks = self.tagger.tag(tagged_sent)
 
		# Transform the result from [((w1, t1), iob1), ...] 
		# to the preferred list of triplets format [(w1, t1, iob1), ...]
		iob_triplets = [(w, t, c) for ((w, t), c) in chunks]
 
		# Transform the list of triplets to nltk.Tree format
		return conlltags2tree(iob_triplets)

"""
Preproses dari format data korpus Name Entity Tag berbeda 
dan melakukan POS Tagger
"""
import re
from nltk.tag import CRFTagger
try:
	import pycrfsuite
except ImportError:
	pass
	print "ga ketemu"

MAP_ENTITY_TAG = {
	"ORGANIZATION": "org",
	"LOCATION": "loc",
	"PERSON": "per"
}

TAGGER3 = CRFTagger()
TAGGER3.set_model_file('data/all_indo_man_tag_corpus_model.crf.tagger')

def getPOSTag(_temporary_tokens):
	strin = []
	for token_tag in _temporary_tokens:
		strin.append(unicode(token_tag[0].decode('utf-8')))

	return [(token.encode('ascii','ignore'), tag.encode('ascii','ignore')) for (token, tag) in TAGGER3.tag_sents([strin])[0]]

def parseEntityName(_sent):
	def getTypeData(_ne):
		"""
		ekstrak jenis Name Entity
		"""
		l_regex = re.compile(r"\<ENAMEX\s+TYPE\=\"")
		r_regex = re.compile(r"\"\>[^<]+\<\/ENAMEX\>")
		a = r_regex.sub(r'\0', l_regex.sub(r'\0', _ne))

		"""
		ekstrak data Name Entity
		"""
		r = re.compile(r"\<ENAMEX\s+TYPE\=\"\w+\"\>")
		s = re.compile(r"\<\/ENAMEX\>")
		b = s.sub(r'\0', r.sub(r'\0', _ne))

		"""
		Hapus karakter bukan alfabet dari jenis Name Entity
		"""
		return re.sub(r'[^\w]', '', a), b


	"""
	semua NE Tag yang ada pada kalimat
	"""
	temporary_tokens = []
	entities_name = re.findall(r"\<ENAMEX\s+TYPE\=\"\w+\"\>[^<]+\<\/ENAMEX\>", _sent)

	temp = []
	for entity_name in entities_name:
		
		"""
		mengambil jenis dan data Name Entity, misal
		('ORGANIZATION', 'Telkon Indonesia')
		"""
		ne_type, ne_data = getTypeData(entity_name)

		"""
		split kalimat menggunakan satu NE pertama ditemukan
		"""
		temp = _sent.strip().split(entity_name, 1)

		"""
		data dibagian kiri dijadikan token dan di set tanda O
		"""
		if temp[0]:
			for token in temp[0].strip().split(' '):
				word = token.replace('\x00', '')
				if word:
					temporary_tokens.append((word, 'O'))
		
		"""
		data Name Entity dipisah menjadi token
		"""
		ne_data_split = ne_data.strip().split(' ')

		"""
		token data Name Entity pertama di set tanda B
		"""
		wordx = ne_data_split[0].replace('\x00', '')
		if wordx:
			temporary_tokens.append((wordx, "B-" + MAP_ENTITY_TAG[ne_type.replace('\x00', '')]))

		"""
		token data Name Entity berikutnya jika ada di set tanda I
		"""
		if len(ne_data_split) > 1:
			for i in range(len(ne_data_split) - 1):
				word = ne_data_split[i + 1].replace('\x00', '')
				if word:
					temporary_tokens.append((word, "I-" + MAP_ENTITY_TAG[ne_type.replace('\x00', '')]))

		"""
		data bagian kanan menjadi kalimat untuk proses berikutnya
		"""
		_sent = temp[1]

	"""
	sisa kalimat dipisah menjadi token dan di set O
	"""
	if len(temp) > 1:
		if temp[1]:
			for token in temp[1].strip().split(' '):
				word = token.replace('\x00', '')
				if word:
					temporary_tokens.append((word, 'O'))

	"""
	token digabung menjadi kalimat lalu di beri POS tag
	lalu digabung lagi dengan NE Tag nya
	"""
	postageed = getPOSTag(temporary_tokens)
	result = []
	for i in range(len(temporary_tokens)):
		str_postagged = (postageed[i][0].encode('ascii','ignore'), postageed[i][1].encode('ascii','ignore'))
		result.append((str_postagged, temporary_tokens[i][1].encode('ascii','ignore')))
	
	return result


f = open('data/data_korpus_ne.txt')
lines = [line.split("\t") for line in f.read().split("\n")]
f.close()

train_data = []
for line in lines:
	train_data.append(parseEntityName(line[0]))

chunker = NamedEntityChunker(train_data)
print chunker.parse(getPOSTag("Per semester pertama 2004, total utang jangka panjang Telkom sebesar Rp 20,648 triliun.".split(' ')))


