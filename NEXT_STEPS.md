# Quick Reference: Next Steps for Testing

## File Updated
✅ **mrulz.py** - Enhanced with comprehensive error diagnostics

**Location:** 
```
c:\Users\Deepthi_Devireddy\Documents\KodiRepos\GujalKodiWork\zips\plugin.video.deccandelight\plugin.video.deccandelight-2.0.57\plugin.video.deccandelight\resources\scrapers\mrulz.py
```

## What Changed (3 Key Improvements)

### 1. New Helper Method: `make_raw_request()`
- Uses direct Python urllib instead of Kodi's client wrapper
- Catches and logs actual HTTP errors (403, 429, 503, etc.)
- Logs network-level errors (connection refused, timeouts)
- Provides most detailed diagnostic information

### 2. Enhanced `get_items()` Method
- **Attempt 1:** client.request() with extended mode (captures HTTP codes)
- **Attempt 2:** client.request() with SSL verification disabled
- **Attempt 3:** Raw urllib fallback for deepest diagnostics

### 3. Better Logging
All requests now log:
- HTTP response codes (200, 403, 429, 503, etc.)
- Content length and headers
- Specific error types and reasons

## What You'll See in Kodi Logs

### Expected Diagnosis
When you run the addon and go to Movie Rulz:

```
[MRULZ] get_items: Making HTTP request with cert verification (extended mode)...
[MRULZ] get_items: HTTP response code: 403
[MRULZ] make_raw_request: HTTPError 403 - Forbidden
[MRULZ] make_raw_request: Error headers: ...
[MRULZ] get_items: ERROR - No HTML received from server after 3 attempts!
```

OR

```
[MRULZ] make_raw_request: URLError - [Errno -2] Name or service not known
```

OR

```
[MRULZ] make_raw_request: HTTPError 429 - Too Many Requests
```

## How to Deploy

1. **Copy the file** `mrulz.py` to your Kodi installation:
   ```
   Your_Kodi_Profile/.kodi/addons/plugin.video.deccandelight/resources/scrapers/mrulz.py
   ```

2. **Restart Kodi** or reload the addon

3. **Check the log file** while testing Movie Rulz

## Where to Find Kodi Logs

- **Windows:** `%APPDATA%\kodi\temp\kodi.log`
- **Android:** Device logs or through Kodi's built-in log viewer
- **Linux:** `~/.kodi/temp/kodi.log`

## Key Lines to Watch For

Search the log for these patterns:

| Pattern | What it Means |
|---------|---------------|
| `HTTP response code: 403` | Cloudflare is blocking Kodi (bot detection) |
| `HTTP response code: 429` | Rate limiting - too many requests |
| `HTTP response code: 502/503` | Server/gateway error |
| `URLError` | Network-level error (DNS, connection refused) |
| `Found 20 movie items` | Success! Scraper worked |

## What We're Testing For

This update will answer:
1. **Is Cloudflare blocking us?** (403 response)
2. **Is it a network error?** (URLError)
3. **Is the domain actually down?** (502/503)
4. **Is there response body but empty?** (200 but no content)
5. **Can we get past the first request?** (any successful response)

## After Diagnosis

Once we see the actual error code/reason:
- **403:** Need Cloudflare bypass (cloudflare-scraper, FlareSolverr, etc.)
- **429:** Need request delays and user-agent rotation
- **502/503:** Try alternative mirror domains (.claims, .travel, .bargains, etc.)
- **URLError:** Network issue - check connectivity or try alternative domain
- **Success (200):** But parsing fails → JavaScript rendering needed

## Important Note

The `settings.xml` is already configured with domain change option:
**Settings → Movie Rulz Settings → Movie Rulz Domain URL**

You can try different domains if more are discovered:
- `https://www.5movierulz.viajes/` (current)
- `https://www.5movierulz.claims/`
- `https://www.4movierulz.ph/`

---

**Ready to test?** Deploy the updated `mrulz.py` to Kodi and run the addon, then check logs! 
The diagnostic output will tell us exactly what's happening.
