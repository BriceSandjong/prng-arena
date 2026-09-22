from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


def _ensure_view_import() -> None:
	"""Ensure View module is importable from the Visual directory."""
	visual_dir = Path(__file__).resolve().parent
	if str(visual_dir) not in sys.path:
		sys.path.insert(0, str(visual_dir))


_ensure_view_import()

from View import parse_result_file, plot_accuracy_curves  # noqa: E402


def _find_batch_root() -> Path:
	"""
	Search for batch_results folder intelligently:
	1. From current working directory and parents
	2. In known relative paths from script/exe location
	3. Default to working directory if not found
	"""
	# Strategy 1: Search from cwd upward
	cwd = Path.cwd()
	current = cwd
	for _ in range(10):  # Go up max 10 levels
		for pattern in ["batch_results", "hackintator-main/batch_results"]:
			candidate = current / pattern
			if candidate.exists() and candidate.is_dir():
				return candidate
		if current.parent == current:  # Reached filesystem root
			break
		current = current.parent

	# Strategy 2: Try from script location
	try:
		script_dir = Path(__file__).resolve().parent
		for pattern in ["batch_results", "../batch_results", "../../batch_results"]:
			candidate = script_dir / pattern
			normalized = candidate.resolve()
			if normalized.exists() and normalized.is_dir():
				return normalized
	except Exception:
		pass

	# Strategy 3: Return cwd as fallback (user can navigate)
	return cwd / "batch_results"


def _list_batch_folders(batch_root: Path) -> list[Path]:
	if not batch_root.exists():
		return []
	return sorted([path for path in batch_root.iterdir() if path.is_dir()], reverse=True)


def _list_csv_files(folder: Path) -> list[Path]:
	return sorted(folder.glob("results_*_vs_*.csv"))


class BatchResultsInterface:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("Batch Results Viewer")
		self.root.geometry("1100x720")
		self.root.minsize(960, 640)

		self.batch_root = _find_batch_root()
		self.folder_paths: list[Path] = []
		self.selected_folder: Path | None = None
		self.csv_vars: dict[Path, tk.BooleanVar] = {}
		self.last_png_path: Path | None = None

		self._build_ui()
		self.refresh_folders()

	def _build_ui(self) -> None:
		style = ttk.Style()
		try:
			style.theme_use("clam")
		except tk.TclError:
			pass

		main = ttk.Frame(self.root, padding=12)
		main.pack(fill=tk.BOTH, expand=True)
		main.pack(fill=tk.BOTH, expand=True)

		top = ttk.Frame(main, style="Card.TFrame")
		top.pack(fill=tk.X, pady=(0, 14))

		title_label = ttk.Label(top, text="Batch Results Viewer", style="Title.TLabel")
		title_label.pack(side=tk.LEFT, anchor=tk.W)

		self.root_label = tk.StringVar(value=f"Dossier racine: {self.batch_root}")
		self.status_label = tk.StringVar(value="Selectionne un dossier batch pour afficher ses CSV.")

		ttk.Label(top, textvariable=self.root_label, style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(16, 0))
		ttk.Button(top, text="Choisir batch_results...", command=self.choose_batch_root, style="Accent.TButton").pack(side=tk.RIGHT)

		content = ttk.Panedwindow(main, orient=tk.HORIZONTAL)
		content.pack(fill=tk.BOTH, expand=True)

		left = ttk.Labelframe(content, text="Dossiers batch", padding=8)
		right = ttk.Labelframe(content, text="CSV a inclure", padding=8)
		content.add(left, weight=1)
		content.add(right, weight=3)

		self.folder_list = tk.Listbox(left, activestyle="none", exportselection=False, height=18)
		folder_scroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.folder_list.yview)
		self.folder_list.configure(yscrollcommand=folder_scroll.set)
		self.folder_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
		folder_scroll.pack(side=tk.RIGHT, fill=tk.Y)
		self.folder_list.bind("<<ListboxSelect>>", self.on_folder_selected)

		folder_actions = ttk.Frame(left)
		folder_actions.pack(fill=tk.X, pady=(10, 0))
		ttk.Button(folder_actions, text="Rafraichir", command=self.refresh_folders).pack(fill=tk.X)

		self.csv_summary = tk.StringVar(value="0 fichier selectionne")
		ttk.Label(right, textvariable=self.csv_summary).pack(anchor=tk.W)

		checkbox_actions = ttk.Frame(right)
		checkbox_actions.pack(fill=tk.X, pady=(8, 8))
		ttk.Button(checkbox_actions, text="Tout cocher", command=self.select_all_csv).pack(side=tk.LEFT)
		ttk.Button(checkbox_actions, text="Tout decocher", command=self.clear_all_csv).pack(side=tk.LEFT, padx=8)
		self.open_png_button = ttk.Button(checkbox_actions, text="Ouvrir dernier PNG", command=self.open_last_png, state=tk.DISABLED)
		self.open_png_button.pack(side=tk.RIGHT, padx=8)
		ttk.Button(checkbox_actions, text="Generer PNG...", command=self.generate_png).pack(side=tk.RIGHT)

		self.csv_canvas = tk.Canvas(right, highlightthickness=0)
		csv_scroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.csv_canvas.yview)
		self.csv_canvas.configure(yscrollcommand=csv_scroll.set)
		csv_scroll.pack(side=tk.RIGHT, fill=tk.Y)
		self.csv_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.csv_frame = ttk.Frame(self.csv_canvas)
		self.csv_window = self.csv_canvas.create_window((0, 0), window=self.csv_frame, anchor="nw")
		self.csv_frame.bind("<Configure>", self._on_csv_frame_configure)
		self.csv_canvas.bind("<Configure>", self._on_csv_canvas_configure)

		stats_frame = ttk.LabelFrame(right, text="Statistiques", padding=8)
		stats_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 8))
		self.stats_text = tk.Text(stats_frame, height=25, wrap=tk.WORD, state=tk.DISABLED, background=self.root.cget("bg"))
		self.stats_text.pack(fill=tk.BOTH, expand=True)

		bottom = ttk.LabelFrame(main, text="Statut", padding=8)
		bottom.pack(fill=tk.X, pady=(10, 0))
		ttk.Label(bottom, textvariable=self.status_label).pack(anchor=tk.W)

	def _on_csv_frame_configure(self, _event: tk.Event[tk.Misc]) -> None:
		self.csv_canvas.configure(scrollregion=self.csv_canvas.bbox("all"))

	def _on_csv_canvas_configure(self, event: tk.Event[tk.Misc]) -> None:
		self.csv_canvas.itemconfigure(self.csv_window, width=event.width)

	def set_status(self, message: str) -> None:
		self.status_label.set(message)
		self.root.update_idletasks()

	def open_last_png(self) -> None:
		if self.last_png_path is None or not self.last_png_path.exists():
			messagebox.showwarning("PNG introuvable", "Aucun PNG genere ou le fichier est introuvable.")
			return

		try:
			if sys.platform.startswith("win"):
				os.startfile(self.last_png_path)
			elif sys.platform.startswith("darwin"):
				subprocess.run(["open", str(self.last_png_path)], check=False)
			else:
				subprocess.run(["xdg-open", str(self.last_png_path)], check=False)
		except Exception as exc:
			messagebox.showerror("Erreur ouverture PNG", str(exc))

	def _set_stats_text(self, text: str) -> None:
		self.stats_text.configure(state=tk.NORMAL)
		self.stats_text.delete("1.0", tk.END)
		self.stats_text.insert(tk.END, text)
		self.stats_text.configure(state=tk.DISABLED)

	def _update_stats_display(self) -> None:
		selected_csvs = self._get_selected_csvs()
		if not selected_csvs:
			self._set_stats_text("Aucun CSV selectionne.")
			return

		curves: list[dict[str, object]] = []
		for csv_path in selected_csvs:
			try:
				curve = parse_result_file(csv_path)
				curve["csv_name"] = csv_path.name
				curves.append(curve)
			except Exception as exc:  # noqa: BLE001
				self._set_stats_text(f"Erreur lecture {csv_path.name}: {exc}")
				return

		text = self._build_stats_text(curves)
		self._set_stats_text(text)

	def _build_stats_text(self, curves: list[dict[str, object]]) -> str:
		if not curves:
			return "Aucune statistique disponible."

		def _format_seconds(value: float | None) -> str:
			if value is None:
				return "N/A"
			return f"{value:.6f} s"

		def _format_percent(value: float | None) -> str:
			if value is None:
				return "N/A"
			return f"{value:.2f}%"

		def _format_kb(value: float | None) -> str:
			if value is None:
				return "N/A"
			return f"{value:.0f} kB"

		total_good = sum(int(curve["good"]) for curve in curves)
		total_items = sum(int(curve["total"]) for curve in curves)
		overall_accuracy = (total_good / total_items) * 100.0 if total_items else 0.0
		overall_error = 100.0 - overall_accuracy
		best_good_streak = max(int(curve["max_good_streak"]) for curve in curves)
		best_error_streak = max(int(curve["max_error_streak"]) for curve in curves)

		execution_times = [float(curve["execution_time"]) for curve in curves if curve.get("execution_time") is not None]
		average_execution_time = sum(execution_times) / len(execution_times) if execution_times else None

		total_combat_times = [float(curve["total_combat_time"]) for curve in curves if curve.get("total_combat_time") is not None]
		total_total_combat_time = sum(total_combat_times) if total_combat_times else None

		cpu_values = [float(curve["cpu_usage"]) for curve in curves if curve.get("cpu_usage") is not None]
		average_cpu_usage = sum(cpu_values) / len(cpu_values) if cpu_values else None

		memory_values = [float(curve["memory_usage"]) for curve in curves if curve.get("memory_usage") is not None]
		average_memory_usage = sum(memory_values) / len(memory_values) if memory_values else None

		predictor_groups: dict[str, list[dict[str, object]]] = {}
		for curve in curves:
			predictor = str(curve["predictor_name"])
			predictor_groups.setdefault(predictor, []).append(curve)

		ranking_lines: list[str] = []
		predictor_rankings = sorted(
			predictor_groups.items(),
			key=lambda item: sum(float(curve["accuracy"]) for curve in item[1]) / len(item[1]),
			reverse=True,
		)
		for index, (predictor, curve_list) in enumerate(predictor_rankings, start=1):
			avg_accuracy = sum(float(curve["accuracy"]) for curve in curve_list) / len(curve_list)
			ranking_lines.append(f"{index}. {predictor}: {avg_accuracy:.2f}%")

		best_predictors_lines: list[str] = []
		generator_groups: dict[str, list[dict[str, object]]] = {}
		for curve in curves:
			generator = str(curve["generator_name"])
			generator_groups.setdefault(generator, []).append(curve)

		for generator, curve_list in generator_groups.items():
			pred_scores: dict[str, list[float]] = {}
			for curve in curve_list:
				predictor = str(curve["predictor_name"])
				pred_scores.setdefault(predictor, []).append(float(curve["accuracy"]))
			best_predictor, scores = max(pred_scores.items(), key=lambda item: sum(item[1]) / len(item[1]))
			best_score = sum(scores) / len(scores)
			best_predictors_lines.append(f"{generator}: {best_predictor} ({best_score:.2f}%)")

		lines = [
			f"Fichiers selectionnes: {len(curves)}",
			f"Taux de reussite moyen: {overall_accuracy:.2f}%",
			f"Erreur moyenne: {overall_error:.2f}%",
			f"Temps d'execution moyen: {_format_seconds(average_execution_time)}",
			f"Temps total des combats: {_format_seconds(total_total_combat_time)}",
			f"CPU moyen utilise: {_format_percent(average_cpu_usage)}",
			f"Cout memoire moyen: {_format_kb(average_memory_usage)}",
			"",
			"Classement des predicteurs:",
		] + [f"  {line}" for line in ranking_lines] + ["", "Meilleur predicteur par generateur:"] + [f"  {line}" for line in best_predictors_lines] + ["", "Statistiques par combat:"]

		for curve in curves:
			accuracy = float(curve["accuracy"])
			error_percent = float(curve["error_percent"])
			cpu_usage = float(curve["cpu_usage"]) if curve.get("cpu_usage") is not None else None
			memory_usage = float(curve["memory_usage"]) if curve.get("memory_usage") is not None else None
			lines.extend([
				f"  {curve.get('csv_name', '<inconnu>')}",
				f"    Generateur: {curve['generator_name']}",
				f"    Predicteur: {curve['predictor_name']}",
				f"    Reussite: {accuracy:.2f}%",
				f"    Erreur: {error_percent:.2f}%",
				f"    Bonnes predictions: {curve['good']} / {curve['total']}",
				f"    Serie max bonnes: {curve['max_good_streak']}",
				f"    Serie max erreurs: {curve['max_error_streak']}",
				f"    Temps d'execution: {_format_seconds(curve.get('execution_time'))}",
				f"    Temps total du combat: {_format_seconds(curve.get('total_combat_time'))}",
				f"    CPU utilise: {_format_percent(cpu_usage)}",
				f"    Cout memoire: {_format_kb(memory_usage)}",
				"",
			])

		return "\n".join(lines)

	def choose_batch_root(self) -> None:
		chosen = filedialog.askdirectory(initialdir=str(self.batch_root), title="Choisir le dossier batch_results")
		if not chosen:
			return
		self.batch_root = Path(chosen)
		self.root_label.set(f"Dossier racine: {self.batch_root}")
		self.refresh_folders()

	def refresh_folders(self) -> None:
		self.folder_paths = _list_batch_folders(self.batch_root)
		self.folder_list.delete(0, tk.END)

		for folder in self.folder_paths:
			self.folder_list.insert(tk.END, folder.name)

		if self.folder_paths:
			self.folder_list.selection_set(0)
			self.folder_list.event_generate("<<ListboxSelect>>")
		else:
			self.selected_folder = None
			self._render_csv_checkboxes([])
			self.csv_summary.set("0 fichier selectionne")
			self._set_stats_text("Aucun CSV selectionne.")
			self.set_status("Aucun dossier batch trouve.")

	def on_folder_selected(self, _event: tk.Event[tk.Misc]) -> None:
		selection = self.folder_list.curselection()
		if not selection:
			return

		index = selection[0]
		if index >= len(self.folder_paths):
			return

		self.selected_folder = self.folder_paths[index]
		csv_files = _list_csv_files(self.selected_folder)
		self._render_csv_checkboxes(csv_files)
		self._update_stats_display()
		self.set_status(f"Dossier selectionne: {self.selected_folder.name} ({len(csv_files)} CSV)")

	def _render_csv_checkboxes(self, csv_files: list[Path]) -> None:
		for widget in self.csv_frame.winfo_children():
			widget.destroy()

		self.csv_vars = {}

		if not csv_files:
			ttk.Label(self.csv_frame, text="Aucun CSV trouve dans ce dossier.").pack(anchor=tk.W, pady=4)
			self.csv_summary.set("0 fichier selectionne")
			self._set_stats_text("Aucun CSV selectionne.")
			return

		for csv_path in csv_files:
			var = tk.BooleanVar(value=True)
			self.csv_vars[csv_path] = var
			ttk.Checkbutton(
				self.csv_frame,
				text=csv_path.name,
				variable=var,
				command=self._update_csv_summary,
			).pack(anchor=tk.W, pady=2)

		self._update_csv_summary()

	def _update_csv_summary(self) -> None:
		selected = sum(1 for var in self.csv_vars.values() if var.get())
		total = len(self.csv_vars)
		self.csv_summary.set(f"{selected}/{total} fichier(s) selectionne(s)")
		self._update_stats_display()

	def select_all_csv(self) -> None:
		for var in self.csv_vars.values():
			var.set(True)
		self._update_csv_summary()

	def clear_all_csv(self) -> None:
		for var in self.csv_vars.values():
			var.set(False)
		self._update_csv_summary()

	def _get_selected_csvs(self) -> list[Path]:
		return [csv_path for csv_path, var in self.csv_vars.items() if var.get()]

	def generate_png(self) -> None:
		if self.selected_folder is None:
			messagebox.showwarning("Selection requise", "Selectionne d'abord un dossier batch.")
			return

		selected_csvs = self._get_selected_csvs()
		if not selected_csvs:
			messagebox.showwarning("Selection requise", "Coche au moins un CSV.")
			return

		curves: list[dict[str, object]] = []
		for csv_path in selected_csvs:
			try:
				curves.append(parse_result_file(csv_path))
			except Exception as exc:  # noqa: BLE001
				messagebox.showerror("Erreur CSV", f"Impossible de lire {csv_path.name}: {exc}")
				return

		graphs_dir = self.selected_folder / "graphs"
		graphs_dir.mkdir(exist_ok=True)
		default_name = f"{self.selected_folder.name}_selection.png"
		save_path = filedialog.asksaveasfilename(
			title="Enregistrer le PNG",
			initialdir=str(graphs_dir),
			initialfile=default_name,
			defaultextension=".png",
			filetypes=[("PNG image", "*.png")],
		)
		if not save_path:
			return

		final_path = Path(save_path)
		try:
			plot_accuracy_curves(curves, save_path=final_path, show_plot=False)
		except ImportError as exc:
			messagebox.showerror("Dependance manquante", str(exc))
			return
		except Exception as exc:  # noqa: BLE001
			messagebox.showerror("Erreur", f"Impossible de generer le PNG: {exc}")
			return

		self.last_png_path = final_path
		self.open_png_button.configure(state=tk.NORMAL)
		self.set_status(f"PNG genere: {final_path}")
		messagebox.showinfo("Succes", f"PNG genere avec succes:\n{final_path}")


def main() -> None:
	root = tk.Tk()
	BatchResultsInterface(root)
	root.mainloop()


if __name__ == "__main__":
	main()
