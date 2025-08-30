import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext
from functions.sanitize import sanitize_file
from PIL import ImageTk, Image


class RedactorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV PII Redactor")
        self.geometry("720x720")
        self.minsize(720, 520)
 
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.sample_rows = tk.StringVar()  # keep as string; we'll validate/convert
        self.no_ner = tk.BooleanVar(value=False)
        self.token = tk.StringVar(value="")

        self._build_ui()
        self._set_busy(False)

    # ---------- UI ----------
    def _build_ui(self):
        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        # Logo
        # img = Image.open("logo.png")
        # img = img.resize((685, 100))
        # img = ImageTk.PhotoImage(img)
        # logo_row = tk.Label(root, image = img)
        # logo_row.image = img
        # logo_row.pack(side = "top", fill = "both", expand = "no", pady=(0,10))

        # Input
        in_row = ttk.Frame(root)
        in_row.pack(fill="x", pady=(0, 10))
        ttk.Label(in_row, text="Input CSV:").pack(side="left", padx=(0, 19))
        in_entry = ttk.Entry(in_row, textvariable=self.input_path)
        in_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(in_row, text="Browse…", command=self._browse_input).pack(side="left", padx=(8, 0))

        # Output
        out_row = ttk.Frame(root)
        out_row.pack(fill="x", pady=(0, 10))
        ttk.Label(out_row, text="Output CSV:").pack(side="left", padx=(0, 8))
        out_entry = ttk.Entry(out_row, textvariable=self.output_path)
        out_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(out_row, text="Browse…", command=self._browse_output).pack(side="left", padx=(8, 0))

        # Options frame
        opts = ttk.LabelFrame(root, text="Options")
        opts.pack(fill="x", pady=(0, 10))

        # Sample rows
        samp_row = ttk.Frame(opts)
        samp_row.pack(fill="x", padx=10, pady=(8, 4))
        ttk.Label(samp_row, text="Sample rows:").pack(side="left")
        samp_entry = ttk.Entry(samp_row, width=18, textvariable=self.sample_rows)
        samp_entry.pack(side="left", padx=(43, 0))
        ttk.Label(
            samp_row, text="Leave blank to process all rows."
        ).pack(side="left", padx=(10, 0))

        # Token
        token_row = ttk.Frame(opts)
        token_row.pack(fill="x", padx=10, pady=(4, 8))
        ttk.Label(token_row, text="Replacement token:").pack(side="left")
        token_entry = ttk.Entry(token_row, width=18, textvariable=self.token)
        token_entry.pack(side="left", padx=(8, 0))
        ttk.Label(
            token_row, text="Leave blank to use redaction categories as tokens."
        ).pack(side="left", padx=(10,0))

        # NER toggle
        ner_row = ttk.Frame(opts)
        ner_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Checkbutton(
            ner_row,
            text="Disable NER (Only use RegEx)",
            variable=self.no_ner,
        ).pack(side="left")

        # Run / progress
        run_row = ttk.Frame(root)
        run_row.pack(fill="x", pady=(0, 10))
        self.run_btn = ttk.Button(run_row, text="Run Redaction", command=self._on_run_click)
        self.run_btn.pack(side="left")
        self.progress = ttk.Progressbar(run_row, mode="indeterminate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(12, 0))

        # Output summary
        ttk.Label(root, text="Redaction summary:").pack(anchor="w")
        self.summary = scrolledtext.ScrolledText(root, height=12, wrap="word")
        self.summary.pack(fill="both", expand=True)

        # Style polish
        try:
            self._apply_ttk_theme()
        except Exception:
            pass

    def _apply_ttk_theme(self):
        style = ttk.Style()
        # Use a platform-appropriate theme if available
        for theme in ("clam", "vista", "xpnative", "aqua"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break

    # ---------- Handlers ----------
    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Select input CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.input_path.set(path)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Choose output CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.output_path.set(path)

    def _validate(self):
        if not self.input_path.get().strip():
            messagebox.showerror("Missing input", "Please choose an input CSV.")
            return False
        if not self.output_path.get().strip():
            messagebox.showerror("Missing output", "Please choose an output CSV.")
            return False

        sample_txt = self.sample_rows.get().strip()
        if sample_txt:
            try:
                val = int(sample_txt)
                if val <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid sample rows",
                    "Sample rows must be a positive integer, or leave blank to process all rows.",
                )
                return False
        return True

    def _on_run_click(self):
        if not self._validate():
            return

        # Clear previous summary
        self.summary.delete("1.0", "end")

        # Collect options
        input_path = self.input_path.get().strip()
        output_path = self.output_path.get().strip()
        sample_txt = self.sample_rows.get().strip()
        sample_rows = int(sample_txt) if sample_txt else None
        use_ner = not self.no_ner.get()
        token = self.token.get()

        # Run in a thread
        self._set_busy(True)

        def worker():
            try:
                result = sanitize_file(
                    input_path=input_path,
                    output_path=output_path,
                    sample_rows=sample_rows,
                    use_ner=use_ner,
                    token=token,
                )
                self._post_success(result)
            except Exception as e:
                self._post_error(e)

        threading.Thread(target=worker, daemon=True).start()

    def _post_success(self, summary_text):
        # jump back to main thread
        self.after(0, lambda: self._on_done(summary_text=summary_text, error=None))

    def _post_error(self, err):
        self.after(0, lambda: self._on_done(summary_text=None, error=err))

    def _on_done(self, summary_text=None, error=None):
        self._set_busy(False)
        if error is not None:
            messagebox.showerror("Error during redaction", str(error))
            return
        if summary_text is None:
            summary_text = "(No summary returned.)"
        self.summary.insert("1.0", self._decode_summary(summary_text))
        self.summary.see("1.0")
        messagebox.showinfo("Completed", "Redaction finished.")
        
    def _decode_summary(self, summary_text):
        summary = "TOTAL REDACTION COUNT:\n" + \
            str(summary_text["total"]["count"]) + "\n\n" + \
            "REDACTION COUNT BY CATEGORY:\n"
        for entry in summary_text["by_label"]:
            summary += entry + ": " + str(summary_text["by_label"][entry]) +"\n"
        summary += "\nREDACTION COUNT BY COLUMN:\n"
        for entry in summary_text["by_column"]:
            summary += entry + ": " + str(summary_text["by_column"][entry]) +"\n"
        return summary

    def _set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        for child in self.winfo_children():
            try:
                # Keep the progress bar and summary enabled appropriately
                if child is self.summary:
                    continue
                child.configure(state=state)
            except tk.TclError:
                pass

        # Specifically control interactive elements
        # Enable/disable all inputs/buttons except the summary
        for widget in (
            self.run_btn,
        ):
            try:
                widget.configure(state="disabled" if busy else "normal")
            except tk.TclError:
                pass

        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()


if __name__ == "__main__":
    app = RedactorGUI()
    app.mainloop()
