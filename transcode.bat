@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1

IF %argC% == 2 (
    for /R %2 %%f in (*) do HandBrakeCLI-10bit.exe -i "%%f" -o "%%~nf.%1" -e x265_10bit --encoder-profile main10 -E copy --all-audio --all-subtitles
) ELSE (
    echo Usage: %0 format srcdir
)
