import requests
from bs4 import BeautifulSoup
import os

def get_webpage_html_as_soup(url: str):
    
    # Set a user agent to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Send HTTP request to the website
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            print("Successfully created BeautifulSoup object!")
            
            # Return the soup object for further processing
            return soup
        
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_bond_lodgment_file_urls(soup):

    urls = [item.get('href') for item in soup.find_all('a') if item.text == 'RTA median rents data']

    return urls


def copy_xlsx_file(urls: list[str]):

    # Set headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/vnd.openxmlformats-officedocument.spresadsheetml.sheet'
    }

    base_url = "https://www.rta.qld.gov.au/"

    for url in urls:
        file_name = url.split("/")[-1]
        full_url = base_url + url
        save_path = f"Proptrack/Bonds/Code/Local/QLD/Data/xlsx/Bulk/{file_name}"

        try:
            # Send GET request to the URL
            response = requests.get(full_url, headers=headers, stream=True)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Write the content to a file
                with open(save_path, 'wb') as file:
                    file.write(response.content)
                print(f"Success! Excel file downloaded to: {os.path.abspath(save_path)}")

            else:
                print(f"Failed to download. Status code: {response.status_code}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        

if __name__ == "__main__":

    # URL of the QLD Government rental bond data webpage
    webpage_url = "https://www.rta.qld.gov.au/forms-resources/rta-quarterly-data/median-rents-quarterly-data"

    webpage_soup = get_webpage_html_as_soup(webpage_url)

    # If HTML content is returned, retrieve the urls of the Excel downloads
    if webpage_soup:
        bond_lodgement_file_urls = get_bond_lodgment_file_urls(webpage_soup)

        copy_xlsx_file(bond_lodgement_file_urls)