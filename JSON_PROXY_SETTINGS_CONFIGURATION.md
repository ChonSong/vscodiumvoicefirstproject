# JSON Extension Proxy Settings Configuration

## Overview

The JSON extension in Theia/VS Code relies on HTTP proxy settings to download JSON schemas from schemastore.org. Since we've added a proxy endpoint to bypass CORS issues, we need to configure these settings correctly.

## Settings Required

The JSON extension uses these settings:

1. **`http.proxy`**: Proxy server URL (format: `http://host:port` or `http://user:pass@host:port`)
2. **`http.proxyStrictSSL`**: Whether to validate SSL certificates strictly (default: `true`)
3. **`http.proxyAuthorization`**: Proxy authorization header (usually `null` if credentials are in the URL)

## Current Status

### ✅ What's Configured

1. **Proxy Endpoint Created**: `/proxy/schemastore/{path}` endpoint in `main.py`
   - This bypasses CORS by proxying requests to schemastore.org
   - Available at: `http://localhost:8000/proxy/schemastore/api/json/catalog.json`

2. **Settings File Created**: `theia-fresh/examples/browser/.theia/settings.json`
   - Contains HTTP proxy settings
   - Currently has `json.schemaDownload.enable: false` to prevent CORS errors

### ⚠️ Configuration Options

Since we're running locally and have a proxy endpoint, you have two options:

#### Option 1: Disable Schema Downloads (Recommended for Now)

This is what the commit message suggests:

```json
{
  "json.schemaDownload.enable": false
}
```

**Pros:**
- Prevents CORS errors
- No proxy configuration needed
- Works immediately

**Cons:**
- JSON schemas won't be automatically downloaded
- Manual schema configuration required

#### Option 2: Use Local Proxy Endpoint

If you want to enable schema downloads through our proxy:

1. **Configure HTTP Proxy** (if using a system proxy):
   ```json
   {
     "http.proxy": "http://localhost:8000",
     "http.proxyStrictSSL": false,
     "http.proxyAuthorization": null,
     "json.schemaDownload.enable": true
   }
   ```

   **Note**: This might not work directly because the JSON extension expects a traditional HTTP proxy, not our REST API endpoint.

2. **Alternative: Modify JSON Extension** (Advanced):
   - Modify the JSON extension to use our `/proxy/schemastore/{path}` endpoint
   - This requires changes to the extension code

## Recommended Configuration

Based on the commit message (which mentions disabling schema downloads), the recommended configuration is:

```json
{
  "http.proxy": "",
  "http.proxyStrictSSL": true,
  "http.proxyAuthorization": null,
  "json.schemaDownload.enable": false
}
```

## How to Apply Settings

### Method 1: Workspace Settings (Theia Browser Example)

Settings file: `theia-fresh/examples/browser/.theia/settings.json`

This file has been created with the recommended settings.

### Method 2: User Settings (Theia Preferences)

In Theia UI:
1. Go to **File** > **Preferences** > **Settings**
2. Search for "proxy" or "json schema"
3. Configure the settings

Or edit the user settings file directly (location varies by Theia installation).

### Method 3: Environment Variables

For Node.js extensions running in Theia backend:

```bash
export http_proxy=http://localhost:8000
export https_proxy=http://localhost:8000
export HTTP_PROXY=http://localhost:8000
export HTTPS_PROXY=http://localhost:8000
```

## Verification

### Check Current Settings

1. **In Theia UI**:
   - Open Settings (Ctrl+,)
   - Search for "http.proxy"
   - Verify settings are correct

2. **Check Settings File**:
   ```bash
   cat theia-fresh/examples/browser/.theia/settings.json
   ```

### Test Proxy Endpoint

Test that the proxy endpoint works:

```bash
curl http://localhost:8000/proxy/schemastore/api/json/catalog.json
```

Expected: JSON response with schema catalog

### Test JSON Extension

1. Open a JSON file in Theia
2. Check if schema validation works
3. Check browser console for CORS errors

## Troubleshooting

### Issue: CORS Errors Still Occurring

**Solution**: Ensure `json.schemaDownload.enable` is set to `false`

### Issue: Proxy Not Working

**Check**:
1. Backend server is running on port 8000
2. Proxy endpoint is accessible: `http://localhost:8000/proxy/schemastore/api/json/catalog.json`
3. Settings file is in the correct location

### Issue: JSON Schema Validation Not Working

**Solution**:
1. Manually configure schemas in `settings.json`:
   ```json
   {
     "json.schemas": [
       {
         "fileMatch": ["package.json"],
         "url": "http://localhost:8000/proxy/schemastore/api/json/catalog.json"
       }
     ]
   }
   ```

## Related Files

- `main.py` - Proxy endpoint implementation
- `theia-fresh/examples/browser/.theia/settings.json` - Workspace settings
- `theia-fresh/packages/plugin-ext/src/hosted/node/plugin-host-proxy.ts` - Proxy resolver implementation

## References

- [VS Code Network Settings](https://code.visualstudio.com/docs/setup/network)
- [VS Code JSON Extension](https://code.visualstudio.com/docs/languages/json)
- Commit a652854: Added proxy endpoint for schemastore.org

---

**Status**: ✅ Settings file created. Configuration depends on whether you want to enable schema downloads or disable them to avoid CORS.

