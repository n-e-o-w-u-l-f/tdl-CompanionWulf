#requires -Version 5.1

<#
.SYNOPSIS
    tdl-sidecart - Telegram Export / Download Manager

.DESCRIPTION
    Interaktive PowerShell-Oberfläche für tdl.exe.

    Hauptfunktionen:

      - Telegram Chats auswählen
      - Topics auswählen
      - Medienarten auswählen
      - tdl chat export
      - tdl dl
      - Multi-Instance Namespaces
      - Threads / Limit / Delay / Pool
      - Takeout
      - Continue / Restart
      - Rewrite-Ext
      - Desc
      - Group
      - Debug
      - NTP
      - Proxy
      - Storage
      - Reconnect Timeout
      - sichere Windows-Dateinamen
      - automatische Behandlung gleichnamiger Dateien
      - gleiches File + gleiche Größe => überspringen
      - gleiches File + andere Größe => vorhandene Datei umbenennen
      - lokalisierte Benutzeroberfläche
      - zusätzliche tdl-Argumente
      - ausführliche Fehlerdiagnose

.PROJECT
    tdl-sidecart

.NOTES
    Projektname:
        tdl-sidecart

    Der Dateiname wird absichtlich mit "filenamify"
    erzeugt, bevor tdl die Datei anlegt.

    Dadurch werden Windows-ungültige Zeichen wie

        < > : " / \ | ? *

    aus Telegram-Dateinamen entfernt.

    Beispiel:

        3. F*CKING SOCIETY.flac

    wird beispielsweise zu:

        3. F_CKING SOCIETY.flac

    Die exakte Normalisierung übernimmt tdl.

#>

[CmdletBinding()]
param(
    # ============================================================
    # BASIS
    # ============================================================

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$TdlPath = ".\tdl.exe",

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$OutputPath,

    # ============================================================
    # SPRACHE
    # ============================================================

    [ValidateSet(
        "Auto",
        "Deutsch",
        "English",
        "Français",
        "Español",
        "Italiano",
        "Português",
        "Nederlands",
        "Polski",
        "Čeština",
        "Slovenčina",
        "Magyar",
        "Română",
        "Türkçe",
        "Русский",
        "Українська",
        "Български",
        "Ελληνικά",
        "Svenska",
        "Dansk",
        "Norsk",
        "Suomi"
    )]
    [string]$Language = "Auto",

    # ============================================================
    # TDL NAMESPACE
    # ============================================================

    [string]$Namespace = "",

    # ============================================================
    # TDL TRANSFER
    # ============================================================

    [ValidateRange(1, 128)]
    [int]$Threads = 10,

    [ValidateRange(1, 128)]
    [int]$Limit = 4,

    [ValidateRange(0, 86400)]
    [int]$Delay = 2,

    [ValidateRange(0, 128)]
    [int]$Pool = 0,

    # ============================================================
    # TDL OPTIONEN
    # ============================================================

    [switch]$Takeout,

    [switch]$ContinueDownload,

    [switch]$RestartDownload,

    [switch]$RewriteExt,

    [switch]$Desc,

    [switch]$Group,

    [switch]$DebugMode,

    [switch]$DisableProgressPs,

    [string]$Proxy = "",

    [string]$Ntp = "",

    [string]$ReconnectTimeout = "",

    [string]$Storage = "",

    # ============================================================
    # DATEINAMEN
    # ============================================================

    [ValidateRange(32, 255)]
    [int]$MaxFileNameLength = 180,

    [switch]$PreserveExistingDifferentSize,

    # ============================================================
    # VERGLEICH
    # ============================================================

    [ValidateSet(
        "Size",
        "Hash"
    )]
    [string]$ExistingFileComparison = "Size",

    # ============================================================
    # ZUSÄTZLICHE TDL ARGUMENTE
    # ============================================================
    #
    # Damit können neue tdl-Optionen verwendet werden,
    # ohne das Skript sofort anpassen zu müssen.
    #
    # Beispiel:
    #
    # -TdlExtraArguments @("--some-new-option", "value")
    #

    [string[]]$TdlExtraArguments = @(),

    # ============================================================
    # VERHALTEN
    # ============================================================

    [switch]$NonInteractive,

    [switch]$NoPause,

    [switch]$WhatIfDownload
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ================================================================
# PROJEKT
# ================================================================

$Script:ProjectName = "tdl-sidecart"
$Script:ProjectVersion = "2.1.1"
$Script:NamespaceWasExplicit = -not [string]::IsNullOrWhiteSpace($Namespace)
$Script:TdataLeaseStreams = @{}
$Script:ActiveTdataPath = $null

# ================================================================
# KONSOLE
# ================================================================

$Script:PageSize = 18

$Script:MenuNormalColor   = [ConsoleColor]::Gray
$Script:MenuSelectedColor = [ConsoleColor]::Green
$Script:MenuCursorColor   = [ConsoleColor]::Yellow
$Script:HeaderColor       = [ConsoleColor]::Cyan
$Script:InfoColor         = [ConsoleColor]::DarkGray
$Script:ErrorColor        = [ConsoleColor]::Red
$Script:WarningColor      = [ConsoleColor]::DarkYellow
$Script:SuccessColor      = [ConsoleColor]::Green

# ================================================================
# LOKALISIERUNG
# ================================================================

$Script:CurrentLanguage = "Deutsch"

$Script:Translations = @{
    "Deutsch" = @{
        Title                  = "tdl-sidecart"
        Chats                  = "TELEGRAM CHATS"
        Topics                 = "TOPICS"
        Media                  = "MEDIEN-AUSWAHL"
        Summary                = "EXPORT-ZUSAMMENFASSUNG"
        Error                  = "FEHLER"
        Done                   = "EXPORT FERTIG"
        LoadingChats           = "Lade Telegram-Chats..."
        CheckingSession        = "Prüfe Telegram-Session..."
        Authenticated          = "Telegram-Session ist authentifiziert."
        NotAuthenticated       = "Namespace ist nicht authentifiziert."
        Namespace              = "Namespace"
        Output                 = "Zielordner"
        Threads                = "Threads"
        Limit                  = "Limit"
        Delay                  = "Delay"
        Pool                   = "Pool"
        MediaTypes             = "Medientypen"
        Extensions             = "Dateiendungen"
        ExportingMessages      = "Exportiere Nachrichten..."
        ExportSuccess          = "Export erfolgreich."
        StartingDownload       = "Starte Download..."
        DownloadSuccess        = "Download abgeschlossen."
        NoChats                = "Es wurden keine Telegram-Chats gefunden."
        NoSelection            = "Keine Einträge ausgewählt."
        Cancelled              = "Vom Benutzer abgebrochen."
        Continue               = "Weiter"
        Selected               = "Ausgewählt"
        Navigation             = "UP/DOWN = Navigieren   SPACE = Auswählen   ENTER = Weiter"
        Navigation2            = "HOME/END = Anfang/Ende   ESC = Abbrechen"
        SameFile               = "Datei bereits vorhanden und gleich groß."
        DifferentFile          = "Gleichnamige Datei mit anderer Größe gefunden."
        RenamedExisting        = "Vorhandene Datei wurde umbenannt:"
        WouldDownload          = "Download würde gestartet werden."
        TdlNotFound            = "tdl.exe wurde nicht gefunden:"
        InvalidOutput          = "OutputPath ist kein Verzeichnis:"
        LoginHint              = "Einmalig ausführen:"
        AutoAuthKnownSearch    = "Suche Telegram-Desktop-Daten in bekannten tdata-Pfaden..."
        AutoAuthSystemSearch   = "Keine verwendbare bekannte Sitzung gefunden. Suche jetzt systemweit nach tdata..."
        AutoAuthFound          = "tdata gefunden:"
        AutoAuthTrying         = "Starte automatische tdl-Authentifizierung mit:"
        AutoAuthSuccess        = "Namespace wurde erfolgreich über Telegram Desktop authentifiziert."
        AutoAuthNoTdata        = "Es wurde kein verwendbarer tdata-Ordner gefunden."
        AutoAuthLoginFailed    = "Die automatische Authentifizierung mit diesem tdata-Ordner war nicht erfolgreich."
        AutoAuthInUse          = "tdata wird bereits von einer anderen tdl-sidecart-Instanz verwendet. Überspringe:"
        AutoAuthInstalling     = "Alle vorhandenen tdata-Sitzungen sind belegt oder unbrauchbar. Installiere einen neuen isolierten Telegram-Desktop-Client..."
        AutoAuthClientReady    = "Neuer Telegram-Desktop-Client wurde gestartet. Bitte dort Telegram anmelden; tdl-sidecart erkennt die neue tdata-Sitzung automatisch."
        AutoAuthWaitingClient  = "Warte auf die Anmeldung im neuen Telegram-Desktop-Client..."
        AutoAuthParallelNs     = "Der Standard-Namespace wird bereits verwendet. Verwende automatisch einen neuen Namespace:"
        ContinueNext           = "Der Export wird mit dem nächsten Eintrag fortgesetzt."
        PressKey               = "Taste drücken zum Fortfahren..."
        Jobs                   = "Export-Jobs"
        Success                = "Erfolgreich"
        Errors                 = "Fehler"
        Total                  = "Gesamt"
        Chat                   = "Chat"
        Topic                  = "Topic"
        Target                 = "Ziel"
        Language               = "Sprache"
        Comparison             = "Dateivergleich"
        FilenamePolicy         = "Dateinamenrichtlinie"
    }

    "English" = @{
        Title                  = "tdl-sidecart"
        Chats                  = "TELEGRAM CHATS"
        Topics                 = "TOPICS"
        Media                  = "MEDIA SELECTION"
        Summary                = "EXPORT SUMMARY"
        Error                  = "ERROR"
        Done                   = "EXPORT COMPLETE"
        LoadingChats           = "Loading Telegram chats..."
        CheckingSession        = "Checking Telegram session..."
        Authenticated          = "Telegram session is authenticated."
        NotAuthenticated       = "Namespace is not authenticated."
        Namespace              = "Namespace"
        Output                 = "Output directory"
        Threads                = "Threads"
        Limit                  = "Limit"
        Delay                  = "Delay"
        Pool                   = "Pool"
        MediaTypes             = "Media types"
        Extensions             = "File extensions"
        ExportingMessages      = "Exporting messages..."
        ExportSuccess          = "Export successful."
        StartingDownload       = "Starting download..."
        DownloadSuccess        = "Download completed."
        NoChats                = "No Telegram chats were found."
        NoSelection            = "No entries selected."
        Cancelled              = "Cancelled by user."
        Continue               = "Continue"
        Selected               = "Selected"
        Navigation             = "UP/DOWN = Navigate   SPACE = Select   ENTER = Continue"
        Navigation2            = "HOME/END = Start/End   ESC = Cancel"
        SameFile               = "File already exists and has the same size."
        DifferentFile          = "A file with the same name but different size was found."
        RenamedExisting        = "Existing file was renamed:"
        WouldDownload          = "Download would be started."
        TdlNotFound            = "tdl.exe was not found:"
        InvalidOutput          = "OutputPath is not a directory:"
        LoginHint              = "Run once:"
        AutoAuthKnownSearch    = "Searching known locations for Telegram Desktop tdata..."
        AutoAuthSystemSearch   = "No usable known session was found. Searching all local drives for tdata..."
        AutoAuthFound          = "Found tdata:"
        AutoAuthTrying         = "Starting automatic tdl authentication with:"
        AutoAuthSuccess        = "The namespace was authenticated successfully from Telegram Desktop."
        AutoAuthNoTdata        = "No usable tdata directory was found."
        AutoAuthLoginFailed    = "Automatic authentication with this tdata directory was not successful."
        AutoAuthInUse          = "tdata is already reserved by another tdl-sidecart instance. Skipping:"
        AutoAuthInstalling     = "All existing tdata sessions are busy or unusable. Installing a new isolated Telegram Desktop client..."
        AutoAuthClientReady    = "A new Telegram Desktop client was started. Sign in there; tdl-sidecart will detect the new tdata session automatically."
        AutoAuthWaitingClient  = "Waiting for sign-in in the new Telegram Desktop client..."
        AutoAuthParallelNs     = "The default namespace is already in use. Automatically using a new namespace:"
        ContinueNext           = "The export will continue with the next item."
        PressKey               = "Press a key to continue..."
        Jobs                   = "Export jobs"
        Success                = "Successful"
        Errors                 = "Errors"
        Total                  = "Total"
        Chat                   = "Chat"
        Topic                  = "Topic"
        Target                 = "Target"
        Language               = "Language"
        Comparison             = "File comparison"
        FilenamePolicy         = "Filename policy"
    }

    "Français" = @{
        Title                  = "tdl-sidecart"
        Chats                  = "CHATS TELEGRAM"
        Topics                 = "SUJETS"
        Media                  = "SÉLECTION DES MÉDIAS"
        Summary                = "RÉSUMÉ DE L'EXPORT"
        Error                  = "ERREUR"
        Done                   = "EXPORT TERMINÉ"
        LoadingChats           = "Chargement des chats Telegram..."
        CheckingSession        = "Vérification de la session Telegram..."
        Authenticated          = "Session Telegram authentifiée."
        NotAuthenticated       = "L'espace de noms n'est pas authentifié."
        Namespace              = "Espace de noms"
        Output                 = "Dossier de sortie"
        Threads                = "Threads"
        Limit                  = "Limite"
        Delay                  = "Délai"
        Pool                   = "Pool"
        MediaTypes             = "Types de médias"
        Extensions             = "Extensions"
        ExportingMessages      = "Exportation des messages..."
        ExportSuccess          = "Export réussi."
        StartingDownload       = "Démarrage du téléchargement..."
        DownloadSuccess        = "Téléchargement terminé."
        NoChats                = "Aucun chat Telegram trouvé."
        NoSelection            = "Aucun élément sélectionné."
        Cancelled              = "Annulé par l'utilisateur."
        Continue               = "Continuer"
        Selected               = "Sélectionné"
        Navigation             = "HAUT/BAS = Naviguer   ESPACE = Sélectionner   ENTRÉE = Continuer"
        Navigation2            = "HOME/END = Début/Fin   ESC = Annuler"
        SameFile               = "Le fichier existe déjà et possède la même taille."
        DifferentFile          = "Un fichier portant le même nom mais une taille différente existe."
        RenamedExisting        = "Le fichier existant a été renommé :"
        WouldDownload          = "Le téléchargement serait lancé."
        TdlNotFound            = "tdl.exe introuvable :"
        InvalidOutput          = "OutputPath n'est pas un dossier :"
        LoginHint              = "Exécuter une fois :"
        ContinueNext           = "L'export continuera avec l'élément suivant."
        PressKey               = "Appuyez sur une touche pour continuer..."
        Jobs                   = "Tâches d'export"
        Success                = "Réussis"
        Errors                 = "Erreurs"
        Total                  = "Total"
        Chat                   = "Chat"
        Topic                  = "Sujet"
        Target                 = "Destination"
        Language               = "Langue"
        Comparison             = "Comparaison"
        FilenamePolicy         = "Politique des noms"
    }

    "Español" = @{
        Title                  = "tdl-sidecart"
        Chats                  = "CHATS DE TELEGRAM"
        Topics                 = "TEMAS"
        Media                  = "SELECCIÓN DE MEDIOS"
        Summary                = "RESUMEN DE EXPORTACIÓN"
        Error                  = "ERROR"
        Done                   = "EXPORTACIÓN COMPLETA"
        LoadingChats           = "Cargando chats de Telegram..."
        CheckingSession        = "Comprobando sesión de Telegram..."
        Authenticated          = "La sesión de Telegram está autenticada."
        NotAuthenticated       = "El espacio de nombres no está autenticado."
        Namespace              = "Espacio de nombres"
        Output                 = "Directorio de salida"
        Threads                = "Hilos"
        Limit                  = "Límite"
        Delay                  = "Retraso"
        Pool                   = "Pool"
        MediaTypes             = "Tipos de medios"
        Extensions             = "Extensiones"
        ExportingMessages      = "Exportando mensajes..."
        ExportSuccess          = "Exportación correcta."
        StartingDownload       = "Iniciando descarga..."
        DownloadSuccess        = "Descarga completada."
        NoChats                = "No se encontraron chats de Telegram."
        NoSelection            = "No se seleccionaron elementos."
        Cancelled              = "Cancelado por el usuario."
        Continue               = "Continuar"
        Selected               = "Seleccionado"
        Navigation             = "ARRIBA/ABAJO = Navegar   ESPACIO = Seleccionar   ENTER = Continuar"
        Navigation2            = "HOME/END = Inicio/Fin   ESC = Cancelar"
        SameFile               = "El archivo ya existe y tiene el mismo tamaño."
        DifferentFile          = "Existe un archivo con el mismo nombre y distinto tamaño."
        RenamedExisting        = "El archivo existente fue renombrado:"
        WouldDownload          = "Se iniciaría la descarga."
        TdlNotFound            = "No se encontró tdl.exe:"
        InvalidOutput          = "OutputPath no es un directorio:"
        LoginHint              = "Ejecutar una vez:"
        ContinueNext           = "La exportación continuará con el siguiente elemento."
        PressKey               = "Pulse una tecla para continuar..."
        Jobs                   = "Trabajos de exportación"
        Success                = "Correctos"
        Errors                 = "Errores"
        Total                  = "Total"
        Chat                   = "Chat"
        Topic                  = "Tema"
        Target                 = "Destino"
        Language               = "Idioma"
        Comparison             = "Comparación"
        FilenamePolicy         = "Política de nombres"
    }

    "Italiano" = @{
        Title                  = "tdl-sidecart"
        Chats                  = "CHAT TELEGRAM"
        Topics                 = "ARGOMENTI"
        Media                  = "SELEZIONE MEDIA"
        Summary                = "RIEPILOGO ESPORTAZIONE"
        Error                  = "ERRORE"
        Done                   = "ESPORTAZIONE COMPLETATA"
        LoadingChats           = "Caricamento chat Telegram..."
        CheckingSession        = "Controllo sessione Telegram..."
        Authenticated          = "Sessione Telegram autenticata."
        NotAuthenticated       = "Il namespace non è autenticato."
        Namespace              = "Namespace"
        Output                 = "Cartella di output"
        Threads                = "Thread"
        Limit                  = "Limite"
        Delay                  = "Ritardo"
        Pool                   = "Pool"
        MediaTypes             = "Tipi di media"
        Extensions             = "Estensioni"
        ExportingMessages      = "Esportazione messaggi..."
        ExportSuccess          = "Esportazione riuscita."
        StartingDownload       = "Avvio download..."
        DownloadSuccess        = "Download completato."
        NoChats                = "Nessuna chat Telegram trovata."
        NoSelection            = "Nessun elemento selezionato."
        Cancelled              = "Annullato dall'utente."
        Continue               = "Continua"
        Selected               = "Selezionato"
        Navigation             = "SU/GIÙ = Naviga   SPAZIO = Seleziona   INVIO = Continua"
        Navigation2            = "HOME/FINE = Inizio/Fine   ESC = Annulla"
        SameFile               = "Il file esiste già e ha la stessa dimensione."
        DifferentFile          = "Esiste un file con lo stesso nome ma dimensione diversa."
        RenamedExisting        = "Il file esistente è stato rinominato:"
        WouldDownload          = "Il download verrebbe avviato."
        TdlNotFound            = "tdl.exe non trovato:"
        InvalidOutput          = "OutputPath non è una directory:"
        LoginHint              = "Eseguire una volta:"
        ContinueNext           = "L'esportazione continuerà con l'elemento successivo."
        PressKey               = "Premere un tasto per continuare..."
        Jobs                   = "Processi di esportazione"
        Success                = "Riusciti"
        Errors                 = "Errori"
        Total                  = "Totale"
        Chat                   = "Chat"
        Topic                  = "Argomento"
        Target                 = "Destinazione"
        Language               = "Lingua"
        Comparison             = "Confronto"
        FilenamePolicy         = "Politica nomi file"
    }

    "Português" = @{
        Title                  = "tdl-sidecart"
        Chats                  = "CHATS DO TELEGRAM"
        Topics                 = "TÓPICOS"
        Media                  = "SELEÇÃO DE MÍDIA"
        Summary                = "RESUMO DA EXPORTAÇÃO"
        Error                  = "ERRO"
        Done                   = "EXPORTAÇÃO CONCLUÍDA"
        LoadingChats           = "Carregando chats do Telegram..."
        CheckingSession        = "Verificando sessão do Telegram..."
        Authenticated          = "Sessão do Telegram autenticada."
        NotAuthenticated       = "O namespace não está autenticado."
        Namespace              = "Namespace"
        Output                 = "Diretório de saída"
        Threads                = "Threads"
        Limit                  = "Limite"
        Delay                  = "Atraso"
        Pool                   = "Pool"
        MediaTypes             = "Tipos de mídia"
        Extensions             = "Extensões"
        ExportingMessages      = "Exportando mensagens..."
        ExportSuccess          = "Exportação concluída."
        StartingDownload       = "Iniciando download..."
        DownloadSuccess        = "Download concluído."
        NoChats                = "Nenhum chat do Telegram encontrado."
        NoSelection            = "Nenhum item selecionado."
        Cancelled              = "Cancelado pelo usuário."
        Continue               = "Continuar"
        Selected               = "Selecionado"
        Navigation             = "CIMA/BAIXO = Navegar   ESPAÇO = Selecionar   ENTER = Continuar"
        Navigation2            = "HOME/END = Início/Fim   ESC = Cancelar"
        SameFile               = "O arquivo já existe e tem o mesmo tamanho."
        DifferentFile          = "Existe um arquivo com o mesmo nome e tamanho diferente."
        RenamedExisting        = "O arquivo existente foi renomeado:"
        WouldDownload          = "O download seria iniciado."
        TdlNotFound            = "tdl.exe não encontrado:"
        InvalidOutput          = "OutputPath não é um diretório:"
        LoginHint              = "Executar uma vez:"
        ContinueNext           = "A exportação continuará com o próximo item."
        PressKey               = "Pressione uma tecla para continuar..."
        Jobs                   = "Trabalhos de exportação"
        Success                = "Sucesso"
        Errors                 = "Erros"
        Total                  = "Total"
        Chat                   = "Chat"
        Topic                  = "Tópico"
        Target                 = "Destino"
        Language               = "Idioma"
        Comparison             = "Comparação"
        FilenamePolicy         = "Política de nomes"
    }
}

# Fallback-Sprachen.
# Nicht separat übersetzte Sprachen verwenden Englisch.
foreach ($languageName in @(
    "Nederlands",
    "Polski",
    "Čeština",
    "Slovenčina",
    "Magyar",
    "Română",
    "Türkçe",
    "Русский",
    "Українська",
    "Български",
    "Ελληνικά",
    "Svenska",
    "Dansk",
    "Norsk",
    "Suomi"
)) {
    if (-not $Script:Translations.ContainsKey($languageName)) {
        $Script:Translations[$languageName] =
            $Script:Translations["English"].Clone()
    }
}

function Initialize-Language {

    if ($Language -eq "Auto") {

        try {

            $culture = [System.Globalization.CultureInfo]::CurrentUICulture

            $code = $culture.TwoLetterISOLanguageName.ToLowerInvariant()

            switch ($code) {

                "de" {
                    $Script:CurrentLanguage = "Deutsch"
                }

                "en" {
                    $Script:CurrentLanguage = "English"
                }

                "fr" {
                    $Script:CurrentLanguage = "Français"
                }

                "es" {
                    $Script:CurrentLanguage = "Español"
                }

                "it" {
                    $Script:CurrentLanguage = "Italiano"
                }

                "pt" {
                    $Script:CurrentLanguage = "Português"
                }

                "nl" {
                    $Script:CurrentLanguage = "Nederlands"
                }

                "pl" {
                    $Script:CurrentLanguage = "Polski"
                }

                "cs" {
                    $Script:CurrentLanguage = "Čeština"
                }

                "sk" {
                    $Script:CurrentLanguage = "Slovenčina"
                }

                "hu" {
                    $Script:CurrentLanguage = "Magyar"
                }

                "ro" {
                    $Script:CurrentLanguage = "Română"
                }

                "tr" {
                    $Script:CurrentLanguage = "Türkçe"
                }

                "ru" {
                    $Script:CurrentLanguage = "Русский"
                }

                "uk" {
                    $Script:CurrentLanguage = "Українська"
                }

                "bg" {
                    $Script:CurrentLanguage = "Български"
                }

                "el" {
                    $Script:CurrentLanguage = "Ελληνικά"
                }

                "sv" {
                    $Script:CurrentLanguage = "Svenska"
                }

                "da" {
                    $Script:CurrentLanguage = "Dansk"
                }

                "no" {
                    $Script:CurrentLanguage = "Norsk"
                }

                "fi" {
                    $Script:CurrentLanguage = "Suomi"
                }

                default {
                    $Script:CurrentLanguage = "English"
                }
            }
        }
        catch {
            $Script:CurrentLanguage = "English"
        }
    }
    else {
        $Script:CurrentLanguage = $Language
    }
}

function T {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Key
    )

    $table = $Script:Translations[$Script:CurrentLanguage]

    if ($null -eq $table) {
        $table = $Script:Translations["English"]
    }

    if ($table.ContainsKey($Key)) {
        return [string]$table[$Key]
    }

    if ($Script:Translations["English"].ContainsKey($Key)) {
        return [string]$Script:Translations["English"][$Key]
    }

    return $Key
}

Initialize-Language

# ================================================================
# DATEITYPEN
# ================================================================

$Script:ArchiveExtensions = @(
    "zip",
    "rar",
    "7z",
    "tar",
    "gz",
    "bz2",
    "xz",
    "tgz",
    "tbz",
    "tbz2",
    "tar.gz",
    "tar.bz2",
    "tar.xz"
)

$Script:AudioExtensions = @(
    "mp3",
    "flac",
    "wav",
    "m4a",
    "aac",
    "ogg",
    "oga",
    "opus",
    "wma",
    "aiff",
    "aif",
    "alac",
    "ape",
    "ac3",
    "mka",
    "amr"
)

$Script:ImageExtensions = @(
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "bmp",
    "tif",
    "tiff",
    "heic",
    "heif",
    "avif"
)

$Script:VideoExtensions = @(
    "mp4",
    "mkv",
    "avi",
    "mov",
    "webm",
    "m4v",
    "wmv",
    "flv",
    "mpeg",
    "mpg",
    "3gp",
    "ts",
    "m2ts",
    "mts"
)

# ================================================================
# KONSOLE
# ================================================================

function Get-ConsoleWidth {

    try {

        $width = [Console]::WindowWidth

        if ($width -lt 40) {
            return 40
        }

        return $width
    }
    catch {
        return 120
    }
}

function Set-ConsoleCursorVisible {

    param(
        [bool]$Visible
    )

    try {
        [Console]::CursorVisible = $Visible
    }
    catch {
    }
}

function Normalize-ConsoleText {

    param(
        [AllowEmptyString()]
        [string]$Text
    )

    if ($null -eq $Text) {
        return ""
    }

    return ([string]$Text).
        Replace("`r", " ").
        Replace("`n", " ")
}

function Write-LineSafe {

    param(
        [AllowEmptyString()]
        [string]$Text = "",

        [ConsoleColor]$Color = [ConsoleColor]::Gray
    )

    Write-Host (
        Normalize-ConsoleText $Text
    ) -ForegroundColor $Color
}

function Clear-Screen {

    try {
        [Console]::Clear()
    }
    catch {
        Clear-Host
    }
}

function Pause-Script {

    if ($NoPause) {
        return
    }

    Write-Host ""
    Write-Host (
        T "PressKey"
    ) -ForegroundColor DarkGray

    try {
        [void][Console]::ReadKey($true)
    }
    catch {
        [void](Read-Host)
    }
}

function Limit-Text {

    param(
        [AllowEmptyString()]
        [string]$Text,

        [int]$MaxLength
    )

    $Text = Normalize-ConsoleText $Text

    if ($MaxLength -lt 1) {
        return ""
    }

    if ($Text.Length -le $MaxLength) {
        return $Text
    }

    if ($MaxLength -le 3) {
        return $Text.Substring(0, $MaxLength)
    }

    return (
        $Text.Substring(0, $MaxLength - 3) +
        "..."
    )
}

# ================================================================
# PROPERTY HELPERS
# ================================================================

function Get-PropertyValue {

    param(
        [Parameter(Mandatory = $true)]
        $Object,

        [Parameter(Mandatory = $true)]
        [string]$Name,

        $Default = $null
    )

    if ($null -eq $Object) {
        return $Default
    }

    $property =
        $Object.PSObject.Properties[$Name]

    if ($null -eq $property) {
        return $Default
    }

    if ($null -eq $property.Value) {
        return $Default
    }

    return $property.Value
}

# ================================================================
# CHAT
# ================================================================

function Get-ChatId {

    param(
        [Parameter(Mandatory = $true)]
        $Chat
    )

    return [string](
        Get-PropertyValue `
            -Object $Chat `
            -Name "id" `
            -Default ""
    )
}

function Get-ChatName {

    param(
        [Parameter(Mandatory = $true)]
        $Chat
    )

    $name =
        Get-PropertyValue `
            -Object $Chat `
            -Name "visible_name" `
            -Default ""

    if ([string]::IsNullOrWhiteSpace([string]$name)) {

        $name =
            Get-PropertyValue `
                -Object $Chat `
                -Name "username" `
                -Default ""
    }

    if ([string]::IsNullOrWhiteSpace([string]$name)) {
        return "(unnamed chat)"
    }

    return [string]$name
}

function Get-ChatType {

    param(
        [Parameter(Mandatory = $true)]
        $Chat
    )

    return [string](
        Get-PropertyValue `
            -Object $Chat `
            -Name "type" `
            -Default "unknown"
    )
}

function Get-Topics {

    param(
        [Parameter(Mandatory = $true)]
        $Chat
    )

    $property =
        $Chat.PSObject.Properties["topics"]

    if ($null -eq $property) {
        return @()
    }

    if ($null -eq $property.Value) {
        return @()
    }

    return @(
        $property.Value
    )
}

function Get-TopicId {

    param(
        [Parameter(Mandatory = $true)]
        $Topic
    )

    return [string](
        Get-PropertyValue `
            -Object $Topic `
            -Name "id" `
            -Default ""
    )
}

function Get-TopicName {

    param(
        [Parameter(Mandatory = $true)]
        $Topic
    )

    $name =
        Get-PropertyValue `
            -Object $Topic `
            -Name "title" `
            -Default ""

    if ([string]::IsNullOrWhiteSpace([string]$name)) {
        return "(unnamed topic)"
    }

    return [string]$name
}

# ================================================================
# WINDOWS DATEINAMEN
# ================================================================

function ConvertTo-SafeWindowsFileName {

    <#
        Dieser Fallback ist für Dateien außerhalb des tdl-Templates.

        tdl selbst verwendet zusätzlich:

            {{ filenamify .FileName 180 }}

        Dadurch wird der problematische Dateiname bereits innerhalb
        von tdl bereinigt, bevor die .tmp-Datei erstellt wird.
    #>

    param(
        [AllowEmptyString()]
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Name)) {
        return "unnamed"
    }

    $result = $Name

    foreach ($char in [System.IO.Path]::GetInvalidFileNameChars()) {

        $result = $result.Replace(
            [string]$char,
            "_"
        )
    }

    $result = $result.Trim()

    # Windows erlaubt keine Namen mit Punkt oder Leerzeichen
    # am Ende.
    $result = $result.TrimEnd(
        [char]'.',
        [char]' '
    )

    if ([string]::IsNullOrWhiteSpace($result)) {
        $result = "unnamed"
    }

    # Windows reservierte Gerätenamen.
    $base =
        [System.IO.Path]::GetFileNameWithoutExtension(
            $result
        )

    $reserved = @(
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9"
    )

    if (
        $reserved -contains
        $base.ToUpperInvariant()
    ) {

        $extension =
            [System.IO.Path]::GetExtension($result)

        $result =
            "_" +
            $base +
            $extension
    }

    if ($result.Length -gt $MaxFileNameLength) {

        $extension =
            [System.IO.Path]::GetExtension($result)

        $nameOnly =
            [System.IO.Path]::GetFileNameWithoutExtension(
                $result
            )

        $available =
            $MaxFileNameLength -
            $extension.Length

        if ($available -lt 1) {
            $available = 1
        }

        if ($nameOnly.Length -gt $available) {

            $nameOnly =
                $nameOnly.Substring(
                    0,
                    $available
                )
        }

        $result =
            $nameOnly +
            $extension
    }

    return $result
}

# ================================================================
# Eindeutiger Dateiname
# ================================================================

function Get-UniqueRenamedPath {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $directory =
        Split-Path `
            -Path $Path `
            -Parent

    $name =
        [System.IO.Path]::GetFileNameWithoutExtension(
            $Path
        )

    $extension =
        [System.IO.Path]::GetExtension(
            $Path
        )

    $counter = 1

    while ($true) {

        $candidate =
            Join-Path `
                -Path $directory `
                -ChildPath (
                    "{0} ({1}){2}" -f
                    $name,
                    $counter,
                    $extension
                )

        if (-not (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }

        $counter++
    }
}

# ================================================================
# HASH
# ================================================================

function Get-FileHashSafe {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {

        return (
            Get-FileHash `
                -LiteralPath $Path `
                -Algorithm SHA256
        ).Hash
    }
    catch {
        return $null
    }
}

# ================================================================
# TDL
# ================================================================

function Test-Tdl {

    $resolved =
        Resolve-Path `
            -LiteralPath $TdlPath `
            -ErrorAction SilentlyContinue

    if ($null -eq $resolved) {

        throw (
            (T "TdlNotFound") +
            "`n" +
            $TdlPath
        )
    }

    $item =
        Get-Item `
            -LiteralPath $resolved.Path

    if ($item.PSIsContainer) {

        throw (
            (T "TdlNotFound") +
            "`n" +
            $TdlPath
        )
    }

    return $item.FullName
}

# ================================================================
# TDL GLOBALE ARGUMENTE
# ================================================================

function Get-TdlGlobalArguments {

    $arguments = [System.Collections.Generic.List[string]]::new()

    [void]$arguments.Add("-n")
    [void]$arguments.Add($Namespace)

    [void]$arguments.Add("-l")
    [void]$arguments.Add([string]$Limit)

    [void]$arguments.Add("-t")
    [void]$arguments.Add([string]$Threads)

    [void]$arguments.Add("--delay")
    [void]$arguments.Add(
        "{0}s" -f $Delay
    )

    [void]$arguments.Add("--pool")
    [void]$arguments.Add([string]$Pool)

    if ($DebugMode) {
        [void]$arguments.Add("--debug")
    }

    if ($DisableProgressPs) {
        [void]$arguments.Add("--disable-progress-ps")
    }

    if (-not [string]::IsNullOrWhiteSpace($Proxy)) {

        [void]$arguments.Add("--proxy")
        [void]$arguments.Add($Proxy)
    }

    if (-not [string]::IsNullOrWhiteSpace($Ntp)) {

        [void]$arguments.Add("--ntp")
        [void]$arguments.Add($Ntp)
    }

    if (-not [string]::IsNullOrWhiteSpace($ReconnectTimeout)) {

        [void]$arguments.Add("--reconnect-timeout")
        [void]$arguments.Add($ReconnectTimeout)
    }

    if (-not [string]::IsNullOrWhiteSpace($Storage)) {

        [void]$arguments.Add("--storage")
        [void]$arguments.Add($Storage)
    }

    return @($arguments)
}

# ================================================================
# TDL DOWNLOAD ARGUMENTE
# ================================================================

function Get-TdlDownloadArguments {

    param(
        [Parameter(Mandatory = $true)]
        [string]$JsonPath,

        [Parameter(Mandatory = $true)]
        [string]$Directory,

        [Parameter(Mandatory = $true)]
        [array]$Extensions
    )

    $arguments =
        [System.Collections.Generic.List[string]]::new()

    [void]$arguments.Add("dl")

    [void]$arguments.Add("-f")
    [void]$arguments.Add($JsonPath)

    [void]$arguments.Add("-d")
    [void]$arguments.Add($Directory)

    if ($Extensions.Count -gt 0) {

        [void]$arguments.Add("-i")
        [void]$arguments.Add(
            ($Extensions -join ",")
        )
    }

    # ============================================================
    # WICHTIG:
    #
    # NICHT:
    #
    #   {{ .FileName }}
    #
    # sondern:
    #
    #   {{ filenamify .FileName 180 }}
    #
    # Dadurch wird beispielsweise:
    #
    #   3. F*CKING SOCIETY.flac
    #
    # zu einem Windows-kompatiblen Dateinamen.
    # ============================================================

    $template =
        '{{ filenamify .FileName 180 }}'

    [void]$arguments.Add("--template")
    [void]$arguments.Add($template)

    # ============================================================
    # Gleiches File + gleiche Größe => skip
    # ============================================================

    [void]$arguments.Add("--skip-same")

    if ($Takeout) {
        [void]$arguments.Add("--takeout")
    }

    if ($ContinueDownload) {
        [void]$arguments.Add("--continue")
    }

    if ($RestartDownload) {
        [void]$arguments.Add("--restart")
    }

    if ($RewriteExt) {
        [void]$arguments.Add("--rewrite-ext")
    }

    if ($Desc) {
        [void]$arguments.Add("--desc")
    }

    if ($Group) {
        [void]$arguments.Add("--group")
    }

    foreach ($argument in $TdlExtraArguments) {

        if (-not [string]::IsNullOrWhiteSpace($argument)) {
            [void]$arguments.Add($argument)
        }
    }

    return @($arguments)
}

# ================================================================
# LIVE NATIVE PROCESS HELPERS
# ================================================================

function ConvertTo-WindowsNativeArgument {

    param(
        [AllowEmptyString()]
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    # ProcessStartInfo.Arguments is one Windows command-line string in
    # Windows PowerShell 5.1. Quote argv elements using the standard
    # backslash/quote rules so paths containing spaces or quotes reach tdl
    # unchanged.
    if ($Value.Length -eq 0) {
        return '""'
    }

    if ($Value -notmatch '[\s"]') {
        return $Value
    }

    $builder = New-Object System.Text.StringBuilder
    [void]$builder.Append('"')
    $backslashes = 0

    foreach ($character in $Value.ToCharArray()) {

        if ($character -eq '\') {
            $backslashes++
            continue
        }

        if ($character -eq '"') {
            if ($backslashes -gt 0) {
                [void]$builder.Append(('\' * ($backslashes * 2)))
            }
            [void]$builder.Append('\"')
            $backslashes = 0
            continue
        }

        if ($backslashes -gt 0) {
            [void]$builder.Append(('\' * $backslashes))
            $backslashes = 0
        }

        [void]$builder.Append($character)
    }

    if ($backslashes -gt 0) {
        [void]$builder.Append(('\' * ($backslashes * 2)))
    }

    [void]$builder.Append('"')
    return $builder.ToString()
}

function Invoke-TdlLiveProcess {

    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $allArguments = @(
        Get-TdlGlobalArguments
        $Arguments
    )

    $isWindowsPlatform =
        [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
            [System.Runtime.InteropServices.OSPlatform]::Windows
        )

    if (-not $isWindowsPlatform) {
        & $TdlPath @allArguments
        return [PSCustomObject]@{
            ExitCode = $LASTEXITCODE
            ProcessId = $null
            RuntimeSeconds = $null
        }
    }

    $quotedArguments = @(
        foreach ($argument in $allArguments) {
            ConvertTo-WindowsNativeArgument -Value ([string]$argument)
        }
    )

    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $TdlPath
    $startInfo.Arguments = ($quotedArguments -join ' ')
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $false
    $startInfo.RedirectStandardOutput = $false
    $startInfo.RedirectStandardError = $false
    $startInfo.RedirectStandardInput = $false
    $startInfo.WorkingDirectory = (Get-Location).Path

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        if (-not $process.Start()) {
            throw "tdl.exe konnte nicht gestartet werden."
        }

        Write-Host (
            "tdl process started. PID: " + $process.Id
        ) -ForegroundColor DarkGray
        Write-Host (
            "Process check: Get-Process -Id " + $process.Id
        ) -ForegroundColor DarkGray
        Write-Host ""

        $process.WaitForExit()
        $stopwatch.Stop()
        $exitCode = $process.ExitCode

        Write-Host ""
        Write-Host (
            "tdl process exited. PID: " + $process.Id +
            ", ExitCode: " + $exitCode +
            ", Runtime: " + [Math]::Round($stopwatch.Elapsed.TotalSeconds, 1) +
            "s"
        ) -ForegroundColor DarkGray

        return [PSCustomObject]@{
            ExitCode = $exitCode
            ProcessId = $process.Id
            RuntimeSeconds = $stopwatch.Elapsed.TotalSeconds
        }
    }
    finally {
        if ($stopwatch.IsRunning) {
            $stopwatch.Stop()
        }
        $process.Dispose()
    }
}

# ================================================================
# TDL INVOKE
# ================================================================

function Invoke-TdlNative {

    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,

        [switch]$CaptureOutput
    )

    $allArguments =
        @(
            Get-TdlGlobalArguments
            $Arguments
        )

    $oldErrorPreference =
        $ErrorActionPreference

    $ErrorActionPreference = "Continue"

    try {

        if ($CaptureOutput) {

            $output =
                & $TdlPath @allArguments 2>&1

            $exitCode =
                $LASTEXITCODE

            return [PSCustomObject]@{
                ExitCode = $exitCode
                Output   = @($output)
                Text     = (
                    $output |
                    Out-String
                ).Trim()
            }
        }

        & $TdlPath @allArguments 2>&1

        $exitCode =
            $LASTEXITCODE

        return [PSCustomObject]@{
            ExitCode = $exitCode
            Output   = @()
            Text     = ""
        }
    }
    finally {

        $ErrorActionPreference =
            $oldErrorPreference
    }
}

# ================================================================
# JSON TDL
# ================================================================

function Invoke-TdlJson {

    param(
        [Parameter(Mandatory = $true)]
        [string[]]$CommandArguments
    )

    $result =
        Invoke-TdlNative `
            -Arguments $CommandArguments `
            -CaptureOutput

    if ($result.ExitCode -ne 0) {

        $text = $result.Text

        if ($text -match "not authorized") {

            throw (
                (T "NotAuthenticated") +
                "`n`n" +
                (T "LoginHint") +
                "`n`n" +
                ".\tdl.exe login -n $Namespace -d `"<tdata-path>`""
            )
        }

        if (
            $text -match
            "database is used by another process"
        ) {

            throw (
                "Die tdl-Datenbank des Namespace '$Namespace' " +
                "wird bereits von einem anderen Prozess verwendet."
            )
        }

        if ([string]::IsNullOrWhiteSpace($text)) {

            $text =
                "tdl.exe wurde mit ExitCode " +
                $result.ExitCode +
                " beendet."
        }

        throw $text
    }

    if ([string]::IsNullOrWhiteSpace($result.Text)) {

        throw (
            "tdl.exe hat keine JSON-Daten zurückgegeben."
        )
    }

    try {

        return (
            $result.Text |
            ConvertFrom-Json
        )
    }
    catch {

        throw (
            "Die Ausgabe von tdl.exe konnte nicht " +
            "als JSON gelesen werden.`n`n" +
            $result.Text
        )
    }
}

# ================================================================
# CHAT LISTE
# ================================================================

function Get-Chats {

    Write-LineSafe `
        (T "LoadingChats") `
        $Script:HeaderColor

    $result =
        Invoke-TdlJson `
            -CommandArguments @(
                "chat",
                "ls",
                "-o",
                "json"
            )

    if ($null -eq $result) {
        throw "tdl hat keine Chats geliefert."
    }

    return @($result)
}

# ================================================================
# AUTH
# ================================================================

function Get-SidecartStateRoot {

    $base = $env:LOCALAPPDATA

    if ([string]::IsNullOrWhiteSpace($base)) {
        $base = [System.IO.Path]::GetTempPath()
    }

    $root = Join-Path $base "tdl-sidecart"

    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        New-Item -ItemType Directory -Path $root -Force | Out-Null
    }

    return $root
}

function Get-StableHexHash {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    $sha = [System.Security.Cryptography.SHA256]::Create()

    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
        $hash = $sha.ComputeHash($bytes)
        return (-join ($hash | ForEach-Object { $_.ToString("x2") }))
    }
    finally {
        $sha.Dispose()
    }
}

function Get-CanonicalTdataPath {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    try {
        $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        $fullPath = [System.IO.Path]::GetFullPath($item.FullName)
    }
    catch {
        $fullPath = [System.IO.Path]::GetFullPath($Path)
    }

    return $fullPath.TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
}

function Try-AcquireTdataLease {

    param(
        [Parameter(Mandatory = $true)]
        [string]$TdataPath
    )

    $canonicalPath = Get-CanonicalTdataPath -Path $TdataPath
    $key = $canonicalPath.ToLowerInvariant()

    if ($Script:TdataLeaseStreams.ContainsKey($key)) {
        return $true
    }

    $lockRoot = Join-Path (Get-SidecartStateRoot) "tdata-locks"

    if (-not (Test-Path -LiteralPath $lockRoot -PathType Container)) {
        New-Item -ItemType Directory -Path $lockRoot -Force | Out-Null
    }

    $hash = Get-StableHexHash -Value $key
    $lockPath = Join-Path $lockRoot ($hash + ".lock")

    try {
        $stream = [System.IO.File]::Open(
            $lockPath,
            [System.IO.FileMode]::OpenOrCreate,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None
        )
    }
    catch [System.IO.IOException] {
        return $false
    }
    catch [System.UnauthorizedAccessException] {
        return $false
    }

    try {
        $metadata = [PSCustomObject]@{
            pid        = $PID
            namespace  = $Namespace
            tdata      = $canonicalPath
            startedUtc = [DateTime]::UtcNow.ToString("o")
        } | ConvertTo-Json -Compress

        $bytes = [System.Text.Encoding]::UTF8.GetBytes($metadata)
        $stream.SetLength(0)
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush()

        $Script:TdataLeaseStreams[$key] = $stream
        $Script:ActiveTdataPath = $canonicalPath
        return $true
    }
    catch {
        $stream.Dispose()
        throw
    }
}

function Release-TdataLease {

    param(
        [Parameter(Mandatory = $true)]
        [string]$TdataPath
    )

    $canonicalPath = Get-CanonicalTdataPath -Path $TdataPath
    $key = $canonicalPath.ToLowerInvariant()

    if (-not $Script:TdataLeaseStreams.ContainsKey($key)) {
        return
    }

    try {
        $Script:TdataLeaseStreams[$key].Dispose()
    }
    finally {
        [void]$Script:TdataLeaseStreams.Remove($key)

        if ($Script:ActiveTdataPath -ieq $canonicalPath) {
            $Script:ActiveTdataPath = $null
        }
    }
}

function Get-NamespaceAssociationPath {

    param(
        [Parameter(Mandatory = $true)]
        [string]$NamespaceName
    )

    $root = Join-Path (Get-SidecartStateRoot) "namespace-tdata"

    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        New-Item -ItemType Directory -Path $root -Force | Out-Null
    }

    $hash = Get-StableHexHash -Value $NamespaceName.ToLowerInvariant()
    return (Join-Path $root ($hash + ".txt"))
}

function Save-NamespaceTdataAssociation {

    param(
        [Parameter(Mandatory = $true)]
        [string]$NamespaceName,

        [Parameter(Mandatory = $true)]
        [string]$TdataPath
    )

    $associationPath = Get-NamespaceAssociationPath -NamespaceName $NamespaceName
    $canonicalPath = Get-CanonicalTdataPath -Path $TdataPath
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($associationPath, $canonicalPath, $encoding)
}

function Get-NamespaceTdataAssociation {

    param(
        [Parameter(Mandatory = $true)]
        [string]$NamespaceName
    )

    $associationPath = Get-NamespaceAssociationPath -NamespaceName $NamespaceName

    if (-not (Test-Path -LiteralPath $associationPath -PathType Leaf)) {
        return $null
    }

    try {
        $path = [System.IO.File]::ReadAllText($associationPath).Trim()

        if (
            -not [string]::IsNullOrWhiteSpace($path) -and
            (Test-Path -LiteralPath $path -PathType Container)
        ) {
            return $path
        }
    }
    catch {
    }

    return $null
}

function Ensure-NamespaceTdataLease {

    param(
        [Parameter(Mandatory = $true)]
        [string]$NamespaceName
    )

    $associatedPath = Get-NamespaceTdataAssociation -NamespaceName $NamespaceName

    if ([string]::IsNullOrWhiteSpace($associatedPath)) {
        return $true
    }

    if (Try-AcquireTdataLease -TdataPath $associatedPath) {
        return $true
    }

    Write-Host ""
    Write-Host (T "AutoAuthInUse") -ForegroundColor DarkYellow
    Write-Host $associatedPath -ForegroundColor Yellow
    return $false
}

function New-ParallelSidecartNamespace {

    $machineHash = Get-StableHexHash -Value ([Environment]::MachineName)
    return ("sidecart_{0}_{1}" -f $machineHash.Substring(0, 10), $PID)
}

function Install-NewTelegramDesktopClient {

    $isWindows = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
        [System.Runtime.InteropServices.OSPlatform]::Windows
    )

    if (-not $isWindows) {
        throw "Die automatische Installation eines neuen Telegram-Desktop-Clients ist in dieser PowerShell-Version nur unter Windows verfügbar."
    }

    Write-Host ""
    Write-Host (T "AutoAuthInstalling") -ForegroundColor Cyan

    $downloadUrl = if ([Environment]::Is64BitOperatingSystem) {
        "https://telegram.org/dl/desktop/win64_portable"
    }
    else {
        "https://telegram.org/dl/desktop/win_portable"
    }

    $clientsRoot = Join-Path (Get-SidecartStateRoot) "telegram-clients"

    if (-not (Test-Path -LiteralPath $clientsRoot -PathType Container)) {
        New-Item -ItemType Directory -Path $clientsRoot -Force | Out-Null
    }

    $clientId = "client_{0}_{1}" -f (
        [DateTime]::Now.ToString("yyyyMMdd_HHmmss")
    ), ([Guid]::NewGuid().ToString("N").Substring(0, 8))

    $clientRoot = Join-Path $clientsRoot $clientId
    $workDir = Join-Path $clientRoot "profile"
    $zipPath = Join-Path ([System.IO.Path]::GetTempPath()) ($clientId + ".zip")

    New-Item -ItemType Directory -Path $clientRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $workDir -Force | Out-Null

    $oldProtocol = [System.Net.ServicePointManager]::SecurityProtocol

    try {
        [System.Net.ServicePointManager]::SecurityProtocol =
            $oldProtocol -bor [System.Net.SecurityProtocolType]::Tls12

        Write-Host ("  Download: {0}" -f $downloadUrl) -ForegroundColor DarkGray
        Write-Host ("  Ziel:     {0}" -f $clientRoot) -ForegroundColor DarkGray

        Invoke-WebRequest `
            -Uri $downloadUrl `
            -OutFile $zipPath `
            -UseBasicParsing `
            -ErrorAction Stop

        $zipInfo = Get-Item -LiteralPath $zipPath -ErrorAction Stop

        if ($zipInfo.Length -lt 1048576) {
            throw "Der heruntergeladene Telegram-Desktop-Client ist unerwartet klein und wird nicht ausgeführt."
        }

        $header = New-Object byte[] 2
        $headerStream = [System.IO.File]::OpenRead($zipPath)
        try {
            $read = $headerStream.Read($header, 0, 2)
        }
        finally {
            $headerStream.Dispose()
        }

        if ($read -ne 2 -or $header[0] -ne 0x50 -or $header[1] -ne 0x4B) {
            throw "Die offizielle Telegram-Portable-Datei ist kein gültiges ZIP-Archiv."
        }

        Expand-Archive -LiteralPath $zipPath -DestinationPath $clientRoot -Force

        $telegramExe = @(
            Get-ChildItem `
                -LiteralPath $clientRoot `
                -Filter "Telegram.exe" `
                -File `
                -Recurse `
                -ErrorAction Stop
        ) | Select-Object -First 1

        if ($null -eq $telegramExe) {
            throw "Telegram.exe wurde im offiziellen Portable-Archiv nicht gefunden."
        }

        Write-Host ""
        Write-Host (T "AutoAuthClientReady") -ForegroundColor Green
        Write-Host ("  Client:  {0}" -f $telegramExe.FullName) -ForegroundColor DarkGray
        Write-Host ("  Workdir: {0}" -f $workDir) -ForegroundColor DarkGray

        $process = Start-Process `
            -FilePath $telegramExe.FullName `
            -ArgumentList @(
                "-many",
                "-workdir",
                ('"' + $workDir + '"')
            ) `
            -WorkingDirectory $telegramExe.DirectoryName `
            -PassThru

        $tdataPath = Join-Path $workDir "tdata"
        $lastStatus = [DateTime]::MinValue

        while ($true) {

            $candidate = New-TdataCandidate -Path $tdataPath -Source "Known"

            if ($null -ne $candidate -and $candidate.HasKeyData) {
                return $candidate
            }

            if ($process.HasExited) {
                throw "Der neue Telegram-Desktop-Client wurde beendet, bevor eine tdata-Sitzung erstellt wurde."
            }

            if (([DateTime]::UtcNow - $lastStatus).TotalSeconds -ge 10) {
                Write-Host (T "AutoAuthWaitingClient") -ForegroundColor DarkGray
                Write-Host "  ESC = Abbrechen" -ForegroundColor DarkGray
                $lastStatus = [DateTime]::UtcNow
            }

            if (-not $NonInteractive) {
                try {
                    if ([Console]::KeyAvailable) {
                        $key = [Console]::ReadKey($true)
                        if ($key.Key -eq [ConsoleKey]::Escape) {
                            throw (T "Cancelled")
                        }
                    }
                }
                catch [System.InvalidOperationException] {
                }
            }

            Start-Sleep -Seconds 2
        }
    }
    finally {
        [System.Net.ServicePointManager]::SecurityProtocol = $oldProtocol
        Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-TdlLoginCandidate {

    param(
        [Parameter(Mandatory = $true)]
        [object]$Candidate
    )

    if (-not (Try-AcquireTdataLease -TdataPath $Candidate.Path)) {
        Write-Host ""
        Write-Host (T "AutoAuthInUse") -ForegroundColor DarkYellow
        Write-Host $Candidate.Path -ForegroundColor Yellow
        return $false
    }

    $keepLease = $false

    try {
        if (Invoke-TdlLoginFromTdata -TdataPath $Candidate.Path) {
            Save-NamespaceTdataAssociation `
                -NamespaceName $Namespace `
                -TdataPath $Candidate.Path

            $keepLease = $true
            return $true
        }

        return $false
    }
    finally {
        if (-not $keepLease) {
            Release-TdataLease -TdataPath $Candidate.Path
        }
    }
}

function New-TdataCandidate {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [ValidateSet("Known", "System")]
        [string]$Source
    )

    try {

        $item =
            Get-Item `
                -LiteralPath $Path `
                -Force `
                -ErrorAction Stop
    }
    catch {
        return $null
    }

    if (-not $item.PSIsContainer) {
        return $null
    }

    if ($item.Name -ine "tdata") {
        return $null
    }

    $hasKeyData =
        Test-Path `
            -LiteralPath (Join-Path $item.FullName "key_data") `
            -PathType Leaf

    try {
        $lastWriteTime = $item.LastWriteTimeUtc
    }
    catch {
        $lastWriteTime = [DateTime]::MinValue
    }

    return [PSCustomObject]@{
        Path          = $item.FullName
        Source        = $Source
        HasKeyData    = [bool]$hasKeyData
        LastWriteTime = $lastWriteTime
    }
}

function Get-UniqueTdataCandidates {

    param(
        [Parameter(Mandatory = $true)]
        [object[]]$Candidates
    )

    $seen = @{}
    $result =
        [System.Collections.Generic.List[object]]::new()

    foreach ($candidate in $Candidates) {

        if ($null -eq $candidate) {
            continue
        }

        $key =
            [string]$candidate.Path

        if ([string]::IsNullOrWhiteSpace($key)) {
            continue
        }

        if ($seen.ContainsKey($key)) {
            continue
        }

        $seen[$key] = $true
        [void]$result.Add($candidate)
    }

    return @($result)
}

function Get-KnownTdataCandidates {

    $candidatePaths =
        [System.Collections.Generic.List[string]]::new()

    function Add-KnownTdataPath {

        param(
            [string]$BasePath,
            [string]$ChildPath
        )

        if ([string]::IsNullOrWhiteSpace($BasePath)) {
            return
        }

        try {
            [void]$candidatePaths.Add(
                (Join-Path $BasePath $ChildPath)
            )
        }
        catch {
        }
    }

    # Explizit bekannte bzw. verbreitete Installations-/Portable-Pfade.
    # Die beiden vom Benutzer genannten Varianten stehen bewusst weit oben.
    Add-KnownTdataPath $env:USERPROFILE "Desktop\tdata"
    Add-KnownTdataPath $env:USERPROFILE "iGram Desktop\tdata"

    # Windows kann Desktop/Dokumente z. B. nach OneDrive umleiten.
    # GetFolderPath liefert dann den tatsächlich verwendeten Benutzerpfad.
    try {
        $desktopFolder =
            [Environment]::GetFolderPath("Desktop")

        Add-KnownTdataPath $desktopFolder "tdata"
        Add-KnownTdataPath $desktopFolder "Telegram Desktop\tdata"
        Add-KnownTdataPath $desktopFolder "iGram Desktop\tdata"
    }
    catch {
    }

    try {
        $documentsFolder =
            [Environment]::GetFolderPath("MyDocuments")

        Add-KnownTdataPath $documentsFolder "Telegram Desktop\tdata"
        Add-KnownTdataPath $documentsFolder "iGram Desktop\tdata"
    }
    catch {
    }
    Add-KnownTdataPath $env:APPDATA "Telegram Desktop\tdata"
    Add-KnownTdataPath $env:LOCALAPPDATA "Telegram Desktop\tdata"
    Add-KnownTdataPath $env:USERPROFILE "Desktop\Telegram Desktop\tdata"
    Add-KnownTdataPath $env:USERPROFILE "Desktop\iGram Desktop\tdata"
    Add-KnownTdataPath $env:USERPROFILE "Downloads\Telegram Desktop\tdata"
    Add-KnownTdataPath $env:USERPROFILE "Downloads\iGram Desktop\tdata"
    Add-KnownTdataPath $env:USERPROFILE "Documents\Telegram Desktop\tdata"
    Add-KnownTdataPath $env:USERPROFILE "Telegram Desktop\tdata"

    # Microsoft-Store/MSIX-Installationen liegen häufig unter LocalAppData\Packages.
    # Nur Telegram-bezogene Pakete werden hier gezielt geprüft; dies ist noch
    # Teil der schnellen Suche und keine rekursive Systemsuche.
    if (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {

        try {
            $packagesRoot =
                Join-Path $env:LOCALAPPDATA "Packages"

            if (Test-Path -LiteralPath $packagesRoot -PathType Container) {

                foreach (
                    $packageDirectory in @(
                        Get-ChildItem `
                            -LiteralPath $packagesRoot `
                            -Directory `
                            -Filter "*Telegram*" `
                            -Force `
                            -ErrorAction SilentlyContinue
                    )
                ) {

                    Add-KnownTdataPath `
                        $packageDirectory.FullName `
                        "LocalCache\Roaming\Telegram Desktop\tdata"

                    Add-KnownTdataPath `
                        $packageDirectory.FullName `
                        "LocalState\Telegram Desktop\tdata"
                }
            }
        }
        catch {
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        Add-KnownTdataPath $PSScriptRoot "tdata"
        Add-KnownTdataPath $PSScriptRoot "Telegram Desktop\tdata"
        Add-KnownTdataPath $PSScriptRoot "iGram Desktop\tdata"
    }

    # Von tdl-sidecart selbst angelegte portable Telegram-Clients gezielt
    # in die schnelle Suchschicht aufnehmen. Dadurch ist nach einem Neustart
    # keine erneute systemweite Suche notwendig.
    try {
        $managedClientsRoot = Join-Path (Get-SidecartStateRoot) "telegram-clients"

        if (Test-Path -LiteralPath $managedClientsRoot -PathType Container) {
            foreach (
                $managedClient in @(
                    Get-ChildItem `
                        -LiteralPath $managedClientsRoot `
                        -Directory `
                        -Force `
                        -ErrorAction SilentlyContinue
                )
            ) {
                Add-KnownTdataPath $managedClient.FullName "profile\tdata"
            }
        }
    }
    catch {
    }

    try {
        $currentDirectory = (Get-Location).Path
        Add-KnownTdataPath $currentDirectory "tdata"
        Add-KnownTdataPath $currentDirectory "Telegram Desktop\tdata"
        Add-KnownTdataPath $currentDirectory "iGram Desktop\tdata"
    }
    catch {
    }

    # Zweiter Teil der schnellen Ebene: nur unmittelbare Unterordner
    # typischer Benutzerverzeichnisse betrachten. Das findet auch
    # portable/fork-spezifische Ordnernamen, ohne bereits das ganze
    # Dateisystem rekursiv zu durchsuchen.
    $commonParents =
        [System.Collections.Generic.List[string]]::new()

    foreach ($basePath in @(
        $env:USERPROFILE,
        $env:APPDATA,
        $env:LOCALAPPDATA
    )) {

        if (-not [string]::IsNullOrWhiteSpace($basePath)) {
            [void]$commonParents.Add($basePath)
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($env:USERPROFILE)) {

        foreach ($child in @(
            "Desktop",
            "Downloads",
            "Documents"
        )) {

            try {
                [void]$commonParents.Add(
                    (Join-Path $env:USERPROFILE $child)
                )
            }
            catch {
            }
        }
    }

    foreach ($parent in $commonParents) {

        if ([string]::IsNullOrWhiteSpace($parent)) {
            continue
        }

        if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
            continue
        }

        try {

            foreach (
                $directory in @(
                    Get-ChildItem `
                        -LiteralPath $parent `
                        -Directory `
                        -Force `
                        -ErrorAction SilentlyContinue
                )
            ) {

                Add-KnownTdataPath `
                    $directory.FullName `
                    "tdata"
            }
        }
        catch {
        }
    }

    $candidates =
        [System.Collections.Generic.List[object]]::new()

    foreach ($path in $candidatePaths) {

        $candidate =
            New-TdataCandidate `
                -Path $path `
                -Source "Known"

        if ($null -ne $candidate) {
            [void]$candidates.Add($candidate)
        }
    }

    return @(
        Get-UniqueTdataCandidates `
            -Candidates @($candidates)
    )
}

function Find-SystemTdataCandidates {

    param(
        [string[]]$ExcludePaths = @()
    )

    $excluded = @{}

    foreach ($path in $ExcludePaths) {
        if (-not [string]::IsNullOrWhiteSpace($path)) {
            $excluded[$path] = $true
        }
    }

    $results =
        [System.Collections.Generic.List[object]]::new()

    $resultPaths = @{}

    $drives = @(
        [System.IO.DriveInfo]::GetDrives() |
        Where-Object {
            $_.IsReady -and
            (
                $_.DriveType -eq [System.IO.DriveType]::Fixed -or
                $_.DriveType -eq [System.IO.DriveType]::Removable
            )
        }
    )

    foreach ($drive in $drives) {

        $root = $drive.RootDirectory.FullName

        Write-Host (
            "  Suche auf Laufwerk {0}" -f $root
        ) -ForegroundColor DarkGray

        $queue =
            [System.Collections.Generic.Queue[string]]::new()

        $queue.Enqueue($root)
        $visitedDirectoryCount = 0

        while ($queue.Count -gt 0) {

            $current = $queue.Dequeue()
            $visitedDirectoryCount++

            try {
                $directories =
                    [System.IO.Directory]::EnumerateDirectories($current)
            }
            catch {
                continue
            }

            foreach ($directory in $directories) {

                try {
                    $attributes =
                        [System.IO.File]::GetAttributes($directory)
                }
                catch {
                    continue
                }

                # Junctions/Symlinks werden nicht verfolgt. Das verhindert
                # Schleifen und das unbeabsichtigte Verlassen lokaler Volumes.
                if (
                    ($attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
                ) {
                    continue
                }

                $leafName =
                    [System.IO.Path]::GetFileName(
                        $directory.TrimEnd(
                            [System.IO.Path]::DirectorySeparatorChar,
                            [System.IO.Path]::AltDirectorySeparatorChar
                        )
                    )

                if ($leafName -ieq "tdata") {

                    $candidate =
                        New-TdataCandidate `
                            -Path $directory `
                            -Source "System"

                    if (
                        $null -ne $candidate -and
                        -not $excluded.ContainsKey($candidate.Path) -and
                        -not $resultPaths.ContainsKey($candidate.Path)
                    ) {

                        $resultPaths[$candidate.Path] = $true
                        [void]$results.Add($candidate)

                        Write-Host (
                            "    {0} {1}" -f
                            (T "AutoAuthFound"),
                            $candidate.Path
                        ) -ForegroundColor Green
                    }

                    # Innerhalb eines tdata-Verzeichnisses muss nicht weiter
                    # nach einem weiteren tdata gesucht werden.
                    continue
                }

                # Diese Verzeichnisse sind entweder absichtlich geschützt
                # oder reine System-Metadaten. Sie enthalten keine normale
                # Telegram-Desktop-Installation und verursachen sonst viel I/O.
                if (
                    $leafName -ieq "System Volume Information" -or
                    $leafName -ieq '$RECYCLE.BIN'
                ) {
                    continue
                }

                $queue.Enqueue($directory)
            }
        }
    }

    return @(
        $results |
        Sort-Object `
            @{ Expression = { -not $_.HasKeyData }; Ascending = $true },
            @{ Expression = { $_.LastWriteTime }; Descending = $true }
    )
}

function Test-TdlAuthorizationRaw {

    $result =
        Invoke-TdlNative `
            -Arguments @(
                "chat",
                "ls",
                "-o",
                "json"
            ) `
            -CaptureOutput

    if ($result.ExitCode -eq 0) {
        return $true
    }

    if (
        $result.Text -match
        "not authorized|not authenticated|nicht authentifiziert"
    ) {
        return $false
    }

    if ([string]::IsNullOrWhiteSpace($result.Text)) {
        throw (
            "tdl.exe wurde mit ExitCode " +
            $result.ExitCode +
            " beendet."
        )
    }

    throw $result.Text
}

function Invoke-TdlLoginFromTdata {

    param(
        [Parameter(Mandatory = $true)]
        [string]$TdataPath
    )

    Write-Host ""
    Write-Host (
        T "AutoAuthTrying"
    ) -ForegroundColor Cyan

    Write-Host `
        $TdataPath `
        -ForegroundColor Yellow

    Write-Host ""

    $loginArguments = @(
        "login",
        "-n",
        $Namespace,
        "-d",
        $TdataPath
    )

    $oldErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {

        # Absichtlich direkter nativer Aufruf statt Invoke-TdlNative:
        # Login darf keine Transfer-Flags (-l/-t/--delay/--pool usw.)
        # erhalten und muss interaktiv mit dem Benutzer kommunizieren können.
        & $TdlPath @loginArguments
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $oldErrorPreference
    }

    if ($exitCode -ne 0) {

        Write-Host (
            T "AutoAuthLoginFailed"
        ) -ForegroundColor DarkYellow

        return $false
    }

    if (Test-TdlAuthorizationRaw) {

        Write-Host ""
        Write-Host (
            T "AutoAuthSuccess"
        ) -ForegroundColor Green

        return $true
    }

    Write-Host (
        T "AutoAuthLoginFailed"
    ) -ForegroundColor DarkYellow

    return $false
}

function Invoke-AutomaticTdlAuthentication {

    Write-Host ""
    Write-Host (
        T "AutoAuthKnownSearch"
    ) -ForegroundColor Cyan

    $knownCandidates =
        @(Get-KnownTdataCandidates)

    foreach ($candidate in $knownCandidates) {

        Write-Host (
            "  {0} {1}" -f
            (T "AutoAuthFound"),
            $candidate.Path
        ) -ForegroundColor Green

        if (Invoke-TdlLoginCandidate -Candidate $candidate) {
            return $true
        }
    }

    Write-Host ""
    Write-Host (
        T "AutoAuthSystemSearch"
    ) -ForegroundColor Cyan

    $systemCandidates =
        @(
            Find-SystemTdataCandidates `
                -ExcludePaths @(
                    $knownCandidates |
                    ForEach-Object { $_.Path }
                )
        )

    foreach ($candidate in $systemCandidates) {

        if (Invoke-TdlLoginCandidate -Candidate $candidate) {
            return $true
        }
    }

    if (
        $knownCandidates.Count -eq 0 -and
        $systemCandidates.Count -eq 0
    ) {

        Write-Host ""
        Write-Host (
            T "AutoAuthNoTdata"
        ) -ForegroundColor DarkYellow
    }

    # Kein vorhandener Kandidat konnte exklusiv für diese Sidecart-Instanz
    # reserviert und erfolgreich importiert werden. Erzeuge deshalb einen
    # neuen, isolierten Telegram-Desktop-Client und warte auf dessen Login.
    $newCandidate = Install-NewTelegramDesktopClient

    if ($null -ne $newCandidate) {
        Write-Host ""
        Write-Host (
            "  {0} {1}" -f
            (T "AutoAuthFound"),
            $newCandidate.Path
        ) -ForegroundColor Green

        if (Invoke-TdlLoginCandidate -Candidate $newCandidate) {
            return $true
        }
    }

    return $false
}

function Test-TdlAuthorization {

    Write-Host ""
    Write-Host (
        T "CheckingSession"
    ) -ForegroundColor Cyan

    Write-Host (
        "$(T 'Namespace'): $Namespace"
    ) -ForegroundColor DarkGray

    try {

        $null =
            Invoke-TdlJson `
                -CommandArguments @(
                    "chat",
                    "ls",
                    "-o",
                    "json"
                )

        if (-not (Ensure-NamespaceTdataLease -NamespaceName $Namespace)) {

            if ($Script:NamespaceWasExplicit) {
                throw (
                    "Der für Namespace '$Namespace' zugeordnete tdata-Ordner " +
                    "wird bereits von einer anderen tdl-sidecart-Instanz verwendet."
                )
            }

            $script:Namespace = New-ParallelSidecartNamespace

            Write-Host ""
            Write-Host (T "AutoAuthParallelNs") -ForegroundColor DarkYellow
            Write-Host $Namespace -ForegroundColor Yellow

            if (Invoke-AutomaticTdlAuthentication) {
                return $true
            }

            throw "Für die parallele Instanz konnte keine Telegram-Sitzung bereitgestellt werden."
        }

        Write-Host (
            T "Authenticated"
        ) -ForegroundColor Green

        return $true
    }
    catch {

        $message =
            $_.Exception.Message

        if (
            $message -match
            "database is used by another process|namespace is already in use|wird bereits von einem anderen Prozess verwendet"
        ) {

            if ($Script:NamespaceWasExplicit) {
                throw
            }

            $script:Namespace = New-ParallelSidecartNamespace

            Write-Host ""
            Write-Host (T "AutoAuthParallelNs") -ForegroundColor DarkYellow
            Write-Host $Namespace -ForegroundColor Yellow

            if (Invoke-AutomaticTdlAuthentication) {
                Write-Host ""
                Write-Host (T "Authenticated") -ForegroundColor Green
                return $true
            }

            throw "Für die parallele Instanz konnte keine Telegram-Sitzung bereitgestellt werden."
        }

        if (
            $message -match
            "not authenticated|nicht authentifiziert"
        ) {

            Write-Host ""
            Write-Host (
                T "NotAuthenticated"
            ) -ForegroundColor Red

            Write-Host ""
            Write-Host (
                "$(T 'Namespace'):"
            ) -ForegroundColor Gray

            Write-Host `
                $Namespace `
                -ForegroundColor Yellow

            if (Invoke-AutomaticTdlAuthentication) {

                Write-Host ""
                Write-Host (
                    T "Authenticated"
                ) -ForegroundColor Green

                return $true
            }

            Write-Host ""
            Write-Host (
                T "LoginHint"
            ) -ForegroundColor Gray

            Write-Host ""
            Write-Host `
                ".\tdl.exe login -n $Namespace -d `"<tdata-path>`"" `
                -ForegroundColor Cyan

            throw
        }

        throw
    }
}

# ================================================================
# MENU
# ================================================================

function Get-VisiblePageStart {

    param(
        [int]$Index,
        [int]$Count,
        [int]$PageSize
    )

    if ($Count -le 0) {
        return 0
    }

    $page =
        [Math]::Floor(
            $Index / $PageSize
        )

    return [int](
        $page * $PageSize
    )
}

function Get-MenuItemLine {

    param(
        [Parameter(Mandatory = $true)]
        $Item,

        [Parameter(Mandatory = $true)]
        [scriptblock]$GetText,

        [Parameter(Mandatory = $true)]
        [scriptblock]$GetSelected,

        [bool]$Cursor = $false
    )

    $selected =
        [bool](
            & $GetSelected $Item
        )

    $mark =
        if ($selected) {
            "[X]"
        }
        else {
            "[ ]"
        }

    $text =
        [string](
            & $GetText $Item
        )

    $prefix =
        if ($Cursor) {
            "> "
        }
        else {
            "  "
        }

    $color =
        if ($Cursor) {
            $Script:MenuCursorColor
        }
        elseif ($selected) {
            $Script:MenuSelectedColor
        }
        else {
            $Script:MenuNormalColor
        }

    return [PSCustomObject]@{
        Text  = "$prefix$mark $text"
        Color = $color
    }
}

function Render-MenuPage {

    param(
        [Parameter(Mandatory = $true)]
        [array]$Items,

        [Parameter(Mandatory = $true)]
        [scriptblock]$GetText,

        [Parameter(Mandatory = $true)]
        [scriptblock]$GetSelected,

        [Parameter(Mandatory = $true)]
        [int]$Index
    )

    Clear-Screen

    Write-Host (
        T "Title"
    ) -ForegroundColor $Script:HeaderColor

    Write-Host ""

    $pageStart =
        Get-VisiblePageStart `
            -Index $Index `
            -Count $Items.Count `
            -PageSize $Script:PageSize

    $pageEnd =
        [Math]::Min(
            $Items.Count - 1,
            $pageStart +
            $Script:PageSize -
            1
        )

    for (
        $i = 0;
        $i -lt $Script:PageSize;
        $i++
    ) {

        $itemIndex =
            $pageStart + $i

        if ($itemIndex -le $pageEnd) {

            $line =
                Get-MenuItemLine `
                    -Item $Items[$itemIndex] `
                    -GetText $GetText `
                    -GetSelected $GetSelected `
                    -Cursor (
                        $itemIndex -eq $Index
                    )

            Write-Host `
                $line.Text `
                -ForegroundColor $line.Color
        }
    }

    Write-Host ""

    $selectedCount =
        @(
            $Items |
            Where-Object {
                [bool](
                    & $GetSelected $_
                )
            }
        ).Count

    Write-Host (
        "$(T 'Selected'): $selectedCount / $($Items.Count)"
    ) -ForegroundColor $Script:InfoColor

    Write-Host ""
    Write-Host (
        T "Navigation"
    ) -ForegroundColor $Script:InfoColor

    Write-Host (
        T "Navigation2"
    ) -ForegroundColor $Script:InfoColor
}

function Select-Items {

    param(
        [Parameter(Mandatory = $true)]
        [array]$Items,

        [Parameter(Mandatory = $true)]
        [scriptblock]$GetText,

        [Parameter(Mandatory = $true)]
        [scriptblock]$GetSelected,

        [Parameter(Mandatory = $true)]
        [scriptblock]$SetSelected,

        [Parameter(Mandatory = $true)]
        [string]$Title
    )

    $Items = @($Items)

    if ($Items.Count -eq 0) {
        throw (T "NoSelection")
    }

    $index = 0

    $oldCursor =
        $true

    try {

        try {
            $oldCursor =
                [Console]::CursorVisible
        }
        catch {
        }

        Set-ConsoleCursorVisible $false

        while ($true) {

            Clear-Screen

            Write-Host `
                $Title `
                -ForegroundColor $Script:HeaderColor

            Write-Host ""

            $pageStart =
                Get-VisiblePageStart `
                    -Index $index `
                    -Count $Items.Count `
                    -PageSize $Script:PageSize

            $pageEnd =
                [Math]::Min(
                    $Items.Count - 1,
                    $pageStart +
                    $Script:PageSize -
                    1
                )

            for (
                $i = $pageStart;
                $i -le $pageEnd;
                $i++
            ) {

                $line =
                    Get-MenuItemLine `
                        -Item $Items[$i] `
                        -GetText $GetText `
                        -GetSelected $GetSelected `
                        -Cursor (
                            $i -eq $index
                        )

                Write-Host `
                    $line.Text `
                    -ForegroundColor $line.Color
            }

            Write-Host ""

            $selectedCount =
                @(
                    $Items |
                    Where-Object {
                        [bool](
                            & $GetSelected $_
                        )
                    }
                ).Count

            Write-Host (
                "$(T 'Selected'): $selectedCount / $($Items.Count)"
            ) -ForegroundColor $Script:InfoColor

            Write-Host ""
            Write-Host (
                T "Navigation"
            ) -ForegroundColor $Script:InfoColor

            Write-Host (
                T "Navigation2"
            ) -ForegroundColor $Script:InfoColor

            $key =
                [Console]::ReadKey($true)

            switch ($key.Key) {

                "UpArrow" {

                    if ($index -gt 0) {
                        $index--
                    }
                }

                "DownArrow" {

                    if ($index -lt ($Items.Count - 1)) {
                        $index++
                    }
                }

                "Home" {

                    $index = 0
                }

                "End" {

                    $index =
                        $Items.Count - 1
                }

                "Spacebar" {

                    $current =
                        [bool](
                            & $GetSelected `
                                $Items[$index]
                        )

                    & $SetSelected `
                        $Items[$index] `
                        (-not $current)
                }

                "Enter" {

                    $selected =
                        @(
                            $Items |
                            Where-Object {
                                [bool](
                                    & $GetSelected $_
                                )
                            }
                        )

                    if ($selected.Count -gt 0) {
                        return @($selected)
                    }
                }

                "Escape" {

                    throw (T "Cancelled")
                }
            }
        }
    }
    finally {

        Set-ConsoleCursorVisible $oldCursor
    }
}

# ================================================================
# CHAT AUSWAHL
# ================================================================

function Select-Chats {

    param(
        [Parameter(Mandatory = $true)]
        [array]$Chats
    )

    foreach ($chat in $Chats) {

        $chat |
            Add-Member `
                -MemberType NoteProperty `
                -Name "__Selected" `
                -Value $false `
                -Force

        $chat |
            Add-Member `
                -MemberType NoteProperty `
                -Name "__TopicCount" `
                -Value (
                    @(Get-Topics $chat).Count
                ) `
                -Force
    }

    $getText = {

        param($chat)

        $name =
            Get-ChatName $chat

        $type =
            Get-ChatType $chat

        $id =
            Get-ChatId $chat

        $topicCount =
            [int]$chat.__TopicCount

        $topicText =
            if ($topicCount -gt 0) {
                " ($topicCount Topics)"
            }
            else {
                ""
            }

        return (
            (Limit-Text $name 60) +
            " [$type]" +
            $topicText +
            "  ID=$id"
        )
    }

    $getSelected = {

        param($chat)

        return [bool]$chat.__Selected
    }

    $setSelected = {

        param(
            $chat,
            $value
        )

        $chat.__Selected =
            [bool]$value
    }

    return @(
        Select-Items `
            -Items $Chats `
            -GetText $getText `
            -GetSelected $getSelected `
            -SetSelected $setSelected `
            -Title (T "Chats")
    )
}

# ================================================================
# TOPICS
# ================================================================

function Select-Topics {

    param(
        [Parameter(Mandatory = $true)]
        $Chat
    )

    $topics =
        @(Get-Topics $Chat)

    if ($topics.Count -eq 0) {
        return @()
    }

    foreach ($topic in $topics) {

        $topic |
            Add-Member `
                -MemberType NoteProperty `
                -Name "__Selected" `
                -Value $false `
                -Force
    }

    $getText = {

        param($topic)

        return (
            (Limit-Text (Get-TopicName $topic) 85) +
            "  ID=" +
            (Get-TopicId $topic)
        )
    }

    $getSelected = {

        param($topic)

        return [bool]$topic.__Selected
    }

    $setSelected = {

        param(
            $topic,
            $value
        )

        $topic.__Selected =
            [bool]$value
    }

    return @(
        Select-Items `
            -Items $topics `
            -GetText $getText `
            -GetSelected $getSelected `
            -SetSelected $setSelected `
            -Title (T "Topics")
    )
}

# ================================================================
# MEDIEN
# ================================================================

function Select-MediaTypes {

    $items = @(
        [PSCustomObject]@{
            Name        = "Archive"
            Description = "ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ"
            Extensions = @(
                $Script:ArchiveExtensions
            )
            __Selected = $false
        }

        [PSCustomObject]@{
            Name        = "Audio"
            Description = "MP3, FLAC, WAV, M4A, AAC, OGG, OPUS"
            Extensions = @(
                $Script:AudioExtensions
            )
            __Selected = $true
        }

        [PSCustomObject]@{
            Name        = "Images"
            Description = "JPG, JPEG, PNG, GIF, WEBP, HEIC, AVIF"
            Extensions = @(
                $Script:ImageExtensions
            )
            __Selected = $false
        }

        [PSCustomObject]@{
            Name        = "Video"
            Description = "MP4, MKV, AVI, MOV, WEBM, M4V"
            Extensions = @(
                $Script:VideoExtensions
            )
            __Selected = $false
        }
    )

    $getText = {

        param($media)

        return (
            $media.Name +
            " - " +
            $media.Description +
            " [" +
            @($media.Extensions).Count +
            "]"
        )
    }

    $getSelected = {

        param($media)

        return [bool]$media.__Selected
    }

    $setSelected = {

        param(
            $media,
            $value
        )

        $media.__Selected =
            [bool]$value
    }

    $selected =
        @(
            Select-Items `
                -Items $items `
                -GetText $getText `
                -GetSelected $getSelected `
                -SetSelected $setSelected `
                -Title (T "Media")
        )

    if ($selected.Count -eq 0) {
        throw (T "NoSelection")
    }

    $extensions =
        [System.Collections.Generic.List[string]]::new()

    foreach ($media in $selected) {

        foreach ($extension in $media.Extensions) {

            if (-not $extensions.Contains($extension)) {

                [void]$extensions.Add($extension)
            }
        }
    }

    return [PSCustomObject]@{
        MediaTypes = @(
            $selected.Name
        )

        Extensions = @(
            $extensions
        )
    }
}

# ================================================================
# EXPORT JOBS
# ================================================================

function Build-ExportJobs {

    param(
        [Parameter(Mandatory = $true)]
        [array]$SelectedChats
    )

    $jobs =
        [System.Collections.Generic.List[object]]::new()

    foreach ($chat in $SelectedChats) {

        $topics =
            @(Get-Topics $chat)

        if ($topics.Count -eq 0) {

            [void]$jobs.Add(
                [PSCustomObject]@{
                    Chat      = $chat
                    Topic     = $null
                    ChatId    = Get-ChatId $chat
                    TopicId   = ""
                    ChatName  = Get-ChatName $chat
                    TopicName = ""
                }
            )

            continue
        }

        $selectedTopics =
            @(Select-Topics $chat)

        if ($selectedTopics.Count -eq 0) {

            throw (
                "Keine Topics für '" +
                (Get-ChatName $chat) +
                "' ausgewählt."
            )
        }

        foreach ($topic in $selectedTopics) {

            [void]$jobs.Add(
                [PSCustomObject]@{
                    Chat      = $chat
                    Topic     = $topic
                    ChatId    = Get-ChatId $chat
                    TopicId   = Get-TopicId $topic
                    ChatName  = Get-ChatName $chat
                    TopicName = Get-TopicName $topic
                }
            )
        }
    }

    return @($jobs)
}

# ================================================================
# JSON EXPORT
# ================================================================

function Export-ChatJson {

    param(
        [Parameter(Mandatory = $true)]
        $Job,

        [Parameter(Mandatory = $true)]
        [string]$Directory
    )

    $safeChat =
        ConvertTo-SafeWindowsFileName `
            -Name $Job.ChatName

    if ($null -ne $Job.Topic) {

        $safeTopic =
            ConvertTo-SafeWindowsFileName `
                -Name $Job.TopicName

        $base =
            "${safeChat}_${safeTopic}"
    }
    else {

        $base =
            $safeChat
    }

    $jsonPath =
        Join-Path `
            -Path $Directory `
            -ChildPath (
                "${base}_tdl-export.json"
            )

    $arguments = @(
        "chat",
        "export",
        "-c",
        $Job.ChatId
    )

    if ($null -ne $Job.Topic) {

        $arguments += "--topic"
        $arguments += $Job.TopicId
    }

    $arguments += "-o"
    $arguments += $jsonPath

    Write-Host ""
    Write-Host (
        T "ExportingMessages"
    ) -ForegroundColor Cyan

    $result =
        Invoke-TdlNative `
            -Arguments $arguments `
            -CaptureOutput

    if ($result.ExitCode -ne 0) {

        throw (
            "tdl chat export fehlgeschlagen." +
            "`nExitCode: " +
            $result.ExitCode +
            "`n" +
            $result.Text
        )
    }

    if (
        -not (
            Test-Path `
                -LiteralPath $jsonPath `
                -PathType Leaf
        )
    ) {

        throw (
            "tdl hat keine Exportdatei erzeugt:`n" +
            $jsonPath
        )
    }

    $info =
        Get-Item `
            -LiteralPath $jsonPath

    if ($info.Length -eq 0) {
        throw "Die erzeugte JSON-Datei ist leer."
    }

    Write-Host (
        T "ExportSuccess"
    ) -ForegroundColor Green

    return $jsonPath
}

# ================================================================
# VORHANDENE DATEIEN
# ================================================================

function Rename-ConflictingExistingFile {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [long]$ExpectedSize
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $false
    }

    $existing =
        Get-Item `
            -LiteralPath $Path

    # ============================================================
    # GLEICHE GRÖSSE
    # ============================================================

    if (
        $ExistingFileComparison -eq "Size" -and
        $existing.Length -eq $ExpectedSize
    ) {

        Write-Host (
            T "SameFile"
        ) -ForegroundColor DarkGreen

        return $false
    }

    # ============================================================
    # HASH-MODUS
    #
    # Hinweis:
    # Der Hash der Telegram-Originaldatei steht nicht zwangsläufig
    # im Export-JSON. Deshalb kann hier nur eine vorhandene lokale
    # Vergleichsinfrastruktur genutzt werden.
    #
    # Für die eigentliche tdl-Entscheidung bleibt die Größe das
    # zuverlässigste vorab verfügbare Merkmal.
    # ============================================================

    if (
        $ExistingFileComparison -eq "Hash"
    ) {

        # Ohne bekannten Remote-Hash kann nicht festgestellt
        # werden, ob die Dateien bitgenau identisch sind.
        #
        # Deshalb wird bei Hash-Modus konservativ umbenannt,
        # sofern die Größe nicht bereits gleich ist.

        if ($existing.Length -eq $ExpectedSize) {

            Write-Host (
                T "SameFile"
            ) -ForegroundColor DarkGreen

            return $false
        }
    }

    # ============================================================
    # UNTERSCHIEDLICHE GRÖSSE
    # ============================================================

    if ($PreserveExistingDifferentSize) {

        $newPath =
            Get-UniqueRenamedPath `
                -Path $Path

        Move-Item `
            -LiteralPath $Path `
            -Destination $newPath `
            -Force

        Write-Host (
            T "DifferentFile"
        ) -ForegroundColor Yellow

        Write-Host (
            "$(T 'RenamedExisting') $newPath"
        ) -ForegroundColor DarkYellow

        return $true
    }

    # Standard:
    # Alte Datei schützen und neuen Telegram-Stand unter dem
    # ursprünglichen Namen herunterladen.

    $newPath =
        Get-UniqueRenamedPath `
            -Path $Path

    Move-Item `
        -LiteralPath $Path `
        -Destination $newPath `
        -Force

    Write-Host (
        T "DifferentFile"
    ) -ForegroundColor Yellow

    Write-Host (
        "$(T 'RenamedExisting') $newPath"
    ) -ForegroundColor DarkYellow

    return $true
}

# ================================================================
# JSON / DATEIGRÖSSEN
# ================================================================

function Get-JsonMessages {

    param(
        [Parameter(Mandatory = $true)]
        [string]$JsonPath
    )

    try {

        $raw =
            Get-Content `
                -LiteralPath $JsonPath `
                -Raw `
                -Encoding UTF8

        return (
            $raw |
            ConvertFrom-Json
        )
    }
    catch {

        Write-Host ""
        Write-Host `
            "JSON konnte nicht lokal analysiert werden." `
            -ForegroundColor DarkYellow

        Write-Host `
            "tdl wird trotzdem mit --skip-same ausgeführt." `
            -ForegroundColor DarkYellow

        return $null
    }
}

function Get-MessageFileName {

    param(
        [Parameter(Mandatory = $true)]
        $Message
    )

    $fileName =
        Get-PropertyValue `
            -Object $Message `
            -Name "file_name" `
            -Default ""

    if ([string]::IsNullOrWhiteSpace([string]$fileName)) {

        $fileName =
            Get-PropertyValue `
                -Object $Message `
                -Name "fileName" `
                -Default ""
    }

    if ([string]::IsNullOrWhiteSpace([string]$fileName)) {
        return $null
    }

    return (
        ConvertTo-SafeWindowsFileName `
            -Name $fileName
    )
}

function Get-MessageFileSize {

    param(
        [Parameter(Mandatory = $true)]
        $Message
    )

    $possibleNames = @(
        "file_size",
        "fileSize",
        "size",
        "Size"
    )

    foreach ($name in $possibleNames) {

        $value =
            Get-PropertyValue `
                -Object $Message `
                -Name $name `
                -Default $null

        if ($null -eq $value) {
            continue
        }

        try {
            return [long]$value
        }
        catch {
        }
    }

    return $null
}

# ================================================================
# VORABPRÜFUNG
# ================================================================

function Prepare-ExistingFiles {

    param(
        [Parameter(Mandatory = $true)]
        [string]$JsonPath,

        [Parameter(Mandatory = $true)]
        [string]$Directory
    )

    $json =
        Get-JsonMessages `
            -JsonPath $JsonPath

    if ($null -eq $json) {
        return
    }

    # tdl-Exports können je nach Version unterschiedlich strukturiert
    # sein. Deshalb werden mehrere mögliche Container untersucht.

    $messages =
        @()

    if ($json -is [System.Array]) {
        $messages = @($json)
    }
    elseif ($json.PSObject.Properties["messages"]) {
        $messages = @($json.messages)
    }
    elseif ($json.PSObject.Properties["data"]) {
        $messages = @($json.data)
    }
    elseif ($json.PSObject.Properties["result"]) {
        $messages = @($json.result)
    }

    if ($messages.Count -eq 0) {
        return
    }

    $prepared = 0
    $renamed = 0

    foreach ($message in $messages) {

        $fileName =
            Get-MessageFileName `
                -Message $message

        if ([string]::IsNullOrWhiteSpace($fileName)) {
            continue
        }

        $size =
            Get-MessageFileSize `
                -Message $message

        if ($null -eq $size) {
            continue
        }

        $target =
            Join-Path `
                -Path $Directory `
                -ChildPath $fileName

        if (
            Test-Path `
                -LiteralPath $target `
                -PathType Leaf
        ) {

            $changed =
                Rename-ConflictingExistingFile `
                    -Path $target `
                    -ExpectedSize $size

            if ($changed) {
                $renamed++
            }

            $prepared++
        }
    }

    if ($prepared -gt 0) {

        Write-Host ""
        Write-Host `
            "Vorhandene Dateien geprüft: $prepared" `
            -ForegroundColor DarkGray

        if ($renamed -gt 0) {

            Write-Host `
                "Umbenannt wegen Größenabweichung: $renamed" `
                -ForegroundColor Yellow
        }
    }
}

# ================================================================
# DOWNLOAD
# ================================================================

function Invoke-Download {

    param(
        [Parameter(Mandatory = $true)]
        [string]$JsonPath,

        [Parameter(Mandatory = $true)]
        [string]$Directory,

        [Parameter(Mandatory = $true)]
        [array]$Extensions
    )

    # ============================================================
    # WICHTIG:
    #
    # Vor dem Start werden bereits vorhandene gleichnamige Dateien
    # behandelt.
    #
    # gleiche Größe:
    #     Datei bleibt erhalten
    #
    # andere Größe:
    #     Datei wird zu
    #
    #     file (1).ext
    #
    #     umbenannt
    #
    # Danach kann tdl die neue Datei unter dem Originalnamen
    # erzeugen.
    # ============================================================

    Prepare-ExistingFiles `
        -JsonPath $JsonPath `
        -Directory $Directory

    $arguments =
        Get-TdlDownloadArguments `
            -JsonPath $JsonPath `
            -Directory $Directory `
            -Extensions $Extensions

    Write-Host ""
    Write-Host (
        T "StartingDownload"
    ) -ForegroundColor Cyan

    Write-Host ""
    Write-Host "tdl-sidecart configuration:" `
        -ForegroundColor DarkGray

    Write-Host (
        "  Namespace : $Namespace"
    ) -ForegroundColor Yellow

    Write-Host (
        "  Threads   : $Threads"
    ) -ForegroundColor White

    Write-Host (
        "  Limit     : $Limit"
    ) -ForegroundColor White

    Write-Host (
        "  Delay     : ${Delay}s"
    ) -ForegroundColor White

    Write-Host (
        "  Pool      : $Pool"
    ) -ForegroundColor White

    Write-Host (
        "  Takeout   : $Takeout"
    ) -ForegroundColor White

    Write-Host (
        "  Continue  : $ContinueDownload"
    ) -ForegroundColor White

    Write-Host (
        "  Restart   : $RestartDownload"
    ) -ForegroundColor White

    Write-Host (
        "  RewriteExt: $RewriteExt"
    ) -ForegroundColor White

    Write-Host (
        "  Group     : $Group"
    ) -ForegroundColor White

    Write-Host (
        "  Desc      : $Desc"
    ) -ForegroundColor White

    Write-Host (
        "  Debug     : $DebugMode"
    ) -ForegroundColor White

    Write-Host ""
    Write-Host (
        "  Template  : {{ filenamify .FileName 180 }}"
    ) -ForegroundColor DarkGray

    Write-Host (
        "  SkipSame  : true"
    ) -ForegroundColor DarkGray

    Write-Host ""
    Write-Host (
        "  Version   : $Script:ProjectVersion"
    ) -ForegroundColor DarkGray

    Write-Host (
        "  Script    : $PSCommandPath"
    ) -ForegroundColor DarkGray

    Write-Host (
        "  tdl.exe   : $TdlPath"
    ) -ForegroundColor DarkGray

    Write-Host ""
    Write-Host "Bereite nativen tdl-Download vor..." -ForegroundColor Cyan

    if ($WhatIfDownload) {

        Write-Host ""
        Write-Host (
            T "WouldDownload"
        ) -ForegroundColor Yellow

        Write-Host ""
        Write-Host (
            $arguments -join " "
        ) -ForegroundColor DarkGray

        return
    }

    # ============================================================
    # LIVE DOWNLOAD OUTPUT
    # ============================================================
    #
    # tdl besitzt für `dl` einen eigenen interaktiven Progress-Renderer.
    # Die Ausgabe darf hier NICHT mit -CaptureOutput gepuffert werden,
    # sonst bleibt die Konsole während des gesamten Downloads scheinbar
    # stehen und der Fortschrittsbalken wird erst nach Prozessende sichtbar.
    #
    # Deshalb wird `tdl dl` direkt an die aktuelle Konsole gebunden.
    # JSON-/Status-Kommandos verwenden weiterhin Invoke-TdlNative mit
    # -CaptureOutput, weil deren Ausgabe maschinell ausgewertet wird.
    # ============================================================

    Write-Host ""
    Write-Host "tdl download progress:" -ForegroundColor Cyan
    Write-Host (
        "Invoking native process now: " + $TdlPath
    ) -ForegroundColor DarkGray
    Write-Host ""

    # Start tdl as a real child process with inherited console handles.
    # No stdout/stderr redirection is used, so tdl can render its native UI.
    # Sidecart also gets a concrete PID and exit code for diagnostics.
    $liveResult =
        Invoke-TdlLiveProcess -Arguments $arguments

    $downloadExitCode = $liveResult.ExitCode

    if ($downloadExitCode -ne 0) {
        throw (
            "tdl dl fehlgeschlagen." +
            "`nExitCode: " +
            $downloadExitCode +
            "`nDie native tdl-Fehlermeldung wurde direkt oben ausgegeben."
        )
    }

    Write-Host ""
    Write-Host (
        T "DownloadSuccess"
    ) -ForegroundColor Green
}

# ================================================================
# EIN JOB
# ================================================================

function Export-ChatJob {

    param(
        [Parameter(Mandatory = $true)]
        $Job,

        [Parameter(Mandatory = $true)]
        [array]$MediaExtensions,

        [Parameter(Mandatory = $true)]
        [array]$MediaTypes
    )

    $targetPath =
        $OutputPath

    if (
        -not (
            Test-Path `
                -LiteralPath $targetPath
        )
    ) {

        New-Item `
            -ItemType Directory `
            -Path $targetPath `
            -Force |
            Out-Null
    }

    Write-Host ""
    Write-Host (
        "============================================================"
    ) -ForegroundColor DarkCyan

    Write-Host (
        "$(T 'Chat'): $($Job.ChatName)"
    ) -ForegroundColor White

    if ($null -ne $Job.Topic) {

        Write-Host (
            "$(T 'Topic'): $($Job.TopicName)"
        ) -ForegroundColor White
    }

    Write-Host (
        "$(T 'Target'): $targetPath"
    ) -ForegroundColor DarkGray

    Write-Host (
        "$(T 'Namespace'): $Namespace"
    ) -ForegroundColor Yellow

    Write-Host (
        "$(T 'MediaTypes'): $($MediaTypes -join ', ')"
    ) -ForegroundColor White

    Write-Host (
        "$(T 'Comparison'): $ExistingFileComparison"
    ) -ForegroundColor White

    Write-Host (
        "$(T 'FilenamePolicy'): filenamify"
    ) -ForegroundColor Green

    Write-Host (
        "============================================================"
    ) -ForegroundColor DarkCyan

    $jsonPath =
        Export-ChatJson `
            -Job $Job `
            -Directory $targetPath

    Invoke-Download `
        -JsonPath $jsonPath `
        -Directory $targetPath `
        -Extensions $MediaExtensions
}

# ================================================================
# ALLE JOBS
# ================================================================

function Export-SelectedJobs {

    param(
        [Parameter(Mandatory = $true)]
        [array]$Jobs,

        [Parameter(Mandatory = $true)]
        [array]$MediaExtensions,

        [Parameter(Mandatory = $true)]
        [array]$MediaTypes
    )

    $success = 0
    $errors = 0
    $number = 0

    foreach ($job in $Jobs) {

        $number++

        Write-Host ""
        Write-Host (
            "[$number/$($Jobs.Count)]"
        ) -ForegroundColor Yellow

        try {

            Export-ChatJob `
                -Job $job `
                -MediaExtensions $MediaExtensions `
                -MediaTypes $MediaTypes

            $success++
        }
        catch {

            $errors++

            Write-Host ""
            Write-Host (
                T "Error"
            ) -ForegroundColor Red

            Write-Host ""
            Write-Host `
                $_.Exception.Message `
                -ForegroundColor Red

            Write-Host ""

            Write-Host (
                T "ContinueNext"
            ) -ForegroundColor DarkYellow

            Pause-Script
        }
    }

    return [PSCustomObject]@{
        Total   = $Jobs.Count
        Success = $success
        Errors  = $errors
    }
}

# ================================================================
# SUMMARY
# ================================================================

function Show-JobSummary {

    param(
        [Parameter(Mandatory = $true)]
        [array]$Jobs,

        [Parameter(Mandatory = $true)]
        [array]$MediaTypes,

        [Parameter(Mandatory = $true)]
        [array]$MediaExtensions
    )

    Clear-Screen

    Write-Host (
        T "Summary"
    ) -ForegroundColor $Script:HeaderColor

    Write-Host ""

    Write-Host (
        "$(T 'Namespace'): $Namespace"
    ) -ForegroundColor Yellow

    Write-Host (
        "$(T 'Language'): $Script:CurrentLanguage"
    ) -ForegroundColor Gray

    Write-Host ""

    $i = 1

    foreach ($job in $Jobs) {

        if ($null -ne $job.Topic) {

            $description =
                "$($job.ChatName) -> $($job.TopicName)"
        }
        else {

            $description =
                "$($job.ChatName) -> complete chat"
        }

        Write-Host (
            "{0,3}. {1}" -f
            $i,
            $description
        ) -ForegroundColor Gray

        $i++
    }

    Write-Host ""

    Write-Host (
        "$(T 'MediaTypes'): $($MediaTypes -join ', ')"
    ) -ForegroundColor White

    Write-Host (
        "$(T 'Extensions'): $($MediaExtensions -join ', ')"
    ) -ForegroundColor DarkGray

    Write-Host ""

    Write-Host (
        "$(T 'Output'): $OutputPath"
    ) -ForegroundColor White

    Write-Host ""

    Write-Host "tdl:" -ForegroundColor Cyan

    Write-Host "  -t          = $Threads"
    Write-Host "  -l          = $Limit"
    Write-Host "  --delay     = ${Delay}s"
    Write-Host "  --pool      = $Pool"

    Write-Host "  --takeout   = $Takeout"
    Write-Host "  --continue  = $ContinueDownload"
    Write-Host "  --restart   = $RestartDownload"
    Write-Host "  --group     = $Group"
    Write-Host "  --desc      = $Desc"
    Write-Host "  --rewrite   = $RewriteExt"
    Write-Host "  --debug     = $DebugMode"

    Write-Host ""

    Write-Host (
        "Filename template:"
    ) -ForegroundColor Cyan

    Write-Host `
        '{{ filenamify .FileName 180 }}' `
        -ForegroundColor Green

    Write-Host ""

    Write-Host (
        "Existing file policy:"
    ) -ForegroundColor Cyan

    Write-Host `
        "same name + same size  -> skip" `
        -ForegroundColor Green

    Write-Host `
        "same name + other size -> rename existing file" `
        -ForegroundColor Yellow

    if ($NonInteractive) {
        return $true
    }

    Write-Host ""
    Write-Host `
        "ENTER = Start    ESC = Cancel" `
        -ForegroundColor DarkGray

    while ($true) {

        $key =
            [Console]::ReadKey($true)

        if ($key.Key -eq "Enter") {
            return $true
        }

        if ($key.Key -eq "Escape") {
            throw (T "Cancelled")
        }
    }
}

# ================================================================
# NAMESPACE
# ================================================================

function Initialize-Namespace {

    if ([string]::IsNullOrWhiteSpace($Namespace)) {

        # Ein stabiler Default-Namespace ist absichtlich wichtig:
        # Ein zufälliger Namespace würde bei jedem Start erneut eine
        # Telegram-Authentifizierung benötigen. Für parallele Instanzen
        # kann weiterhin explizit -Namespace verwendet werden.
        $script:Namespace = "sidecart"
    }
    else {
        $script:Namespace = $Namespace.Trim()
    }

    if ($script:Namespace.Length -eq 0) {

        throw (
            "Der tdl Namespace darf nicht leer sein."
        )
    }
}

# ================================================================
# OUTPUT VALIDATION
# ================================================================

function Initialize-OutputDirectory {

    if (
        -not (
            Test-Path `
                -LiteralPath $OutputPath
        )
    ) {

        New-Item `
            -ItemType Directory `
            -Path $OutputPath `
            -Force |
            Out-Null
    }

    $item =
        Get-Item `
            -LiteralPath $OutputPath

    if (-not $item.PSIsContainer) {

        throw (
            (T "InvalidOutput") +
            "`n" +
            $OutputPath
        )
    }

    $script:OutputPath =
        $item.FullName
}

# ================================================================
# HAUPTPROGRAMM
# ================================================================

try {

    Clear-Screen

    Initialize-Namespace

    $resolvedTdl =
        Test-Tdl

    $script:TdlPath = $resolvedTdl

    Initialize-OutputDirectory

    Write-Host ""
    Write-Host `
        "============================================================" `
        -ForegroundColor Cyan

    Write-Host `
        "                         tdl-sidecart" `
        -ForegroundColor Cyan

    Write-Host `
        "                         v$Script:ProjectVersion" `
        -ForegroundColor DarkGray

    Write-Host `
        "============================================================" `
        -ForegroundColor Cyan

    Write-Host ""

    Write-Host `
        "tdl:" `
        -ForegroundColor Gray

    Write-Host `
        $resolvedTdl `
        -ForegroundColor White

    Write-Host ""

    Write-Host (
        "$(T 'Namespace'): $Namespace"
    ) -ForegroundColor Yellow

    Write-Host (
        "$(T 'Output'): $OutputPath"
    ) -ForegroundColor White

    Write-Host (
        "$(T 'Language'): $Script:CurrentLanguage"
    ) -ForegroundColor Gray

    Write-Host ""

    # ============================================================
    # VALIDIERUNG
    # ============================================================

    if (
        $ContinueDownload -and
        $RestartDownload
    ) {

        throw (
            "--continue und --restart dürfen nicht gleichzeitig " +
            "verwendet werden."
        )
    }

    # ============================================================
    # AUTH
    # ============================================================

    Test-TdlAuthorization |
        Out-Null

    # ============================================================
    # CHATS
    # ============================================================

    $chats =
        @(Get-Chats)

    if ($chats.Count -eq 0) {

        throw (
            T "NoChats"
        )
    }

    $chats =
        @(
            $chats |
            Sort-Object -Property @{
                Expression = {
                    Get-ChatName $_
                }

                Ascending = $true
            }
        )

    # ============================================================
    # AUSWAHL
    # ============================================================

    $selectedChats =
        @(
            Select-Chats `
                -Chats $chats
        )

    if ($selectedChats.Count -eq 0) {
        throw (T "NoSelection")
    }

    # ============================================================
    # JOBS
    # ============================================================

    $jobs =
        @(
            Build-ExportJobs `
                -SelectedChats $selectedChats
        )

    if ($jobs.Count -eq 0) {
        throw "Keine Export-Jobs erstellt."
    }

    # ============================================================
    # MEDIEN
    # ============================================================

    $media =
        Select-MediaTypes

    $mediaTypes =
        @($media.MediaTypes)

    $mediaExtensions =
        @($media.Extensions)

    if ($mediaExtensions.Count -eq 0) {

        throw (
            "Keine Dateiendungen für den Download vorhanden."
        )
    }

    # ============================================================
    # SUMMARY
    # ============================================================

    Show-JobSummary `
        -Jobs $jobs `
        -MediaTypes $mediaTypes `
        -MediaExtensions $mediaExtensions |
        Out-Null

    # ============================================================
    # EXPORT
    # ============================================================

    $result =
        Export-SelectedJobs `
            -Jobs $jobs `
            -MediaExtensions $mediaExtensions `
            -MediaTypes $mediaTypes

    # ============================================================
    # FERTIG
    # ============================================================

    Clear-Screen

    Write-Host ""
    Write-Host `
        "============================================================" `
        -ForegroundColor Green

    Write-Host `
        "                       tdl-sidecart" `
        -ForegroundColor Green

    Write-Host `
        "                      EXPORT COMPLETE" `
        -ForegroundColor Green

    Write-Host `
        "============================================================" `
        -ForegroundColor Green

    Write-Host ""

    Write-Host (
        "$(T 'Namespace'): $Namespace"
    ) -ForegroundColor Yellow

    Write-Host (
        "$(T 'Output'): $OutputPath"
    ) -ForegroundColor White

    Write-Host ""

    Write-Host (
        "$(T 'Total'): $($result.Total)"
    ) -ForegroundColor Gray

    Write-Host (
        "$(T 'Success'): $($result.Success)"
    ) -ForegroundColor Green

    $errorColor =
        if ($result.Errors -gt 0) {
            [ConsoleColor]::Red
        }
        else {
            [ConsoleColor]::Green
        }

    Write-Host (
        "$(T 'Errors'): $($result.Errors)"
    ) -ForegroundColor $errorColor

    Write-Host ""

    Write-Host `
        "Dateinamen werden über tdl filenamify Windows-sicher erzeugt." `
        -ForegroundColor DarkGray

    Write-Host `
        "Gleiche Datei + gleiche Größe: --skip-same" `
        -ForegroundColor DarkGray

    Write-Host `
        "Gleicher Name + andere Größe: vorhandene Datei wird geschützt." `
        -ForegroundColor DarkGray

    Write-Host ""

    Pause-Script
}
catch {

    try {
        Clear-Host
    }
    catch {
    }

    Write-Host ""
    Write-Host `
        "============================================================" `
        -ForegroundColor Red

    Write-Host `
        "                         tdl-sidecart" `
        -ForegroundColor Red

    Write-Host `
        (T "Error") `
        -ForegroundColor Red

    Write-Host `
        "============================================================" `
        -ForegroundColor Red

    Write-Host ""

    Write-Host `
        $_.Exception.Message `
        -ForegroundColor Red

    Write-Host ""

    Write-Host `
        "$(T 'Namespace'): $Namespace" `
        -ForegroundColor DarkGray

    Write-Host `
        "$(T 'Output'): $OutputPath" `
        -ForegroundColor DarkGray

    Write-Host `
        "$(T 'Language'): $Script:CurrentLanguage" `
        -ForegroundColor DarkGray

    if (
        $_.InvocationInfo -and
        $_.InvocationInfo.PositionMessage
    ) {

        Write-Host ""
        Write-Host `
            "PowerShell:" `
            -ForegroundColor DarkRed

        Write-Host `
            $_.InvocationInfo.PositionMessage `
            -ForegroundColor DarkGray
    }

    Write-Host ""

    Pause-Script

    exit 1
}