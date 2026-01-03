# HACS Installation Fix for v1.0.0.2 and v1.0.0.4

## Problem

HACS fails to download and install the Bambu Lab integration with errors like:
```
Failed to download https://github.com/ian-morgan99/ha-bambulab/releases/download/v1.0.0.4/bambu_lab.zip
```

## Root Cause

The `bambu_lab.zip` file is missing from the v1.0.0.2 and v1.0.0.4 release assets. The Publish workflow that creates this file was added in v1.0.0.4, but it didn't run automatically for that release (or retroactively for v1.0.0.2).

## Solution for Repository Owners

You need to generate and upload the `bambu_lab.zip` file to the releases. There are three ways to do this:

### Option 1: Manually Trigger the Publish Workflow (Recommended)

The easiest solution is to trigger the existing workflow:

1. Go to [Actions > Publish](https://github.com/ian-morgan99/ha-bambulab/actions/workflows/publish.yml)
2. Click the "Run workflow" dropdown button
3. Select the `main` branch
4. Enter the release tag (e.g., `v1.0.0.4`)
5. Click "Run workflow"
6. Wait for the workflow to complete (it will automatically upload the zip to the release)

Repeat for v1.0.0.2 if needed.

### Option 2: Build and Upload Manually Using the Script

If you prefer to build locally:

```bash
# Clone the repository at the specific tag
git clone https://github.com/ian-morgan99/ha-bambulab.git
cd ha-bambulab
git checkout v1.0.0.4

# Build the zip file
./scripts/build_release_zip.sh 1.0.0.4

# Upload to the release (requires gh CLI)
gh release upload v1.0.0.4 custom_components/bambu_lab/bambu_lab.zip
```

Repeat for v1.0.0.2 if needed:
```bash
git checkout v1.0.0.2
./scripts/build_release_zip.sh 1.0.0.2
gh release upload v1.0.0.2 custom_components/bambu_lab/bambu_lab.zip
```

### Option 3: Create a New Release

If you prefer a fresh start:

```bash
# Tag and create a new release (e.g., v1.0.0.5)
git tag v1.0.0.5
git push origin v1.0.0.5

# Then create the release via GitHub UI or CLI
gh release create v1.0.0.5 --title "v1.0.0.5" --notes "Fix HACS installation by adding release zip"
```

The Publish workflow will automatically run and attach the zip file.

## Verification

After uploading the zip file, verify it's accessible:

```bash
curl -I https://github.com/ian-morgan99/ha-bambulab/releases/download/v1.0.0.4/bambu_lab.zip
```

You should see `HTTP/1.1 200 OK` (not `404 Not Found`).

You can also visit the release page and confirm that `bambu_lab.zip` is listed under Assets:
https://github.com/ian-morgan99/ha-bambulab/releases/tag/v1.0.0.4

## For Users Experiencing This Issue

If you're a user trying to install this integration via HACS and encountering download errors:

1. **Wait for the fix**: The repository owner needs to upload the missing zip file using one of the methods above
2. **Install from a different version**: Try installing from v1.0.0.1 if that has the zip file
3. **Manual installation**: You can manually install the integration:
   - Download the repository as a zip from GitHub
   - Extract it
   - Copy the `custom_components/bambu_lab` folder to your Home Assistant `custom_components` directory
   - Restart Home Assistant

## Future Releases

For all future releases (v1.0.0.5 and beyond), the Publish workflow will automatically:
1. Run when a release is published
2. Update the manifest.json version to match the release tag
3. Create the `bambu_lab.zip` file
4. Upload it to the release assets

No manual intervention will be needed.

## Technical Details

The integration uses HACS with `zip_release: true` configuration, which tells HACS to download a pre-built zip file from the release assets instead of downloading the entire repository. This is more efficient and ensures users get exactly the files intended for that release.

The expected download URL format is:
```
https://github.com/{owner}/{repo}/releases/download/{tag}/{filename}
```

For this repository:
```
https://github.com/ian-morgan99/ha-bambulab/releases/download/v1.0.0.4/bambu_lab.zip
```

## Related Files

- [Publish Workflow](../.github/workflows/publish.yml) - Automates zip creation and upload
- [Build Script](../scripts/build_release_zip.sh) - Manual zip building script
- [Release Documentation](../RELEASE.md) - Full release process documentation
- [HACS Configuration](../hacs.json) - HACS integration settings
