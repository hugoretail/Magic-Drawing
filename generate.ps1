param(
  [string]$JsonPath = ".\response.json"
)

$json = Get-Content $JsonPath -Raw | ConvertFrom-Json

if ($json.worksheet_png) {
  [IO.File]::WriteAllBytes("worksheet.png", [Convert]::FromBase64String($json.worksheet_png))
  Write-Host "Saved worksheet.png"
}
if ($json.preview_png) {
  [IO.File]::WriteAllBytes("preview.png", [Convert]::FromBase64String($json.preview_png))
  Write-Host "Saved preview.png"
}
