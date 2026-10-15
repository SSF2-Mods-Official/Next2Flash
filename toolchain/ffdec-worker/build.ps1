# Builds ffdec-worker.jar next to the bundled FFDec tree.
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$ffdec = Join-Path $root "..\ffdec"
$src = Join-Path $root "src"
$out = Join-Path $root "out"
$jar = Join-Path $ffdec "ffdec-worker.jar"

if (-not (Test-Path (Join-Path $ffdec "ffdec.jar"))) {
    throw "ffdec.jar not found at $ffdec"
}

$javac = Get-Command javac -ErrorAction SilentlyContinue
if (-not $javac) {
    throw "javac not found on PATH. Install a JDK to build the worker."
}

Remove-Item -Recurse -Force $out -ErrorAction SilentlyContinue
New-Item -ItemType Directory $out | Out-Null

$cp = @(
    (Join-Path $ffdec "ffdec.jar")
) + (Get-ChildItem (Join-Path $ffdec "lib\*.jar") | ForEach-Object { $_.FullName })
$classpath = ($cp -join ";")

$javaFiles = @(Get-ChildItem $src -Recurse -Filter *.java | ForEach-Object { $_.FullName })
if ($javaFiles.Count -eq 0) { throw "No .java sources under $src" }
Write-Host "Compiling $($javaFiles.Count) source(s)…"
& javac -encoding UTF-8 -classpath $classpath -d $out $javaFiles
if ($LASTEXITCODE -ne 0) { throw "javac failed" }

Push-Location $out
try {
    & jar --create --file $jar -C $out .
    if ($LASTEXITCODE -ne 0) {
        # Older jar syntax
        & jar cf $jar -C $out .
    }
} finally {
    Pop-Location
}

Write-Host "Wrote $jar"
