import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
import re

def search_google(query, num_results=5):
    """
    Search Google and return URLs from results.
    Note: This uses a simple scraping approach which may be blocked.
    Consider using Google Custom Search API for production use.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = []
        
        # Extract URLs from search results
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/url?q=' in href:
                url = href.split('/url?q=')[1].split('&')[0]
                if url.startswith('http') and 'google.com' not in url:
                    urls.append(url)
                    if len(urls) >= num_results:
                        break
        
        return urls
    except Exception as e:
        print(f"Search error: {e}")
        return []

def find_pdf_links(url):
    """Find PDF links on a webpage."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Check if link points to a PDF
            if href.lower().endswith('.pdf') or 'pdf' in href.lower():
                full_url = urljoin(url, href)
                pdf_links.append(full_url)
        
        return pdf_links
    except Exception as e:
        print(f"Error extracting PDFs from {url}: {e}")
        return []

def download_pdf(url, filename):
    """Download a PDF file."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Check if content type is PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
            print(f"Warning: URL may not be a PDF: {url}")
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def sanitize_filename(name):
    """Create a safe filename from council name."""
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.replace(' ', '_')
    return name

def search_and_download_council_pdfs(councils, output_dir='Documents'):
    """
    Search for and download fees and charges PDFs for a list of councils.
    
    Args:
        councils: List of council names
        output_dir: Directory to save PDFs
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    for council in councils:
        print(f"\n{'='*60}")
        print(f"Processing: {council}")
        print(f"{'='*60}")
        
        # Create search query
        search_query = f"{council} fees and charges 2025/26"
        print(f"Search query: {search_query}")
        
        # Search for the document
        search_results = search_google(search_query, num_results=5)
        
        if not search_results:
            print(f"No search results found for {council}")
            results[council] = "No results found"
            continue
        
        print(f"Found {len(search_results)} search results")
        
        # Try to find and download PDF from search results
        pdf_downloaded = False
        
        for i, result_url in enumerate(search_results, 1):
            print(f"\nChecking result {i}: {result_url}")
            
            # Check if the URL itself is a PDF
            if result_url.lower().endswith('.pdf'):
                filename = os.path.join(output_dir, f"{sanitize_filename(council)}_fees_charges_2025-26.pdf")
                if download_pdf(result_url, filename):
                    results[council] = filename
                    pdf_downloaded = True
                    break
            else:
                # Search the page for PDF links
                pdf_links = find_pdf_links(result_url)
                
                if pdf_links:
                    print(f"Found {len(pdf_links)} PDF link(s) on page")
                    # Try to download the first PDF that looks relevant
                    for pdf_url in pdf_links:
                        if any(term in pdf_url.lower() for term in ['fee', 'charge', '2025', '2026']):
                            filename = os.path.join(output_dir, f"{sanitize_filename(council)}_fees_charges_2025-26.pdf")
                            if download_pdf(pdf_url, filename):
                                results[council] = filename
                                pdf_downloaded = True
                                break
                    
                    if pdf_downloaded:
                        break
        
        if not pdf_downloaded:
            print(f"Could not find/download PDF for {council}")
            results[council] = "PDF not found or download failed"
        
        # Be respectful with requests
        time.sleep(2)
    
    return results

# Example usage
if __name__ == "__main__":
    # List of councils to search for
    councils = [
        "Bayside Council",
        "Blacktown City Council",
        "Burwood Council",
        "Camden Council",
        "Campbelltown City Council",
        "Canterbury Bankstown Council",
        "City of Canada Bay Council",
        "City of Parramatta Council",
        "City of Ryde Council",
        "City of Sydney Council",
        "Cumberland City Council",
        "Fairfield City Council",
        "Georges River Council",
        "Hawkesbury City Council",
        "Hills Shire Council",
        "Hornsby Shire Council",
        "Hunters Hill Council",
        "Inner West Council",
        "Ku-ring-gai Council",
        "Lane Cove Council",
        "Liverpool City Council",
        "Mosman Municipal Council",
        "Northern Beaches Council",
        "North Sydney Council",
        "Penrith City Council",
        "Randwick City Council",
        "Strathfield Council",
        "Sutherland Shire Council",
        "Waverley Council",
        "Willoughby City Council",
        "Wollondilly Shire Council",
        "Woollahra Municipal Council"
    ]
    
    print("Starting council PDF download process...")
    print(f"Looking for 2025/26 fees and charges documents")
    
    results = search_and_download_council_pdfs(councils)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for council, result in results.items():
        print(f"{council}: {result}")