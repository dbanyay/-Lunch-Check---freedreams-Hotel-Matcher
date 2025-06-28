import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import base64
import argparse
import os
from pathlib import Path


def setup_driver():
    """
    Sets up and returns a Selenium Chrome WebDriver instance.
    Configures the driver for headless mode and other common options.
    """
    chrome_options = webdriver.ChromeOptions()
    # Run in headless mode (no visible browser window)
    chrome_options.add_argument("--headless")
    # Bypass OS security model (necessary for some environments, e.g., Docker)
    chrome_options.add_argument("--no-sandbox")
    # Overcome limited resource problems
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Suppress verbose logging from Chromium
    chrome_options.add_argument("--log-level=3")
    # Set a default window size, important for consistent screenshots in headless mode
    chrome_options.add_argument("--window-size=1920,1080")
    # Disable GPU hardware acceleration (often recommended for headless)
    chrome_options.add_argument("--disable-gpu")
    # Ignore certificate errors (useful for some development or self-signed certs)
    chrome_options.add_argument("--ignore-certificate-errors")
    # Disable browser extensions
    chrome_options.add_argument("--disable-extensions")
    # Disable setuid sandbox (another security bypass for certain environments)
    chrome_options.add_argument("--disable-setuid-sandbox")
    # Disable browser notifications
    chrome_options.add_argument("--disable-notifications")
    # Exclude specific switches to prevent certain console messages (e.g., DevTools listening)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Setup WebDriver Service. Assumes chromedriver is in your system's PATH.
    # If not, you'll need to specify its path: Service(executable_path='/path/to/chromedriver')
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except WebDriverException as e:
        print(f"Error initializing WebDriver: {e}")
        print("Please ensure chromedriver is installed and accessible in your system's PATH.")
        print(
            "You can download the appropriate chromedriver for your Chrome version from: https://chromedriver.chromium.org/downloads")
        return None


def scrape_hotel_images(input_csv_path):
    """
    Reads URLs from the specified CSV, visits each URL, and scrapes a screenshot
    of the target div, returning a list of base64 encoded images with their URLs.
    """
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: The input CSV file '{input_csv_path}' was not found.")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

    if 'freedreams_webpage' not in df.columns:
        print("Error: The CSV file must contain a column named 'freedreams_webpage'.")
        return []

    image_data_list = []
    driver = setup_driver()
    if not driver:
        return []  # Exit if driver couldn't be initialized

    # Define the CSS selector for the target div
    # This selector combines all classes for specificity
    target_div_selector = '.js-hotel-detail-page.s-hotel-detail-page.s-content-box.s-content-box-white-solid.is-relative'

    for index, row in df.iterrows():
        url = row['freedreams_webpage']
        # Skip if the URL is missing or not a string
        if pd.isna(url) or not isinstance(url, str):
            print(f"Skipping row {index}: Invalid or missing URL.")
            continue

        print(f"Processing URL ({index + 1}/{len(df)}): {url}")
        try:
            driver.get(url)
            # Wait up to 20 seconds for the target div to be present on the page
            wait = WebDriverWait(driver, 20)
            target_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target_div_selector)))

            # Take a screenshot of the specific element
            png_bytes = target_div.screenshot_as_png
            # Encode the PNG bytes to base64 for embedding in HTML
            base64_encoded_image = base64.b64encode(png_bytes).decode('utf-8')

            image_data_list.append({
                'url': url,
                'image_base64': base64_encoded_image
            })
            print(f"Successfully scraped image for {url}")

        except TimeoutException:
            print(f"Timeout: The target element was not found on page for {url}. Skipping.")
        except WebDriverException as e:
            print(f"WebDriver error occurred while processing {url}: {e}. Skipping.")
        except Exception as e:
            print(f"An unexpected error occurred for {url}: {e}. Skipping.")

    driver.quit()  # Close the browser when all URLs are processed
    return image_data_list


def generate_html_report(image_data_list, output_html_path="hotel_screenshots.html"):
    """
    Generates an HTML file displaying all collected screenshots with their source URLs.
    """
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotel Detail Page Screenshots</title>
    <style>
        /* Import Google Font - Inter for a modern look */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        body {
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4; /* Light grey background */
            color: #333; /* Dark text for readability */
            line-height: 1.6;
        }

        .container {
            max-width: 900px; /* Max width for content */
            margin: 0 auto; /* Center the container */
            padding: 30px;
            background-color: #fff; /* White background for the content area */
            border-radius: 12px; /* Rounded corners for the container */
            box-shadow: 0 6px 20px rgba(0,0,0,0.08); /* Soft shadow */
        }

        h1 {
            text-align: center;
            color: #2c3e50; /* Dark blue-grey for main heading */
            margin-bottom: 40px;
            font-size: 2.8em; /* Larger font size */
            font-weight: 700; /* Bolder font weight */
            border-bottom: 2px solid #ececec; /* Subtle underline */
            padding-bottom: 20px;
        }

        .hotel-entry {
            background-color: #fcfcfc; /* Slightly off-white for individual entries */
            border-radius: 10px; /* Rounded corners */
            box-shadow: 0 3px 10px rgba(0,0,0,0.06); /* Lighter shadow */
            margin-bottom: 35px;
            padding: 25px;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* Smooth transition on hover */
            border: 1px solid #e9e9e9; /* Light border */
        }

        .hotel-entry:hover {
            transform: translateY(-7px); /* Lift effect on hover */
            box-shadow: 0 8px 20px rgba(0,0,0,0.1); /* Enhanced shadow on hover */
        }

        .hotel-entry h2 {
            color: #34495e; /* Medium blue-grey for subheadings */
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.6em;
            word-break: break-all; /* Ensures long URLs break and don't overflow */
            font-weight: 600;
        }

        .hotel-entry img {
            max-width: 100%; /* Ensure images are fully responsive */
            height: auto; /* Maintain aspect ratio */
            border-radius: 8px; /* Rounded corners for images */
            display: block; /* Ensures image takes its own line */
            margin: 20px auto; /* Center images with vertical spacing */
            box-shadow: 0 2px 8px rgba(0,0,0,0.15); /* Shadow for images */
            border: 1px solid #ddd; /* Light border for images */
        }

        .hotel-entry a {
            color: #007bff; /* Standard blue link color */
            text-decoration: none; /* No underline by default */
            font-weight: 600; /* Bolder link text */
            transition: color 0.2s ease-in-out, text-decoration 0.2s ease-in-out;
        }

        .hotel-entry a:hover {
            color: #0056b3; /* Darker blue on hover */
            text-decoration: underline; /* Underline on hover */
        }

        .no-data {
            text-align: center;
            color: #7f8c8d; /* Grey text for no data message */
            font-style: italic;
            padding: 50px;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hotel Detail Page Screenshots</h1>
"""
    if not image_data_list:
        html_content += """
        <p class="no-data">No hotel detail page screenshots were collected. This could be due to:</p>
        <ul class="no-data" style="list-style-type: disc; text-align: left; display: inline-block;">
            <li>The input CSV file not being found or having errors.</li>
            <li>The 'webpage' column being missing or empty.</li>
            <li>Issues with the WebDriver setup (e.g., chromedriver not in PATH).</li>
            <li>The target element not being present on the webpages within the given timeout.</li>
            <li>Network issues during scraping.</li>
        </ul>
        <p class="no-data">Please check the console logs for more details.</p>
        """
    else:
        for data in image_data_list:
            html_content += f"""
        <div class="hotel-entry">
            <h2>Source URL: <a href="{data['url']}" target="_blank">{data['url']}</a></h2>
            <img src="data:image/png;base64,{data['image_base64']}" alt="Screenshot of {data['url']}">
        </div>
        """

    html_content += """
    </div>
</body>
</html>
"""
    try:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML report generated successfully at: {output_html_path}")
    except IOError as e:
        print(f"Error writing HTML file '{output_html_path}': {e}")


def main():
    # Setup argument parser to accept the input CSV file path
    parser = argparse.ArgumentParser(description="Scrape hotel detail page images from a CSV of URLs.")
    parser.add_argument("--input-file", type=str, required=True,
                        help="Path to the input CSV file containing hotel detail page URLs.")
    parser.add_argument("--output-html-path", type=str, default="hotel_screenshots.html",
                        help="Path to save the generated HTML report. Default is 'hotel_screenshots.html'.")
    args = parser.parse_args()

    # Define the output HTML file name
    output_html_file = Path.cwd() / args.output_html_path

    # Scrape images and get the list of data
    scraped_images = scrape_hotel_images(args.input_file)

    # Generate the HTML report
    generate_html_report(scraped_images, output_html_file)


if __name__ == "__main__":
    main()
