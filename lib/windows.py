import tkinter as tk
import tkinter.messagebox as tkmb
import customtkinter as ctk
import os
import threading
from PIL import Image, ImageTk
import random

MODES = ["Lookup Only", "Sparkle Notes", "Immersion Mode", "Word Blossom", "Sentence Whisper"]

current_folder = os.path.dirname(os.path.abspath(__file__))
repo_folder = os.path.dirname(current_folder)
os.chdir(repo_folder)
try:
    from lib.localai import OllamaClient
except ImportError as e:
    from localai import OllamaClient

    print(f"Error importing OllamaClient: {e}")

# --- GLOBAL THEME SETTINGS ---
DARK_BG = "#0d0d0d"
CARD_BG = "#151515"
CARD_HOVER = "#1c1c1c"
ACCENT_GREEN = "#00D287"
TEXT_LIGHT = "#ffffff"
TEXT_MUTED = "#888888"


class ControlPanel:
    def __init__(self, app_callback=None, ai_client: OllamaClient = OllamaClient()):
        ctk.set_appearance_mode("dark")
        # Fallback to standard dark theme if custom theme isn't found
        try:
            ctk.set_default_color_theme(os.path.join(current_folder, "theme.json"))
        except:
            ctk.set_default_color_theme("dark-blue")

        self.ai = ai_client
        self.ai_opened = True
        self.opened = False
        self.done = False
        self.app_callback = app_callback
        self.mode_index = 1
        self.response_mode = MODES[self.mode_index]

        self.root = ctk.CTk()
        self.root.title("Monitor")
        self.root.resizable(width=False, height=False)
        self.root.wm_attributes("-topmost", True)
        self.root.configure(fg_color=DARK_BG)

        self.status_label = ctk.CTkLabel(self.root, text="AI Status: Unknown", text_color="gray")
        self.status_label.pack(side="top", fill="x", padx=10, pady=5)

        self.ai_btn = ctk.CTkButton(self.root, text="Unload Model (Free VRAM)", fg_color="#4a4a4a",
                                    command=self.toggle_ai)
        self.ai_btn.pack(side="top", fill="x", padx=10, pady=5)

        self.mode_btn = ctk.CTkButton(self.root, text=f"Mode: {self.response_mode}", command=self.toggle_mode)
        self.mode_btn.pack(side="top", fill="x", padx=10, pady=5)

        self.state_btn = ctk.CTkButton(self.root, text="Start", fg_color=ACCENT_GREEN, text_color="black",
                                       command=self.toggle_state)
        self.state_btn.pack(side="top", fill="x", padx=10, pady=5)

        self.app_btn = ctk.CTkButton(self.root, text="Open Main App", command=self.open_app)
        self.app_btn.pack(side="top", fill="x", padx=10, pady=5)

        self.exit_btn = ctk.CTkButton(self.root, text="Exit", fg_color="#942626", hover_color="#731d1d",
                                      command=self.cancel)
        self.exit_btn.pack(side="top", fill="x", padx=10, pady=5)

    def update_ai_status(self, status_text, color):
        self.root.after(0, lambda: self.status_label.configure(text=f"AI Status: {status_text}", text_color=color))

    def load_ai(self):
        def task():
            self.update_ai_status("Loading...", "orange")
            if self.ai.manage_model("load"):
                self.update_ai_status("Loaded (VRAM Occupied)", ACCENT_GREEN)

        threading.Thread(target=task, daemon=True).start()

    def unload_ai(self):
        def task():
            self.update_ai_status("Unloading...", "orange")
            if self.ai.manage_model("unload"):
                self.update_ai_status("Unloaded (VRAM Free)", "gray")

        threading.Thread(target=task, daemon=True).start()

    def toggle_ai(self):
        if self.ai_opened:
            self.unload_ai()
            self.ai_opened = False
            self.ai_btn.configure(text="Load Model (Use VRAM)", fg_color="#4a4a4a")
        else:
            self.load_ai()
            self.ai_opened = True
            self.ai_btn.configure(text="Unload Model (Free VRAM)", fg_color="#4a4a4a")

    def toggle_state(self):
        self.opened = not self.opened
        if self.opened:
            self.state_btn.configure(text="Pause", fg_color="orange")
            self.update_ai_status("Running", ACCENT_GREEN)
        else:
            self.state_btn.configure(text="Start", fg_color=ACCENT_GREEN, text_color="black")
            self.update_ai_status("Paused", "gray")

    def toggle_mode(self):
        self.mode_index = (self.mode_index + 1) % len(MODES)
        self.response_mode = MODES[self.mode_index]
        self.mode_btn.configure(text=f"Mode: {self.response_mode}")

    def open_app(self):
        if self.app_callback:
            try:
                self.app_callback()
            except Exception as e:
                tkmb.showerror("Error", f"Failed to open app: {e}")

    def show(self):
        self.root.mainloop()

    def cancel(self):
        self.done = True
        self.root.destroy()


def popup_message(title, message):
    root = tk.Tk()
    root.withdraw()
    tkmb.showinfo(title, message)
    root.destroy()


class Long_message_popup:
    def __init__(self, title, message, master: ControlPanel, display_image=True):
        self.long_popup = ctk.CTkToplevel(master.root)
        self.long_popup.geometry("600x300")
        self.long_popup.title(title)
        self.long_popup.attributes("-topmost", True)
        self.long_popup.configure(fg_color=DARK_BG)

        title_label = ctk.CTkLabel(self.long_popup, text=title, font=("Helvetica", 24, "bold"), text_color=TEXT_LIGHT)
        title_label.pack(pady=(15, 5))

        if display_image:
            img_num = random.randint(1, 5)
            try:
                img_path = os.path.join(repo_folder, ".misc", "long_response", f"{img_num}.png")
                img = Image.open(img_path)
                img_size = img.size
                max_size = (150, 150)
                scale_factor = min(max_size[0] / img_size[0], max_size[1] / img_size[1])
                new_size = (int(img_size[0] * scale_factor), int(img_size[1] * scale_factor))
                photo = ctk.CTkImage(img, size=new_size)
                img_label = ctk.CTkLabel(self.long_popup, image=photo, text="")
                img_label.image = photo
                img_label.pack(side="left", padx=10, pady=0)
            except Exception as e:
                pass

        self.text_box = ctk.CTkTextbox(self.long_popup, wrap="word", font=("Helvetica", 16), fg_color=CARD_BG,
                                       text_color=TEXT_LIGHT)
        self.text_box.insert("1.0", message)
        self.text_box.configure(state="disabled")
        self.text_box.pack(padx=20, pady=10, fill="both", expand=True)

    def append_text(self, new_text):
        self.text_box.configure(state="normal")
        self.text_box.insert("end", new_text)
        self.text_box.configure(state="disabled")
        self.text_box.see("end")

    def show(self):
        self.long_popup.focus_set()

    def add_button(self, text, command):
        btn = ctk.CTkButton(self.long_popup, text=text, command=command, fg_color=ACCENT_GREEN, text_color="black")
        btn.pack(pady=10)


class StatCard(ctk.CTkFrame):
    """Custom animated stat card for the dashboard"""

    def __init__(self, master, title, subtitle, target_progress, value_text, **kwargs):
        super().__init__(master, fg_color=CARD_BG, corner_radius=15, **kwargs)
        self.target_progress = target_progress
        self.current_progress = 0.0

        self.title_lbl = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_LIGHT)
        self.title_lbl.pack(anchor="w", padx=15, pady=(15, 0))

        self.sub_lbl = ctk.CTkLabel(self, text=subtitle, font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.sub_lbl.pack(anchor="w", padx=15, pady=(0, 10))

        # Status indicator matching the screenshot
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(anchor="w", padx=15)
        self.dot = ctk.CTkLabel(self.status_frame, text="●", text_color=ACCENT_GREEN, font=ctk.CTkFont(size=10))
        self.dot.pack(side="left", padx=(0, 5))
        self.status_txt = ctk.CTkLabel(self.status_frame, text="Optimal", text_color=TEXT_LIGHT,
                                       font=ctk.CTkFont(size=12, weight="bold"))
        self.status_txt.pack(side="left")

        self.val_lbl = ctk.CTkLabel(self, text=value_text, font=ctk.CTkFont(size=24, weight="bold"),
                                    text_color=TEXT_LIGHT)
        self.val_lbl.pack(side="right", padx=15, pady=15, anchor="s")

        self.progress = ctk.CTkProgressBar(self, progress_color=ACCENT_GREEN, fg_color="#2b2b2b", height=6)
        self.progress.pack(side="bottom", fill="x", padx=15, pady=15)
        self.progress.set(0)

    def animate(self):
        if self.current_progress < self.target_progress:
            self.current_progress += 0.02
            self.progress.set(self.current_progress)
            self.after(20, self.animate)


class HomeFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, ai_client, db, **kwargs):
        super().__init__(master, fg_color=DARK_BG, **kwargs)
        self.ai = ai_client
        self.db = db
        self.is_generating = False

        # Grid Configuration
        self.grid_columnconfigure((0, 1, 2), weight=1)

        # --- Top Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))

        self.welcome_label = ctk.CTkLabel(self.header_frame, text="Welcome back", font=ctk.CTkFont(size=14),
                                          text_color=TEXT_MUTED)
        self.welcome_label.pack(anchor="w")
        self.name_label = ctk.CTkLabel(self.header_frame, text="Master", font=ctk.CTkFont(size=32, weight="bold"),
                                       text_color=TEXT_LIGHT)
        self.name_label.pack(anchor="w")

        # --- Top Stat Cards (Animated) ---
        self.card1 = StatCard(self, "Daily Goal", "Words & Characters", 0.0, "0%")
        self.card1.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="nsew")

        self.card2 = StatCard(self, "Vocabulary", "Total Mastered", 0.0, "0%")
        self.card2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.card3 = StatCard(self, "Accuracy", "Recent Reviews", 0.0, "0%")
        self.card3.grid(row=1, column=2, padx=(10, 0), pady=10, sticky="nsew")

        # Trigger Animations
        self.after(500, self.card1.animate)
        self.after(700, self.card2.animate)
        self.after(900, self.card3.animate)

        # --- Daily AI Challenge Section ---
        self.insight_card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=15)
        self.insight_card.grid(row=2, column=0, columnspan=2, padx=(0, 10), pady=10, sticky="nsew")
        self.insight_card.grid_columnconfigure(0, weight=1)
        self.insight_card.grid_rowconfigure(1, weight=1)

        self.insight_header = ctk.CTkFrame(self.insight_card, fg_color="transparent")
        self.insight_header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        self.insight_title = ctk.CTkLabel(self.insight_header, text="Performance Analyzer",
                                          font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_LIGHT)
        self.insight_title.pack(side="left")

        self.refresh_btn = ctk.CTkButton(self.insight_header, text="Generate Challenge", width=120, fg_color="#2b2b2b",
                                         hover_color="#3b3b3b", command=self.generate_challenge)
        self.refresh_btn.pack(side="right")

        self.insight_text = ctk.CTkTextbox(self.insight_card, wrap="word", font=("Helvetica", 14), fg_color="#1a1a1a",
                                           text_color=TEXT_LIGHT, height=150, corner_radius=10)
        self.insight_text.configure(state="disabled")
        self.insight_text.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="nsew")

        # --- Words Summary Section ---
        self.summary_card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=15)
        self.summary_card.grid(row=2, column=2, padx=(10, 0), pady=10, sticky="nsew")
        self.summary_card.grid_columnconfigure(0, weight=1)
        self.summary_card.grid_rowconfigure(1, weight=1)

        self.summary_header = ctk.CTkFrame(self.summary_card, fg_color="transparent")
        self.summary_header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        self.summary_title = ctk.CTkLabel(self.summary_header, text="Optimization",
                                          font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_LIGHT)
        self.summary_title.pack(side="left")

        self.summary_btn = ctk.CTkButton(self.summary_header, text="Summarize", width=100, fg_color="#2b2b2b",
                                         hover_color="#3b3b3b", command=self.generate_summary, state="disabled")
        self.summary_btn.pack(side="right")

        self.summary_text = ctk.CTkTextbox(self.summary_card, wrap="word", font=("Helvetica", 14), fg_color="#1a1a1a",
                                           text_color=TEXT_LIGHT, height=150, corner_radius=10)
        self.summary_text.configure(state="disabled")
        self.summary_text.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="nsew")

        self.last_words = []

    def append_text(self, text, box):
        box.configure(state="normal")
        box.insert("end", text)
        box.configure(state="disabled")
        box.see("end")

    def _set_text(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")
        box.see("1.0")

    # The backend AI generation logic remains untouched
    def generate_challenge(self):
        if self.is_generating:
            tkmb.showwarning("In Progress", "Already generating. Please wait.")
            return

        if not self.ai or not self.db:
            self._set_text(self.insight_text, "❌ AI Client or Database not available")
            return

        try:
            self.last_words = self.db.get_recent_words(limit=3)
        except Exception as e:
            self.last_words = []
            print(f"Error reading recent words: {e}")

        self.is_generating = True
        self.refresh_btn.configure(state="disabled")
        self.summary_btn.configure(state="disabled")

        self.insight_text.configure(state="normal")
        self.insight_text.delete("1.0", "end")
        self.insight_text.insert("1.0", "Analyzing performance and generating challenge...")
        self.insight_text.configure(state="disabled")

        def generate():
            try:
                if not self.last_words:
                    final_text = "No data found. Begin reviewing words to generate insights."
                    self.after(0, lambda text=final_text: self._set_text(self.insight_text, text))
                else:
                    word_list = ", ".join([w[1] for w in self.last_words])
                    prompt = f"Word Blossom Mode: {word_list}"

                    full_response = ""
                    for chunk in self.ai.generate_response(prompt):
                        if full_response == "":
                            self.after(0, lambda: self._set_text(self.insight_text, ""))
                        full_response += chunk
                        self.after(0, lambda text=chunk: self.append_text(text, self.insight_text))

                    self.after(0, lambda: self.summary_btn.configure(state="normal", fg_color=ACCENT_GREEN,
                                                                     text_color="black"))

            except Exception as e:
                error_msg = f"Error generating challenge: {str(e)}"
                self.after(0, lambda msg=error_msg: self._set_text(self.insight_text, msg))
            finally:
                self.is_generating = False
                self.after(0, lambda: self.refresh_btn.configure(state="normal"))

        threading.Thread(target=generate, daemon=True).start()

    def generate_summary(self):
        if self.is_generating or not self.last_words:
            return

        self.is_generating = True
        self.refresh_btn.configure(state="disabled")
        self._set_text(self.summary_text, "Optimizing summary data...")

        def generate():
            try:
                word_list = ", ".join([w[1] for w in self.last_words])
                prompt = f"Summarize these words with Sparkle Notes Mode: {word_list}"

                full_summary = ""
                for chunk in self.ai.generate_response(prompt):
                    if full_summary == "":
                        self.after(0, lambda: self._set_text(self.summary_text, ""))
                    full_summary += chunk
                    self.after(0, lambda text=chunk: self.append_text(text, self.summary_text))

            except Exception as e:
                error_msg = f"Error generating summary: {str(e)}"
                self.after(0, lambda msg=error_msg: self._set_text(self.summary_text, msg))
            finally:
                self.is_generating = False
                self.after(0, lambda: self.refresh_btn.configure(state="normal"))
                self.after(0, lambda: self.summary_btn.configure(fg_color="#2b2b2b", text_color=TEXT_LIGHT))

        threading.Thread(target=generate, daemon=True).start()


class ReviewFrame(ctk.CTkFrame):
    def __init__(self, master, reviewer, **kwargs):
        super().__init__(master, fg_color=DARK_BG, **kwargs)
        self.reviewer = reviewer
        self._setup_ui()
        self._load_words()

    def _setup_ui(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.title = ctk.CTkLabel(self.header_frame, text="Review character", font=ctk.CTkFont(size=24, weight="bold"),
                                  text_color=TEXT_LIGHT)
        self.title.pack(side="left")

        self.progress_label = ctk.CTkLabel(self.header_frame, text="", text_color=TEXT_MUTED)
        self.progress_label.pack(side="right", pady=5)

        card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=15)
        card.pack(fill="both", expand=True, pady=10)

        self.word_label = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=48, weight="bold"), text_color=TEXT_LIGHT,
                                       wraplength=400)
        self.word_label.pack(pady=(50, 10))

        self.trans_label = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=24), text_color=ACCENT_GREEN)
        self.trans_label.pack(pady=10)

        self.example_label = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=16, slant="italic"),
                                          text_color=TEXT_MUTED, wraplength=400)
        self.example_label.pack(pady=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)

        self.hard_btn = ctk.CTkButton(btn_frame, text="Need Review", fg_color="#4a2525", hover_color="#633232",
                                      text_color="#ff6b6b", height=40, corner_radius=8,
                                      command=lambda: self._review("hard"))
        self.hard_btn.pack(side="left", padx=10, expand=True)

        self.good_btn = ctk.CTkButton(btn_frame, text="Done Review", fg_color="#1a3b2b", hover_color="#24523c",
                                      text_color=ACCENT_GREEN, height=40, corner_radius=8,
                                      command=lambda: self._review("good"))
        self.good_btn.pack(side="left", padx=10, expand=True)

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", pady=10)

        self.prev_btn = ctk.CTkButton(nav_frame, text="← Previous", fg_color="transparent", border_width=1,
                                      border_color="#333", hover_color=CARD_HOVER, command=self._prev_word)
        self.prev_btn.pack(side="left")

        self.next_btn = ctk.CTkButton(nav_frame, text="Next →", fg_color="transparent", border_width=1,
                                      border_color="#333", hover_color=CARD_HOVER, command=self._next_word)
        self.next_btn.pack(side="right")

    def _load_words(self):
        if self.reviewer:
            self.reviewer.load_review_words()
            self._update_display()

    def _update_display(self):
        if not self.reviewer: return
        word = self.reviewer.get_current_word()
        if word:
            self.word_label.configure(text=word[1])
            self.trans_label.configure(text=word[2])
            self.example_label.configure(text=f'"{word[3]}"' if word[3] else "")
            self.progress_label.configure(text=self.reviewer.get_progress())
            self.prev_btn.configure(state="normal" if self.reviewer.current_index > 0 else "disabled")
            self.next_btn.configure(
                state="normal" if self.reviewer.current_index < len(self.reviewer.words) - 1 else "disabled")
        else:
            self.word_label.configure(text="✨ Today's words")
            self.trans_label.configure(text="")
            self.example_label.configure(text="No recent words counted")

    def _review(self, quality):
        if self.reviewer and self.reviewer.has_words():
            next_date = self.reviewer.review_current(quality)
            self._update_display()

    def _prev_word(self):
        if self.reviewer and self.reviewer.current_index > 0:
            self.reviewer.current_index -= 1
            self._update_display()

    def _next_word(self):
        if self.reviewer and self.reviewer.next_word():
            self._update_display()


class App(ctk.CTk):
    def __init__(self, reviewer=None, ai_client=None, db=None):
        super().__init__()
        self.reviewer = reviewer
        self.ai_client = ai_client
        self.db = db

        # Window configuration
        self.title("IQON - VocabMaster")
        self.geometry("1100x700")
        self.configure(fg_color=DARK_BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sleek Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=15, fg_color=CARD_BG)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(15, 0), pady=15)
        self.sidebar.grid_rowconfigure(5, weight=1)  # Push bottom items down

        # Logo Area
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=30, sticky="ew")
        self.logo = ctk.CTkLabel(self.logo_frame, text="VocabMaster", font=ctk.CTkFont(size=22, weight="bold"),
                                 text_color=TEXT_LIGHT)
        self.logo.pack(side="left")
        self.beta_badge = ctk.CTkLabel(self.logo_frame, text="beta", font=ctk.CTkFont(size=10), fg_color="#1a3b2b",
                                       text_color=ACCENT_GREEN, corner_radius=5)
        self.beta_badge.pack(side="left", padx=5)

        # Main Menu Label
        self.menu_lbl = ctk.CTkLabel(self.sidebar, text="MAIN", font=ctk.CTkFont(size=11, weight="bold"),
                                     text_color=TEXT_MUTED)
        self.menu_lbl.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        # Navigation Buttons
        self.btn_home = ctk.CTkButton(self.sidebar, text="Dashboard", anchor="w", fg_color="transparent",
                                      text_color=TEXT_LIGHT, hover_color=CARD_HOVER,
                                      command=lambda: self.show_frame("home"))
        self.btn_home.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.btn_review = ctk.CTkButton(self.sidebar, text="Review", anchor="w", fg_color="transparent",
                                        text_color=TEXT_LIGHT, hover_color=CARD_HOVER,
                                        command=lambda: self.show_frame("review"))
        self.btn_review.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        # Bottom Support Box
        self.support_box = ctk.CTkFrame(self.sidebar, fg_color=DARK_BG, corner_radius=10)
        self.support_box.grid(row=6, column=0, padx=15, pady=20, sticky="ew")
        self.support_lbl = ctk.CTkLabel(self.support_box, text="find bugs?", font=ctk.CTkFont(size=14, weight="bold"),
                                        text_color=TEXT_LIGHT)
        self.support_lbl.pack(anchor="w", padx=15, pady=(15, 0))
        self.support_sub = ctk.CTkLabel(self.support_box, text="24/7 assistance available", font=ctk.CTkFont(size=11),
                                        text_color=TEXT_MUTED)
        self.support_sub.pack(anchor="w", padx=15, pady=(0, 10))
        self.support_btn = ctk.CTkButton(self.support_box, text="Talk to admin", fg_color=ACCENT_GREEN,
                                         text_color="black", hover_color="#00b373")
        self.support_btn.pack(padx=15, pady=(0, 15), fill="x")

        # Initialize Main Content Frames
        self.frames = {}
        self.frames["home"] = HomeFrame(self, self.ai_client, self.db)
        self.frames["review"] = ReviewFrame(self, self.reviewer)

        self.show_frame("home")

    def show_frame(self, page_name):
        for frame in list(self.frames.values()):
            frame.grid_forget()

        # Highlight active sidebar button
        self.btn_home.configure(fg_color="#2b2b2b" if page_name == "home" else "transparent")
        self.btn_review.configure(fg_color="#2b2b2b" if page_name == "review" else "transparent")

        self.frames[page_name].grid(row=0, column=1, sticky="nsew", padx=25, pady=25)


if __name__ == "__main__":
    # Test Launch
    app = App()
    app.mainloop()
