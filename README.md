# Named Entity Tagger ID

Named Entity Tagger dengan korpus bahasa Indonesia menggunakan nltk ClassifierBasedTagger melakukan klasifikasi bagian kalimat yang merupakan Named Entity nama sesorang, lokasi, organisasi, waktu, dll.

## Installation

Dependensi python:

- Sastrawi stemmer
- CRFTagger (nltk)

## Usage

`python main.py`

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Current Issue

Hasil train terakhir dicoba tidak terlalu baik, untuk kasus kalimat

```
Per semester pertama 2004, total utang jangka panjang Telkom sebesar Rp 20,648 triliun.

hasil tag = (S
  (org P/NN s/NNP)
  p/NNP
  2/CD
  t/FW
  (org u/FW)
  (org j/FW)
  (org p/FW)
  (loc T/NNP s/NNP)
  (loc R/NNP 2/CD)
  t/NND)

# keluaran:
[Per semester] [pertama] [2004,] [total] [utang] [jangka] [panjang] [Telkom sebesar] [Rp 20,648] [triliun.]
 org            -         -       -       org     org      org       loc              loc         -

# ekspektasi:
[Per] [semester] [pertama] [2004,] [total] [utang] [jangka] [panjang] [Telkom] [sebesar] [Rp] [20,648] [triliun.]
 -     -          -         -       -       -       -        -         org      -         -    -        -
```

## Credits

Named Entity Extraction with Python (sebagian besar menggunakan tutorial ini)

http://nlpforhackers.io/named-entity-extraction/

Data Training NETagger

https://github.com/yohanesgultom/nlp-experiments/blob/master/data/ner/training_data.txt

POS Tagger & NER Bahasa Indonesia dengan Python

https://yudiwbs.wordpress.com/2018/02/20/pos-tagger-bahasa-indonesia-dengan-pytho/
https://yudiwbs.wordpress.com/2018/02/18/ner-named-entity-recognition-bahasa-indonesia-dengan-stanford-ner/

Sastrawi Stemmer Python

https://github.com/har07/PySastrawi
