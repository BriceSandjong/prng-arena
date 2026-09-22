from __future__ import annotations

import argparse
import re
from pathlib import Path


def _compute_matches(tokens: list[str]) -> tuple[int, int]:
	"""Return (good_predictions, total_predictions) from generator/predictor token pairs."""
	if len(tokens) < 2:
		raise ValueError("Pas assez de valeurs pour comparer générateur et prédicteur.")
	
	if len(tokens) % 2 != 0:
		raise ValueError("Le nombre de valeurs est impair: attendu des paires générateur/prédicteur.")

	good = 0
	total = len(tokens) // 2

	for i in range(0, len(tokens), 2):
		generator_value = tokens[i]
		predictor_value = tokens[i + 1]
		if generator_value == predictor_value:
			good += 1

	return good, total


def _compute_streaks(tokens: list[str]) -> tuple[int, int]:
	"""Return the longest matching and longest error streak in the token pairs."""
	max_good = 0
	max_error = 0
	current_good = 0
	current_error = 0

	for i in range(0, len(tokens), 2):
		generator_value = tokens[i]
		predictor_value = tokens[i + 1]
		if generator_value == predictor_value:
			current_good += 1
			current_error = 0
			max_good = max(max_good, current_good)
		else:
			current_error += 1
			current_good = 0
			max_error = max(max_error, current_error)

	return max_good, max_error


def _extract_values_line(lines: list[str]) -> tuple[str, int]:
	"""Return the line that contains the generator/predictor value stream and its index."""
	for index, line in enumerate(lines):
		if ";" in line and any(char.isdigit() for char in line):
			return line, index
	raise ValueError("Aucune ligne de valeurs ';' trouvée dans le fichier.")


def _extract_execution_metrics(lines: list[str], values_index: int) -> dict[str, float | None]:
	"""Extract ratio, execution time, CPU and memory metrics from lines after the values line."""
	metrics = {
		"ratio": None,
		"execution_time": None,
		"cpu_usage": None,
		"memory_usage": None,
	}

	def _to_float(value: str) -> float | None:
		cleaned = value.strip().replace(";", "").replace(",", ".")
		if not cleaned:
			return None
		try:
			return float(cleaned)
		except ValueError:
			return None

	numeric_values: list[float] = []
	for line in lines[values_index + 1 :]:
		parsed = _to_float(line)
		if parsed is not None:
			numeric_values.append(parsed)

	# Two common formats exist in result files:
	# - [ratio, execution_time, cpu_usage, memory_usage]
	# - [execution_time, cpu_usage, memory_usage]
	if len(numeric_values) >= 4:
		metrics["ratio"] = numeric_values[0]
		metrics["execution_time"] = numeric_values[1]
		metrics["cpu_usage"] = numeric_values[2]
		metrics["memory_usage"] = numeric_values[3]
	elif len(numeric_values) >= 3:
		metrics["execution_time"] = numeric_values[0]
		metrics["cpu_usage"] = numeric_values[1]
		metrics["memory_usage"] = numeric_values[2]
	elif len(numeric_values) >= 1:
		metrics["execution_time"] = numeric_values[0]

	return metrics


def _extract_run_metadata(lines: list[str]) -> tuple[str, str]:
	"""Extract generator and predictor names from command line if present."""
	default_generator = "Generateur"
	default_predictor = "Predicteur"

	for line in lines:
		if " -g " in line and " -p " in line:
			g_match = re.search(r"\s-g\s+([^\s]+)", line)
			p_match = re.search(r"\s-p\s+([^\s]+)", line)
			generator = g_match.group(1) if g_match else default_generator
			predictor = p_match.group(1) if p_match else default_predictor
			return generator, predictor

	return default_generator, default_predictor


def _read_nonempty_lines(csv_path: Path) -> list[str]:
	return [line.strip() for line in csv_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def predictor_accuracy_percent(csv_path: Path) -> float:
	"""Compute predictor success rate (%) by comparing generator/predictor pairs."""
	raw_lines = _read_nonempty_lines(csv_path)
	values_line = _extract_values_line(raw_lines)

	tokens = [token for token in values_line.split(";") if token]
	good, total = _compute_matches(tokens)
	return (good / total) * 100.0


def predictor_counts(csv_path: Path) -> tuple[int, int]:
	"""Return (good_predictions, total_predictions)."""
	raw_lines = _read_nonempty_lines(csv_path)
	values_line = _extract_values_line(raw_lines)
	tokens = [token for token in values_line.split(";") if token]
	return _compute_matches(tokens)


def predictor_accuracy_curve(csv_path: Path) -> tuple[list[int], list[float]]:
	"""Return x/y data for cumulative accuracy percentage over generated values."""
	raw_lines = _read_nonempty_lines(csv_path)
	values_line = _extract_values_line(raw_lines)
	tokens = [token for token in values_line.split(";") if token]

	# Validate token structure via existing checks.
	_compute_matches(tokens)

	x_values: list[int] = []
	y_values: list[float] = []
	good_so_far = 0

	for pair_index, i in enumerate(range(0, len(tokens), 2), start=1):
		if tokens[i] == tokens[i + 1]:
			good_so_far += 1
		x_values.append(pair_index)
		y_values.append((good_so_far / pair_index) * 100.0)

	return x_values, y_values


def parse_result_file(csv_path: Path) -> dict[str, object]:
	"""Parse one result file and return metadata plus curve data and performance metrics."""
	raw_lines = _read_nonempty_lines(csv_path)
	generator_name, predictor_name = _extract_run_metadata(raw_lines)
	values_line, values_index = _extract_values_line(raw_lines)
	tokens = [token for token in values_line.split(";") if token]

	good, total = _compute_matches(tokens)
	accuracy = (good / total) * 100.0 if total else 0.0
	error_percent = 100.0 - accuracy
	max_good_streak, max_error_streak = _compute_streaks(tokens)

	execution_metrics = _extract_execution_metrics(raw_lines, values_index)

	# Read total combat time from combat_times.csv if available
	total_combat_time = None
	combat_times_path = csv_path.parent / "combat_times.csv"
	if combat_times_path.exists():
		try:
			with open(combat_times_path, "r", encoding="utf-8") as f:
				for line in f:
					parts = line.strip().split(";")
					if len(parts) >= 3 and parts[1] == generator_name and parts[2] == predictor_name:
						total_combat_time = float(parts[0])
						break
		except Exception:
			pass  # Ignore errors reading combat times

	x_values: list[int] = []
	y_values: list[float] = []
	good_so_far = 0

	for pair_index, i in enumerate(range(0, len(tokens), 2), start=1):
		if tokens[i] == tokens[i + 1]:
			good_so_far += 1
		x_values.append(pair_index)
		y_values.append((good_so_far / pair_index) * 100.0)

	return {
		"generator_name": generator_name,
		"predictor_name": predictor_name,
		"good": good,
		"total": total,
		"accuracy": accuracy,
		"error_percent": error_percent,
		"max_good_streak": max_good_streak,
		"max_error_streak": max_error_streak,
		"execution_time": execution_metrics["execution_time"],
		"cpu_usage": execution_metrics["cpu_usage"],
		"memory_usage": execution_metrics["memory_usage"],
		"total_combat_time": total_combat_time,
		"x_values": x_values,
		"y_values": y_values,
	}


def _find_results_csv(directory: Path) -> list[Path]:
	"""Find all results_*_vs_*.csv files recursively in a directory."""
	return sorted(directory.rglob("results_*_vs_*.csv"))


def plot_accuracy_curves(curves: list[dict[str, object]], save_path: Path | None = None, show_plot: bool = True) -> None:
	"""Plot one or multiple cumulative accuracy curves with predictor legend."""
	try:
		import matplotlib.pyplot as plt
	except ImportError as exc:
		raise ImportError(
			"matplotlib n'est pas installé. Installez-le avec: pip install matplotlib"
		) from exc

	if not curves:
		raise ValueError("Aucune donnee a tracer.")

	generator_names = {str(curve["generator_name"]) for curve in curves}
	if len(generator_names) == 1:
		title = next(iter(generator_names))
	else:
		title = "Plusieurs generateurs"

	fig, ax = plt.subplots(figsize=(8, 5))
	max_x = 1
	for curve in curves:
		x_values = curve["x_values"]
		y_values = curve["y_values"]
		predictor_name = str(curve["predictor_name"])
		if not x_values:
			continue
		max_x = max(max_x, max(x_values))
		label = f"{predictor_name} ({y_values[-1]:.2f}%)"
		ax.plot(x_values, y_values, linewidth=2, marker="o", markersize=3, label=label)

	ax.set_title(title)
	ax.set_xlabel("Nombre de nombres generes")
	ax.set_ylabel("Pourcentage de bonnes reponses (%)")
	ax.set_xlim(1, max_x)
	ax.set_ylim(0, 100)
	ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.6)
	ax.legend(title="Predicteurs", loc="best")
	fig.tight_layout()

	if save_path is not None:
		save_path.parent.mkdir(parents=True, exist_ok=True)
		fig.savefig(save_path, dpi=150)

	if show_plot:
		plt.show()
	else:
		plt.close(fig)


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Calcule le pourcentage de bonnes reponses du predicteur contre le generateur."
	)
	parser.add_argument(
		"csv_paths",
		nargs="*",
		default=["../hackintator-main/output/results.csv"],
		help="Un ou plusieurs chemins vers results.csv ou repertoires contenant des results.csv.",
	)
	parser.add_argument(
		"--plot",
		action="store_true",
		help="Affiche une courbe matplotlib (%% bonnes reponses vs nombre genere).",
	)
	parser.add_argument(
		"--save",
		default="",
		help="Sauvegarde le graphique dans un fichier image (ex: output/accuracy.png).",
	)
	parser.add_argument(
		"--by-folder",
		action="store_true",
		help="Cree un graphique par dossier (uniquement avec des repertoires).",
	)
	args = parser.parse_args()

	# Expand directories to find all results.csv files
	all_csv_paths: list[Path] = []
	for path_str in args.csv_paths:
		path = Path(path_str).resolve()
		if path.is_dir():
			csv_files = _find_results_csv(path)
			if not csv_files:
				raise FileNotFoundError(f"Aucun fichier results.csv trouve dans: {path}")
			all_csv_paths.extend(csv_files)
		else:
			if not path.exists():
				raise FileNotFoundError(f"Fichier introuvable: {path}")
			all_csv_paths.append(path)

	# Group by parent folder if requested
	if args.by_folder:
		groups: dict[Path, list[Path]] = {}
		for csv_path in all_csv_paths:
			folder = csv_path.parent
			if folder not in groups:
				groups[folder] = []
			groups[folder].append(csv_path)

		for folder, csv_files in sorted(groups.items()):
			print(f"\n=== Dossier: {folder.name} ===")
			curves: list[dict[str, object]] = []
			for csv_path in csv_files:
				try:
					curve = parse_result_file(csv_path)
					curves.append(curve)
					good = int(curve["good"])
					total = int(curve["total"])
					predictor_name = str(curve["predictor_name"])
					accuracy = (good / total) * 100.0 if total else 0.0
					print(f"{predictor_name}: {accuracy:.2f}% ({good}/{total})")
				except Exception as e:
					print(f"Erreur avec {csv_path}: {e}")

			if curves and (args.plot or args.save):
				save_path = None
				if args.save:
					save_dir = Path(args.save).parent
					save_name = f"{folder.name}_{Path(args.save).name}"
					save_path = save_dir / save_name
				plot_accuracy_curves(curves, save_path=save_path, show_plot=args.plot)
				if save_path is not None:
					print(f"Graphique sauvegarde: {save_path}")
	else:
		# Original behavior: all files on same graph
		curves: list[dict[str, object]] = []
		for csv_path in all_csv_paths:
			try:
				curve = parse_result_file(csv_path)
				curves.append(curve)
				good = int(curve["good"])
				total = int(curve["total"])
				predictor_name = str(curve["predictor_name"])
				accuracy = (good / total) * 100.0 if total else 0.0
				print(f"{predictor_name}: {accuracy:.2f}% ({good}/{total})")
			except Exception as e:
				print(f"Erreur avec {csv_path.name}: {e}")


		save_path = Path(args.save).resolve() if args.save else None
		if args.plot or save_path is not None:
			plot_accuracy_curves(curves, save_path=save_path, show_plot=args.plot)
			if save_path is not None:
				print(f"Graphique sauvegarde: {save_path}")



if __name__ == "__main__":
	main()
