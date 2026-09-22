from __future__ import annotations

import subprocess
import threading
import sys
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime


def resolve_base_dir() -> Path:
    # When frozen by PyInstaller, resolve paths from the real exe location.
    if getattr(sys, "frozen", False):
        launcher_dir = Path(sys.executable).resolve().parent
    else:
        launcher_dir = Path(__file__).resolve().parent

    if (launcher_dir / "apps").exists() and (launcher_dir / "output").exists():
        return launcher_dir

    if (launcher_dir.parent / "apps").exists() and (launcher_dir.parent / "output").exists():
        return launcher_dir.parent

    return launcher_dir


BASE_DIR = resolve_base_dir()
APPS_DIR = BASE_DIR / "apps"
OUTPUT_DIR = BASE_DIR / "output"
RESULTS_ARCHIVE = BASE_DIR / "batch_results"


def find_profiles() -> tuple[list[str], list[str]]:
    generators: list[str] = []
    guessers: list[str] = []

    for ini_file in sorted(APPS_DIR.glob("*.ini")):
        name = ini_file.stem
        if name.endswith("_generator"):
            generators.append(name)
        elif name.endswith("_guesser"):
            guessers.append(name)

    return generators, guessers


def find_executable() -> Path:
    candidates = [OUTPUT_DIR / "main.exe", OUTPUT_DIR / "main"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


class LauncherUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Hackintator Launcher - Multi Generateur/Predicteur")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)

        self.generators, self.guessers = find_profiles()
        self.executable = find_executable()

        self.iterations_var = tk.StringVar(value="100")
        self.gen_args_var = tk.StringVar(value="42 100")
        self.guess_args_var = tk.StringVar(value="")
        self.source_size_var = tk.StringVar(value="")

        # Checkbutton variables
        self.gen_checks: dict[str, tk.BooleanVar] = {}
        self.guess_checks: dict[str, tk.BooleanVar] = {}
        self.gen_list_frame: ttk.Frame | None = None
        self.guess_list_frame: ttk.Frame | None = None

        self._build_layout()
        self._log_environment()

    def _create_scrollable_checkbox_area(self, parent: ttk.Frame) -> ttk.Frame:
        """Create a fixed-height scrollable container for many checkboxes."""
        container = ttk.Frame(parent)

        canvas = tk.Canvas(container, height=160, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        content = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def _on_content_configure(_event: tk.Event[tk.Misc]) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event: tk.Event[tk.Misc]) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def _on_mousewheel(event: tk.Event[tk.Misc]) -> None:
            # Windows/macOS: MouseWheel with delta. Linux: Button-4/5 handled below.
            delta = getattr(event, "delta", 0)
            if delta:
                step = -1 if delta > 0 else 1
                canvas.yview_scroll(step, "units")

        def _on_mousewheel_linux_up(_event: tk.Event[tk.Misc]) -> None:
            canvas.yview_scroll(-1, "units")

        def _on_mousewheel_linux_down(_event: tk.Event[tk.Misc]) -> None:
            canvas.yview_scroll(1, "units")

        def _bind_mousewheel(_event: tk.Event[tk.Misc]) -> None:
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel_linux_up)
            canvas.bind_all("<Button-5>", _on_mousewheel_linux_down)

        def _unbind_mousewheel(_event: tk.Event[tk.Misc]) -> None:
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        content.bind("<Configure>", _on_content_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return container

    def _populate_profile_checkboxes(self) -> None:
        if self.gen_list_frame is None or self.guess_list_frame is None:
            return

        for widget in self.gen_list_frame.winfo_children():
            widget.destroy()
        for widget in self.guess_list_frame.winfo_children():
            widget.destroy()

        self.gen_checks = {}
        self.guess_checks = {}

        for gen in self.generators:
            var = tk.BooleanVar(value=True)
            self.gen_checks[gen] = var
            ttk.Checkbutton(self.gen_list_frame, text=gen, variable=var).pack(anchor=tk.W)

        for guesser in self.guessers:
            var = tk.BooleanVar(value=True)
            self.guess_checks[guesser] = var
            ttk.Checkbutton(self.guess_list_frame, text=guesser, variable=var).pack(anchor=tk.W)

    def _set_all_generators(self, value: bool) -> None:
        for var in self.gen_checks.values():
            var.set(value)

    def _set_all_guessers(self, value: bool) -> None:
        for var in self.guess_checks.values():
            var.set(value)

    def _build_layout(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(main_frame, text="Configuration", padding=12)
        form.pack(fill=tk.X, pady=(0, 10))

        profiles_frame = ttk.Frame(form)
        profiles_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=4)
        profiles_frame.columnconfigure(0, weight=1)
        profiles_frame.columnconfigure(1, weight=1)

        gen_group = ttk.LabelFrame(profiles_frame, text="Generateurs (cochez les choix)", padding=8)
        gen_group.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))

        gen_actions = ttk.Frame(gen_group)
        gen_actions.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(gen_actions, text="[+] Tout cocher", command=lambda: self._set_all_generators(True)).pack(side=tk.LEFT)
        ttk.Button(gen_actions, text="[-] Tout decocher", command=lambda: self._set_all_generators(False)).pack(side=tk.LEFT, padx=6)

        gen_scroll = self._create_scrollable_checkbox_area(gen_group)
        gen_scroll.pack(fill=tk.BOTH, expand=True)
        self.gen_list_frame = gen_scroll.winfo_children()[0].winfo_children()[0]

        guess_group = ttk.LabelFrame(profiles_frame, text="Predicteurs/Guessers (cochez les choix)", padding=8)
        guess_group.grid(row=0, column=1, sticky=tk.NSEW, padx=(6, 0))

        guess_actions = ttk.Frame(guess_group)
        guess_actions.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(guess_actions, text="[+] Tout cocher", command=lambda: self._set_all_guessers(True)).pack(side=tk.LEFT)
        ttk.Button(guess_actions, text="[-] Tout decocher", command=lambda: self._set_all_guessers(False)).pack(side=tk.LEFT, padx=6)

        guess_scroll = self._create_scrollable_checkbox_area(guess_group)
        guess_scroll.pack(fill=tk.BOTH, expand=True)
        self.guess_list_frame = guess_scroll.winfo_children()[0].winfo_children()[0]

        self._populate_profile_checkboxes()

        # Parameters
        ttk.Label(form, text="Iterations (-n):").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(form, textvariable=self.iterations_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=4)

        ttk.Label(form, text="Generator args (-ag):").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(form, textvariable=self.gen_args_var).grid(row=2, column=1, sticky=tk.EW, pady=4)

        ttk.Label(form, text="Guesser args (-ap):").grid(row=3, column=0, sticky=tk.W, pady=4)
        ttk.Entry(form, textvariable=self.guess_args_var).grid(row=3, column=1, sticky=tk.EW, pady=4)

        ttk.Label(form, text="Source size optionnel (-ns):").grid(row=4, column=0, sticky=tk.W, pady=4)
        ttk.Entry(form, textvariable=self.source_size_var).grid(row=4, column=1, sticky=tk.EW, pady=4)

        form.columnconfigure(1, weight=1)

        # Actions
        actions = ttk.Frame(main_frame)
        actions.pack(fill=tk.X, pady=(10, 8))

        self.run_button = ttk.Button(actions, text="Lancer Batch", command=self.run_project)
        self.run_button.pack(side=tk.LEFT)

        ttk.Button(actions, text="Ouvrir results.csv", command=self.open_results).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Ouvrir archive batch", command=self.open_archive).pack(side=tk.LEFT, padx=0)
        ttk.Button(actions, text="Rafraichir profils", command=self.refresh_profiles).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="voir les statistiques", command=self.view_statistics).pack(side=tk.LEFT, padx=8)

        # Logs
        logs = ttk.LabelFrame(main_frame, text="Logs", padding=8)
        logs.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(logs, wrap=tk.WORD, height=20)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(logs, orient=tk.VERTICAL, command=self.log_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scroll.set)

    def log(self, message: str) -> None:
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def _log_environment(self) -> None:
        self.log(f"Projet: {BASE_DIR}")
        self.log(f"Executable cible: {self.executable}")
        self.log(f"Generators detectes: {', '.join(self.generators) if self.generators else '(aucun)'}")
        self.log(f"Guessers detectes: {', '.join(self.guessers) if self.guessers else '(aucun)'}")

    def refresh_profiles(self) -> None:
        self.generators, self.guessers = find_profiles()
        self.executable = find_executable()
        self.log("Profils rafraichis.")
        self.log(f"Executable cible: {self.executable}")
        self._populate_profile_checkboxes()
        self.log(f"Generators detectes: {len(self.generators)}")
        self.log(f"Guessers detectes: {len(self.guessers)}")

    def validate_inputs(self, selected_gens: list[str], selected_guesses: list[str]) -> bool:
        if not selected_gens:
            messagebox.showerror("Erreur", "Selectionne au moins 1 generateur.")
            return False
        if not selected_guesses:
            messagebox.showerror("Erreur", "Selectionne au moins 1 guesser/predicteur.")
            return False

        try:
            n_value = int(self.iterations_var.get())
            if n_value <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Le nombre d'iterations doit etre un entier > 0.")
            return False

        if self.source_size_var.get().strip():
            try:
                ns_value = int(self.source_size_var.get())
                if ns_value <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erreur", "La source size (-ns) doit etre un entier > 0.")
                return False

        if not self.executable.exists():
            messagebox.showerror(
                "Executable introuvable",
                "Aucun binaire trouve dans output/. Compile d'abord le projet via CMake.",
            )
            return False

        return True

    def build_command(self, generator: str, guesser: str) -> list[str]:
        cmd: list[str] = [
            str(self.executable),
            "-g",
            generator,
            "-p",
            guesser,
            "-n",
            self.iterations_var.get().strip(),
        ]

        gen_args = self.gen_args_var.get().strip()
        if gen_args:
            cmd.extend(["-ag", gen_args])

        guess_args = self.guess_args_var.get().strip()
        if guess_args:
            cmd.extend(["-ap", guess_args])

        source_size = self.source_size_var.get().strip()
        if source_size:
            cmd.extend(["-ns", source_size])

        return cmd

    def run_project(self) -> None:
        # Get selections from Checkbuttons
        selected_gens = [gen for gen, var in self.gen_checks.items() if var.get()]
        selected_guesses = [guesser for guesser, var in self.guess_checks.items() if var.get()]

        self.log(f"Generators selectionnes: {selected_gens}")
        self.log(f"Guessers selectionnes: {selected_guesses}")

        if not self.validate_inputs(selected_gens, selected_guesses):
            return

        self.run_button.config(state=tk.DISABLED)

        thread = threading.Thread(
            target=self._run_batch,
            args=(selected_gens, selected_guesses),
            daemon=True,
        )
        thread.start()

    def _run_batch(self, generators: list[str], guessers: list[str]) -> None:
        self.root.after(0, lambda: self.log("=" * 80))
        self.root.after(0, lambda: self.log(f"Batch: {len(generators)} generator(s) x {len(guessers)} guesser(s) = {len(generators) * len(guessers)} run(s)"))

        # Create archive directory
        RESULTS_ARCHIVE.mkdir(exist_ok=True)
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = RESULTS_ARCHIVE / batch_id
        batch_dir.mkdir(exist_ok=True)

        summary_file = batch_dir / "SUMMARY.txt"
        summary_lines = [f"Batch Results: {batch_id}\n", f"Total combinations: {len(generators)} x {len(guessers)}\n", "=" * 80 + "\n"]

        combo_count = 0
        for gen in generators:
            for guesser in guessers:
                combo_count += 1
                self.root.after(
                    0,
                    lambda g=gen, gs=guesser, cn=combo_count, total=len(generators) * len(guessers):
                        self.log(f"\n[{cn}/{total}] Lancement: {g} + {gs}")
                )

                cmd = self.build_command(gen, guesser)
                self.root.after(0, lambda c=cmd: self.log("Commande: " + " ".join(c)))

                try:
                    battle_start = time.perf_counter()
                    process = subprocess.run(
                        cmd,
                        cwd=BASE_DIR,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    battle_duration = time.perf_counter() - battle_start

                    code = process.returncode

                    self.root.after(0, lambda c=code, d=battle_duration: self.log(f"Code retour: {c} | Temps total: {d:.6f}s"))

                    # Write to combat times file
                    combat_times_file = batch_dir / "combat_times.csv"
                    with open(combat_times_file, "a", encoding="utf-8") as f:
                        f.write(f"{battle_duration:.6f};{gen};{guesser};{batch_id}\n")

                    # Copy results
                    results_file = OUTPUT_DIR / "results.csv"
                    if results_file.exists():
                        dest = batch_dir / f"results_{gen}_vs_{guesser}.csv"
                        results_content = results_file.read_text(encoding="utf-8", errors="ignore")
                        dest.write_text(results_content, encoding="utf-8")

                        # Parse ratio from results
                        lines = results_content.splitlines()
                        if len(lines) > 2:
                            ratio_line = lines[2]
                            summary_lines.append(f"{gen} vs {guesser}: ratio = {ratio_line}\n")

                        self.root.after(0, lambda r=results_content: self._display_results_preview(r))

                except Exception as exc:  # noqa: BLE001
                    msg = f"Erreur Python: {exc}"
                    self.root.after(0, lambda m=msg: self.log(m))
                    summary_lines.append(f"{gen} vs {guesser}: ERREUR - {exc}\n")

        summary_lines.append("\n" + "=" * 80 + "\n")
        summary_lines.append(f"Batch termine: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        summary_file.write_text("".join(summary_lines), encoding="utf-8")

        self.root.after(0, lambda: self.log(f"\n{'=' * 80}"))
        self.root.after(0, lambda: self.log(f"Batch complete ! Resultats archives dans: {batch_dir}"))
        self.root.after(0, lambda: self.log(f"Resume: {summary_file}"))
        self.run_button.config(state=tk.NORMAL)

    def _display_results_preview(self, results_content: str) -> None:
        preview = results_content.splitlines()[:4]
        if preview:
            self.log("Apercu results.csv:")
            for line in preview:
                self.log(line)

    def open_results(self) -> None:
        results_file = OUTPUT_DIR / "results.csv"
        if not results_file.exists():
            messagebox.showwarning("Info", "results.csv introuvable pour l'instant.")
            return

        try:
            subprocess.Popen(["notepad.exe", str(results_file)])
        except OSError as exc:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir results.csv: {exc}")

    def open_archive(self) -> None:
        if not RESULTS_ARCHIVE.exists():
            messagebox.showinfo("Info", "Pas d'archives batch pour l'instant.")
            return

        try:
            subprocess.Popen(["explorer.exe", str(RESULTS_ARCHIVE)])
        except OSError as exc:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir archive: {exc}")

    def view_statistics(self) -> None:
        workspace_root = BASE_DIR.parent
        stats_interface = workspace_root / "Visual" / "InterfaceView.py"

        try:
            if getattr(sys, "frozen", False):
                # In frozen mode, sys.executable is this launcher exe. Running it with a .py argument
                # relaunches the launcher, so prefer the dedicated stats exe.
                stats_exe_candidates = [
                    workspace_root / "Visual" / "exe" / "BatchResultsViewer.exe",
                    workspace_root / "Visual" / "dist" / "BatchResultsViewer.exe",
                    workspace_root / "Visual" / "BatchResultsViewer.exe",
                ]
                stats_exe = next((path for path in stats_exe_candidates if path.exists()), None)
                if stats_exe is None:
                    messagebox.showerror(
                        "Erreur",
                        "Executable statistiques introuvable.\n"
                        "Compile d'abord Visual/InterfaceView.py en BatchResultsViewer.exe.",
                    )
                    return
                subprocess.Popen([str(stats_exe)], cwd=str(stats_exe.parent))
                return

            if not stats_interface.exists():
                messagebox.showerror("Erreur", f"Fichier d'interface de statistiques introuvable: {stats_interface}")
                return

            subprocess.Popen([sys.executable, str(stats_interface)], cwd=str(stats_interface.parent))
        except OSError as exc:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir l'interface de statistiques: {exc}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherUI(root)
    root.mainloop()
