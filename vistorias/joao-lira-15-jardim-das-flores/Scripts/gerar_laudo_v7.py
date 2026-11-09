#!/usr/bin/env python3
"""
gerar_laudo_v7.py
─────────────────
Usa Model-01.docx como base intacta (páginas 1 e 2),
atualiza os dados do Solar Caravelas → Jardim das Flores,
e acrescenta o laudo a partir da Seção 3 (página 3 em diante).

Changelog vs v6:
  - Base: Model-01.docx real (não mais construído do zero)
  - Páginas 1 e 2 preservadas — só dados substituídos
  - Seção 3 em diante adicionada após o conteúdo existente
  - Estilos Heading 1/2/3 herdados do modelo (cor, fonte, espaçamento reais)
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re, os, copy

# ─── Caminhos ─────────────────────────────────────────────────────────────────
_SCRIPT    = os.path.abspath(__file__)
_VISTORIA  = os.path.dirname(os.path.dirname(_SCRIPT))
_LAUDO_DIR = os.path.join(_VISTORIA, "Laudo")
_ASSETS    = os.path.join(_VISTORIA, "assets")
_FOTOS     = os.path.join(_VISTORIA, "fotos_vistoria")

MODEL_01 = os.path.join(_ASSETS,    "Model-01.docx")
LAUDO_MD = os.path.join(_LAUDO_DIR, "Laudo_Jardim_das_Flores.md")
OUT_V7   = os.path.join(_LAUDO_DIR, "Laudo_Jardim_das_Flores_v7.docx")

# ─── Validação ────────────────────────────────────────────────────────────────
for f, label in [(MODEL_01, "Model-01.docx"), (LAUDO_MD, "Laudo MD")]:
    if not os.path.exists(f):
        raise FileNotFoundError(f"❌ {label} não encontrado: {f}")

fotos_presentes = [x for x in os.listdir(_FOTOS) if x.lower().endswith(('.jpeg','.jpg','.png'))]
print(f"  Fotos disponíveis: {len(fotos_presentes)}")

# ─── Cores ────────────────────────────────────────────────────────────────────
AZUL  = RGBColor(0x2E, 0x74, 0xB5)   # mesma do modelo
P1    = RGBColor(0xC0, 0x00, 0x00)
P2    = RGBColor(0xED, 0x7D, 0x31)
P3    = RGBColor(0x7F, 0x6B, 0x00)
CINZA = RGBColor(0x60, 0x60, 0x60)
BRANCO= RGBColor(0xFF, 0xFF, 0xFF)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)

def set_cell_borders(cell, color='BFBFBF'):
    tcPr   = cell._tc.get_or_add_tcPr()
    tcBrds = OxmlElement('w:tcBorders')
    for side in ('top','left','bottom','right'):
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'),   'single')
        b.set(qn('w:sz'),    '4')
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
    bot.set(qn('w:color'), '2E74B5')
    pBdr.append(bot)
    pPr.append(pBdr)

def add_table(doc, headers, rows):
    if not headers or not rows: return
    table = doc.add_table(rows=len(rows)+1, cols=len(headers))
    table.style = 'Normal Table'
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        txt  = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
        cell.paragraphs[0].clear()
        run  = cell.paragraphs[0].add_run(txt)
        run.font.bold=True; run.font.color.rgb=BRANCO; run.font.size=Pt(9)
        set_cell_bg(cell, '2E74B5'); set_cell_borders(cell, '2E74B5')
    for i, row in enumerate(rows):
        bg = 'DFE6F0' if i%2==0 else 'FFFFFF'
        for j in range(len(headers)):
            cell = table.cell(i+1, j)
            txt  = re.sub(r'\*\*(.+?)\*\*', r'\1', row[j] if j < len(row) else '')
            cell.paragraphs[0].clear()
            run  = cell.paragraphs[0].add_run(txt)
            run.font.size=Pt(9)
            if   '🔴' in txt or txt.strip()=='P1': run.font.color.rgb=P1; run.font.bold=True
            elif '🟠' in txt or txt.strip()=='P2': run.font.color.rgb=P2; run.font.bold=True
            elif '🟡' in txt or txt.strip()=='P3': run.font.color.rgb=P3; run.font.bold=True
            set_cell_bg(cell, bg); set_cell_borders(cell)
    doc.add_paragraph()

def insert_foto(doc, fpath, caption):
    if not os.path.exists(fpath):
        print(f"  ⚠️  foto não encontrada: {os.path.basename(fpath)}")
        return
    try:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(fpath, width=Cm(14))
        cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(f"Foto: {caption}")
        r.font.size=Pt(8.5); r.font.italic=True; r.font.color.rgb=CINZA
        print(f"  📸 {os.path.basename(fpath)}")
    except Exception as e:
        print(f"  ⚠️  erro ao inserir {os.path.basename(fpath)}: {e}")

# ─── Mapeamento fotos → seções ─────────────────────────────────────────────────
FOTO_MAP = [
    ('COBERTURA',              'F02_cobertura.jpeg',    'Vista geral da cobertura'),
    ('GUARDA-CORPO',           'F03_guarda_corpo.jpeg', 'Guarda-corpo — madeira apodrecida'),
    ('VARANDA DA COBERTURA',   'F06_infiltracao.jpeg',  'Infiltração na varanda da cobertura'),
    ('APARTAMENTO DE COBERTURA','F06_infiltracao.jpeg', None),
    ('FACHADA',                'F01_fachada.jpeg',      'Fachada — pedras sem fixação mecânica'),
    ('REVESTIMENTO',           'F11_revestimento.jpeg', 'Revestimento deteriorado'),
    ('PRISMA DE VENTIL',       'F07_prisma.jpeg',       'Prisma de ventilação — pastilhas soltas'),
    ('ESCADA DE INC',          'F05_escada.jpeg',       'Escada de incêndio — ventilação obstruída'),
    ('SINALIZAÇÃO',            'F05_escada.jpeg',       None),
    ('ELEVADORES',             'F04_casa_maquinas.jpeg','Casa de máquinas — corrosão nos motores'),
    ('CASAS DE M',             'F04_casa_maquinas.jpeg',None),
    ('ACADEMIA',               'F08_academia.jpeg',     'Academia — instalações elétricas'),
    ('DEPÓSITO',               'F08_academia.jpeg',     None),
    ('DEPOSITO',               'F08_academia.jpeg',     None),
    ('PAVIMENTOS',             'F09_garagem.jpeg',      'Garagem / pavimentos tipo'),
]

def process_md_from_section3(doc, md_path):
    """
    Lê o laudo MD e insere no doc apenas o conteúdo
    a partir da Seção 3 (LEGISLAÇÃO E NORMAS APLICÁVEIS).
    """
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()

    # Encontrar a linha que começa a seção 3
    start_idx = None
    for i, line in enumerate(lines):
        if re.match(r'^##\s+3\.', line.strip()):
            start_idx = i
            break

    if start_idx is None:
        print("  ⚠️  Seção 3 não encontrada no MD — inserindo tudo após seção 2")
        start_idx = 0
    else:
        print(f"  Seção 3 encontrada na linha {start_idx+1} do MD — inserindo a partir daqui")

    lines = lines[start_idx:]

    fotos_inseridas = set()

    def try_insert_foto(titulo):
        tu = titulo.upper()
        for kw, fname, legenda in FOTO_MAP:
            if kw in tu:
                if fname not in fotos_inseridas and legenda is not None:
                    insert_foto(doc, os.path.join(_FOTOS, fname), legenda)
                    fotos_inseridas.add(fname)
                break

    i = 0
    table_buf = []

    def flush_table():
        nonlocal table_buf
        if not table_buf: return
        headers, rows = [], []
        for tl in table_buf:
            tl = tl.strip()
            if re.match(r'^\|[\s\-:|]+\|$', tl): continue
            cells = [c.strip() for c in tl.split('|') if c.strip() != '']
            if not headers: headers = cells
            else: rows.append(cells)
        if headers: add_table(doc, headers, rows)
        table_buf.clear()

    while i < len(lines):
        s = lines[i].strip()

        if s.startswith('|'):
            table_buf.append(s); i += 1; continue
        else:
            flush_table()

        if not s: i += 1; continue
        if re.match(r'^---+$', s): hr(doc); i += 1; continue

        # Títulos — usar estilos do modelo
        m = re.match(r'^(#{1,4})\s+(.+)', s)
        if m:
            lvl = len(m.group(1))
            txt = re.sub(r'\*\*(.+?)\*\*', r'\1', m.group(2)).strip()
            if lvl == 1:
                p = doc.add_paragraph(style='Heading 1')
                p.add_run(txt)
            elif lvl == 2:
                p = doc.add_paragraph(style='Heading 2')
                p.add_run(txt)
            elif lvl == 3:
                p = doc.add_paragraph(style='Heading 3')
                p.add_run(txt)
                try_insert_foto(txt)
            else:
                p = doc.add_paragraph(style='Heading 3')
                run = p.add_run(txt); run.font.italic=True
                try_insert_foto(txt)
            i += 1; continue

        # Prioridade
        if re.search(r'Prioridade:\s*\d', s) or '**Prioridade' in s:
            txt = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
            p   = doc.add_paragraph()
            run = p.add_run(txt)
            run.font.bold=True; run.font.size=Pt(10)
            if   '1 —' in txt or ': 1' in txt: run.font.color.rgb=P1
            elif '2 —' in txt or ': 2' in txt: run.font.color.rgb=P2
            else:                               run.font.color.rgb=P3
            i += 1; continue

        # Blockquote
        if s.startswith('>'):
            txt = re.sub(r'^>\s*','',s)
            txt = re.sub(r'\*\*(.+?)\*\*',r'\1',txt)
            p   = doc.add_paragraph()
            p.paragraph_format.left_indent=Cm(1)
            run = p.add_run(txt)
            run.font.size=Pt(9.5); run.font.italic=True
            run.font.color.rgb=RGBColor(0x40,0x40,0x60)
            i += 1; continue

        # Lista com marcador
        if re.match(r'^[-*]\s+', s):
            while i < len(lines) and re.match(r'^[-*]\s+', lines[i].strip()):
                item = re.sub(r'^[-*]\s+','', lines[i].strip())
                item = re.sub(r'\*\*(.+?)\*\*',r'\1', item)
                p = doc.add_paragraph(style='List Paragraph')
                run = p.add_run(item); run.font.size=Pt(10)
                p.paragraph_format.left_indent=Cm(0.6)
                p.paragraph_format.space_after=Pt(2)
                # bullet manual
                pPr = p._p.get_or_add_pPr()
                numPr = OxmlElement('w:numPr')
                ilvl = OxmlElement('w:ilvl'); ilvl.set(qn('w:val'), '0')
                numId = OxmlElement('w:numId'); numId.set(qn('w:val'), '0')
                numPr.append(ilvl); numPr.append(numId)
                pPr.append(numPr)
                i += 1
            continue

        # Lista numerada
        if re.match(r'^\d+\.\s+', s):
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                item = re.sub(r'^\d+\.\s+','', lines[i].strip())
                item = re.sub(r'\*\*(.+?)\*\*',r'\1', item)
                p = doc.add_paragraph(style='List Paragraph')
                p.add_run(item).font.size=Pt(10)
                p.paragraph_format.left_indent=Cm(0.6)
                i += 1
            continue

        # Parágrafo normal com negrito inline
        if s:
            p = doc.add_paragraph()
            p.paragraph_format.space_after=Pt(4)
            parts = re.split(r'\*\*(.+?)\*\*', s)
            for idx2, part in enumerate(parts):
                r = p.add_run(part)
                r.font.size=Pt(10)
                if idx2 % 2 == 1: r.font.bold=True
        i += 1

    flush_table()
    return fotos_inseridas


# ══════════════════════════════════════════════════════════════════════════════
# GERAR v7
# ══════════════════════════════════════════════════════════════════════════════
print("─── Gerando Laudo_Jardim_das_Flores_v7.docx ───")
print(f"  Base: {MODEL_01}")

doc = Document(MODEL_01)

# ─── Atualizar dados nas páginas 1 e 2 ────────────────────────────────────────
# Substituições de texto no documento inteiro (páginas 1 e 2)
substituicoes = {
    'CONDOMINIO DO EDIFICIO SOLAR CARAVELAS':  'CONDOMÍNIO JARDIM DAS FLORES',
    'Condomínio Solar Caravelas':              'Condomínio Jardim das Flores',
    'Solar Caravelas':                         'Jardim das Flores',
    'Rua João Lira, nº 60 — Leblon, Rio de Janeiro/RJ': 'Rua João Lira, nº 15 — Leblon, Rio de Janeiro/RJ',
    'TD 071/2026':                             'LTVP-2026-JDF-015',
    '29 de Março de 2026':                     '08 de novembro de 2026',
    'Março de 2026 (inicial) / 10 de maio de 2026 (complementar — Apto 301 e fachada)': '05 de novembro de 2026',
    'Superior a 50 anos':                      'A confirmar documentalmente',
    'Revestimento em mármore':                 'Revestimento em pedra (fixação mecânica)',
    'Subsolo + Garagem + Térreo + PUC + 7 pavimentos tipo': 'Cobertura duplex + 4 pavimentos tipo + garagem',
    'A menos de 500m da orla marítima (atmosfera marinha — classe de agressividade III/IV conforme NBR 6118)': 'Próximo à orla marítima — classe de agressividade III/IV (NBR 6118)',
}

def replace_in_para(para, subs):
    full = para.text
    new  = full
    for old, new_val in subs.items():
        new = new.replace(old, new_val)
    if new != full:
        # Preservar formatação do primeiro run, substituir texto
        for run in para.runs:
            run.text = ''
        if para.runs:
            para.runs[0].text = new
        else:
            para.add_run(new)
        print(f"  ✏️  '{full[:50]}' → '{new[:50]}'")

print("\n  Atualizando dados nas páginas 1 e 2...")
for p in doc.paragraphs:
    replace_in_para(p, substituicoes)

for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                replace_in_para(p, substituicoes)

# ─── Adicionar quebra de página e seção 3 em diante ───────────────────────────
print("\n  Adicionando quebra de página → Seção 3...")
doc.add_page_break()

print("  Processando laudo MD a partir da Seção 3...")
fotos = process_md_from_section3(doc, LAUDO_MD)

# ─── Salvar ───────────────────────────────────────────────────────────────────
doc.save(OUT_V7)
size_kb = os.path.getsize(OUT_V7) / 1024
print(f"\n  ✅ {OUT_V7}")
print(f"     Tamanho : {size_kb:.0f} KB")
print(f"     Fotos   : {len(fotos)} inseridas")
if size_kb < 300:
    print(f"  ⚠️  AVISO: arquivo parece pequeno ({size_kb:.0f} KB) — verificar conteúdo")
