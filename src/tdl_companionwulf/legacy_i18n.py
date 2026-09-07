from __future__ import annotations

# Legacy Sidecart UI vocabulary. The original 2.1.1 source carried full German
# and English catalogs plus dedicated French/Spanish/Italian/Portuguese UI
# strings. Other supported locale families intentionally fell back to English.

_EN = {
    "Title": "tdl-sidecart", "Chats": "TELEGRAM CHATS", "Topics": "TOPICS",
    "Media": "MEDIA SELECTION", "Summary": "EXPORT SUMMARY", "Error": "ERROR",
    "Done": "EXPORT COMPLETE", "LoadingChats": "Loading Telegram chats...",
    "CheckingSession": "Checking Telegram session...", "Authenticated": "Telegram session is authenticated.",
    "NotAuthenticated": "Namespace is not authenticated.", "Namespace": "Namespace",
    "Output": "Output directory", "Threads": "Threads", "Limit": "Limit",
    "Delay": "Delay", "Pool": "Pool", "MediaTypes": "Media types",
    "Extensions": "File extensions", "ExportingMessages": "Exporting messages...",
    "ExportSuccess": "Export successful.", "StartingDownload": "Starting download...",
    "DownloadSuccess": "Download completed.", "NoChats": "No Telegram chats were found.",
    "NoSelection": "No entries selected.", "Cancelled": "Cancelled by user.",
    "Continue": "Continue", "Selected": "Selected", "SameFile": "File already exists and has the same size.",
    "DifferentFile": "A file with the same name but different size was found.",
    "RenamedExisting": "Existing file was renamed:", "WouldDownload": "Download would be started.",
    "TdlNotFound": "tdl.exe was not found:", "InvalidOutput": "OutputPath is not a directory:",
    "LoginHint": "Run once:", "AutoAuthKnownSearch": "Searching known locations for Telegram Desktop tdata...",
    "AutoAuthSystemSearch": "No usable known session was found. Searching all local drives for tdata...",
    "AutoAuthFound": "Found tdata:", "AutoAuthTrying": "Starting automatic tdl authentication with:",
    "AutoAuthSuccess": "The namespace was authenticated successfully from Telegram Desktop.",
    "AutoAuthNoTdata": "No usable tdata directory was found.",
    "AutoAuthLoginFailed": "Automatic authentication with this tdata directory was not successful.",
    "AutoAuthInUse": "tdata is already reserved by another tdl-sidecart instance. Skipping:",
    "AutoAuthInstalling": "All existing tdata sessions are busy or unusable. Installing a new isolated Telegram Desktop client...",
    "AutoAuthClientReady": "A new Telegram Desktop client was started. Sign in there; tdl-sidecart will detect the new tdata session automatically.",
    "AutoAuthWaitingClient": "Waiting for sign-in in the new Telegram Desktop client...",
    "AutoAuthParallelNs": "The default namespace is already in use. Automatically using a new namespace:",
    "ContinueNext": "The export will continue with the next item.", "PressKey": "Press a key to continue...",
    "Jobs": "Export jobs", "Success": "Successful", "Errors": "Errors", "Total": "Total",
    "Chat": "Chat", "Topic": "Topic", "Target": "Target", "Language": "Language",
    "Comparison": "File comparison", "FilenamePolicy": "Filename policy",
}

_DE = dict(_EN, **{
    "Chats": "TELEGRAM CHATS", "Topics": "TOPICS", "Media": "MEDIEN-AUSWAHL",
    "Summary": "EXPORT-ZUSAMMENFASSUNG", "Error": "FEHLER", "Done": "EXPORT FERTIG",
    "LoadingChats": "Lade Telegram-Chats...", "CheckingSession": "Prüfe Telegram-Session...",
    "Authenticated": "Telegram-Session ist authentifiziert.", "NotAuthenticated": "Namespace ist nicht authentifiziert.",
    "Output": "Zielordner", "MediaTypes": "Medientypen", "Extensions": "Dateiendungen",
    "ExportingMessages": "Exportiere Nachrichten...", "ExportSuccess": "Export erfolgreich.",
    "StartingDownload": "Starte Download...", "DownloadSuccess": "Download abgeschlossen.",
    "NoChats": "Es wurden keine Telegram-Chats gefunden.", "NoSelection": "Keine Einträge ausgewählt.",
    "Cancelled": "Vom Benutzer abgebrochen.", "Continue": "Weiter", "Selected": "Ausgewählt",
    "SameFile": "Datei bereits vorhanden und gleich groß.", "DifferentFile": "Gleichnamige Datei mit anderer Größe gefunden.",
    "RenamedExisting": "Vorhandene Datei wurde umbenannt:", "WouldDownload": "Download würde gestartet werden.",
    "TdlNotFound": "tdl.exe wurde nicht gefunden:", "InvalidOutput": "OutputPath ist kein Verzeichnis:",
    "AutoAuthKnownSearch": "Suche Telegram-Desktop-Daten in bekannten tdata-Pfaden...",
    "AutoAuthSystemSearch": "Keine verwendbare bekannte Sitzung gefunden. Suche jetzt systemweit nach tdata...",
    "AutoAuthFound": "tdata gefunden:", "AutoAuthTrying": "Starte automatische tdl-Authentifizierung mit:",
    "AutoAuthSuccess": "Namespace wurde erfolgreich über Telegram Desktop authentifiziert.",
    "AutoAuthNoTdata": "Es wurde kein verwendbarer tdata-Ordner gefunden.",
    "AutoAuthInUse": "tdata wird bereits von einer anderen tdl-sidecart-Instanz verwendet. Überspringe:",
    "AutoAuthParallelNs": "Der Standard-Namespace wird bereits verwendet. Verwende automatisch einen neuen Namespace:",
    "Jobs": "Export-Jobs", "Success": "Erfolgreich", "Errors": "Fehler", "Total": "Gesamt",
    "Target": "Ziel", "Language": "Sprache", "Comparison": "Dateivergleich", "FilenamePolicy": "Dateinamenrichtlinie",
})

_FR = dict(_EN, **{"Chats":"CHATS TELEGRAM","Topics":"SUJETS","Media":"SÉLECTION DES MÉDIAS","Summary":"RÉSUMÉ DE L'EXPORT","NoChats":"Aucun chat Telegram trouvé.","NoSelection":"Aucun élément sélectionné.","Language":"Langue","Comparison":"Comparaison"})
_ES = dict(_EN, **{"Chats":"CHATS DE TELEGRAM","Topics":"TEMAS","Media":"SELECCIÓN DE MEDIOS","Summary":"RESUMEN DE EXPORTACIÓN","NoChats":"No se encontraron chats de Telegram.","NoSelection":"No se seleccionaron elementos.","Language":"Idioma","Comparison":"Comparación"})
_IT = dict(_EN, **{"Chats":"CHAT TELEGRAM","Topics":"ARGOMENTI","Media":"SELEZIONE MEDIA","Summary":"RIEPILOGO ESPORTAZIONE","NoChats":"Nessuna chat Telegram trovata.","NoSelection":"Nessun elemento selezionato.","Language":"Lingua","Comparison":"Confronto"})
_PT = dict(_EN, **{"Chats":"CHATS DO TELEGRAM","Topics":"TÓPICOS","Media":"SELEÇÃO DE MÍDIA","Summary":"RESUMO DA EXPORTAÇÃO","NoChats":"Nenhum chat do Telegram encontrado.","NoSelection":"Nenhum item selecionado.","Language":"Idioma","Comparison":"Comparação"})

_CATALOGS = {"de": _DE, "en": _EN, "fr": _FR, "es": _ES, "it": _IT, "pt": _PT}


def legacy_text(language: str, key: str) -> str:
    catalog = _CATALOGS.get((language or "en").casefold(), _EN)
    return catalog.get(key, _EN.get(key, key))
