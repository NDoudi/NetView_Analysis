# Tape ceci UNE FOIS pour générer ton fichier d'identifiants sécurisé
$cred = Get-Credential
$cred | Export-Clixml -Path "$env:USERPROFILE\gmail-cred_logs.xml"
