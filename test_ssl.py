import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = 'https://www.5movierulz.claims/category/telugu-movie/'

# Firefox user-agent the addon uses
firefox_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0'
}

print("Testing with Firefox User-Agent (SSL verification DISABLED):")
print("=" * 60)
try:
    response = requests.get(url, headers=firefox_headers, timeout=10, verify=False)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)} bytes")
    if len(response.text) > 0:
        print(f"Content Preview: {response.text[:500]}")
        if 'boxed film' in response.text:
            print("✓ SUCCESS: Contains expected HTML class 'boxed film'")
        else:
            print("✗ WARNING: HTML received but missing 'boxed film' class")
    else:
        print("✗ ERROR: Empty response body")
except Exception as e:
    print(f"Error: {e}")
