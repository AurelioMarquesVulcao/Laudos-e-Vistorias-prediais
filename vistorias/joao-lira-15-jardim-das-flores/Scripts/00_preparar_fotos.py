#!/usr/bin/env python3
"""
ETAPA 0 — Preparar e copiar fotos da pasta original para Fotos_Organizadas/
Converte HEIC/PNG para JPEG, renomeia sequencialmente se necessário,
e gera um índice CSV com nome original → nome final.
"""
import os, glob, shutil, csv
from pathlib import Path

BASE     = os.path.dirname(os.path.abspath(__file__))
RAIZ     = os.path.abspath(os.path.join(BASE, ".."))
SRC_DIR  = os.path.abspath(os.path.join(RAIZ, "..", "Fotos Vistoria"))
DEST_DIR = os.path.join(RAIZ, "Fotos_Organizadas")
INDEX_CSV = os.path.join(RAIZ, "Fotos_Organizadas", "indice_fotos.csv")

os.makedirs(DEST_DIR, exist_ok=True)

# Extensões aceitas
EXTS = {".jpg", ".jpeg", ".png", ".heic", ".JPG", ".JPEG", ".PNG", ".HEIC"}

fotos_src = sorted([
    f for f in Path(SRC_DIR).iterdir()
    if f.suffix in EXTS and f.name != ".DS_Store"
])

print(f"📂 Origem: {SRC_DIR}")
print(f"📸 Fotos encontradas: {len(fotos_src)}")

copiadas = []
erros = []

for foto in fotos_src:
    dest = Path(DEST_DIR) / (foto.stem + ".jpeg")
    try:
        if foto.suffix.lower() in (".heic", ".png"):
            # Converter via sips (macOS nativo)
            os.system(f'sips -s format jpeg "{foto}" --out "{dest}" -s formatOptions 85 > /dev/null 2>&1')
            if dest.exists():
                print(f"  🔄 {foto.name} → {dest.name}")
                copiadas.append((foto.name, dest.name, "convertido"))
            else:
                raise Exception("sips falhou")
        else:
            shutil.copy2(str(foto), str(dest))
            copiadas.append((foto.name, dest.name, "copiado"))
    except Exception as e:
        print(f"  ❌ {foto.name}: {e}")
        erros.append((foto.name, str(e)))

# Gerar índice
with open(INDEX_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["original", "destino", "acao"])
    writer.writerows(copiadas)

print(f"\n✅ {len(copiadas)} fotos prontas em: {DEST_DIR}")
print(f"📋 Índice salvo em: {INDEX_CSV}")
if erros:
    print(f"⚠️  {len(erros)} erros — verifique manualmente")
