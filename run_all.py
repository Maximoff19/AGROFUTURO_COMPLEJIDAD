#!/usr/bin/env python3
"""
Bootstrap y ejecución cross-platform (Windows/macOS/Linux) para AgroFuturo.
Uso:
  python run_all.py --setup          # instala deps, verifica datasets, sanity
  python run_all.py                  # levanta backend en http://localhost:8000
  python run_all.py --frontend       # sirve frontend en http://localhost:8080
Flags:
  --port PORT             Puerto backend (default 8000 o $PORT)
  --frontend-port PORT    Puerto frontend (default 8080 o $FRONTEND_PORT)
"""

import argparse
import compileall
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
REQ_FILE = ROOT / "backend" / "requirements.txt"
CLIMATE_CSV = ROOT / "IGP_EstacionEMA_2018-2024_Dataset.xlsx - Worksheet.csv"
SOIL_CSV = ROOT / "soil_huancayo_sintetico_50kv.2.xlsx - Sheet1.csv"


def venv_python() -> Path:
    if os.name == "nt":
        cand = VENV / "Scripts" / "python.exe"
    else:
        cand = VENV / "bin" / "python"
    return cand


def ensure_venv() -> Path:
    py_bin = sys.executable
    if not VENV.exists():
        subprocess.run([py_bin, "-m", "venv", str(VENV)], check=True)
    vp = venv_python()
    if not vp.exists():
        raise RuntimeError(f"No se encontró el python del venv en {vp}")
    subprocess.run([str(vp), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(vp), "-m", "pip", "install", "-r", str(REQ_FILE)], check=True)
    return vp


def sanity(vp: Path) -> None:
    compileall.compile_dir(str(ROOT / "backend"), quiet=1)
    code = """
from backend.data_loader import load_climate, load_soil
from backend.graph import build_zone_graph
climate_df, _ = load_climate()
_, soil_grouped, _ = load_soil()
graph = build_zone_graph(soil_grouped)
print(f"Sanity OK: clima={len(climate_df)} filas, distritos_suelo={len(graph.nodes)}")
"""
    subprocess.run([str(vp), "-c", code], check=True)
    missing = []
    if not CLIMATE_CSV.exists():
        missing.append(f"Falta dataset de clima: {CLIMATE_CSV}")
    if not SOIL_CSV.exists():
        missing.append(f"Falta dataset de suelo: {SOIL_CSV}")
    if missing:
        print("\n".join(missing), file=sys.stderr)
    else:
        print("Datasets presentes.")


def run_backend(vp: Path, port: int) -> None:
    print(f"Backend en http://localhost:{port} (docs en /docs)")
    subprocess.run([str(vp), "-m", "uvicorn", "backend.main:app", "--reload", "--port", str(port)], check=True)


def run_frontend(vp: Path, port: int) -> None:
    print(f"Frontend en http://localhost:{port}")
    subprocess.run([str(vp), "-m", "http.server", str(port), "--directory", str(ROOT / "FRONTEND")], check=True)


def parse_args():
    parser = argparse.ArgumentParser(description="AgroFuturo bootstrap")
    parser.add_argument("--setup", action="store_true", help="Instala deps y corre sanity")
    parser.add_argument("--frontend", action="store_true", help="Sirve el frontend en vez de backend")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="Puerto backend")
    parser.add_argument(
        "--frontend-port", type=int, default=int(os.environ.get("FRONTEND_PORT", 8080)), help="Puerto frontend"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    vp = ensure_venv()
    if args.setup:
        sanity(vp)
        print("\nListo. Para backend: python run_all.py | frontend: python run_all.py --frontend")
        return
    if args.frontend:
        run_frontend(vp, args.frontend_port)
    else:
        run_backend(vp, args.port)


if __name__ == "__main__":
    main()
