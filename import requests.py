import requests
from bs4 import BeautifulSoup
import concurrent.futures
import csv
import json
from openpyxl import Workbook

# Function to fetch website data (scrape content)
def fetch_website_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title
        page_title = soup.title.string if soup.title else 'No title found'

        # Extract headings (h1, h2, h3)
        headings = soup.find_all(['h1', 'h2', 'h3'])
        heading_texts = [heading.get_text() for heading in headings]

        # Extract all links
        links = soup.find_all('a', href=True)
        all_links = [link['href'] for link in links]

        # Extract images
        images = soup.find_all('img', src=True)
        image_sources = [img['src'] for img in images]

        return {
            'url': url,
            'title': page_title,
            'headings': heading_texts,
            'links': all_links,
            'images': image_sources
        }

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return {'url': url, 'title': 'Error'}

# Function to scrape multiple websites concurrently
def scrape_websites(urls):
    scraped_data = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(fetch_website_data, urls)

        for result in results:
            scraped_data.append(result)

    # Save data to CSV
    with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'title', 'headings', 'links', 'images']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scraped_data)

    # Save data to JSON
    with open('scraped_data.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(scraped_data, jsonfile, ensure_ascii=False, indent=4)

    print("Scraped data saved to 'scraped_data.csv' and 'scraped_data.json'.")

    # Save data to Excel
    save_to_excel(scraped_data)

# Function to save the scraped data to Excel
def save_to_excel(data, filename='scraped_data.xlsx'):
    # Create a new Excel workbook and sheet
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Scraped Data"

    # Write headers to Excel sheet
    headers = ['URL', 'Title', 'Headings', 'Links', 'Images']
    sheet.append(headers)

    # Write data rows to Excel sheet
    for entry in data:
        # Prepare data for each row
        headings = ', '.join(entry['headings'][:5])  # Display first 5 headings
        links = ', '.join(entry['links'][:5])  # Display first 5 links
        images = ', '.join(entry['images'][:5])  # Display first 5 images

        # Write row to the sheet
        sheet.append([entry['url'], entry['title'], headings, links, images])

    # Save the Excel file
    wb.save(filename)
    print(f"Scraped data saved to '{filename}'.")

# List of websites to scrape
urls = [
    'https://www.google.com',
    'https://www.wikipedia.org',
    'https://www.bbc.com'
]

# Start scraping
if __name__ == "__main__":
    scrape_websites(urls)
