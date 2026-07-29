param(
    [string]$Remote = "brais.gomez.lopez@hpc-login2.inv.usc.es",
    [string]$RemoteDir = "~/medical-qa-sft"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$archiveName = "medical-qa-sft_deploy.tar.gz"
$archivePath = Join-Path ([System.IO.Path]::GetTempPath()) $archiveName

if (Test-Path $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}

Write-Host "Creating deployment archive from $repoRoot"
tar `
    --exclude ".git" `
    --exclude ".venv" `
    --exclude "__pycache__" `
    --exclude "artifacts" `
    --exclude "results" `
    -czf $archivePath `
    -C $repoRoot `
    .

Write-Host "Creating remote directory $RemoteDir"
ssh $Remote "mkdir -p $RemoteDir"

Write-Host "Uploading archive"
scp $archivePath "${Remote}:$RemoteDir/$archiveName"

Write-Host "Extracting archive on CiTIUS"
ssh $Remote "tar -xzf $RemoteDir/$archiveName -C $RemoteDir && rm -f $RemoteDir/$archiveName"

Remove-Item -LiteralPath $archivePath -Force

Write-Host "Deployment completed. On CiTIUS run:"
Write-Host "  cd $RemoteDir"
Write-Host "  sbatch hpc/slurm/who_generation/who_qa_preflight_local_gpu.sh"
