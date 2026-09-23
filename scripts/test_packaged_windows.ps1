[CmdletBinding()]
param(
    [string]$ExecutablePath = ".\dist\PhaseAnnotator\PhaseAnnotator.exe",
    [int]$TimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$executable = if ([System.IO.Path]::IsPathRooted($ExecutablePath)) {
    [System.IO.Path]::GetFullPath($ExecutablePath)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $projectRoot $ExecutablePath))
}

if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
    throw "Packaged executable not found: $executable"
}

$process = Start-Process `
    -FilePath $executable `
    -ArgumentList "--artifact-smoke-test" `
    -PassThru `
    -WindowStyle Hidden

if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
    Stop-Process -Id $process.Id
    throw "Packaged artifact smoke test exceeded $TimeoutSeconds seconds."
}

if ($process.ExitCode -ne 0) {
    throw "Packaged artifact smoke test failed with exit code $($process.ExitCode)."
}

Write-Output "Packaged artifact smoke test passed: $executable"
Write-Output "Verified every registered procedure resource and MainWindow construction."
