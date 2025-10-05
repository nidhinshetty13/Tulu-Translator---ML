import csv
import sys
import difflib
import os
import tkinter as tk
from tkinter import messagebox

# Paths
CSV_FILE = r"C:\Users\Nidhin Shetty\OneDrive\Desktop\tulu\transl.csv"
MISSING_FILE = r"C:\Users\Nidhin Shetty\OneDrive\Desktop\missing_words.csv"

# Load translations
def load_translations(csv_file):
    translations = {}
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    translations[row[0].strip().lower()] = row[1].strip()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load CSV: {e}")
    return translations

# Store missing word
def store_missing(word, missing_list_widget=None):
    word = word.strip()
    # Ensure missing file exists
    if not os.path.exists(MISSING_FILE):
        with open(MISSING_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["English"])  # header

    # Check if word already exists
    existing = set()
    with open(MISSING_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row:
                existing.add(row[0].strip().lower())

    if word.lower() not in existing:
        with open(MISSING_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([word])
        if missing_list_widget:
            missing_list_widget.insert(tk.END, word)

# Translate sentence / word
def translate_sentence(sentence, translations, missing_list_widget=None):
    sentence = sentence.strip().lower()
    if sentence in translations:
        return translations[sentence]

    words = sentence.split()
    translated_words = []

    for word in words:
        if word in translations:
            translated_words.append(translations[word])
        else:
            close = difflib.get_close_matches(word, translations.keys(), n=1, cutoff=0.7)
            if close:
                translated_words.append(translations[close[0]])
            else:
                store_missing(word, missing_list_widget)
                translated_words.append(f"[{word}]")  # mark as missing

    return " ".join(translated_words)

# Copy all missing words to clipboard
def copy_missing_words(missing_list_widget):
    words = missing_list_widget.get(0, tk.END)
    if words:
        all_words = "\n".join(words)
        root.clipboard_clear()
        root.clipboard_append(all_words)
        root.update()
        messagebox.showinfo("Copied", "All missing words copied to clipboard!")

# ----------------- GUI -----------------
def run_app():
    global root
    translations = load_translations(CSV_FILE)

    root = tk.Tk()
    root.title("🌐 English → Tulu Translator")
    root.geometry("850x650")
    root.configure(bg="#f1f3f6")
    root.eval('tk::PlaceWindow . center')

    # Title
    title = tk.Label(root, text="🌐 English → Tulu Translator 🌐",
                     font=("Helvetica", 22, "bold"), bg="#f1f3f6", fg="#333")
    title.pack(pady=15)

    # Input
    tk.Label(root, text="Enter English word or sentence:", font=("Helvetica", 14), bg="#f1f3f6").pack()
    entry = tk.Entry(root, font=("Helvetica", 14), width=60, bd=3, relief="solid")
    entry.pack(pady=10)

    # Output
    output_label = tk.Label(root, text="", font=("Helvetica", 18, "bold"), fg="#28a745",
                            bg="#e9f7ef", wraplength=750, justify="center",
                            relief="solid", bd=2, padx=15, pady=15)
    output_label.pack(pady=20)

    # Missing Words Panel
    tk.Label(root, text="Missing Words / Phrases:", font=("Helvetica", 14, "bold"), bg="#f1f3f6").pack()
    missing_list = tk.Listbox(root, height=10, width=60, font=("Helvetica", 12), bg="#fff3cd", fg="#856404")
    missing_list.pack(pady=5)

    # Load existing missing words
    if os.path.exists(MISSING_FILE):
        with open(MISSING_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row:
                    missing_list.insert(tk.END, row[0])

    # Buttons
    def on_translate():
        text = entry.get().strip()
        if text:
            result = translate_sentence(text, translations, missing_list_widget=missing_list)
            output_label.config(text=result)
        else:
            messagebox.showwarning("Input Error", "Please enter a word or sentence.")
        # Function to clear missing words
    def clear_missing_words(missing_list_widget):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear all missing words?")
        if confirm:
            missing_list_widget.delete(0, tk.END)  # Clear UI list
            with open(MISSING_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["English"])  # reset file with header
            messagebox.showinfo("Cleared", "All missing words have been cleared.")

    def clear_input():
        entry.delete(0, tk.END)

    def clear_output():
        output_label.config(text="")

    button_frame = tk.Frame(root, bg="#f1f3f6")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Clear Missing Words", font=("Helvetica", 14, "bold"),
          bg="#fd7e14", fg="white", relief="flat", padx=20, pady=6,
          command=lambda: clear_missing_words(missing_list)).grid(row=0, column=5, padx=8)
    tk.Button(button_frame, text="🔍 Translate", font=("Helvetica", 14, "bold"),
              bg="#28a745", fg="white", relief="flat", padx=20, pady=6, command=on_translate).grid(row=0, column=0, padx=8)
    tk.Button(button_frame, text="Clear Input", font=("Helvetica", 14, "bold"),
              bg="#ffc107", fg="#212529", relief="flat", padx=20, pady=6, command=clear_input).grid(row=0, column=1, padx=8)
    tk.Button(button_frame, text="Clear Output", font=("Helvetica", 14, "bold"),
              bg="#17a2b8", fg="white", relief="flat", padx=20, pady=6, command=clear_output).grid(row=0, column=2, padx=8)
    tk.Button(button_frame, text="Copy Missing Words", font=("Helvetica", 14, "bold"),
              bg="#6f42c1", fg="white", relief="flat", padx=20, pady=6,
              command=lambda: copy_missing_words(missing_list)).grid(row=0, column=3, padx=8)
    tk.Button(button_frame, text="Exit", font=("Helvetica", 14, "bold"),
              bg="#dc3545", fg="white", relief="flat", padx=20, pady=6, command=root.quit).grid(row=0, column=4, padx=8)

    root.mainloop()


if __name__ == "__main__":
    if sys.platform.startswith('win'):
        import os
        os.system('chcp 65001')
    run_app()
