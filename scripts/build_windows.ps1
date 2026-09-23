[CmdletBinding()]
param(
    [string]$PythonPath = ".\.release-venv\Scripts\python.exe",
    [switch]$AllowCondaForExploration
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$python = if ([System.IO.Path]::IsPathRooted($PythonPath)) {
    [System.IO.Path]::GetFullPath($PythonPath)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $projectRoot $PythonPath))
}

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Python executable not found: $python"
}

$basePrefix = (& $python -c "import sys; print(sys.base_prefix)").Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Unable to determine the base Python interpreter."
}
$condaMetadata = Join-Path $basePrefix "conda-meta"
if ((Test-Path -LiteralPath $condaMetadata -PathType Container) -and -not $AllowCondaForExploration) {
    throw (
        "Release builds require a standard CPython environment, but this interpreter " +
        "inherits from Conda at $basePrefix. Use a clean standard CPython environment. " +
        "-AllowCondaForExploration is permitted only for non-release investigation."
    )
}

$specPath = Join-Path $projectRoot "PhaseAnnotator.spec"
$workPath = Join-Path $projectRoot "build\pyinstaller"
$distPath = Join-Path $projectRoot "dist"

Push-Location $projectRoot
try {
    & $python -m PyInstaller `
        --noconfirm `
        --clean `
        --workpath $workPath `
        --distpath $distPath `
        $specPath
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }
} finally {
    Pop-Location
}

$applicationRoot = Join-Path $distPath "PhaseAnnotator"
$requiredFiles = @(
    (Join-Path $applicationRoot "PhaseAnnotator.exe"),
    (Join-Path $applicationRoot "_internal\phase_annotator\config\default_appendectomy.json"),
    (Join-Path $applicationRoot "_internal\phase_annotator\config\cholec80_cholecystectomy.json")
)

foreach ($requiredFile in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Release-critical packaged file is missing: $requiredFile"
    }
}

$artifactFiles = Get-ChildItem -LiteralPath $applicationRoot -Recurse -File
$artifactBytes = ($artifactFiles | Measure-Object -Property Length -Sum).Sum
Write-Output "Built: $applicationRoot"
Write-Output "Base Python: $basePrefix"
Write-Output ("Files: {0}" -f $artifactFiles.Count)
Write-Output ("Size: {0:N1} MiB" -f ($artifactBytes / 1MB))
Write-Output "Verified: executable and both packaged procedure resources"
