[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Path
)

$ErrorActionPreference = "Stop"

$file = (Resolve-Path -LiteralPath $Path).Path
$signature = Get-AuthenticodeSignature -LiteralPath $file
if ($signature.Status -ne "Valid" -or $null -eq $signature.SignerCertificate) {
    throw "The release XLL must have a trusted Authenticode signature: $($signature.Status). $($signature.StatusMessage)"
}
if ($null -eq $signature.TimeStamperCertificate) {
    throw "The release XLL must have an Authenticode timestamp."
}

Write-Host "Verified release signature: $($signature.SignerCertificate.Subject)"
