import argparse
import subprocess
import os
import whisper
import math

def seconds_to_timestamp(seconds):
    """Wandelt Sekunden in das SRT-Zeitformat HH:MM:SS,mmm um."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    milliseconds = int((secs - int(secs)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{milliseconds:03d}"

def transcribe_video(video_path, model_size="base"):
    """Transkribiert das Video mit dem angegebenen Whisper-Modell."""
    print("Starte Transkription (dies kann einige Zeit dauern)...")
    model = whisper.load_model(model_size)
    result = model.transcribe(video_path)
    return result['segments']

def generate_srt(segments, srt_path, max_words):
    """Erstellt eine SRT-Datei aus den Transkript-Segmenten.
       Bei zu langen Segmenten wird anhand von max_words aufgeteilt.
    """
    with open(srt_path, "w", encoding="utf-8") as f:
        index = 1
        for segment in segments:
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()
            words = text.split()
            if len(words) <= max_words:
                # Ein Eintrag genügt
                f.write(f"{index}\n")
                f.write(f"{seconds_to_timestamp(start)} --> {seconds_to_timestamp(end)}\n")
                f.write(" ".join(words) + "\n\n")
                index += 1
            else:
                # Segment in mehrere Einträge aufteilen
                n_groups = math.ceil(len(words) / max_words)
                segment_duration = end - start
                group_duration = segment_duration / n_groups
                for i in range(n_groups):
                    group_words = words[i*max_words : (i+1)*max_words]
                    group_start = start + i * group_duration
                    group_end = group_start + group_duration
                    f.write(f"{index}\n")
                    f.write(f"{seconds_to_timestamp(group_start)} --> {seconds_to_timestamp(group_end)}\n")
                    f.write(" ".join(group_words) + "\n\n")
                    index += 1

def hex_to_ffmpeg_color(hex_color):
    """Konvertiert einen Hexadezimal-Farbcode (z.B. #RRGGBB) in das FFmpeg-Format (&H00BBGGRR)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r = hex_color[0:2]
        g = hex_color[2:4]
        b = hex_color[4:6]
        bgr = b + g + r
        return f"&H00{bgr}"
    return hex_color

def burn_subtitles(input_video, srt_path, output_video, font_color, font_size, font_name, outline, outline_color):
    """Brennt die Untertitel in das Video ein, wobei Stiloptionen berücksichtigt werden."""
    ffmpeg_font_color = hex_to_ffmpeg_color(font_color)
    ffmpeg_outline_color = hex_to_ffmpeg_color(outline_color)
    
    # Erstelle den Filter-String mit den gewählten Stileinstellungen
    subtitles_filter = (
        f"subtitles={srt_path}:force_style='FontName={font_name},"
        f"Fontsize={font_size},PrimaryColour={ffmpeg_font_color},"
        f"Outline={outline},OutlineColour={ffmpeg_outline_color}'"
    )
    
    command = [
        "ffmpeg",
        "-i", input_video,
        "-vf", subtitles_filter,
        "-c:a", "copy",
        output_video
    ]
    print("Untertitel werden in das Video eingebrannt...")
    subprocess.run(command, check=True)
    print(f"Das Ausgabevideo wurde unter '{output_video}' gespeichert.")

def main():
    parser = argparse.ArgumentParser(
        description="Erstellt ein Video mit eingebrannten, synchronisierten Untertiteln aus einem Video ohne Untertitel."
    )
    parser.add_argument("--input", required=True, help="Pfad zum Eingabevideo.")
    parser.add_argument("--output", required=True, help="Pfad zum Ausgabevideo.")
    parser.add_argument("--max_words", type=int, default=10, help="Maximale Anzahl von Wörtern pro Untertitelzeile (Standard: 10).")
    parser.add_argument("--font_color", type=str, default="#FFFFFF", help="Schriftfarbe (Hexadezimal, z.B. '#FFFFFF' für Weiß).")
    parser.add_argument("--font_size", type=int, default=24, help="Schriftgröße (Standard: 24).")
    parser.add_argument("--font_name", type=str, default="Arial", help="Schriftart (Standard: Arial).")
    parser.add_argument("--outline", type=int, default=1, help="Umrandungsstärke (Standard: 1).")
    parser.add_argument("--outline_color", type=str, default="#000000", help="Umrandungsfarbe (Hexadezimal, z.B. '#000000' für Schwarz).")
    parser.add_argument("--model_size", type=str, default="base", help="Whisper-Modellgröße (tiny, base, small, medium, large; Standard: base).")
    
    args = parser.parse_args()
    
    temp_srt = "temp_subtitles.srt"
    
    # Schritt 1: Transkription
    segments = transcribe_video(args.input, args.model_size)
    print("Transkription abgeschlossen. Erstelle SRT-Datei...")
    
    # Schritt 2: SRT-Datei generieren
    generate_srt(segments, temp_srt, args.max_words)
    print("SRT-Datei wurde erfolgreich erstellt.")
    
    # Schritt 3: Untertitel in Video einbrennen
    burn_subtitles(
        args.input,
        temp_srt,
        args.output,
        args.font_color,
        args.font_size,
        args.font_name,
        args.outline,
        args.outline_color
    )
    
    # Temporäre SRT-Datei entfernen
    if os.path.exists(temp_srt):
        os.remove(temp_srt)

if __name__ == "__main__":
    main()
