cd queue
for /D %%r in (*.*) do (
  cd "%%r"
  for /D %%d in (*.*) do (
    "C:\Program Files\7-Zip\7z.exe" a -tzip "C:\Users\bebechien\Desktop\mm\%%d.zip" "%%d"
  )
  cd ..
  mkdir "..\done\%%r"
  mv "C:\Users\bebechien\Desktop\mm\*" "..\done\%%r\"
  mv "%%r" ..\trash
)

cd ..
