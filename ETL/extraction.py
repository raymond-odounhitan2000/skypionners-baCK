import xarray as xr
import pandas as pd
import os
from glob import glob
import argparse
import logging
from pathlib import Path



logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def main(input_dir: str = "merra2_data", output_dir: str = "data/csv", pattern: str = "*.nc4"):
    """Lire tous les fichiers netCDF (.nc4) du répertoire d'entrée et les concaténer en un CSV.

    Le script écrit en mode 'append' pour éviter d'accumuler tous les DataFrame en mémoire.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Candidate directories to look for data (helps when script is run from different cwd)
    candidates = [Path(input_dir), Path.cwd() / input_dir,
                  Path(__file__).resolve().parent.parent / input_dir]

    files = []
    tried = []
    for cand in candidates:
        tried.append(str(cand))
        if cand.exists():
            found = sorted(cand.glob(pattern))
            if found:
                files = found
                logging.info("Using input directory: %s", cand)
                break

    logging.info("Tried candidate directories: %s", ", ".join(tried))
    logging.info("Nombre de fichiers trouvés : %d", len(files))
    if not files:
        logging.warning("Aucun fichier trouvé dans les emplacements essayés avec le pattern %s", pattern)
        return

    out_file = output_path / "tempo_merra2_all.csv"
    first_write = True

    i = 0

    for file_path in files:
        if i == 0:
         i=1
         logging.info("Lecture de %s", file_path)
         try:
             # Use context manager to ensure file handles are closed promptly
             with xr.open_dataset(file_path) as ds:
                 df = ds.to_dataframe().reset_index()

             # Append to CSV to avoid keeping everything in memory
             df.to_csv(out_file, mode="w" if first_write else "a", header=first_write, index=False)
             first_write = False
             # free memory
             del df

         except Exception as e:
             logging.exception("Erreur en traitant %s : %s", file_path, e)
        else:
            break

    logging.info("✅ Fichier fusionné sauvegardé : %s", out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge netCDF (.nc4) files into a single CSV")
    parser.add_argument("--input", default="merra2_data", help="Input directory containing .nc4 files")
    parser.add_argument("--output", default="data/csv", help="Output directory for CSV")
    parser.add_argument("--pattern", default="*.nc4", help="Glob pattern to match files")
    args = parser.parse_args()
    main(args.input, args.output, args.pattern)
