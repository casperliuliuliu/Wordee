import requests
from bs4 import BeautifulSoup

def find_paragraph_in_news(url, word):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors

        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')

        for paragraph in paragraphs:
            if word.lower() in paragraph.get_text().lower():
                return paragraph.get_text()
        return "Word not found in any paragraph."

    except requests.RequestException as e:
        return f"Error fetching the URL: {e}"

if __name__ == "__main__":
    url = "https://edtrust.org/the-equity-line/rigor-and-representation-in-childrens-books-foster-a-love-of-reading/"
    url = "https://actualnewsmagazine.com/english/salary-increases-for-state-employees-legault-speaks-of-budgetary-rigor-to-come/"
    word = "rigor"
    print(find_paragraph_in_news(url, word))
