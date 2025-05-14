# === CONFIGURATION DE BASE ===

# ⚡ Forcer TLS 1.2 pour les connexions sécurisées
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# 📧 Paramètres SMTP Gmail
$smtpServer = "smtp.gmail.com"
$port = 587
$from = "pincygrace242@gmail.com"
$to = "princygrace242@gmail.com"
$subject = "NetView_Logs Windows"
$body = @"
<html>
    <body>
        <p>Bonjour,</p>
        <p>Veuillez trouver ci-joint les logs Windows compressés provenant de la machine <strong>$computerName</strong>.</p>
         <p>Nous avons collecté les <strong>100 000</strong> logs récents des catégories Système et Application.</p>
        <p>Voici quelques détails supplémentaires :</p>
        <ul>
            <li><strong>Nom de la machine :</strong> $computerName</li>
            <li><strong>Numéro de série :</strong> $serialNumber</li>
        </ul>
        <p>Cordialement,</p>
        <p><strong>NetView Agent</strong></p>
    </body>
</html>
"@

# 🔐 Import du fichier d'identifiants sécurisé
$credPath = "$env:USERPROFILE\gmail-cred_logs.xml"
if (-not (Test-Path $credPath)) {
    $errorMessage = "❌ Fichier d'identifiants introuvable : $credPath"
    Write-Host $errorMessage -ForegroundColor Red
    exit
}
$credential = Import-Clixml -Path $credPath

# === Récupération du nom de la machine et du numéro de série ===
$computerName = $env:COMPUTERNAME
$serialNumber = (Get-WmiObject -Class Win32_BIOS).SerialNumber

# === COLLECTE DES LOGS ===
$logs = $null
try {
    $logs = Get-WinEvent -LogName 'Application','System' -MaxEvents 100000 |
        Select-Object TimeCreated, ProviderName, LevelDisplayName, Message, ComputerName, LogName, Id
                    
    if ($logs.Count -eq 0) {
        $errorMessage = "❌ Aucun log trouvé."
        Write-Host $errorMessage -ForegroundColor Red
        exit
    }
}
catch {
    $errorMessage = "❌ Erreur lors de la collecte des logs : $_"
    Write-Host $errorMessage -ForegroundColor Red
    exit
}

# === EXPORT EN CSV ===
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$logPath = "$env:TEMP\$computerName`_$serialNumber`_Logs_$timestamp.csv"
try {
    $logs | Export-Csv -Path $logPath -NoTypeInformation -Encoding UTF8
    Write-Host "✅ Logs exportés à $logPath" -ForegroundColor Green
}
catch {
    $errorMessage = "❌ Erreur lors de l'export des logs en CSV : $_"
    Write-Host $errorMessage -ForegroundColor Red
    exit
}

# === COMPRESSION EN ZIP ===
$zipPath = "$env:TEMP\$computerName`_$serialNumber`_Logs_$timestamp.zip"
try {
    Compress-Archive -Path $logPath -DestinationPath $zipPath -Force
    Write-Host "✅ Logs compressés à $zipPath" -ForegroundColor Green
}
catch {
    $errorMessage = "❌ Erreur lors de la compression des logs : $_"
    Write-Host $errorMessage -ForegroundColor Red
    exit 1
}

# === ENVOI PAR MAIL ===
try {
    Send-MailMessage -From $from -To $to -Subject $subject -Body $body `
        -SmtpServer $smtpServer -Port $port -UseSsl `
        -Credential $credential -Attachments $zipPath -BodyAsHtml -Encoding UTF8
    Write-Host "✅ Email envoyé avec succès." -ForegroundColor Green
}
catch {
    $errorMessage = "❌ Erreur lors de l'envoi de l'email : $_"
    Write-Host $errorMessage -ForegroundColor Red
    exit
}

# === NETTOYAGE ===
try {
    Remove-Item $logPath -Force
    Remove-Item $zipPath -Force
    Write-Host "✅ Fichiers temporaires supprimés." -ForegroundColor Green
}
catch {
    $errorMessage = "❌ Erreur lors de la suppression des fichiers temporaires : $_"
    Write-Host $errorMessage -ForegroundColor Red
}
