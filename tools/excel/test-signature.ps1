[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$UnsignedPath
)

$ErrorActionPreference = "Stop"
$verify = Join-Path $PSScriptRoot "verify-signature.ps1"

function Assert-Rejected([string]$File) {
    $rejected = $false
    try {
        & $verify -Path $File
    }
    catch {
        $rejected = $true
        Write-Host "Rejected invalid release artifact: $($_.Exception.Message)"
    }
    if (-not $rejected) {
        throw "Signature verification accepted an invalid release artifact: $File"
    }
}

$unsigned = (Resolve-Path -LiteralPath $UnsignedPath).Path
if ((Get-AuthenticodeSignature -LiteralPath $unsigned).Status -ne "NotSigned") {
    throw "The development XLL must be unsigned for this test."
}
Assert-Rejected $unsigned

$directory = Join-Path ([IO.Path]::GetTempPath()) ("quantsupport-signature-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $directory | Out-Null
try {
    # PowerShell's signed executable is a real timestamped PE fixture on the Windows runner.
    $signed = Join-Path $directory "signed.xll"
    Copy-Item -LiteralPath (Join-Path $PSHOME "pwsh.exe") -Destination $signed
    & $verify -Path $signed

    $tampered = Join-Path $directory "tampered.xll"
    Copy-Item -LiteralPath $signed -Destination $tampered
    $bytes = [IO.File]::ReadAllBytes($tampered)
    $bytes[1024] = $bytes[1024] -bxor 1
    [IO.File]::WriteAllBytes($tampered, $bytes)
    Assert-Rejected $tampered
}
finally {
    Remove-Item -LiteralPath $directory -Recurse -Force
}
