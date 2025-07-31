@echo off
echo Building LeviLauncherDex...

REM Check if ANDROID_HOME is set
if "%ANDROID_HOME%"=="" (
    echo ERROR: ANDROID_HOME environment variable is not set
    echo Please set ANDROID_HOME to your Android SDK path
    pause
    exit /b 1
)

REM Check if Java is available
java -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java is not installed or not in PATH
    echo Please install Java and add it to your PATH
    pause
    exit /b 1
)

REM Check for Android platform android.jar
set ANDROID_JAR=
for /f "delims=" %%i in ('dir /b /ad "%ANDROID_HOME%\platforms" ^| sort /r') do (
    if exist "%ANDROID_HOME%\platforms\%%i\android.jar" (
        set "ANDROID_JAR=%ANDROID_HOME%\platforms\%%i\android.jar"
        goto :found_android_jar
    )
)

:found_android_jar
if not defined ANDROID_JAR (
    echo ERROR: No android.jar found in Android SDK platforms
    pause
    exit /b 1
)

echo Using platform: %ANDROID_JAR%

REM Create build directories
if not exist "build\classes" mkdir build\classes
if not exist "build\libs" mkdir build\libs

echo Compiling Java sources...
javac -cp "%ANDROID_JAR%" -d build\classes src\main\java\com\mojang\minecraftpe\*.java src\main\java\com\mojang\minecraftpe\store\*.java src\main\java\com\mojang\minecraftpe\store\amazonappstore\*.java src\main\java\com\mojang\minecraftpe\store\googleplay\*.java

if errorlevel 1 (
    echo ERROR: Java compilation failed
    pause
    exit /b 1
)

echo Creating JAR file...
jar cf build\libs\LeviLauncherDex-1.0.jar -C build\classes .

if errorlevel 1 (
    echo ERROR: JAR creation failed
    pause
    exit /b 1
)

echo Converting JAR to DEX...
REM Find the latest build-tools version
for /f "delims=" %%i in ('dir /b /ad "%ANDROID_HOME%\build-tools" ^| sort /r') do (
    set BUILD_TOOLS_VERSION=%%i
    goto :found_build_tools
)

:found_build_tools
if "%BUILD_TOOLS_VERSION%"=="" (
    echo ERROR: No build-tools found in Android SDK
    pause
    exit /b 1
)

echo Using build-tools version: %BUILD_TOOLS_VERSION%

REM Try d8 first, fallback to dx
if exist "%ANDROID_HOME%\build-tools\%BUILD_TOOLS_VERSION%\d8.bat" (
    echo Using d8 tool...
    "%ANDROID_HOME%\build-tools\%BUILD_TOOLS_VERSION%\d8.bat" --output build\libs\ build\libs\LeviLauncherDex-1.0.jar
    if exist "build\libs\classes.dex" (
        move /Y build\libs\classes.dex build\libs\launcher.dex
    )
) else (
    echo Using dx tool...
    "%ANDROID_HOME%\build-tools\%BUILD_TOOLS_VERSION%\dx.bat" --dex --output=build\libs\launcher.dex build\libs\LeviLauncherDex-1.0.jar
)

if errorlevel 1 (
    echo ERROR: DEX conversion failed
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo JAR file: build\libs\LeviLauncherDex-1.0.jar
echo DEX file: build\libs\launcher.dex

REM Run the DEX modification script
echo.
echo Optimizing DEX file...
python modify_dex.py
if errorlevel 1 (
    echo Warning: DEX optimization failed. You may need to run 'python modify_dex.py' manually.
)

echo.
pause