#!/bin/bash
# Script to build the release zip file for HACS distribution
# Usage: ./build_release_zip.sh [version]
# Example: ./build_release_zip.sh 1.0.0.2

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST_FILE="$REPO_ROOT/custom_components/bambu_lab/manifest.json"
BACKUP_FILE="/tmp/manifest.json.bak"

# Get version from argument or use current version from manifest
if [ -n "$1" ]; then
    VERSION="$1"
else
    VERSION=$(grep -oP '"version":\s*"\K[^"]+' "$MANIFEST_FILE")
fi

echo "Building release zip for version $VERSION"

# Create backup of manifest in /tmp
cp "$MANIFEST_FILE" "$BACKUP_FILE"

# Update manifest version
sed -i 's/"version": "[^"]*"/"version": "'"$VERSION"'"/' "$MANIFEST_FILE"

# Create zip file (matching the GitHub Actions workflow - no exclusions)
cd "$REPO_ROOT/custom_components/bambu_lab"
zip -r bambu_lab.zip .

# Restore original manifest
mv "$BACKUP_FILE" "$MANIFEST_FILE"

echo "✓ Created bambu_lab.zip"
echo "  Location: $REPO_ROOT/custom_components/bambu_lab/bambu_lab.zip"
echo ""

# Check if we should publish the release
if [ "$PUBLISH" = "true" ]; then
    echo "Creating GitHub release v$VERSION..."
    
    # Create git tag if it doesn't exist
    if ! git rev-parse "v$VERSION" >/dev/null 2>&1; then
        git tag -a "v$VERSION" -m "Release version $VERSION"
        git push origin "v$VERSION"
        echo "✓ Created and pushed tag v$VERSION"
    else
        echo "✓ Tag v$VERSION already exists"
    fi
    
    # Create or update the release
    if gh release view "v$VERSION" >/dev/null 2>&1; then
        echo "✓ Release v$VERSION already exists, uploading zip..."
        gh release upload "v$VERSION" "$REPO_ROOT/custom_components/bambu_lab/bambu_lab.zip" --clobber
    else
        echo "✓ Creating new release v$VERSION..."
        gh release create "v$VERSION" \
            --title "v$VERSION" \
            --notes "Release version $VERSION" \
            "$REPO_ROOT/custom_components/bambu_lab/bambu_lab.zip"
    fi
    
    echo "✓ Published release v$VERSION"
else
    echo "To upload to a release, use:"
    echo "  gh release upload v$VERSION $REPO_ROOT/custom_components/bambu_lab/bambu_lab.zip"
    echo ""
    echo "Or run with PUBLISH=true to automatically create and publish the release:"
    echo "  PUBLISH=true ./scripts/build_release_zip.sh $VERSION"
fi
