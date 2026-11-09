#!/usr/bin/env python3
"""
gerar_laudo_v11.py
──────────────────
V10 — combina estilo do 02_gerar_laudo_docx.py (Tahoma, margens 2.5cm)
com Model-01.1.docx como base e todas as 12 fotos incorporadas.

Fotos: F01–F12 todas inseridas nas seções corretas.
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re, os, io
from PIL import Image

# ─── Caminhos ─────────────────────────────────────────────────────────────────
_SCRIPT   = os.path.abspath(__file__)
_VISTORIA = os.path.dirname(os.path.dirname(_SCRIPT))
_LAUDO_DIR= os.path.join(_VISTORIA, "Laudo")
_ASSETS   = os.path.join(_VISTORIA, "assets")
_FOTOS    = os.path.join(_VISTORIA, "fotos_vistoria")

MODEL_01  = os.path.join(_ASSETS,    "Model-01.1.docx")
LAUDO_MD  = os.path.join(_LAUDO_DIR, "Laudo_Jardim_das_Flores.md")
OUT_V11   = os.path.join(_LAUDO_DIR, "Laudo_Jardim_das_Flores_v11.docx")

FONT_NAME = "Tahoma"
FONT_BODY = Pt(10)
FONT_H1   = Pt(14)
FONT_H2   = Pt(12)
FONT_H3   = Pt(11)
FONT_H4   = Pt(10)

PRETO = RGBColor(0x00, 0x00, 0x00)
AZUL  = RGBColor(0x1F, 0x49, 0x7D)

# ─── Validação ────────────────────────────────────────────────────────────────
for f, label in [(MODEL_01, "Model-01.1.docx"), (LAUDO_MD, "Laudo MD")]:
    if not os.path.exists(f):
        raise FileNotFoundError(f"❌ {label} não encontrado: {f}")

fotos_presentes = [x for x in os.listdir(_FOTOS) if x.lower().endswith(('.jpeg','.jpg','.png'))]
print(f"  Fotos disponíveis: {len(fotos_presentes)}")

# ─── Mapeamento: keyword no título → (arquivo, legenda) ────────────────────────
# Todas as 12 fotos mapeadas
FOTO_MAP = [
    ('FACHADA',                  'F01_fachada.jpeg',      'Fachada — pedras sem fixação mecânica'),
    ('COBERTURA',                'F02_cobertura.jpeg',    'Vista geral da cobertura'),
    ('GUARDA-CORPO',             'F03_guarda_corpo.jpeg', 'Guarda-corpo — madeira apodrecida (risco imediato)'),
    ('CASAS DE M',               'F04_casa_maquinas.jpeg','Casa de máquinas — corrosão nos motores dos elevadores'),
    ('ELEVADORES',               'F04_casa_maquinas.jpeg', None),
    ('ESCADA DE INC',            'F05_escada.jpeg',       'Escada de incêndio — 5° andar, ventilação obstruída'),
    ('SINALIZAÇÃO',              'F05_escada.jpeg',        None),
    ('INFILTR',                  'F06_infiltracao.jpeg',  'Infiltração — varanda da cobertura'),
    ('APARTAMENTO DE COBERTURA', 'F06_infiltracao.jpeg',   None),
    ('PRISMA DE VENTIL',         'F07_prisma.jpeg',       'Prisma de ventilação — pastilhas soltas'),
    ('ACADEMIA',                 'F08_academia.jpeg',     'Academia — instalações elétricas sem conformidade'),
    ('DEPÓSI',                   'F08_academia.jpeg',      None),
    ('GARAGEM',                  'F09_garagem.jpeg',      'Garagem — infiltração e revestimento deteriorado'),
    ('PAVIMENTOS',               'F09_garagem.jpeg',       None),
    ('GÁS',                      'F10_gas.jpeg',          'Instalações de gás — central do prédio'),
    ('GAS',                      'F10_gas.jpeg',           None),
    ('REVESTIMENTO',             'F11_revestimento.jpeg', 'Revestimento cerâmico — desprendimento e trincas'),
    ('GERAL',                    'F12_geral.jpeg',        'Vista geral — área comum'),
]

# ─── Helpers ──────────────────────────────────────────────────────────────────
def set_font(run, bold=False, size=FONT_BODY, color=None, italic=False):
    run.font.name = FONT_NAME
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    # Forçar Tahoma em todos os scripts
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = run._element.makeelement(qn('w:rFonts'), {})
        rPr.insert(0, rFonts)
    for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rFonts.set(qn(attr), FONT_NAME)

def set_cell_borders(cell, color='BFBFBF', sz='4'):
    tcPr   = cell._tc.get_or_add_tcPr()
    tcBrds = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'),   'single')
        b.set(qn('w:sz'),    sz)
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), color)
        tcBrds.append(b)
    tcPr.append(tcBrds)

def hr(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    '6')
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), '1F497D')
    pBdr.append(bot)
    pPr.append(pBdr)

def add_para(doc, text, bold=False, size=FONT_BODY, align=None, color=None, italic=False):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.space_before = Pt(2)
    if text:
        parts = re.split(r'\*\*(.+?)\*\*', text)
        for idx, part in enumerate(parts):
            if part:
                r = p.add_run(part)
                set_font(r, bold=(bold or idx % 2 == 1), size=size, color=color, italic=italic)
    return p

def prepare_image(fpath, max_dim=1568, max_bytes=3_400_000):
    """Redimensiona mantendo orientação correta."""
    img = Image.open(fpath)
    # Aplicar rotação EXIF se existir
    try:
        exif = img._getexif()
        if exif:
            orient = exif.get(274)
            rotations = {3: 180, 6: -90, 8: 90}
            if orient in rotations:
                img = img.rotate(rotations[orient], expand=True)
    except Exception:
        pass
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    w, h = img.size
    if max(w, h) > max_dim:
        ratio = max_dim / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    for quality in (85, 75, 60, 45):
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality)
        if buf.tell() <= max_bytes:
            buf.seek(0)
            return buf
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=50)
    buf.seek(0)
    return buf

def insert_foto(doc, fname, legenda):
    fpath = os.path.join(_FOTOS, fname)
    if not os.path.exists(fpath):
        print(f"  ⚠️  não encontrada: {fname}")
        return
    try:
        buf = prepare_image(fpath)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after  = Pt(2)
        p.add_run().add_picture(buf, width=Cm(14))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(f"Foto: {legenda}")
        set_font(r, size=Pt(8.5), italic=True, color=RGBColor(0x60,0x60,0x60))
        cap.paragraph_format.space_after = Pt(8)
        print(f"  📸 {fname}")
    except Exception as e:
        print(f"  ⚠️  erro ao inserir {fname}: {e}")

def add_table(doc, headers, rows):
    if not headers or not rows:
        return
    table = doc.add_table(rows=len(rows)+1, cols=len(headers))
    table.style = 'Normal Table'
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        txt  = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
        cell.paragraphs[0].clear()
        r = cell.paragraphs[0].add_run(txt)
        set_font(r, bold=True, size=Pt(9))
        set_cell_borders(cell, color='2E74B5', sz='6')
        # fundo azul no cabeçalho
        tcPr = cell._tc.get_or_add_tcPr()
        shd  = OxmlElement('w:shd')
        shd.set(qn('w:val'),   'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'),  '2E74B5')
        tcPr.append(shd)
        r.font.color.rgb = RGBColor(255,255,255)
    for i, row in enumerate(rows):
        bg = 'DFE6F0' if i % 2 == 0 else 'FFFFFF'
        for j in range(len(headers)):
            cell = table.cell(i+1, j)
            raw  = row[j] if j < len(row) else ''
            txt  = re.sub(r'\*\*(.+?)\*\*', r'\1', raw)
            cell.paragraphs[0].clear()
            r = cell.paragraphs[0].add_run(txt)
            set_font(r, size=Pt(9))
            is_p1 = 'P1' in txt or 'CRÍTICO' in txt or '🔴' in txt
            is_p2 = 'P2' in txt or 'REGULAR' in txt or '🟠' in txt
            if is_p1:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xC0,0x00,0x00)
            elif is_p2:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xED,0x7D,0x31)
            set_cell_borders(cell)
            tcPr = cell._tc.get_or_add_tcPr()
            shd  = OxmlElement('w:shd')
            shd.set(qn('w:val'),   'clear')
            shd.set(qn('w:color'), 'auto')
            shd.set(qn('w:fill'),  bg)
            tcPr.append(shd)
    doc.add_paragraph()

# ─── Processamento do MD ───────────────────────────────────────────────────────
def process_md(doc, md_path):
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()

    # Começar da seção 3
    start = 0
    for i, line in enumerate(lines):
        if re.match(r'^##\s+3\.', line.strip()):
            start = i
            break
    lines = lines[start:]
    print(f"  Seção 3 encontrada — processando {len(lines)} linhas")

    fotos_inseridas = set()

    def try_foto(titulo):
        tu = titulo.upper()
        for kw, fname, legenda in FOTO_MAP:
            if kw in tu:
                if fname not in fotos_inseridas and legenda is not None:
                    insert_foto(doc, fname, legenda)
                    fotos_inseridas.add(fname)
                break

    i = 0
    table_buf = []

    def flush_table():
        nonlocal table_buf
        if not table_buf:
            return
        headers, rows = [], []
        for tl in table_buf:
            tl = tl.strip()
            if re.match(r'^\|[\s\-:|]+\|$', tl):
                continue
            cells = [c.strip() for c in tl.split('|') if c.strip()]
            if not headers:
                headers = cells
            else:
                rows.append(cells)
        if headers:
            add_table(doc, headers, rows)
        table_buf.clear()

    while i < len(lines):
        s = lines[i].strip()

        if s.startswith('|'):
            table_buf.append(s); i += 1; continue
        else:
            flush_table()

        if not s:               i += 1; continue
        if re.match(r'^---+$', s): hr(doc); i += 1; continue

        m = re.match(r'^(#{1,4})\s+(.+)', s)
        if m:
            lvl = len(m.group(1))
            txt = re.sub(r'\*\*(.+?)\*\*', r'\1', m.group(2)).strip()
            if lvl == 1:
                add_para(doc, txt, bold=True, size=FONT_H1, color=AZUL)
            elif lvl == 2:
                doc.add_paragraph()
                add_para(doc, txt, bold=True, size=FONT_H2, color=AZUL)
            elif lvl == 3:
                add_para(doc, txt, bold=True, size=FONT_H3)
                try_foto(txt)
            else:
                add_para(doc, txt, bold=True, size=FONT_H4, italic=True)
                try_foto(txt)
            i += 1; continue

        if re.search(r'Prioridade:\s*\d', s) or '**Prioridade' in s:
            txt = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
            p   = doc.add_paragraph()
            r   = p.add_run(txt)
            set_font(r, bold=True, size=FONT_BODY)
            if 'P1' in txt or '1 —' in txt: r.font.color.rgb = RGBColor(0xC0,0x00,0x00)
            elif 'P2' in txt:               r.font.color.rgb = RGBColor(0xED,0x7D,0x31)
            elif 'P3' in txt:               r.font.color.rgb = RGBColor(0x7F,0x6B,0x00)
            i += 1; continue

        if s.startswith('>'):
            txt = re.sub(r'^>\s*', '', s)
            txt = re.sub(r'\*\*(.+?)\*\*', r'\1', txt)
            p   = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(1)
            r   = p.add_run(txt)
            set_font(r, size=Pt(9.5), italic=True)
            i += 1; continue

        if re.match(r'^[-*]\s+', s):
            while i < len(lines) and re.match(r'^[-*]\s+', lines[i].strip()):
                item = re.sub(r'^[-*]\s+', '', lines[i].strip())
                item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.5)
                p.paragraph_format.space_after  = Pt(2)
                r = p.add_run(f"• {item}")
                set_font(r, size=FONT_BODY)
                i += 1
            continue

        if re.match(r'^\d+\.\s+', s):
            num = 1
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                item = re.sub(r'^\d+\.\s+', '', lines[i].strip())
                item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.5)
                p.paragraph_format.space_after  = Pt(2)
                r = p.add_run(f"{num}. {item}")
                set_font(r, size=FONT_BODY)
                num += 1
                i += 1
            continue

        # Parágrafo normal
        if s:
            add_para(doc, s, size=FONT_BODY)
        i += 1

    flush_table()

    # Inserir fotos que ainda não foram inseridas no final (F12_geral)
    for kw, fname, legenda in FOTO_MAP:
        if fname not in fotos_inseridas and legenda is not None:
            if fname == 'F12_geral.jpeg':
                doc.add_paragraph()
                add_para(doc, "Registro fotográfico geral", bold=True, size=FONT_H3)
                insert_foto(doc, fname, legenda)
                fotos_inseridas.add(fname)

    return fotos_inseridas

def add_assinatura(doc):
    doc.add_paragraph()
    hr(doc)
    doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("Rio de Janeiro, novembro de 2026.")
    set_font(r, size=FONT_BODY)
    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("_" * 50)
    set_font(r, size=FONT_BODY)
    p = doc.add_paragraph()
    r = p.add_run("Eng.º Civil Rafael Mendes Cavalcanti")
    set_font(r, bold=True, size=FONT_BODY)
    p = doc.add_paragraph()
    r = p.add_run("CREA-RJ 2019114-7  |  ART: XXXX")
    set_font(r, size=FONT_BODY)
    p = doc.add_paragraph()
    r = p.add_run("Responsável Técnico")
    set_font(r, italic=True, size=FONT_BODY)

# ══════════════════════════════════════════════════════════════════════════════
print("─── Gerando Laudo_Jardim_das_Flores_v11.docx ───")
print(f"  Base: {MODEL_01}")

doc = Document(MODEL_01)

# Ajustar margens para 2.5cm (estilo 02_gerar_laudo_docx)
for sec in doc.sections:
    sec.top_margin    = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin   = Cm(2.5)
    sec.right_margin  = Cm(2.5)

# Substituições nas páginas 1 e 2
substituicoes = {
    'CONDOMINIO DO EDIFICIO SOLAR CARAVELAS': 'CONDOMÍNIO JARDIM DAS FLORES',
    'Rua João Lira, nº 60 — Leblon, Rio de Janeiro/RJ': 'Rua João Lira, nº 15 — Leblon, Rio de Janeiro/RJ',
    'TD 071/2026': 'LTVP-2026-JDF-015',
    '29 de Março de 2026': '08 de novembro de 2026',
    'Março de 2026 (inicial) / 10 de maio de 2026 (complementar — Apto 301 e fachada)': '05 de novembro de 2026',
    'Superior a 50 anos': 'A confirmar documentalmente',
    'Revestimento em mármore': 'Revestimento em pedra (fixação mecânica)',
    'Subsolo + Garagem + Térreo + PUC + 7 pavimentos tipo': 'Cobertura duplex + 4 pavimentos tipo + garagem',
    'A menos de 500m da orla marítima (atmosfera marinha — classe de agressividade III/IV conforme NBR 6118)': 'Próximo à orla marítima — classe de agressividade III/IV (NBR 6118)',
}

def replace_in_para(para, subs):
    full = para.text
    new  = full
    for old, nv in subs.items():
        new = new.replace(old, nv)
    if new != full:
        for run in para.runs:
            run.text = ''
        if para.runs:
            para.runs[0].text = new
        else:
            para.add_run(new)
        print(f"  ✏️  '{full[:55]}' → '{new[:55]}'")

print("\n  Atualizando dados nas páginas 1 e 2...")
for p in doc.paragraphs:
    replace_in_para(p, substituicoes)
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                replace_in_para(p, substituicoes)

print("\n  Adicionando conteúdo a partir da Seção 3...")
doc.add_page_break()
fotos = process_md(doc, LAUDO_MD)

print("  Adicionando assinatura...")
add_assinatura(doc)

doc.save(OUT_V11)
size_kb = os.path.getsize(OUT_V11) / 1024
print(f"\n  ✅ {OUT_V11}")
print(f"     Tamanho: {size_kb:.0f} KB")
print(f"     Fotos  : {len(fotos)} inseridas")
