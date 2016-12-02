@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1

IF %argC% == 1 (
    mkdir %1

    :COPYFILES
    if not exist queue\* (goto NOFILES)

    FOR %%f IN (queue\*) DO (
        move "%%f" %1
REM     HandBrakeCLI-10bit.exe -i "%~1\%%~nxf" -o "%%~nf.mp4" -e x265_10bit --encoder-profile main10 -E copy --all-audio --all-subtitles
        HandBrakeCLI-10bit.exe --vfr -b 1024k -i "%~1\%%~nxf" -o "%%~nf.mp4" -e x265_10bit --encoder-profile main10 -E copy --all-audio --all-subtitles
        goto COPYFILES
    )

    :NOFILES
    set /p DUMMY=Job done! Hit ENTER to continue...
    goto :EOF

) ELSE (
    echo Usage: %0 working_dir
)
