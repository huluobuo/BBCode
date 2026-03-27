; NSIS Installation Script for BBCode
; NSIS Installer for BBCode

; Include Modern UI
!include "MUI2.nsh"

; Application Information
!define APPNAME "BBCode"
!define COMPANYNAME "huluobuo"
!define DESCRIPTION "BBCode - Python IDE"
!define VERSIONMAJOR 2
!define VERSIONMINOR 0
!define VERSIONBUILD 2
!define VERSIONPATCH 1
!define HELPURL "https://github.com/huluobuo/BBCode"
!define UPDATEURL "https://github.com/huluobuo/BBCode/releases"
!define ABOUTURL "https://github.com/huluobuo/BBCode"

; Installer Output File
OutFile "BBCode_Setup.exe"

; Default Installation Directory (User Profile)
InstallDir "$LOCALAPPDATA\BBCode"

; Get Installation Directory from Registry (if already installed)
InstallDirRegKey HKCU "Software\BBCode" "Install_Dir"

; Request User Level (No Admin Required)
RequestExecutionLevel user

; Installer Icon
!define MUI_ICON "res\bbc.ico"
!define MUI_UNICON "res\bbc.ico"

; UI Settings
!define MUI_ABORTWARNING
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\nsis3-metro.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\nsis3-metro.bmp"

; Welcome Page
!insertmacro MUI_PAGE_WELCOME

; License Agreement Page
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"

; Installation Directory Selection Page
!insertmacro MUI_PAGE_DIRECTORY

; Installation Page
!insertmacro MUI_PAGE_INSTFILES

; Finish Page - Add Run Option
!define MUI_FINISHPAGE_RUN "$INSTDIR\BBCode.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Run BBCode"
!insertmacro MUI_PAGE_FINISH

; Uninstall Pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language Settings
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.${VERSIONPATCH}"
VIAddVersionKey "ProductName" "BBCode"
VIAddVersionKey "CompanyName" "${COMPANYNAME}"
VIAddVersionKey "LegalCopyright" "Copyright (C) 2026 huluobuo"
VIAddVersionKey "FileDescription" "${DESCRIPTION}"
VIAddVersionKey "FileVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.${VERSIONPATCH}"
VIAddVersionKey "ProductVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.${VERSIONPATCH}"

; Installation Section
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Add Main Program Files
    File "BBCode.exe"
    File "BBCode.bat"
    File "BBCodew.bat"
    File "launcher.py"
    File "pyvenv.cfg"
    File "LICENSE.txt"
    File "README.md"
    
    ; Create Directories and Copy Contents
    SetOutPath "$INSTDIR\Scripts"
    File /r "Scripts\*.*"
    
    SetOutPath "$INSTDIR\Lib"
    File /r "Lib\*.*"
    
    SetOutPath "$INSTDIR\bbcode"
    File /r "bbcode\*.*"
    
    SetOutPath "$INSTDIR\data"
    File /r "data\*.*"
    
    SetOutPath "$INSTDIR\licenses"
    File /r "licenses\*.*"
    
    SetOutPath "$INSTDIR\locale"
    File /r "locale\*.*"
    
    SetOutPath "$INSTDIR\python"
    File /r "python\*.*"
    
    SetOutPath "$INSTDIR\res"
    File /r "res\*.*"
    
    ; Create Start Menu Shortcuts
    CreateDirectory "$SMPROGRAMS\BBCode"
    CreateShortcut "$SMPROGRAMS\BBCode\BBCode.lnk" "$INSTDIR\BBCode.exe" "" "$INSTDIR\res\bbc.ico" 0
    CreateShortcut "$SMPROGRAMS\BBCode\Uninstall BBCode.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\res\bbc.ico" 0
    
    ; Create Desktop Shortcut
    CreateShortcut "$DESKTOP\BBCode.lnk" "$INSTDIR\BBCode.exe" "" "$INSTDIR\res\bbc.ico" 0
    
    ; Create Uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Write Registry Information (Current User)
    WriteRegStr HKCU "Software\BBCode" "Install_Dir" "$INSTDIR"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "DisplayName" "BBCode"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "QuietUninstallString" '"$INSTDIR\uninstall.exe" /S'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "InstallLocation" "$INSTDIR"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "DisplayIcon" "$INSTDIR\res\bbc.ico"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "HelpLink" "${HELPURL}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.${VERSIONPATCH}"
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode" "NoRepair" 1
SectionEnd

; Uninstall Section
Section "Uninstall"
    ; Delete Start Menu Shortcuts
    Delete "$SMPROGRAMS\BBCode\BBCode.lnk"
    Delete "$SMPROGRAMS\BBCode\Uninstall BBCode.lnk"
    RMDir "$SMPROGRAMS\BBCode"
    
    ; Delete Desktop Shortcut
    Delete "$DESKTOP\BBCode.lnk"
    
    ; Delete Installed Files
    Delete "$INSTDIR\BBCode.exe"
    Delete "$INSTDIR\BBCode.bat"
    Delete "$INSTDIR\BBCodew.bat"
    Delete "$INSTDIR\launcher.py"
    Delete "$INSTDIR\main.py"
    Delete "$INSTDIR\pyvenv.cfg"
    Delete "$INSTDIR\LICENSE.txt"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\uninstall.exe"
    
    ; Delete Directories
    RMDir /r "$INSTDIR\Scripts"
    RMDir /r "$INSTDIR\Lib"
    RMDir /r "$INSTDIR\bbcode"
    RMDir /r "$INSTDIR\data"
    RMDir /r "$INSTDIR\licenses"
    RMDir /r "$INSTDIR\locale"
    RMDir /r "$INSTDIR\python"
    RMDir /r "$INSTDIR\res"
    
    ; Remove Installation Directory
    RMDir "$INSTDIR"
    
    ; Delete Registry Keys (Current User)
    DeleteRegKey HKCU "Software\BBCode"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\BBCode"
SectionEnd
