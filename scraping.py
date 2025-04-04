import requests
from bs4 import BeautifulSoup
import re
from rapidfuzz import fuzz, process

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
        
    def normalize(self, text : str):
        text = re.sub(r"op\.*\s*(\d+)", r"opus \1", text.lower())
        text = re.sub(r"no\.*\s*(\d+)", r"number \1", text)
        text = re.sub(r"[^a-z0-9 ]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def extract_difficulty_map(self, html : str):
        soup = BeautifulSoup(html, "html.parser")
        difficulty_map = {}

        for h3 in soup.find_all("h3", class_="section_title"):
            # "Difficulty 1.5 (42)" becomes "1.5"
            difficulty = h3.get_text().split()[1]
            ul = h3.find_next_sibling("ul")
            while ul and ul.name == "ul":
                for li in ul.find_all("li"):
                    # Extract links and text
                    a = li.find("a")
                    if a:
                        title = a.get_text()
                        difficulty_map[self.normalize(title)] = difficulty
                ul = ul.find_next_sibling("ul")
        return difficulty_map
    
    def match_files_difficulty(self, html, file_list):
        result = {}
        difficulty_map = self.extract_difficulty_map(html)
        keys =  difficulty_map.keys()
        for file in file_list:
            text = self.normalize(file)
            match, score, _ = process.extractOne(text, keys, scorer=fuzz.token_sort_ratio)
            if score > 70:
                result[file] = difficulty_map.get(match, "")
        return result
                
        
  
if __name__ == "__main__":
    html = requests.get('https://www.pianolibrary.org/difficulty/chopin/', timeout=2)
    scraper = PianoLibraryScraper()
    difficulty_map = scraper.extract_difficulty_map(html.text)
    text = scraper.normalize('Mazurka op7 n2')
    match, score, _ = process.extractOne(text, difficulty_map.keys(), scorer=fuzz.token_sort_ratio)
    print(score)
    if score > 70:
        print(f"Best match: {match} with score: {score}")
    print(text)
    print(difficulty_map.get(text, "Difficulty not found"))    
    
    
        
        