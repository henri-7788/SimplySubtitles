# Video Subtitle Generator

Dieses Python-Projekt ermöglicht es, aus einem Video ohne Untertitel ein Video mit synchronisierten Untertiteln zu erzeugen. Dabei wird zuerst der Audioinhalt mittels OpenAI Whisper transkribiert, anschließend ein SRT-Datei generiert und abschließend mit FFmpeg in das Video "eingebrannt".

## Features

- **Transkription:** Nutzt [OpenAI Whisper](https://github.com/openai/whisper) zur Transkription des Audioinhalts.
- **Untertitel-Erstellung:** Generiert SRT-Dateien, wobei längere Textsegmente anhand einer maximalen Wörterzahl automatisch aufgeteilt werden.
- **Video-Bearbeitung:** Bindet die generierten Untertitel mithilfe von FFmpeg in das Video ein.
- **Anpassbare Einstellungen:** Konfigurierbar sind u.a. Schriftfarbe, Schriftgröße, Schriftart, Umrandungsstärke und Umrandungsfarbe der Untertitel.

## Voraussetzungen

- Python 3.8 oder höher
- [FFmpeg](https://ffmpeg.org/download.html) muss installiert und im Systempfad verfügbar sein.
- Die im `requirements.txt` gelisteten Python-Pakete.

## Installation

1. Klone das Repository:

   ```bash
   git clone https://github.com/henri-7788/SimplySubtitles.git
   cd video-subtitle-generator
