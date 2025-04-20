[app]

# (string) title of your application
title = Qwota_Messenger

# (string) package.name domain of your application (needed for android/ios package)
package.name = qwota.messenger
# (string) package.domain domain of your application (needed for android/ios package)
package.domain = org.example

# (string) source.path path to main application python file
source.path = MB.py

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,atlas,ttf

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of inclusions using pattern matching
# Do not remove the default include of main.py
source.include_patterns = main.py, images/*, fonts/*

# (list) List of exclusions using pattern matching
source.exclude_patterns = license.txt, README.md

# (string) Icon file (for android, iOS, desktop)
icon.filename = img/love.png  

# (string) Presplash image file (for android, iOS)
presplash.filename = img/S.jpg

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 33  # Или 30, 31, в зависимости от вашего SDK

# (int) Android SDK version to use
android.sdk = 33  # Или 30, 31, в зависимости от вашего SDK

# (int) Android NDK version to use
android.ndk = 21c # Проверьте, какая версия NDK у вас установлена (часто 21c)

# (string) Android NDK directory (if automatic download fails)
#android.ndk_path = /путь/к/вашему/android-ndk

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Supported orientations
orientation = portrait

# (list) requirements
requirements = kivy==2.0.0, matplotlib, webbrowser, pillow, pygame

# (str) Supported archs for build
android.archs = arm64-v8a

# (str) The Java version to use
android.gradle_java_version = 11
