mkdir done
mkdir trash
mkdir working

SET curpath=%~dp0

cd queue
for /D %%r in (*.*) do (
  cd "%%r"
  for /D %%d in (*.*) do (
    "C:\Program Files\7-Zip\7z.exe" a -tzip "%curpath%working\%%d.zip" "%%d"
  )
  cd ..

:: from queue
  mkdir "..\done\%%r"
  move "..\working\*" "..\done\%%r"
  move "%%r" ..\trash
)

cd ..
