del main.pptx
rmdir /q /s out
xcopy base\ out\ /E
del /S out\*.empty
py src\main.py
"C:Program Files\WinRAR\WinRAR.exe" a -afzip -r -ep1 main.pptx out\*