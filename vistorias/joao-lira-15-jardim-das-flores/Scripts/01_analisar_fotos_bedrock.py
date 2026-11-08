#!/usr/bin/env python3
"""
ETAPA 1 — Análise fotográfica via AWS Bedrock (Claude com visão)
Condomínio Jardim das Flores — Rua João Lira, 15 — Leblon/RJ

Processa as 210 fotos em lotes de 5, gera Analise_Fotografica_Completa.md
"""
import boto3, json, os, glob, time, io, sys
sys.stdout.reconfigure(line_buffering=True)

try:
    from PIL import Image
except ImportError:
    os.system("pip3 install Pillow -q")
    from PIL import Image

# ── Config ──────────────────────────────────────────────────────────────────
BASE       = os.path.dirname(os.path.abspath(__file__))
RAIZ       = os.path.abspath(os.path.join(BASE, ".."))
FOTO_DIR   = os.path.join(RAIZ, "Fotos_Organizadas")
OUTPUT_MD  = os.path.join(RAIZ, "Laudo", "Analise_Fotografica_Completa.md")
MODEL_ID   = "us.anthropic.claude-sonnet-4-6-20260830-v1:0"
BATCH_SIZE = 5
MAX_IMAGE_BYTES = 3_400_000
MAX_DIMENSION   = 1568

# ── Credenciais AWS ──────────────────────────────────────────────────────────
# ATENÇÃO: substitua pelas credenciais corretas antes de rodar,
# ou configure via ~/.aws/credentials / variáveis de ambiente.
session = boto3.Session(
    aws_access_key_id     = os.environ.get("AWS_ACCESS_KEY_ID", "COLE_AQUI"),
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "COLE_AQUI"),
    region_name           = "us-east-1",
)
client = session.client("bedrock-runtime", region_name="us-east-1")

# ── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Você é um engenheiro civil especialista em inspeção predial e autovistoria (NBR 16747:2020).
Analise as imagens de uma vistoria predial no Condomínio Jardim das Flores (Rua João Lira, 15 — Leblon/RJ).
Edificação residencial multifamiliar. Leblon, próximo à orla (atmosfera marinha — classe de agressividade III/IV conforme NBR 6118).
Não há laudo anterior disponível para comparação.

Para CADA imagem, forneça:
1. Sistema inspecionado (estrutura/fachada/elétrica/gás/elevador/incêndio/rotas de fuga/cobertura/garagem/área comum)
2. Anomalias visíveis (lista objetiva, sem inventar o que não aparece)
3. Prioridade: 🔴 P1-CRÍTICO | 🟠 P2-REGULAR | 🟡 P3-MÍNIMO | ⚪ INDETERMINADO
4. Normas de referência pertinentes
5. Recomendação objetiva

Seja técnico e conciso. Use o nome do arquivo como referência. Se a imagem não mostrar anomalia, registre "Sem anomalias visíveis"."""


def resize_image(path):
    img = Image.open(path)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    for quality in (75, 60, 45, 30):
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality)
        if buf.tell() <= MAX_IMAGE_BYTES:
            return buf.getvalue()
    w, h = img.size
    img = img.resize((w // 2, h // 2), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=50)
    return buf.getvalue()


def analyze_batch(image_paths):
    content = []
    included = []
    for p in image_paths:
        try:
            data = resize_image(p)
            content.append({"image": {"format": "jpeg", "source": {"bytes": data}}})
            content.append({"text": f"[{os.path.basename(p)}]"})
            included.append(os.path.basename(p))
        except Exception as e:
            print(f"    ⚠️  Erro ao processar {os.path.basename(p)}: {e}")
    if not content:
        return "Nenhuma imagem processável neste lote.\n"
    content.append({"text": f"Analise as {len(included)} imagens acima."})
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": content}],
        inferenceConfig={"maxTokens": 4000, "temperature": 0.1},
    )
    return response["output"]["message"]["content"][0]["text"]


def main():
    fotos = sorted(
        glob.glob(FOTO_DIR + "/*.jpg") +
        glob.glob(FOTO_DIR + "/*.jpeg") +
        glob.glob(FOTO_DIR + "/*.JPG") +
        glob.glob(FOTO_DIR + "/*.JPEG")
    )
    fotos = [f for f in fotos if ".DS_Store" not in f]

    if not fotos:
        print(f"⚠️  Nenhuma foto encontrada em: {FOTO_DIR}")
        print("   Execute primeiro: python Scripts/00_preparar_fotos.py")
        return

    print(f"📸 Total de fotos: {len(fotos)}")
    batches = [fotos[i:i+BATCH_SIZE] for i in range(0, len(fotos), BATCH_SIZE)]
    print(f"📦 Lotes: {len(batches)} (×{BATCH_SIZE} fotos)\n")

    results = [
        "# Análise Fotográfica Completa — Vistoria Predial\n",
        "## Condomínio Jardim das Flores — Rua João Lira, 15 — Leblon/RJ\n",
        f"**Total:** {len(fotos)} imagens | **Lotes:** {len(batches)}\n",
        f"**Modelo:** {MODEL_ID}\n",
        "---\n",
    ]

    for i, batch in enumerate(batches):
        print(f"[{i+1}/{len(batches)}] {len(batch)} imgs...", end=" ", flush=True)
        try:
            analysis = analyze_batch(batch)
            results.append(f"\n## Lote {i+1}\n")
            results.append(analysis)
            results.append("\n---\n")
            print("✅")
        except Exception as e:
            results.append(f"\n## Lote {i+1} — ERRO: `{str(e)[:100]}`\n---\n")
            print(f"❌ {str(e)[:80]}")

        # Salvar progresso a cada lote
        with open(OUTPUT_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(results))

        if i < len(batches) - 1:
            time.sleep(2)

    print(f"\n✅ Concluído: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
