"""
FIND IMSLP
----------

Given an IMSLP download file name, find the associated
work and get the work information

Author: Hugo Middeldorp
"""

import requests
import json
import re
from bs4 import BeautifulSoup

def findIMSLP(file_name):

    if file_name.index("IMSLP") == 0:
        index = file_name.index("-") + 1
        file_name = file_name[index:]
    else: return 0

    url = "https://imslp.org/wiki/File:{}".format(file_name)
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    file_usage = soup.find('ul', attrs={"class": "mw-imagepage-linkstoimage"})
    title_composer = file_usage.li.a.text
    search = re.search("\((.*)\)", title_composer)

    # Grabs the string until the first comma (catalog numbers usually come after)
    title = title_composer[:title_composer.index(",")]
    # Grab everything between (but not including) brackets
    composer = search.group()[1:-1]

    return {'title': title, 'composer': composer}


print(findIMSLP("IMSLP425723-PMLP01842-nma_196_104_121.pdf"))

