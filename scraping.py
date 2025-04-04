import requests
from bs4 import BeautifulSoup

     
class PianoLibraryScraper:
    def __init__(self):
        self.base_url = 'https://www.pianolibrary.org'
        self.composers = [
          'Johann Sebastian Bach',
          'Ludwig van Beethoven',
          'Frédéric Chopin',
          'George Frideric Handel',
          'Wolfgang Amadeus Mozart',
          'Domenico Scarlatti',
          'Franz Schubert',
        ]
        self.composer_url_map = self.get_composer_links()
        
        

    
    def get_composer_links(self):
        url = 'https://www.pianolibrary.org/composers/'
        response = requests.get(url, timeout=2)
        soup = BeautifulSoup(response.text, 'html.parser')
        composer_a_tags = soup.find('table', class_='table_borders').find_all('a')
        composer_url_map = {}
        for composer in composer_a_tags:
            composer_name = composer.text.strip()
            if composer_name in self.composers:
                relative_url = composer['href'].lstrip('./')
                composer_url_map[composer_name] = url + relative_url.removesuffix('/index.html')
        return composer_url_map

    def get_song_url(self, url : str, song_name):
        response = requests.get(url, timeout=2)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            if song_name in link.text:
                return url + link['href'].lstrip('.').removesuffix('/index.html')
              
    def get_song_difficulty(self, url : str):
        response = requests.get(url, timeout=2)
        soup = BeautifulSoup(response.text, 'html.parser')
        p_tags = soup.find_all('p')
        for p in p_tags:
            if 'Difficulty' in p.text:
                link = p.find('a')
                if link:
                  return link.text
        return None
    
    def get_difficulty_for_composer(self, composer_name, song_name):
        if composer_name in self.composer_url_map:
            song_url = self.get_song_url(self.composer_url_map[composer_name], song_name)
            if song_url:
                return self.get_song_difficulty(song_url)
        return None

          
if __name__ == "__main__":
    scrapper = PianoLibraryScraper()
    composer_name = 'Johann Sebastian Bach'
    song_name = 'Prelude'
    difficulty = scrapper.get_difficulty_for_composer(composer_name, song_name)
    if difficulty:
        print(f"The difficulty of '{song_name}' by {composer_name} is: {difficulty}")
    else:
        print(f"Difficulty not found for '{song_name}' by {composer_name}.")
    
        
        