param(
    [string]$Remote = "brais.gomez.lopez@hpc-login2.inv.usc.es",
    [string]$RemoteDir = "~/medical-qa-sft"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$localDir = Join-Path $repoRoot "artifacts\from_citius"

New-Item -ItemType Directory -Force -Path $localDir | Out-Null

Write-Host "Downloading generated artifacts and Slurm logs from $RemoteDir"
scp -r "${Remote}:$RemoteDir/artifacts" $localDir
scp -r "${Remote}:$RemoteDir/results/logs" $localDir

Write-Host "Results saved in: $localDir"
