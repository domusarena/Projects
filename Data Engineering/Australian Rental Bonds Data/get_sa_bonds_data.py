import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from urllib.parse import urljoin
import pytz


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
        
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            print("Successfully created BeautifulSoup object!")

            # Return the soup object for further processing
            return soup

        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None


def get_bond_lodgment_file_urls(soup):
    # Set variable as title text to search for
    title_search_text = "Private Rental Report"

    resource_items = soup.find_all('li', {'class':'resource-item'})

    rental_report_items = [item for item in resource_items if title_search_text in item.find('a', {'class': 'heading'}).get('title')]

    bond_lodgement_file_urls = [item.find('a', {'class': 'resource-url-analytics'}).get('href') for item in rental_report_items]

    return bond_lodgement_file_urls


def copy_all_xlsx_files(urls: list[str]):

    # Set headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/vnd.openxmlformats-officedocument.spresadsheetml.sheet'
    }

    for url in urls:
        file_name = url.split("/")[-1]
        save_path = f"Proptrack/Bonds/Code/Local/SA/Data/xlsx/Bulk/{file_name}"
    
        try:
            # Send GET request to the URL
            response = requests.get(url, headers=headers, stream=True)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Make directory if it doesn't exist
                os.makedirs('Proptrack/Bonds/Code/Local/SA/Data/xlsx/Bulk', exist_ok=True)

                # Write the content to a file
                with open(save_path, 'wb') as file:
                    file.write(response.content)
                print(f"Success! Excel file downloaded to: {os.path.abspath(save_path)}")

            else:
                print(f"Failed to download. Status code: {response.status_code}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")


def is_first_15_days_of_quarter():
    """Check if current date is in the first 15 days of a quarter"""
    sydney_tz = pytz.timezone('Australia/Sydney')
    sydney_now = datetime.now(sydney_tz)
    today = sydney_now.date()
    
    # Determine which quarter we're in and the start month
    quarter_start_months = [1, 4, 7, 10]  # Jan, Apr, Jul, Oct
    
    for start_month in quarter_start_months:
        if start_month <= today.month < start_month + 3:
            # We're in this quarter
            quarter_start = date(today.year, start_month, 1)
            days_into_quarter = (today - quarter_start).days + 1
            return days_into_quarter <= 15
    
    return False


if __name__ == "__main__":

    # URL of the NSW Government rental bond data webpage
    webpage_url = "https://data.sa.gov.au/data/dataset/private-rent-report"
    
    webpage_soup = get_webpage_html_as_soup(webpage_url)

    if webpage_soup:
        bond_lodgement_urls = get_bond_lodgment_file_urls(webpage_soup)

        # copy_all_xlsx_files(bond_lodgement_urls)

        for url in bond_lodgement_urls:
            print(url)