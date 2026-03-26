import requests
from bs4 import BeautifulSoup
import time

TOTAL_PAGES = 49


def fetch_page(url):
    back_off = 1
    response = requests.get(url)

    if response.status_code == 429:
        print("Too many requests")
        failed = True
        while failed == True:
            back_off += 1
            print(f"waiting for {back_off}")
            time.sleep(back_off)
            response = requests.get(url)
            if response.status_code != 429:
                failed = False
    else:
        # All other HTTP errors we raise an exception
        response.raise_for_status()
    return response


def unpaginate_docs():
    base_url = "https://developer.wordpress.org/reference/functions/page/"
    output_file = "wordpress_functions_combined.html"

    # Start the combined HTML structure
    combined_html = "<html><head><meta charset='UTF-8'><title>WP Functions Combined</title>"
    combined_html += "<style>body{font-family:sans-serif; line-height:1.6; padding:40px; max-width:900px; margin:auto;} "
    combined_html += "main{border-bottom: 2px solid #eee; margin-bottom: 40px; padding-bottom: 20px;}</style></head><body>"

    for i in range(1, TOTAL_PAGES):
        url = f"{base_url}{i}/"
        print(f"Fetching page {i}...")

        try:
            response = fetch_page(url)

            soup = BeautifulSoup(response.text, "html.parser")

            # Find the <main> tag

            if main_content := soup.find("main"):
                if pagination := main_content.find("nav", class_="wp-block-query-pagination"):
                    pagination.decompose()

                if heading := main_content.find("h1", class_="wp-block-query-title"):
                    heading.decompose()

                if function_prefixes := main_content.find_all(
                    "span", class_="wp-block-wporg-code-short-title__type"
                ):
                    for function_prefix in function_prefixes:
                        function_prefix.decompose()

                combined_html += str(main_content)

            else:
                print(f"Warning: No <main> tag found on page {i}")

        except Exception as e:
            print(f"Error with page {i}: {e}")
            if input("Continue? y/n") == "y":
                continue
            else:
                raise e

    combined_html += "</body></html>"

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(combined_html)

    print(f"\nDone! Combined documentation saved to {output_file}")


if __name__ == "__main__":
    unpaginate_docs()
