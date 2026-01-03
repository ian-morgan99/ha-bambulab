# Release Process

This document describes how to create a release for the Bambu Lab integration.

## Prerequisites

- You need write access to this repository
- All changes should be merged to the main branch before creating a release

## Creating a Release

### Option 1: Using GitHub UI

1. Go to the [Releases page](../../releases)
2. Click "Draft a new release"
3. Click "Choose a tag"
4. Type the new version number (e.g., `v1.0.0`) and click "Create new tag"
5. Fill in the release title (e.g., `v1.0.0`)
6. Add release notes describing what's new or changed
7. Click "Publish release"

The [publish workflow](../../actions/workflows/publish.yml) will automatically:
- Update the manifest.json version to match the tag
- Create bambu_lab.zip containing the integration files
- Attach the zip file to the release

### Option 2: Using GitHub CLI

```bash
# Create and publish a release
gh release create v1.0.0 \
  --title "v1.0.0" \
  --notes "Release notes here" \
  --repo ian-morgan99/ha-bambulab
```

The publish workflow will run automatically and attach the zip file.

## Version Numbering

This project uses semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes (backwards compatible)

Always prefix version tags with `v` (e.g., `v1.0.0`).

## HACS Installation

Once a release is published with the zip file attached, HACS will be able to install the integration automatically. Users can install it by:

1. Opening HACS in Home Assistant
2. Clicking "Integrations"
3. Clicking the menu (⋮) and selecting "Custom repositories"
4. Adding `https://github.com/ian-morgan99/ha-bambulab` as an Integration
5. Finding and installing "Bambu Lab"

## Troubleshooting

### The zip file is not attached to the release

Check the [publish workflow runs](../../actions/workflows/publish.yml) to see if there were any errors. The workflow should run automatically when a release is published.

### HACS cannot download the integration

Ensure that:
- The release tag follows the format `v1.0.0` (with the `v` prefix)
- The `bambu_lab.zip` file is attached to the release
- The `hacs.json` file has `zip_release: true` and `filename: "bambu_lab.zip"`
