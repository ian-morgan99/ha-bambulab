# Troubleshooting HACS Installation Issues

## Common Issues and Solutions

### Issue 1: HACS Download Fails with 404 Error

**Symptoms:**
```
Failed to download https://github.com/ian-morgan99/ha-bambulab/releases/download/v1.0.0.4/bambu_lab.zip
```
or
```
Failed to download https://github.com/ian-morgan99/ha-bambulab/releases/download/tags/v1.0.0.4/bambu_lab.zip
```

**Root Causes:**

#### A. Missing Release Zip File
If the error shows a URL **without** `/tags/` in the path, the release zip file is missing from that release.

**Solution:**  
The repository owner needs to upload the zip file. See [HACS_INSTALLATION_FIX.md](HACS_INSTALLATION_FIX.md) for instructions.

#### B. HACS Bug (versions 2.0.2 and 2.0.3)
If the error shows a URL **with** `/tags/` in the path (e.g., `.../releases/download/tags/v1.0.0.4/...`), this is a known bug in HACS versions 2.0.2 and 2.0.3.

**The Bug:**  
HACS incorrectly constructs the download URL by inserting `/tags/` before the version tag:
- ❌ **Incorrect**: `https://github.com/.../releases/download/tags/v1.0.0.4/bambu_lab.zip`
- ✅ **Correct**: `https://github.com/.../releases/download/v1.0.0.4/bambu_lab.zip`

GitHub doesn't recognize URLs with `/tags/` in that position, resulting in 404 errors.

**Solution - Update HACS:**
1. Check your HACS version in Home Assistant: `Settings` > `Integrations` > `HACS`
2. If you're on version 2.0.2 or 2.0.3, update to a newer version:
   - Go to `Settings` > `Updates`
   - Look for HACS update
   - Click "Update" 

**Solution - Manual Update if Auto-Update Fails:**

If the HACS auto-update fails due to this bug (it tries to update itself using the broken URL), you'll need to manually update HACS:

```bash
# SSH into your Home Assistant
# Then run:
wget -O - https://get.hacs.xyz | bash
```

After manual update, restart Home Assistant and try installing the Bambu Lab integration again.

**Solution - Workaround (Temporary):**

If you cannot update HACS, you can install the integration manually:
1. Download the latest release from: https://github.com/ian-morgan99/ha-bambulab/releases/latest
2. Extract the zip file
3. Copy the `custom_components/bambu_lab` folder to your Home Assistant `custom_components` directory
4. Restart Home Assistant
5. Add the integration via UI: `Settings` > `Devices & Services` > `Add Integration` > search for "Bambu Lab"

### Issue 2: HACS Validation Workflow Fails

**Symptoms:**  
The GitHub Actions workflow `.github/workflows/validate.yml` fails.

**Common Causes:**

1. **Invalid hacs.json**: Check that your `hacs.json` follows the correct format
2. **Missing required topics**: Repository must have the `home-assistant` topic
3. **Missing required files**: Repository must have a `README.md`

**How to Test Locally:**

The validation workflow uses the official HACS action. You can't run it locally, but you can verify your hacs.json is valid JSON:

```bash
python -m json.tool hacs.json
```

### Issue 3: Integration Updates Don't Show in HACS

**Symptoms:**  
New releases are published but don't appear as available updates in HACS.

**Solutions:**

1. **Force refresh HACS:**
   - Go to HACS
   - Click the three dots menu (top right)
   - Select "Reload HACS configuration"

2. **Clear browser cache:**  
   Sometimes the UI is cached in your browser

3. **Check release format:**  
   - Releases must have a semantic version tag (e.g., `v1.0.0`, not `1.0.0` or `release-1.0.0`)
   - The tag should match the version in `manifest.json`

## Related Known Issues

### HACS Version Compatibility

| HACS Version | Status | Notes |
|-------------|---------|-------|
| 2.0.0 | ✅ Working | Stable |
| 2.0.1 | ✅ Working | Stable |
| 2.0.2 | ⚠️ Has Bug | `/tags/` URL bug - update to newer version |
| 2.0.3 | ⚠️ Has Bug | `/tags/` URL bug - update to newer version |
| 2.0.4+ | ✅ Working | Bug fixed in later versions |

### References

- [HACS Issue #4331: Update to 2.0.2 fails - wrong URL](https://github.com/hacs/integration/issues/4331)
- [HACS Issue #4346: HACS does not update from 2.0.1 to 2.0.2](https://github.com/hacs/integration/issues/4346)
- [HACS Issue #4385: Problem with update with 2.0.3 and 2.0.2](https://github.com/hacs/integration/issues/4385)
- [HACS Official Documentation](https://hacs.xyz/)

## Getting Help

If you continue to experience issues:

1. **Check the HACS logs**: `Settings` > `System` > `Logs`, search for "hacs"
2. **Check Home Assistant logs**: Look for any error messages related to custom components
3. **Open an issue**: https://github.com/ian-morgan99/ha-bambulab/issues (Note: Discord invites may expire - check the repository for current community links)

When reporting issues, please include:
- Your HACS version
- Your Home Assistant version  
- The exact error message
- The URL that failed (if shown in logs)
- Whether the URL contains `/tags/`
