del main.pptx
rmdir /q /s src
xcopy base\ src\ /E
del /S src\*.empty
py main.py
"C:Program Files\WinRAR\WinRAR.exe" a -afzip -r -ep1 main.pptx src\*