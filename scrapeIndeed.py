import bs4, requests, urllib, re
import time as timetime
from datetime import datetime
from datetime import time
from datetime import timedelta


# https://www.indeed.com/jobs?q=data+analyst+i&l=Sunnyvale%2C+CA
# print(urllib.parse.quote_plus('Sunnyvale, CA'))
r = ''
n = 1
urlIndeed = 'https://www.indeed.com'

def parseLocation(location):
    regexLocation = re.compile(r'([a-zA-Z\s]+),\s?([a-zA-Z]{2})\s|([a-zA-Z\s]+),\s?([a-zA-Z]{2})$')
    city = ''
    state = ''

    mo = regexLocation.search(location)

    if mo is not None:
        if mo.group(1) is not None:
            city = mo.group(1)
        elif mo.group(3) is not None:
            city = mo.group(3)
        else:
            city = 'N/A'

        if mo.group(2) is not None:
            state = mo.group(2)
        elif mo.group(4) is not None:
            state = mo.group(4)
        else:
            state = 'N/A'

        return [city,state]
    else:
        return ['N/A','N/A']

def extractJobPostings(r, f):
    global n
    print('Scraping Page %s..' % n)
    n+=1
    soup = bs4.BeautifulSoup(r.text,'html.parser')
    jobCards = soup.select('.jobsearch-SerpJobCard')
    
    for i in jobCards:
        location = parseLocation(i.select('.sjcl > .location')[0].getText().strip())

        f.write('|'.join(
                [
                    i.select('.title > a')[0].getText().strip().replace(',',''),    # title
                    i.select('.company')[0].getText().strip().replace(',',''),      # company
                    location[0],                                                    # city
                    location[1],                                                    # state
                    urlIndeed + i.select('.title > a')[0].attrs['href']             # link to job posting
                ]) + '\n')
    
    nextPage = soup.select('.pagination > a > .pn > .np')
    if nextPage:
        nextPageText = soup.select('.pagination > a')[-1]
        if (nextPageText.getText().lower().startswith('next')):
            nextPagePath = nextPageText.attrs['href']
            nextPageLink = urlIndeed + nextPagePath
            r2 = requests.get(nextPageLink)
            timetime.sleep(3)
            extractJobPostings(r2, f)
    else:
        print('[X] Scraping stopped prematurely due to Next Page link not found.')


if __name__ == '__main__':
    what = input('What position would you like to search for?\n')
    whereCity = input('Which city would you like to search in?\n')
    whereState = input('Which state would you like to search in?\n(2 letter abbreviation. e.g. WA)\n')
    searchIndeed = 'https://www.indeed.com/jobs?q=' + urllib.parse.quote_plus(what) + '&l=' + \
        urllib.parse.quote_plus(whereCity + ', ' + whereState)
    try:
        r = requests.get(searchIndeed)
        try:
            r.raise_for_status()
            cols = ['title','company','city','state','link']
            fileIndeed = open('results/' + ''.join(what.split()) + '_' + ''.join(whereCity.split()) + whereState.upper() + '.csv','a')
            fileIndeed.write('|'.join(cols) + '\n')
            startTime = datetime.now()
            extractJobPostings(r, fileIndeed)
            fileIndeed.close()
            timeDuration = datetime.now() - startTime
            print('Duration: ' + str(timeDuration))
            print('done!')
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
