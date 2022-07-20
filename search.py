from bs4 import BeautifulSoup
import requests
import re


def scrape(query):
    query = re.sub("[- _]", "+", query)
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"
    headers = {"user-agent": USER_AGENT}
    url = "https://www.google.com/search?q={}".format(query)
    resp = requests.get(url, headers=headers)

    results = []

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")

        for g in soup.find_all('div', id='search'):
            anchors = g.find_all('a')
            for a in anchors:
                if "imslp.org" in a.text: # Just IMSLP for now, later Wikipedia?
                    results.append(a["href"])
    else:
        return -1

    return results


def getInfo(url):
    resp = requests.get(url)

    soup = BeautifulSoup(resp.content, "html.parser")

    if "File" in url: # Exception if IMSLP result is file page
        file_usage = soup.find('ul', attrs={"class": "mw-imagepage-linkstoimage"})
        title_composer = file_usage.li.a.text
        search = re.search("\((.*)\)", title_composer)

        title = title_composer[:title_composer.index("(") - 1]
        composer = search.group()[1:-1]
    
    else:
        h1 = soup.body.find("h1").text
        h1 = re.sub("[\t\n\r]", "", h1)

        title = h1[:h1.index(" (")]
        composer = h1[h1.index("(") + 1:-1]

    if "," in composer:
        first_name = composer[composer.index(",") + 2:] 
        last_name = composer[:composer.index(",")]

        composer = first_name + " " + last_name

    return {'title': title, 'composer': composer}


def search(query):
    results = scrape(query)
    if results:
        try: return getInfo(results[0])
        except:
#            print("Found the file on IMSLP but had an error retrieving its info.")
            return -1
#    elif results == -1:
#        print("Error with the search crawl.")
#    else:
#        print("Could not find any results.")
    return -1


if __name__ == "__main__":
    results = scrape("Bach, J.S. - Six English Suites")
    if results:
        print(getInfo(results[0]))
    elif results == -1:
        print("Error with the search crawl.")
    else:
        print("Could not find any results.")
