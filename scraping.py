import requests
from bs4 import BeautifulSoup


composers = [
  'Johann Sebastian Bach',
  'Ludwig van Beethoven',
  'Frédéric Chopin',
  'George Frideric Handel',
  'Wolfgang Amadeus Mozart',
  'Domenico Scarlatti',
  'Franz Schubert',
]

base_url = 'https://www.pianolibrary.org'
        
def get_composer_links():
    url = 'https://www.pianolibrary.org/composers/'
    response = requests.get(url, timeout=2)
    soup = BeautifulSoup(response.text, 'html.parser')
    composer_links = soup.find('table', class_='table_borders').find_all('a')
    urls = []
    for composer in composer_links:
      composer_name = composer.text.strip()
      if composer_name in composers:
          relative_url = composer['href'].lstrip('./')
          urls.append(url + relative_url.removesuffix('/index.html'))
          print(f"Found composer link: {composer_name} - {url + relative_url}")
    return urls

def get_song_url(url : str, song_name):
    response = requests.get(url, timeout=2)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        if song_name in link.text:
            return url + link['href'].lstrip('.').removesuffix('/index.html')
          
def get_song_difficulty(url : str):
    response = requests.get(url, timeout=2)
    soup = BeautifulSoup(response.text, 'html.parser')
    p_tags = soup.find_all('p')
    for p in p_tags:
      if 'Difficulty' in p.text:
        link = p.find('a')
        if link:
          return link.text
    return None

          
if __name__ == "__main__":
    composer_links = get_composer_links()
    for composer_link in composer_links:
        song_url = get_song_url(composer_link, 'prelude')
        if song_url:
            difficulty = get_song_difficulty(song_url)
            if difficulty:
                print(f"Difficulty for {song_url}: {difficulty}")
        
        