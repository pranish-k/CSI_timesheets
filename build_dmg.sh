#!/bin/bash
set -e

# ====== CONFIGURE THESE ======
SIGN_IDENTITY="Developer ID Application: Pranish Khanal (7WXW567MR7)"
NOTARY_PROFILE="notary-csi"
APP_NAME="CSI Timesheet Generator"
DMG_NAME="CSI_Timesheet_Generator.dmg"
# =============================

echo "=== Building $APP_NAME ==="

source .venv/bin/activate
pip install pyinstaller --quiet

# Clean previous builds
rm -rf build dist *.dmg

# Build the app
echo "Building .app bundle..."
pyinstaller CSI_Timesheet_Generator.spec --clean

if [ ! -d "dist/$APP_NAME.app" ]; then
    echo "ERROR: App bundle was not created!"
    exit 1
fi

# Sign every binary inside the bundle (deep), with hardened runtime + entitlements
echo "Code signing..."
codesign --force --deep --options runtime --timestamp \
  --entitlements entitlements.plist \
  --sign "$SIGN_IDENTITY" \
  "dist/$APP_NAME.app"

# Verify signature
echo "Verifying signature..."
codesign --verify --deep --strict --verbose=2 "dist/$APP_NAME.app"

# Create DMG
echo "Creating DMG..."
mkdir -p dmg_temp
cp -R "dist/$APP_NAME.app" dmg_temp/
ln -s /Applications dmg_temp/Applications

hdiutil create -volname "$APP_NAME" \
  -srcfolder dmg_temp -ov -format UDZO \
  "$DMG_NAME"

rm -rf dmg_temp

# Sign the DMG itself
echo "Signing DMG..."
codesign --force --sign "$SIGN_IDENTITY" --timestamp "$DMG_NAME"

# Notarize
echo "Submitting for notarization (this can take 1-10 min)..."
xcrun notarytool submit "$DMG_NAME" \
  --keychain-profile "$NOTARY_PROFILE" \
  --wait

# Staple the notarization ticket so it works offline
echo "Stapling..."
xcrun stapler staple "$DMG_NAME"

# Verify
echo "Verifying notarization..."
spctl -a -t open --context context:primary-signature -v "$DMG_NAME"

echo ""
echo "=== Build Complete ==="
ls -lh "$DMG_NAME"
echo ""
echo "DMG is signed, notarized, and ready to distribute!"
