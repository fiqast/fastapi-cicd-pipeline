$ErrorActionPreference = "Continue"
$active = "none"
if (Test-Path ".active") { $active = (Get-Content ".active").Trim() }
$new = if ($active -eq "blue") { "green" } else { "blue" }
Write-Host "Active: $active -> deploying to: $new"

docker compose pull app-$new
docker compose up -d --force-recreate app-$new

$healthy = $false
for ($i = 0; $i -lt 15; $i++) {
    docker compose exec -T app-$new python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" 2>$null
    if ($LASTEXITCODE -eq 0) { $healthy = $true; break }
    Start-Sleep -Seconds 2
}

if (-not $healthy) {
    Write-Host "Health check FAILED. Rolling back: keeping $active."
    docker compose stop app-$new
    exit 1
}

Set-Content -Path "nginx/upstream.inc" -Value "server app-${new}:8000;"
docker compose up -d nginx
docker compose exec -T nginx nginx -s reload
Set-Content -Path ".active" -Value $new

if ($active -ne "none") { docker compose stop app-$active }
Write-Host "Deploy OK. Active: $new"