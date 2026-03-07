import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# List of known MovieRulz mirror domains to test
mirrors = [
    'https://www.5movierulz.claims',
    'https://www.5movierulz.travel', 
    'https://movierulez.click',
    'https://www.5movierulz.bargains',
    'https://www.5movierulz.cloud',
    'https://www.movierulezz.com',
]

firefox_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
}

print("Testing MovieRulz Mirror Availability")
print("=" * 70)

for mirror in mirrors:
    try:
        url = mirror + '/category/telugu-movie/'
        response = requests.get(url, headers=firefox_headers, timeout=10, verify=False)
        status = response.status_code
        length = len(response.text)
        has_content = 'boxed film' in response.text
        
        status_str = "✓ OK" if status == 200 else f"Status {status}"
        content_str = " | Has content" if has_content else " | NO CONTENT"
        
        print(f"{mirror:45} | {status_str:12} | {length:6} bytes{content_str}")
    except requests.exceptions.SSLError:
        print(f"{mirror:45} | SSL ERROR")
    except requests.exceptions.ConnectionError:
        print(f"{mirror:45} | CONNECTION ERROR")
    except requests.exceptions.Timeout:
        print(f"{mirror:45} | TIMEOUT")
    except Exception as e:
        print(f"{mirror:45} | ERROR: {str(e)[:30]}")

print("=" * 70)
