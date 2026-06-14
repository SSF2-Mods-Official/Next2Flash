# Deploy latest roundtrip.swf to ADL + PSB folders and print verification.
$ErrorActionPreference = "Stop"
$App = Split-Path -Parent $PSScriptRoot
Set-Location $App

$Rt = Join-Path $App "converted\ssf2-roundtrip\roundtrip.swf"
if (-not (Test-Path $Rt)) {
    Write-Error "Missing $Rt — run: py -3 n2f.py ssf2 --no-overlay first"
}

py -3 -c @"
import hashlib, os, ssf2_runner as s
rt = os.path.abspath(r'$Rt')
adl = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1'
psb = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\PSB 1.4 v2'
def sha(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]
h = sha(rt)
for label, root in [('ADL', adl), ('PSB', psb)]:
    info = s.deploy_swf(rt, root)
    dest = info['deployed']
    print(f'{label}: {dest}')
    print(f'  size={info[\"size\"]} sha={sha(dest)} match={sha(dest)==h}')
print('Done. Quit old ADL/game windows, then launch from VS Code or ADL.')
"@
