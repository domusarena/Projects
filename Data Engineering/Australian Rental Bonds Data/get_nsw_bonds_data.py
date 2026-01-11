import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin


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

  
def get_bond_lodgement_file_urls(soup):

    accordian_content = soup.find('div', {'class': 'nsw-accordion__content'})
    accordian_content_class =  accordian_content.find('div', {'class': 'nsw-wysiwyg-content'})
    excel_links_html = accordian_content_class.find_all('a')
    excel_links = [link.get('href') for link in excel_links_html]

    return excel_links
    

def copy_excel_files_historical(urls: list[str]):

    # Set headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/vnd.openxmlformats-officedocument.spresadsheetml.sheet'
    }

    base_url = "https://www.nsw.gov.au/"

    for url in urls:
        file_name = url.split("/")[-1]
        full_url = base_url + url
        save_path = f"Proptrack/Bonds/Code/Local/NSW/Data/xlsx/Bulk/{file_name}"
    
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


def copy_excel_file_for_month():

    # Get current date
    today = datetime.now()
    
    # Check if it's within the first 10 days of the month (Assuming this as a buffer for state government upload)
    if today.day > 10:
        # Calculate current month code
        posting_year_month = today.strftime("%Y-%m")

        # Calculate previous month name
        previous_month = today.replace(day=1) - timedelta(days=1)
        lodgement_month = previous_month.strftime("%B")
        lodgement_year = previous_month.strftime("%Y")

    else:
        # Calculate previous month
        previous_month = today.replace(day=1) - timedelta(days=1)
        posting_year_month = previous_month.strftime("%Y-%m")
        
        # Calculate two months ago name
        two_months_ago = previous_month.replace(day=1) - timedelta(days=1)
        lodgement_month = two_months_ago.strftime("%B")
        lodgement_year = two_months_ago.strftime("%Y")

    # Set headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/vnd.openxmlformats-officedocument.spresadsheetml.sheet'
    }

    url = f"https://www.nsw.gov.au/sites/default/files/noindex/{posting_year_month}/rental-bond-lodgements-{lodgement_month.lower()}-{lodgement_year}.xlsx"

    filename = url.split("/")[-1]
    save_path = f"Proptrack/Bonds/Code/Local/NSW/Data/xlsx/Single/{posting_year_month.replace("-", "")}/{filename}"

    # Create directory
    os.makedirs(f"Proptrack/Bonds/Code/Local/NSW/Data/xlsx/Single/{posting_year_month.replace("-", "")}")
    
    try:
        # Send GET request to the URL
        response = requests.get(url, headers=headers, stream=True)
        
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

    # URL of the NSW Government rental bond data webpage
    webpage_url = "https://www.nsw.gov.au/housing-and-construction/rental-forms-surveys-and-data/rental-bond-data"

    webpage_soup = get_webpage_html_as_soup(webpage_url)

    if webpage_soup:
        bond_lodgement_file_urls = get_bond_lodgement_file_urls(webpage_url)
    
        # Get URLs of each Excel download
        copy_excel_files_historical(bond_lodgement_file_urls)

        # # Copy last month's Excel file to local storage location
        # copy_excel_file_for_month()