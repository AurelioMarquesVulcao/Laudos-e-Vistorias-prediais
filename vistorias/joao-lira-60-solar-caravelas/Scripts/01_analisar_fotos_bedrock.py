#!/usr/bin/env python3
"""
Analisa fotos da vistoria predial em lotes via AWS Bedrock (Claude com visão).
Redimensiona imagens grandes para caber no limite da API.
"""
import boto3, json, os, glob, time, io, sys
sys.stdout.reconfigure(line_buffering=True)

try:
    from PIL import Image
except ImportError:
    os.system("pip3 install Pillow -q")
    from PIL import Image

# Config
FOTO_DIR = os.path.dirname(os.path.abspath(__file__)) + "/Fotos JPEG"
OUTPUT_FILE = os.path.dirname(os.path.abspath(__file__)) + "/Analise Fotográfica Completa.md"
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
BATCH_SIZE = 5
MAX_IMAGE_BYTES = 3_400_000  # 3.4MB limite seguro
MAX_DIMENSION = 1568  # max recomendado pelo Claude para visão

session = boto3.Session(
    aws_access_key_id     = os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1",
)
client = session.client("bedrock-runtime", region_name="us-east-1")

SYSTEM_PROMPT = """Você é um engenheiro civil especialista em inspeção predial e autovistoria (NBR 16747:2020).
Analise as imagens de uma vistoria predial no Edifício Solar Caravelas (Rua João Lira, 60 - Leblon/RJ).
Edificação residencial multifamiliar com mais de 50 anos, fachada em mármore, a menos de 500m do mar.

Para CADA imagem, forneça:
1. Sistema inspecionado (estrutura/fachada/elétrica/gás/elevador/incêndio/rotas de fuga)
2. Anomalias visíveis (lista objetiva)
3. Prioridade: 🔴 P1-CRÍTICO | 🟠 P2-REGULAR | 🟡 P3-MÍNIMO
4. Normas violadas

Seja técnico e conciso. Use o nome do arquivo como referência."""


def resize_image(path):
    """Redimensiona imagem para caber no limite da API. Retorna bytes JPEG."""
    img = Image.open(path)
    # Converter RGBA para RGB se necessário
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Redimensionar se maior que MAX_DIMENSION
    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    
    # Comprimir para JPEG com qualidade decrescente até caber
    for quality in (75, 60, 45, 30):
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality)
        if buf.tell() <= MAX_IMAGE_BYTES:
            return buf.getvalue()
    
    # Último recurso: reduzir mais
    w, h = img.size
    img = img.resize((w // 2, h // 2), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=50)
    return buf.getvalue()


def analyze_batch(image_paths):
    """Envia lote de imagens para Claude via Bedrock Converse API."""
    content = []
    included = []
    for p in image_paths:
        try:
            data = resize_image(p)
            content.append({"image": {"format": "jpeg", "source": {"bytes": data}}})
            content.append({"text": f"[{os.path.basename(p)}]"})
            included.append(os.path.basename(p))
        except Exception as e:
            print(f"    ⚠️ Erro ao processar {os.path.basename(p)}: {e}")
    
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
    fotos = sorted(glob.glob(FOTO_DIR + "/*.jpg") + glob.glob(FOTO_DIR + "/*.jpeg"))
    fotos = [f for f in fotos if ".DS_Store" not in f]
    
    print(f"Total de fotos: {len(fotos)}")
    batches = [fotos[i:i+BATCH_SIZE] for i in range(0, len(fotos), BATCH_SIZE)]
    print(f"Lotes: {len(batches)}")
    
    results = []
    results.append("# Análise Fotográfica Completa — Vistoria Predial\n")
    results.append("## Edifício Solar Caravelas — Rua João Lira, 60 — Leblon/RJ\n")
    results.append(f"**Total:** {len(fotos)} imagens | **Lotes:** {len(batches)}\n")
    results.append("---\n")
    
    for i, batch in enumerate(batches):
        print(f"\n[{i+1}/{len(batches)}] {len(batch)} imgs...")
        
        try:
            analysis = analyze_batch(batch)
            results.append(f"\n## Lote {i+1}\n")
            results.append(analysis)
            results.append("\n---\n")
            print(f"  ✅ OK")
        except Exception as e:
            results.append(f"\n## Lote {i+1} — ERRO: `{str(e)[:100]}`\n---\n")
            print(f"  ❌ {str(e)[:80]}")
        
        # Salvar progresso a cada lote
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        
        if i < len(batches) - 1:
            time.sleep(2)
    
    print(f"\n✅ Concluído: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
