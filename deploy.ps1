# Load environment variables from .env
$envPath = ".env"
if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.+)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $value)
        }
    }
    Write-Host "Loaded .env file"
} else {
    Write-Error ".env file not found!"
    exit 1
}

# Set project details
$functionName = $env:FUNCTION_NAME
$region = $env:REGION
$runtime = $env:RUNTIME
$triggerTopic = $env:TRIGGER_TOPIC
$entryPoint = $env:ENTRY_POINT
$envFile = $env:ENV_FILE
$dbsFile = $env:DBS_FILE

Write-Host "Converting $dbsFile to $envFile..."

# Read and escape the JSON
if (Test-Path $dbsFile) {
    $rawJson = Get-Content -Raw -Path $dbsFile
    $escapedJson = $rawJson -replace '"', '\"' -replace '\n|\r', ''
    $quotedJson = "`"$escapedJson`""

    # Write the env.yaml file
    "DATABASE_URLS: $quotedJson" | Out-File -Encoding UTF8 -FilePath $envFile
    Write-Host "Generated $envFile from $dbsFile"
} else {
    Write-Error "$dbsFile not found. Aborting."
    exit 1
}

Write-Host "🚀 Deploying $functionName to region $region..."

# Run gcloud deploy
gcloud functions deploy $functionName `
  --gen2 `
  --runtime $runtime `
  --region $region `
  --entry-point $entryPoint `
  --source "." `
  --trigger-topic $triggerTopic `
  --env-vars-file $envFile

Write-Host "Deployment finished!"
