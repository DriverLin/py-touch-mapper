@echo off
adb push app-debug.apk /data/local/tmp/app-debug.jar
adb shell CLASSPATH=/data/local/tmp/app-debug.jar  app_process ./ com.genymobile.scrcpy.Server 1.0
pause