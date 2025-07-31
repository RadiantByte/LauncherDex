# LauncherDex

This project builds the `launcher.dex` file used by [LeviLaunchroid](https://github.com/LiteLDev/LeviLaunchroid), a third-party Minecraft Bedrock Edition launcher. The generated DEX file contains essential Java classes that enable Minecraft launching functionality within the LeviLaunchroid Android application.

## About

LeviLaunchroid is a third-party launcher for Minecraft Bedrock Edition that requires specific Java classes to function properly. This project compiles those classes into a DEX file (`launcher.dex`) that gets placed in the LeviLaunchroid app's assets directory (`app/src/main/assets/launcher.dex`).



## Prerequisites

1. **Java Development Kit (JDK) 21 or higher**
   - Download from: https://adoptium.net/
   - Verify installation: `java -version`

2. **Android SDK**
   - Install Android Studio or standalone SDK tools
   - Set the `ANDROID_HOME` environment variable to your Android SDK path
   - **Windows**: `ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk`

3. **Python 3.6+** (for the DEX modification script)
   - Download from: https://python.org/

## Building the DEX File

```batch
# Clone the repository
git clone https://github.com/RadiantByte/LauncherDex.git
cd LauncherDex

# Set your Android SDK path
set ANDROID_HOME=C:\path\to\your\android\sdk

# Build launcher.dex
build.bat

# Run Python script to get the final DEX file for LeviLaunchroid
python modify_dex.py

# The final launcher.dex will be in build/libs/launcher.dex
```

### Output

After building, you'll find:
- **`build/libs/launcher.dex`** - The optimized DEX file for LeviLaunchroid (≈5.8KB)
- **`build/libs/LeviLauncherDex-1.0.jar`** - Intermediate JAR file (≈8.7KB)

## Integration with LeviLaunchroid

### Step 1: Build the DEX file
Follow the build instructions above to generate `launcher.dex`.

### Step 2: Copy to LeviLaunchroid
Copy the generated `launcher.dex` file to your LeviLaunchroid project.

### Step 3: Build LeviLaunchroid
Build your LeviLaunchroid app as usual. The launcher.dex will be included in the APK and loaded at runtime to provide Minecraft launching capabilities.

## What's in the DEX file?

The optimized `launcher.dex` contains only the essential classes needed for Minecraft launching:

### Included Classes:
- **`com.mojang.minecraftpe.Launcher`**
- **`com.mojang.minecraftpe.NotificationListenerService`**
- **`com.mojang.minecraftpe.store.amazonappstore.AmazonAppStore`**
- **`com.mojang.minecraftpe.store.googleplay.GooglePlayStore`**

### Removed Classes:
- `MainActivity`
- `FilePickerManagerHandler`
- `ExtraLicenseResponseData`
- `Product`, `Purchase`, `Store`, `StoreListener`

The build process automatically removes these unused classes using the `modify_dex.py` script, reducing the final DEX file size from ~8KB to ~6KB.

## Related Projects

- **[LeviLaunchroid](https://github.com/LiteLDev/LeviLaunchroid)**