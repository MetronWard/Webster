import json
import logging
import os

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


class Webster:
    def __init__(self):
        """Initiates the Web scraping class"""
        self.dictionary = 'https://www.merriam-webster.com/dictionary/'
        self.thesaurus = 'https://www.merriam-webster.com/thesaurus/'
        logging.info('The Webster class has been created')

    def get_dict(self, word: list) -> tuple | None:
        """Receives a list containing a word or phrase, returns the definition(s) as well as reference
        link if any, or returns None"""
        site = f"{self.dictionary}{'%20'.join(item for item in word)}"
        response = requests.get(site)
        logging.info(f'request sent to {site}')
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.info(f'No word definition found for the word {word}')
            return None
        else:
            logging.info(f'The status cone is {response.status_code}')
            soup = BeautifulSoup(response.text, features="html.parser")
            word_entries = soup.find(class_='vg')
            if word_entries:
                logging.info('Word entry found')
            else:
                logging.info('No entry found on the site')
            definitions = []
            # to cater for def with the class - dtText
            clean_dt = BeautifulSoup(str(word_entries), features="html.parser").find_all(class_='dtText')
            if clean_dt:
                logging.info('Definitions found with the class dtText')
                for items in clean_dt:
                    definitions.append(items.text)
                    logging.info('Definitions cleaned and stored in the variable - definitions')
            # to cater for def with the class - unText
            clean_un = BeautifulSoup(str(word_entries), features="html.parser").find_all(class_='unText')
            if clean_un:
                logging.info('Definitions found with the class unText')
                for items in clean_un:
                    definitions.append(items.text)
                    logging.info('Definitions cleaned and stored in the variable - definitions')
            logging.info('Results stored in the variable "definition" have been returned')
            return definitions, site

    def get_thes(self, word_in: list) -> tuple | None:
        """Receives a list containing a word or phrase, returns the synonyms(s) and/or antonym(s) as well as reference
                link if any, or returns None"""
        site = f"{self.thesaurus}{'%20'.join(item for item in word_in)}"
        response = requests.get(site)
        logging.info(f'request sent to {site}')
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.info(f'No entries found for the word {word_in}')
            return None
        else:
            logging.info(f'The status cone is {response.status_code}')
            soup = BeautifulSoup(response.text, features="html.parser")
            word_entries = soup.find(class_='sense-content')
            syn_ant = BeautifulSoup(str(word_entries), features="html.parser").find_all(class_='thes-list')
            thes = {}
            for words in syn_ant:
                dictionary = []
                word = BeautifulSoup(str(words), features="html.parser").find(class_='function-label')
                syl = BeautifulSoup(str(words), features="html.parser").find_all(class_='syl')
                for item in syl:
                    dictionary.append(item.text)
                thes[word.text] = dictionary
                logging.info(f'{word.text}s have been found for the word {word_in} and stored in ')
            return thes, site


if __name__ == '__main__':
    # make webster class
    web = Webster()
    # word list
    def_word_list = [['tea'], ['in'], ['in', 'other', 'words'], ['ftftf']]
    syn_list = [['rest'], ['rrrr'], ['walk']]
    # make folders
    os.mkdir('thes')
    os.mkdir('def')
    # definitions
    for words in def_word_list:
        result = web.get_dict(words)
        with open(f'def/{words}.docx', mode='w') as doc_file:
            for items in result[0]:
                doc_file.write(f"{items}\n")
    # thesaurus
    for item in syn_list:
        result = web.get_thes(item)
        with open(f'thes/{item}.json', mode='w') as json_file:
            json.dump(result[0], json_file, indent=4)
