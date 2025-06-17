import requests
from bs4 import BeautifulSoup
import urllib3
import os
from datetime import datetime, timedelta


def get_webpage_html_as_soup(url: str):
    
    # Set a user agent to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Send HTTP request to the website with verify=False to bypass SSL verification
        # NOTE: This is not recommended for production as it introduces security risks
        response = requests.get(url, headers=headers, verify=False)
        
        # Suppress only the single InsecureRequestWarning
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
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

    
def get_all_bond_lodgement_file_urls(soup) -> list[str]:
    # Set variable as title text to search for
    title_search_text = "Monthly Bond Lodgement Summary"

    # Find all resources
    resources = soup.find_all("li", class_="resource-item")

    # Only use resources with the title "Monthly Bond Lodgement Summary"
    bond_lodgment_resources = [item for item in resources if title_search_text in item.find('a', {'class': 'heading'}).get('title')]

    bond_lodgement_filenames = [item.find('a', {'class':'resource-url-analytics'}).get('href') for item in bond_lodgment_resources]

    return bond_lodgement_filenames


def copy_all_csv_files(urls: list[str]):

    for url in urls:
        filename = url.split("/")[-1]
        save_path = f"Proptrack/Bonds/Code/Local/WA/Data/csv/Bulk/{filename}"
        
        try:
            # Send HTTP request to the website with verify=False to bypass SSL verification
            # NOTE: This is not recommended for production as it introduces security risks
            response = requests.get(url, timeout=30, verify=False)

            # Suppress only the single InsecureRequestWarning
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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


def copy_last_month_csv_file():

    # Get current date
    today = datetime.now()

    # Check if it's within the first 10 days of the month (Assuming this as a buffer for state government upload)
    if today.day > 10:
        # Calculate previous month
        previous_month = today.replace(day=1) - timedelta(days=1)

        folder_name = previous_month.strftime("%Y%m")
        lodgement_month_last_day = previous_month.strftime("%d-%m-%Y")
        lodgement_month_first_day = previous_month.replace(day=1).strftime("%d-%m-%Y")
    
    else:
        # Calculate previous month and two months ago
        previous_month = today.replace(day=1) - timedelta(days=1)
        two_months_ago = previous_month.replace(day=1) - timedelta(days=1)

        folder_name = two_months_ago.strftime("%Y%m")
        lodgement_month_last_day = two_months_ago.strftime("%d-%m-%Y")
        lodgement_month_first_day = two_months_ago.replace(day=1).strftime("%d-%m-%Y")
 
    url = f"https://data.ahdap.org/RentalBondsWA/Monthly+Bond+Lodgement+Summary+%28CSV%29-%28{lodgement_month_first_day}-{lodgement_month_last_day}%29.csv"
    filename = url.split("/")[-1]
    save_path = f"Proptrack/Bonds/Code/Local/NSW/Data/csv/Single/{folder_name}/{filename}"

    try:
        # Send HTTP request to the website with verify=False to bypass SSL verification
        # NOTE: This is not recommended for production as it introduces security risks
        response = requests.get(url, timeout=30, verify=False)

        # Suppress only the single InsecureRequestWarning
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    webpage_url = "https://housingdata.ahdap.org/dataset/west-australia-rental-bonds-data-2023-current"

    webpage_soup = get_webpage_html_as_soup(webpage_url)
    
    # If HTML content is returned, retrieve the urls of the CSV downloads
    if webpage_soup:
        bond_lodgement_file_urls = get_all_bond_lodgement_file_urls(webpage_soup)
    
        # Copy all CSV files to local storage
        copy_all_csv_files(bond_lodgement_file_urls)

        # # Copy last month's CSV file to Excel storage
        # copy_last_month_csv_file()