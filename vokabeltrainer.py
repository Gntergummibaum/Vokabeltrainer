import customtkinter as ctk
import csv
import random
import os
from PIL import Image
import json

# Statistik speichern
def statistik_speichern(vokabel_statistik):
    speicherbares_dict = {f"{de}|{en}": werte for (de, en), werte in vokabel_statistik.items()}
    with open(STATISTIK_DATEI, 'w', encoding='utf-8') as f:
        json.dump(speicherbares_dict, f, indent=4, ensure_ascii=False)

#gespeicherte Satistik laden
def statistik_laden():
    if os.path.exists(STATISTIK_DATEI):
        with open(STATISTIK_DATEI, 'r', encoding='utf-8') as f:
            geladen = json.load(f)
        # zurück in Tupel umwandeln
        return {tuple(key.split('|')): werte for key, werte in geladen.items()}
    else:
        return {}
    
STATISTIK_DATEI = 'statistik.json'

#laden der statistik
vokabel_statistik = statistik_laden()

# Einstellungen
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Vokabeltrainer")
app.state('zoomed')  # Start im Vollbildmodus

# Globale Variablen
alle_vokabeln = []
vokabeln_zu_lernen = []
punktzahl = 100
aktuelle_vokabel = None
runde_status = {}

haus_icon = None
birne_icon = None
tipp_icon = None

statistik_frame = None

# Vokabeln laden
def lade_vokabeln(dateiname):
    global alle_vokabeln, vokabeln_zu_lernen
    alle_vokabeln = []
    with open(dateiname, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            vokabel = {'Deutsch': row['Deutsch'].strip(), 'Englisch': row['Englisch'].strip()}
            alle_vokabeln.append(vokabel)
            key = (vokabel['Deutsch'], vokabel['Englisch'])
            if key not in vokabel_statistik:
                vokabel_statistik[key] = {'richtig': 0, 'falsch': 0}
    vokabeln_zu_lernen[:] = list(alle_vokabeln)
    random.shuffle(vokabeln_zu_lernen)


lade_vokabeln('vokabeln.csv')

# Frame-Management
frames = {}


def zeige_frame(name):
    for f in frames.values():
        f.pack_forget()
    frames[name].pack(fill='both', expand=True)


# Dynamik: Schriftgrößen anpassen
base_font_size = 20


def update_font_sizes(event):
    width = app.winfo_width()
    height = app.winfo_height()
    scale = min(width / 1200, height / 800)
    font_size = max(int(base_font_size * scale), 12)
    
    frage_label.configure(font=("Arial", font_size + 10))
    eingabe.configure(font=("Arial", font_size))
    feedback_label.configure(font=("Arial", font_size))
    punktzahl_label.configure(font=("Arial", font_size))


# Startbildschirm
def startbildschirm():
    frame = ctk.CTkFrame(app)
    frames['start'] = frame

    titel = ctk.CTkLabel(frame, text="Vokabeltrainer", font=('Arial', 40))
    titel.pack(pady=40)

    start_btn = ctk.CTkButton(frame, text="Start", command=lambda: [zeige_frame('trainer'), naechste_vokabel()], width=200, height=50, corner_radius=20)
    start_btn.pack(pady=20)

    statistik_btn = ctk.CTkButton(frame, text="Statistiken", command=lambda: [zeige_frame('statistik'), zeige_statistik()], width=200, height=50, corner_radius=20)
    statistik_btn.pack(pady=20)

    # Glühbirne oben als Symbol
    birnen_frame = ctk.CTkFrame(frame, fg_color="transparent")  # hier transparent gesetzt
    birnen_frame.pack(pady=20)

    birne_btn = ctk.CTkButton(birnen_frame, image=birne_icon, text="", width=60, height=60, corner_radius=30, 
                              command=wechsel_mode, fg_color="transparent", hover_color="lightgrey", border_width=0)
    birne_btn.pack()

    zeige_frame('start')

# Trainer
def trainer():
    frame = ctk.CTkFrame(app)
    frames['trainer'] = frame

    global frage_label, eingabe, feedback_label, punktzahl_label, fortschritt

    top_frame = ctk.CTkFrame(frame)
    top_frame.pack(side='top', fill='x')

    home_btn = ctk.CTkButton(top_frame, image=haus_icon, text="", width=40, height=40, corner_radius=20, command=lambda: zeige_frame('start'))
    home_btn.pack(side='left', padx=10, pady=10)

    tipp_btn = ctk.CTkButton(top_frame, image=tipp_icon, text="", width=40, height=40, corner_radius=20, command=zeige_tipp)
    tipp_btn.pack(side='right', padx=10, pady=10)

    frage_label = ctk.CTkLabel(frame, text="", font=('Arial', 30))
    frage_label.pack(pady=30)

    eingabe = ctk.CTkEntry(frame, font=('Arial', 20), width=400)
    eingabe.pack(pady=10)
    eingabe.bind('<Return>', pruefe_antwort)

    antwort_btn = ctk.CTkButton(frame, text="Antwort prüfen", command=pruefe_antwort, width=200, height=50, corner_radius=20)
    antwort_btn.pack(pady=10)

    feedback_label = ctk.CTkLabel(frame, text="", font=('Arial', 20))
    feedback_label.pack(pady=10)

    punktzahl_label = ctk.CTkLabel(frame, text=f"Punktzahl: {punktzahl}", font=('Arial', 20))
    punktzahl_label.pack(pady=10)

    fortschritt = ctk.CTkProgressBar(frame, width=400)
    fortschritt.set(0)
    fortschritt.pack(pady=10)


# Statistik
# Statistik
def statistik():
    frame = ctk.CTkFrame(app)
    frames['statistik'] = frame

    home_btn = ctk.CTkButton(frame, image=haus_icon, text="", width=40, height=40, corner_radius=20, command=lambda: zeige_frame('start'))
    home_btn.pack(side='top', anchor='nw', padx=10, pady=10)

    titel = ctk.CTkLabel(frame, text="Statistiken", font=('Arial', 30))
    titel.pack(pady=20)

    global statistik_frame
    statistik_frame = ctk.CTkScrollableFrame(frame, width=600, height=400)
    statistik_frame.pack(padx=20, pady=20)

    statistik_frame.pack(fill='both', expand=True)


import customtkinter as ctk
import tkinter as tk

# Funktion zum Anzeigen der Statistik
# Funktion zum Anzeigen der Statistik
def zeige_statistik():
    global statistik_frame

    if 'statistik' not in frames:
        statistik_frame = ctk.CTkFrame(app)
        frames['statistik'] = statistik_frame
    else:
        statistik_frame = frames['statistik']

    # Alte Inhalte löschen
    for widget in statistik_frame.winfo_children():
        widget.destroy()

    # Scrollbar mit Canvas
    canvas = tk.Canvas(statistik_frame)
    scrollbar = tk.Scrollbar(statistik_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.config(yscrollcommand=scrollbar.set)

    # Veränderte pack-Optionen für die korrekte Skalierung
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Hier wird der scrollable_frame so skaliert, dass es den gesamten verfügbaren Platz einnimmt
    scrollable_frame.pack(fill='both', expand=True)

    # Kopfzeile
    header_font = ('Arial', 16, 'bold')
    ctk.CTkLabel(scrollable_frame, text="Vokabel (Deutsch - Englisch)", width=300, anchor='w', font=header_font).grid(row=0, column=0, padx=5, pady=5)
    ctk.CTkLabel(scrollable_frame, text="Richtig", width=80, anchor='center', font=header_font).grid(row=0, column=1, padx=5, pady=5)
    ctk.CTkLabel(scrollable_frame, text="Falsch", width=80, anchor='center', font=header_font).grid(row=0, column=2, padx=5, pady=5)
    ctk.CTkLabel(scrollable_frame, text="Prozent richtig", width=120, anchor='center', font=header_font).grid(row=0, column=3, padx=5, pady=5)

    row = 1
    richtig_gesamt = 0
    falsch_gesamt = 0

    # Vokabelstatistik anzeigen
    for (de, en), stats in vokabel_statistik.items():
        gesamt = stats['richtig'] + stats['falsch']
        prozent = (stats['richtig'] / gesamt * 100) if gesamt > 0 else 0

        # Farbmarkierung
        if prozent >= 80:
            farbe = 'green'
        elif prozent >= 50:
            farbe = 'orange'
        else:
            farbe = 'red'

        ctk.CTkLabel(scrollable_frame, text=f"{de} - {en}", width=300, anchor='w').grid(row=row, column=0, sticky='w', padx=5, pady=2)
        ctk.CTkLabel(scrollable_frame, text=str(stats['richtig']), width=80, anchor='center').grid(row=row, column=1, padx=5, pady=2)
        ctk.CTkLabel(scrollable_frame, text=str(stats['falsch']), width=80, anchor='center').grid(row=row, column=2, padx=5, pady=2)
        ctk.CTkLabel(scrollable_frame, text=f"{prozent:.2f}%", width=120, anchor='center', fg_color=farbe).grid(row=row, column=3, padx=5, pady=2)

        richtig_gesamt += stats['richtig']
        falsch_gesamt += stats['falsch']
        row += 1

    # Zusammenfassung
    prozent = (richtig_gesamt / (richtig_gesamt + falsch_gesamt) * 100) if (richtig_gesamt + falsch_gesamt) > 0 else 0
    row += 1
    ctk.CTkLabel(scrollable_frame, text="GESAMT", width=300, anchor='w', font=header_font).grid(row=row, column=0, sticky='w', padx=5, pady=(10,2))
    ctk.CTkLabel(scrollable_frame, text=str(richtig_gesamt), width=80, anchor='center', font=header_font).grid(row=row, column=1, padx=5, pady=(10,2))
    ctk.CTkLabel(scrollable_frame, text=str(falsch_gesamt), width=80, anchor='center', font=header_font).grid(row=row, column=2, padx=5, pady=(10,2))

    row += 1
    ctk.CTkLabel(scrollable_frame, text=f"Prozent richtig: {prozent:.2f}%", width=300, anchor='w').grid(row=row, column=0, columnspan=3, padx=5, pady=(10,2))

    # Canvas für Scrollregion aktualisieren
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Buttons am Ende
    row += 1
    home_button = ctk.CTkButton(
        scrollable_frame, text="🏠 Zurück zum Home",
        command=lambda: zeige_frame('start'), width=200, height=40, corner_radius=20
    )
    home_button.grid(row=row, column=0, columnspan=2, padx=10, pady=10)

    reset_button = ctk.CTkButton(
        scrollable_frame, text="🔃 Statistik zurücksetzen",
        command=statistik_zuruecksetzen, width=200, height=40, corner_radius=20
    )
    reset_button.grid(row=row, column=2, columnspan=2, padx=10, pady=10)






# Beispiel für die Initialisierung
def initialisiere_statistik_frame(master_frame):
    global statistik_frame
    statistik_frame = ctk.CTkFrame(master_frame)
    statistik_frame.pack(fill="both", expand=True)

    # Statistik-Funktion
def statistik():
    global frame  # Stelle sicher, dass frame global ist
    frame = ctk.CTkFrame(app)
    frames['statistik'] = frame
    # Weitere Initialisierungen, falls nötig

def statistik_zuruecksetzen():
    global runde_status
    for stats in vokabel_statistik.values():
        stats['richtig'] = 0
        stats['falsch'] = 0
    
    runde_status = {}
    statistik_speichern(vokabel_statistik)  # Speichere die zurückgesetzte Statistik
    zeige_statistik()

    ctk.CTkLabel(frames['statistik'], text="Statistik zurückgesetzt ✅", font=('Arial', 16)).pack(pady=5)






# Tipp-Funktion
def zeige_tipp():
    if aktuelle_vokabel:
        englisch = aktuelle_vokabel['Englisch']
        deutsch = aktuelle_vokabel['Deutsch']
        
        # Tipp für englische Vokabeln (prüft, ob das Wort mit artikeln bzw. to beginnt)
        if englisch.lower().startswith("to "):
            tipp = "to " + englisch[3:5] + "****" 
        elif englisch.lower().startswith("a "):
            tipp = "a " + englisch[2:4] + "****"
        elif englisch.lower().startswith("an "):
            tipp = "an " + englisch[3:5] + "****"
        elif englisch.lower().startswith("the "):
            tipp = "the " + englisch[4:6] + "****"
        elif englisch.lower().startswith("le "):
            tipp = "le " + englisch[3:5] + "****" 
        elif englisch.lower().startswith("la "):
            tipp = "la " + englisch[3:5] + "****" 
        elif englisch.lower().startswith("les "):
            tipp = "les " + englisch[4:6] + "****"
        elif englisch.lower().startswith("l'"):
            tipp = "l'" + englisch[3:5] + "****"
        elif englisch.lower().startswith("un "):
            tipp = "un " + englisch[3:5] + "****"
        elif englisch.lower().startswith("une "):
            tipp = "une " + englisch[4:6] + "****"
        elif englisch.lower().startswith("des "):
            tipp = "des " + englisch[4:6] + "****"
        elif englisch.lower().startswith("de "):
            tipp = "de " + englisch[3:5] + "****"
        elif englisch.lower().startswith("du "):
            tipp = "du " + englisch[3:5] + "****"
        elif englisch.lower().startswith("de la "):
            tipp = "de la " + englisch[6:8] + "****"
        elif englisch.lower().startswith("de l'"):
            tipp = "de l'" + englisch[6:8] + "****"
        else:
            tipp = englisch[:2] + "****"

        feedback_label.configure(text=f"Tipp: {tipp}")





# Dark/Light Mode
def wechsel_mode():
    aktueller_modus = ctk.get_appearance_mode()

    if aktueller_modus == "Dark":
        ctk.set_appearance_mode("Light")

        # Anpassungen für den Light Mode
        for widget in app.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(fg_color="#E3E3E3", hover_color="#CCCCCC", text_color="#333333", border_color="#999999", border_width=1)

    else:
        ctk.set_appearance_mode("Dark")

        # Anpassungen für den Dark Mode
        for widget in app.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.configure(fg_color="#444444", hover_color="#3A3A3A", text_color="#E0E0E0", border_color="#666666", border_width=1)


# Nächste Vokabel
def naechste_vokabel():
    global aktuelle_vokabel
    ungelernte = [v for v in alle_vokabeln if vokabel_statistik[(v['Deutsch'], v['Englisch'])]['richtig'] == 0]

    if vokabeln_zu_lernen:
        aktuelle_vokabel = vokabeln_zu_lernen.pop(0)
    elif ungelernte:
        vokabeln_zu_lernen.extend(ungelernte)
        random.shuffle(vokabeln_zu_lernen)
        aktuelle_vokabel = vokabeln_zu_lernen.pop(0)
    else:
        endbildschirm()
        return

    frage_label.configure(text=f"Was heißt: {aktuelle_vokabel['Deutsch']}?")
    eingabe.delete(0, ctk.END)
    feedback_label.configure(text="")
    update_fortschritt()


def update_fortschritt():
    gelernt = sum(1 for v in alle_vokabeln if runde_status.get((v['Deutsch'], v['Englisch']), False))
    fortschritt.set(gelernt / len(alle_vokabeln) if alle_vokabeln else 0)


# Antwort prüfen
def pruefe_antwort(event=None):
    global punktzahl
    antwort = eingabe.get().strip().lower()
    korrekt = aktuelle_vokabel['Englisch'].strip().lower()
    key = (aktuelle_vokabel['Deutsch'], aktuelle_vokabel['Englisch'])

    if antwort == korrekt:
        if not runde_status.get(key, False):
            runde_status[key] = True
        feedback_label.configure(text="✅ Richtig!")
        vokabel_statistik[key]["richtig"] += 1
    else:
        feedback_label.configure(text=f"❌ Falsch! Richtig: {korrekt}")
        punktzahl = max(0, punktzahl - 5)
        vokabel_statistik[key]["falsch"] += 1
        # Füge die Vokabel zurück in die Lern-Liste (hinten anstellen)
        vokabeln_zu_lernen.append(aktuelle_vokabel)

    punktzahl_label.configure(text=f"Punktzahl: {punktzahl}")
    update_fortschritt()
    app.after(1500, naechste_vokabel)
    statistik_speichern(vokabel_statistik)


# Endbildschirm
def endbildschirm():
    frame = ctk.CTkFrame(app)
    frames['ende'] = frame

    titel = ctk.CTkLabel(frame, text="🎉 Fertig gelernt!", font=('Arial', 40))
    titel.pack(pady=40)

    punktzahl_label = ctk.CTkLabel(frame, text=f"Deine Punktzahl: {punktzahl}", font=('Arial', 20))
    punktzahl_label.pack(pady=20)

    wiederholen_btn = ctk.CTkButton(frame, text="Wiederholen", command=starte_neu, width=200, height=50, corner_radius=20)
    wiederholen_btn.pack(pady=20)

    home_btn = ctk.CTkButton(frame, text="Zum Startbildschirm", command=zurücksetzen, width=200, height=50, corner_radius=20)
    home_btn.pack(pady=20)

    zeige_frame('ende')

def reset_for_new_attempt():
    global punktzahl, vokabeln_zu_lernen, runde_status
    punktzahl = 100
    vokabeln_zu_lernen = list(alle_vokabeln)
    random.shuffle(vokabeln_zu_lernen)
    runde_status = {}

def zurücksetzen():
    reset_for_new_attempt()
    punktzahl_label.configure(text=f"Punktzahl: {punktzahl}")  # Punktzahl auf dem Startbildschirm zurücksetzen
    zeige_frame('start')

def starte_neu():
    reset_for_new_attempt()
    punktzahl_label.configure(text=f"Punktzahl: {punktzahl}")  # Punktzahl auf dem Trainerbildschirm zurücksetzen
    update_fortschritt()
    naechste_vokabel()
    zeige_frame('trainer')
    

# Initialisierung
if __name__ == "__main__":
    try:
        haus_image = Image.open("haus.png")
        haus_icon = ctk.CTkImage(light_image=haus_image, dark_image=haus_image, size=(30, 30))
    except FileNotFoundError:
        print("Die Datei 'haus.png' wurde nicht gefunden!")

    try:
        birne_image = Image.open("birne.png")
        birne_icon = ctk.CTkImage(light_image=birne_image, dark_image=birne_image, size=(30, 30))
    except FileNotFoundError:
        print("Die Datei 'birne.png' wurde nicht gefunden!")

    try:
        tipp_image = Image.open("tipp.png")
        tipp_icon = ctk.CTkImage(light_image=tipp_image, dark_image=tipp_image, size=(30, 30))
    except FileNotFoundError:
        print("Die Datei 'tipp.png' wurde nicht gefunden!")

    startbildschirm()
    trainer()
    statistik()
    app.bind('<Configure>', update_font_sizes)
    app.mainloop()
