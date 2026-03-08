# Movie Rulz Scraper - Enhanced Error Diagnostics

## Summary of Changes

The Movie Rulz scraper has been updated with comprehensive error logging and diagnostics to identify why HTTP requests are returning no data. The issue is that Cloudflare is blocking Kodi's non-browser requests at the network level, but the errors were being silently swallowed.

## Files Modified

### `plugin.video.deccandelight/resources/scrapers/mrulz.py`

#### 1. New Helper Method: `make_raw_request()`
This method provides detailed error logging by using raw urllib requests:
- Catches `HTTPError` exceptions and logs: HTTP code, reason, response headers, and body
- Catches `URLError` exceptions and logs network-level errors
- Catches all exceptions and logs type and message
- Returns decoded HTML on success, None on failure

```python
def make_raw_request(self, url, headers):
    """Make a raw HTTP request with detailed error logging."""
    # Attempts direct URLopen with comprehensive error handling
```

#### 2. Enhanced `get_items()` Method
Updated to implement three-tier retry strategy:

**Attempt 1:** Uses `client.request()` with extended mode
- Retrieves: HTTP response code, headers, content length, final URL
- Logs Server header and response details
- Can detect 403, 429, 503 Cloudflare blocks

**Attempt 2:** Retries with SSL verification disabled
- Handles misconfigured SSL certificates
- Uses same extended mode for diagnostics
- Provides separate logging for context

**Attempt 3:** Falls back to raw urllib request
- Uses new `make_raw_request()` helper
- Logs specific error types (HTTPError vs URLError)
- Provides deepest diagnostic information

#### 3. Import Additions
```python
import sys
from six.moves import urllib_request, urllib_error
```

## What You'll See in Logs

When the updated addon runs, the enhanced logging will show:

### Success Case (if it works):
```
[MRULZ] get_items: HTTP response code: 200
[MRULZ] get_items: Response content length: 42000 bytes
[MRULZ] get_items: Server header: nginx
```

### Cloudflare Block (expected):
```
[MRULZ] get_items: HTTP response code: 403
[MRULZ] make_raw_request: HTTPError 403 - Forbidden
[MRULZ] make_raw_request: Error body length: 1234 bytes
```

### Network Error (timeouts, connection refused):
```
[MRULZ] make_raw_request: URLError - Connection refused
[MRULZ] make_raw_request: URLError - _ssl.c:1100: The handshake operation timed out
```

## Installation Instructions

1. Copy the updated `mrulz.py` to your Kodi addon directory:
   ```
   .kodi/addons/plugin.video.deccandelight/resources/scrapers/mrulz.py
   ```

2. Restart Kodi (or reload the addon)

3. Try to access Movie Rulz categories in the addon

4. Check the Kodi log file (usually in `.kodi/temp/kodi.log`) for enhanced error messages

## Expected Outcomes

After running with this update, we should see one of:

1. **403 Forbidden** - Cloudflare is detecting and blocking Kodi
   - Solution: Need Cloudflare bypass (cloudflare-scraper, FlareSolverr, etc.)

2. **429 Too Many Requests** - Rate limiting
   - Solution: Add delays between requests, rotate user-agents

3. **502/503 Bad Gateway** - Server issues
   - Solution: Try alternative mirror domains

4. **Network timeouts/connection errors** - DNS/network level blocks
   - Solution: Try alternative domains or VPN

5. **200 OK with empty body** - Cloudflare JavaScript challenge
   - Solution: Need JavaScript execution (cloudflare-scraper)

## Testing Movie Rulz Domains

The addon is configured to try these domains (in order of reliability):
- `https://www.5movierulz.viajes/` (current default)
- `https://www.5movierulz.claims/` (alternative)
- `https://www.4movierulz.ph/` (if available)

You can change the domain in addon settings: 
**Settings → Movie Rulz Settings → Movie Rulz Domain URL**

## Technical Details

### Why Cloudflare is Blocking
- Kodi uses Python's urllib, which sends a default Python user-agent
- Cloudflare sees this as a bot/scraper and immediately rejects
- The rejection happens at network level BEFORE returning HTML
- This is why normal error handling doesn't work (no HTTP response to parse)

### Why Silent Failures Happened Before
The `client.request()` function in Kodi catches exceptions broadly:
- `URLError` is caught and silently returns `''` (empty string)
- `except BaseException` returns `None`
- No logging of what actually went wrong
- The addon just sees `None` and can't diagnose further

### Why This Solution Works
- Raw urllib access gives us the actual exception
- Exception includes error code, reason, and potentially headers
- We can see if it's 403/429 (Cloudflare) vs socket error (network)
- Allows identifying the exact block mechanism

## Next Steps

1. **Run with updated addon** and check logs for specific error
2. **Implement appropriate solution** based on error type:
   - For 403: Use cloudflare-scraper or FlareSolverr
   - For 429: Add request delays and user-agent rotation
   - For network errors: Try alternative domains or check connectivity
3. **Update mrulz.py** with the appropriate fix once error is identified

