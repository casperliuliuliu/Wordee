# Wordee

Wordee is a random word picker with dictionary and news attached. Help you memorize vocabularies using CLI.
Useful for english tests preparations like TOEFL or GRE.

## Install Packages

```shell
pip install .
```

## Pick a word

```shell
python wordee.py --hide -i gre_vocabularies.txt # picks from a words list file.
```


```shell

python wordee.py --hide -i gre_vocabularies.txt --translate ja # with Japanese translation
```

```shell
python wordee.py --hide -i gre_vocabularies.txt --translate zh # with Simplified Chinese translation
```

```shell
python wordee.py --hide -i gre_vocabularies.txt --translate zh-TW # with Traditional Chinese translation
```


```shell
python wordee.py --news -i gre_vocabularies.txt # always shows the news related to the word
```


<!-- ``python3 wordee.py --bookmarked 0.5 -i gre_vocabularies.txt`` specifies probability to pick next random word from bookmarked list. -->

```shell
python wordee.py --bookmarked -i gre_vocabularies.txt # always pick next random word from bookmarked list. Probability can also be specified.
```


```shell
python3 wordee.py -h # for help
```


## More informations

[Google translate languages code](https://cloud.google.com/translate/docs/languages)

[dictionaryapi.dev](https://dictionaryapi.dev/)
