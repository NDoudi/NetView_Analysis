# === CONFIGURATION ===
$clientName = $env:COMPUTERNAME  # ou une autre variable si tu préfères personnaliser
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$logPath = "$env:TEMP\${clientName}_Logs_$timestamp.csv"
    # Chemin du fichier CSV
$apiUrl = " https://353b-143-244-56-179.ngrok-free.app/upload" # Remplace avec ton URL ngrok

# === ÉTAPE 1 : Collecte des logs Windows (Application + System) ===
try {
    # Récupérer les 1000 logs les plus récents de 'Application' et 'System'
       $logs = Get-WinEvent -LogName 'Application','System' -MaxEvents 100000 | 
            Select-Object TimeCreated, ProviderName, LevelDisplayName, Message, ComputerName, LogName, Id

    # Si aucune donnée n'a été récupérée
    if ($logs.Count -eq 0) {
        Write-Host "❌ Aucun log trouvé."
        exit
    }

    # Exporter les logs en CSV (chaque ligne contient les informations d'un log)
    $logs | Export-Csv -Path $logPath -NoTypeInformation -Encoding UTF8
    Write-Host "✅ Logs exportés avec succès à $logPath"
} 
catch {
    Write-Error "❌ Erreur lors de la collecte des logs : $_"
    exit
}

# === ÉTAPE 2 : Envoi du fichier CSV à l'API ===
try {
    # Créer un objet FileInfo pour lire le fichier
    $fileInfo = New-Object System.IO.FileInfo($logPath)

    # Construire le corps de la requête multipart/form-data correctement
    $boundary = [System.Guid]::NewGuid().ToString()
    
    # Charger le fichier CSV en texte brut
    $fileContent = [System.IO.File]::ReadAllText($fileInfo.FullName)

    # Créer les en-têtes nécessaires
    $headers = @{
        "Content-Type" = "multipart/form-data; boundary=$boundary"
    }

    # Construire le corps de la requête avec le fichier
    $body = @"
--$boundary
Content-Disposition: form-data; name="file"; filename="$($fileInfo.Name)"
Content-Type: text/csv

$fileContent

--$boundary--
"@

    # Envoyer la requête POST avec le fichier en multipart/form-data
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $body -Headers $headers

    # Vérification de la réponse
    if ($response.status -eq "success") {
        Write-Host "✅ Log envoyé avec succès à $apiUrl"
    } else {
        Write-Host "❌ Erreur lors de l'envoi du log. Message : $($response.status)"
    }
} 
catch {
    Write-Error "❌ Erreur lors de l'envoi du log : $_"
}

# === ÉTAPE 3 : Nettoyage des fichiers temporaires ===
try {
    # Suppression du fichier CSV temporaire après l'envoi
    Remove-Item $logPath -Force
    Write-Host "✅ Fichier temporaire supprimé."
} 
catch {
    Write-Error "❌ Erreur lors de la suppression du fichier temporaire : $_"
}

