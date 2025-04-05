import requests
from bs4 import BeautifulSoup
import re
from rapidfuzz import fuzz, process
from pathlib import Path

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
        """
        Normalize text by converting to lower case, and replacing acroynms with full words.
        """
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
                        d_number = self.extract_d_number(title)
                        if d_number:
                            difficulty_map[d_number] = difficulty
                        else:
                            difficulty_map[self.normalize(title)] = difficulty
                ul = ul.find_next_sibling("ul")
        return difficulty_map
    
    def extract_d_number(self, title: str) -> str | None:
        """Extract D, K, or BWV numbers like D960, K123, BWV123, or BWV.123 from title"""
        match = re.search(r"\b(D|K|BWV)\.?\s?(\d+)\b", title, re.IGNORECASE)
        if match:
            return f"{match.group(1).lower()}{match.group(2)}"
        return None
    
    def extract_opus_number(self, title: str) -> str | None:
        """Extract catalog number like opus119, op33, hess073, etc."""
        title = title.lower()

        # Match 'op.', 'opus', 'hess', etc.
        match = re.search(r"\b(op(?:us)?|hess)\.?\s*(\d+)", title)
        if match:
            return f"{match.group(1)}{match.group(2)}"
        return None
    
    def extract_bwv_number(self, title: str) -> str | None:
        """Extract BWV or BWV Anh. number"""
        title = title.lower()

        # Match BWV or BWV Anh. numbers like 'bwv 1055' or 'bwv anh 151'
        match = re.search(r"\bbwv\s*(anh\.?)?\s*(\d+)\b", title)
        if match:
            prefix = "bwv"
            if match.group(1):  # it's 'anh.'
                prefix += "anh"
            return f"{prefix}{match.group(2)}"
        return None

    def match_files_difficulty(self, difficulty_map, file):
        file_norm = self.normalize(file)
        file_bwv = self.extract_bwv_number(file)
        file_opus = self.extract_opus_number(file)

        # Filter difficulty_map based on catalog number
        filtered_keys = list(difficulty_map)
        if file_bwv:
            filtered_keys = [
                key for key in filtered_keys
                if file_bwv in key or self.extract_bwv_number(key) == file_bwv
            ]
        elif file_opus:
            filtered_keys = [
                key for key in filtered_keys
                if file_opus in key or self.extract_opus_number(key) == file_opus
            ]

        if not filtered_keys:
            return None

        # Fuzzy match on filtered subset
        match, score, _ = process.extractOne(file_norm, filtered_keys, scorer=fuzz.token_sort_ratio)
        if score > 50:
            print(score, match, file)
            return difficulty_map.get(match, "")
        return None
                
    def get_composer_urls(self, html : str):
        """
        Get all composer difficulty urls from given html
        """
        soup = BeautifulSoup(html, "html.parser")
        composer_urls = {}
        for composer in self.composers:
            a_tags = soup.find_all("a")
            for a in a_tags:
                if composer.lower() in a.get_text().lower():
                    url = a.get("href")
                    composer_urls[composer] = f"{self.base_url}{'/difficulty'}{url.lstrip('.')}"
        return composer_urls
  
    def get_all_composer_difficulty_map(self):
        """
        Get all difficulty levels for a given composer
        """
        composer_html = requests.get('https://www.pianolibrary.org/difficulty/', timeout=2)
        composer_urls = self.get_composer_urls(composer_html.text)
        difficulty_map = {}
        for composer in self.composers:
            composer_url = composer_urls.get(composer)
            response = requests.get(composer_url, timeout=2)
            difficulty_map[composer] = self.extract_difficulty_map(response.text)
        return difficulty_map

        
  
if __name__ == "__main__":
    scraper = PianoLibraryScraper()
    all_files = Path('./ALL').glob("*.csv")
    all_difficulty_map = scraper.get_all_composer_difficulty_map()
    print('all files length', len(list(all_files)))
    # print(all_files)
    count = 0
    for file in all_files:
        composer = file.name.split(' ')[0]
        for c in scraper.composers:
            if composer.lower() in c.lower():
                difficulty = scraper.match_files_difficulty(all_difficulty_map[c], file.name)
                if difficulty:
                    count = count + 1
                    
    print('matched files', count)
    # t = scraper.get_all_composer_difficulty_map()
    # print(t)
 
    
    
        
        