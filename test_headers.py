import requests

url = 'https://www.5movierulz.claims/category/telugu-movie/'

# Headers the addon currently uses
firefox_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0'
}

# Chrome user-agent from your screenshot
chrome_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
}

# Test with Firefox headers
print("=" * 60)
print("Testing with Firefox User-Agent (current addon):")
print("=" * 60)
try:
    response = requests.get(url, headers=firefox_headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)} bytes")
    print(f"Content Preview: {response.text[:500]}")
    if 'telugu' in response.text.lower():
        print("✓ Contains Telugu content")
    if 'boxed film' in response.text:
        print("✓ Contains expected HTML class")
except Exception as e:
    print(f"Error: {e}")

# Test with Chrome headers
print("\n" + "=" * 60)
print("Testing with Chrome User-Agent:")
print("=" * 60)
try:
    response = requests.get(url, headers=chrome_headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)} bytes")
    print(f"Content Preview: {response.text[:500]}")
    if 'telugu' in response.text.lower():
        print("✓ Contains Telugu content")
    if 'boxed film' in response.text:
        print("✓ Contains expected HTML class")
except Exception as e:
    print(f"Error: {e}")

# Test with no user-agent
print("\n" + "=" * 60)
print("Testing with NO User-Agent header:")
print("=" * 60)
try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)} bytes")
except Exception as e:
    print(f"Error: {e}")
