import pandas as pd
import requests
import zipfile
from io import BytesIO
from bs4 import BeautifulSoup

def get_zip_url(base_url, target_file):
    """Scrape the directory listing and find the desired ZIP file."""
    response = requests.get(base_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the directory listing: {response.status_code}")
    
    # Parse the HTML to find links
    soup = BeautifulSoup(response.content, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    
    # Find the target file
    for link in links:
        if target_file in link:
            return base_url + link
    raise ValueError(f"Target file '{target_file}' not found in the directory.")

def download_and_extract_zip(zip_url):
    """Download a zip file from a URL and extract its contents."""
    response = requests.get(zip_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download the file: {response.status_code}")
    
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        # List the contents of the zip archive
        z.printdir()
        
        # Filter out CSV files from the archive
        csv_files = [name for name in z.namelist() if name.endswith('.csv')]
        
        if not csv_files:
            raise ValueError("No CSV files found in the zip archive.")
        
        # Print available CSV files for transparency
        print(f"Found the following CSV files in the archive: {csv_files}")
        
        # Select the first CSV file
        csv_filename = csv_files[0]
        print(f"Processing file: {csv_filename}")
        
        # Read and return the selected CSV file as a DataFrame
        with z.open(csv_filename) as f:
            return pd.read_csv(f)

def transform_data(df):
    """Transform the dataset by filtering, selecting, and renaming columns."""
    # Replace nulls with zero
    df.fillna(0, inplace=True)

    # Filter records
    df = df[(df['MAR'] != 1) & (df['AGEP'] >= 18)]

    # Select and process demographic data
    demographic_data = df[['SERIALNO', 'RAC1P', 'PAOC', 'PERNP', 'MAR', 'AGEP', 'SCHL', 'SEX']].copy()
    demographic_data.columns = demographic_data.columns.str.lower()

    # Select and process origins data
    origins = df[['SERIALNO', 'RAC1P', 'LANP', 'ANC1P']].copy()
    origins.columns = origins.columns.str.lower()

    return demographic_data, origins

def save_to_csv(df, filename):
    """Save a DataFrame to a CSV file."""
    df.to_csv(filename, index=False)
    print(f"File saved: {filename}")

def main():
    # Define the base URL and target file
    base_url = 'https://www2.census.gov/programs-surveys/acs/data/pums/2023/1-Year/'
    target_file = 'csv_ptx.zip'
    
    # Step 1: Extract
    print("Finding and downloading the zip file...")
    try:
        zip_url = get_zip_url(base_url, target_file)
        print(f"Found file URL: {zip_url}")
        df = download_and_extract_zip(zip_url)
    except Exception as e:
        print(f"Error during extraction: {e}")
        return

    # Step 2: Transform
    print("Transforming data...")
    demographic_data, origins = transform_data(df)

    # Step 3: Load
    print("Saving data...")
    save_to_csv(demographic_data, 'demographic_data.csv')
    save_to_csv(origins, 'origins.csv')

    print("ETL process completed successfully.")

if __name__ == "__main__":
    main()
