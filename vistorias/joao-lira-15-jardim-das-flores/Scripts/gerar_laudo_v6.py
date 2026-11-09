#!/usr/bin/env python3
"""
gerar_laudo_v6.py
─────────────────
Gera Laudo_Jardim_das_Flores_v6.docx com:
  • Papel timbrado Time Designer (header logo + footer endereço + paginação)
  • Capa com foto geral F12, tabela de dados e contagem correta de ocorrências
  • 12 fotos inseridas nas seções corretas do laudo
  • Contagem correta: 7×P1, 10×P2, 3×P3
  • Margens exatas do padrão Solar Caravelas

Changelog vs v5:
  - Capa: foto F12_geral.jpeg como imagem de abertura
  - Capa: contagem corrigida (10×P2, 3×P3)
  - Mapeamento fotos: keywords alinhados aos títulos reais do MD
  - F09_garagem e F10_gas: mapeados para seção 5.7 (ELEVADORES E CASAS)
  - F11_revestimento: mapeado para seção 5.3 FACHADA (REVESTIMENTO)
  - Versão no nome do arquivo (v6) para não sobrescrever versões anteriores
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re, os

# ─── Caminhos ─────────────────────────────────────────────────────────────────
_SCRIPT    = os.path.abspath(__file__)
_REPO      = os.path.dirname(os.path.dirname(_SCRIPT))   # Scripts/../ = pasta da vistoria
_LAUDO_DIR = os.path.join(_REPO, "Laudo")
_ASSETS    = os.path.join(_REPO, "assets")
_FOTOS     = os.path.join(_REPO, "fotos_vistoria")

LOGO_PNG = os.path.join(_ASSETS, "header_logo.png")
LAUDO_MD = os.path.join(_LAUDO_DIR, "Laudo_Jardim_das_Flores.md")
OUT_V6   = os.path.join(_LAUDO_DIR, "Laudo_Jardim_das_Flores_v6.docx")

# ─── Validação de entrada ──────────────────────────────────────────────────────
for f, label in [(LAUDO_MD, "Laudo MD"), (LOGO_PNG, "Logo PNG")]:
    if not os.path.exists(f):
        raise FileNotFoundError(f"❌ {label} não encontrado: {f}")

fotos_presentes = [x for x in os.listdir(_FOTOS) if x.endswith(('.jpeg','.jpg','.png'))]
print(f"  Fotos disponíveis em fotos_vistoria/: {len(fotos_presentes)}")
if len(fotos_presentes) == 0:
    print("  ⚠️  Nenhuma foto encontrada — DOCX será gerado sem fotos")

# ─── Cores ────────────────────────────────────────────────────────────────────
AZUL  = RGBColor(0x1F, 0x49, 0x7D)
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
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    '6')
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), '2E74B5')
    pBdr.append(bot)
    pPr.append(pBdr)

def add_page_num(para):
    def fld(instr):
        fc1 = OxmlElement('w:fldChar');  fc1.set(qn('w:fldCharType'), 'begin')
        it  = OxmlElement('w:instrText'); it.text = instr
        fc2 = OxmlElement('w:fldChar');  fc2.set(qn('w:fldCharType'), 'end')
        r = para.add_run()
        r._r.append(fc1); r._r.append(it); r._r.append(fc2)
        r.font.size = Pt(8); r.font.color.rgb = CINZA
    fld(' PAGE ')
    r = para.add_run(' / '); r.font.size = Pt(8); r.font.color.rgb = CINZA
    fld(' NUMPAGES ')

def setup_header_footer(doc):
    sec = doc.sections[0]
    sec.different_first_page_header_footer = False

    # ── Header: logo ──────────────────────────────────────────────────────────
    hdr = sec.header
    for p in list(hdr.paragraphs): p._p.getparent().remove(p._p)
    hp = hdr.add_paragraph()
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if os.path.exists(LOGO_PNG):
        try:
            hp.add_run().add_picture(LOGO_PNG, height=Cm(1.6))
        except Exception as e:
            r = hp.add_run("TIME DESIGNER"); r.font.bold=True
            r.font.size=Pt(13); r.font.color.rgb=AZUL
            print(f"  ⚠️  logo: {e}")
    else:
        r = hp.add_run("TIME DESIGNER")
        r.font.bold=True; r.font.size=Pt(13); r.font.color.rgb=AZUL
    # linha azul sob header
    pPr = hp._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),'single'); bot.set(qn('w:sz'),'8')
    bot.set(qn('w:space'),'1');    bot.set(qn('w:color'),'1F497D')
    pBdr.append(bot); pPr.append(pBdr)

    # ── Footer: endereço + paginação ──────────────────────────────────────────
    ftr = sec.footer
    for p in list(ftr.paragraphs): p._p.getparent().remove(p._p)

    p1 = ftr.add_paragraph(); p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run("Rua Marechal Floriano, 38 – sala 610 – Centro / Rio de Janeiro RJ")
    r1.font.size=Pt(8); r1.font.color.rgb=CINZA

    p2 = ftr.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("cesar@timedesigner.com.br  |  timedesigner.com.br")
    r2.font.size=Pt(8); r2.font.color.rgb=CINZA

    p3 = ftr.add_paragraph(); p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run("LTVP-2026-JDF-015   |   Pág. ")
    r3.font.size=Pt(8); r3.font.color.rgb=CINZA
    add_page_num(p3)


def add_table(doc, headers, rows):
    if not headers or not rows: return
    table = doc.add_table(rows=len(rows)+1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    # cabeçalho
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        txt  = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
        cell.paragraphs[0].clear()
        run = cell.paragraphs[0].add_run(txt)
        run.font.bold=True; run.font.color.rgb=BRANCO; run.font.size=Pt(9)
        set_cell_bg(cell, '2E74B5'); set_cell_borders(cell, '2E74B5')
    # linhas
    for i, row in enumerate(rows):
        bg = 'DFE6F0' if i%2==0 else 'FFFFFF'
        for j in range(len(headers)):
            cell = table.cell(i+1, j)
            txt  = re.sub(r'\*\*(.+?)\*\*', r'\1', row[j] if j < len(row) else '')
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(txt)
            run.font.size=Pt(9)
            if '🔴' in txt or txt.strip()=='P1': run.font.color.rgb=P1; run.font.bold=True
            elif '🟠' in txt or txt.strip()=='P2': run.font.color.rgb=P2; run.font.bold=True
            elif '🟡' in txt or txt.strip()=='P3': run.font.color.rgb=P3; run.font.bold=True
            set_cell_bg(cell, bg); set_cell_borders(cell)
    doc.add_paragraph()


def insert_foto(doc, fpath, caption):
    """Insere foto centralizada com legenda."""
    if not os.path.exists(fpath):
        print(f"  ⚠️  foto não encontrada: {fpath}")
        return
    try:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(fpath, width=Cm(14))
        cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(f"Foto: {caption}")
        r.font.size=Pt(8.5); r.font.italic=True; r.font.color.rgb=CINZA
        print(f"  📸 {os.path.basename(fpath)}")
    except Exception as e:
        print(f"  ⚠️  erro ao inserir {fpath}: {e}")


# ─── Mapeamento fotos → seções ─────────────────────────────────────────────────
# Chave: substring do título H3/H4 em MAIÚSCULAS
# Valor: (arquivo, legenda)
# Cada foto inserida apenas 1× (na primeira ocorrência do keyword)
FOTO_MAP = [
    ('COBERTURA',              'F02_cobertura.jpeg',    'Vista geral da cobertura'),
    ('GUARDA-CORPO',           'F03_guarda_corpo.jpeg', 'Guarda-corpo danificado — madeira apodrecida'),
    ('PISCINA',                'F02_cobertura.jpeg',    None),  # cobertura já inserida acima; pular
    ('VARANDA',                'F06_infiltracao.jpeg',  'Infiltração na varanda da cobertura'),
    ('APARTAMENTO DE COBERTURA','F06_infiltracao.jpeg', None),  # mesmo arquivo; controle pelo set
    ('FACHADA',                'F01_fachada.jpeg',      'Fachada — pedras sem fixação mecânica'),
    ('REVESTIMENTO',           'F11_revestimento.jpeg', 'Revestimento cerâmico danificado'),
    ('PRISMA DE VENTIL',       'F07_prisma.jpeg',       'Prisma de ventilação — pastilhas soltas'),
    ('ESCADA DE INC',          'F05_escada.jpeg',       'Escada de incêndio — ventilação obstruída'),
    ('SINALIZAÇÃO',            'F05_escada.jpeg',       None),  # já inserida; pular
    ('ELEVADORES',             'F04_casa_maquinas.jpeg','Casa de máquinas — corrosão nos motores'),
    ('CASAS DE MÁQ',           'F04_casa_maquinas.jpeg',None),
    ('CASAS DE MAC',           'F04_casa_maquinas.jpeg',None),
    ('GARAGEM',                'F09_garagem.jpeg',      'Garagem'),
    ('GÁS',                    'F10_gas.jpeg',          'Instalações de gás'),
    ('GAS',                    'F10_gas.jpeg',          None),
    ('ACADEMIA',               'F08_academia.jpeg',     'Academia — instalações elétricas e equipamentos'),
    ('DEPÓSITO',               'F08_academia.jpeg',     None),
    ('DEPOSITO',               'F08_academia.jpeg',     None),
    ('PAVIMENTOS',             'F09_garagem.jpeg',      None),
]


def process_md(doc, md_path):
    """Converte laudo MD para DOCX, inserindo fotos nas seções corretas."""
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()

    fotos_inseridas = set()   # controla arquivos já inseridos

    def try_insert_foto(titulo):
        tu = titulo.upper()
        for kw, fname, legenda in FOTO_MAP:
            if kw in tu:
                if fname not in fotos_inseridas and legenda is not None:
                    fpath = os.path.join(_FOTOS, fname)
                    insert_foto(doc, fpath, legenda)
                    fotos_inseridas.add(fname)
                break  # só testa o primeiro match por título

    i = 0
    table_buf = []

    def flush_table():
        nonlocal table_buf
        if not table_buf: return
        headers, rows = [], []
        for tl in table_buf:
            tl = tl.strip()
            if re.match(r'^\|[\s\-:|]+\|$', tl): continue  # separador
            cells = [c.strip() for c in tl.split('|') if c.strip() != '']
            if not headers: headers = cells
            else: rows.append(cells)
        if headers: add_table(doc, headers, rows)
        table_buf.clear()

    while i < len(lines):
        raw = lines[i]
        s   = raw.strip()

        # Acumular tabelas
        if s.startswith('|'):
            table_buf.append(s); i += 1; continue
        else:
            flush_table()

        if not s: i += 1; continue
        if re.match(r'^---+$', s): hr(doc); i += 1; continue

        # Títulos
        m = re.match(r'^(#{1,4})\s+(.+)', s)
        if m:
            lvl = len(m.group(1))
            txt = re.sub(r'\*\*(.+?)\*\*', r'\1', m.group(2)).strip()
            p   = doc.add_paragraph()
            run = p.add_run(txt)
            if lvl == 1:
                run.font.size=Pt(15); run.font.bold=True; run.font.color.rgb=AZUL
                p.paragraph_format.space_before=Pt(18)
            elif lvl == 2:
                run.font.size=Pt(12); run.font.bold=True; run.font.color.rgb=AZUL
                p.paragraph_format.space_before=Pt(14)
            elif lvl == 3:
                run.font.size=Pt(10.5); run.font.bold=True; run.font.color.rgb=AZUL
                p.paragraph_format.space_before=Pt(10)
                try_insert_foto(txt)
            else:
                run.font.size=Pt(10); run.font.bold=True; run.font.italic=True
                p.paragraph_format.space_before=Pt(8)
                try_insert_foto(txt)
            i += 1; continue

        # Linhas de prioridade
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

        # Listas com marcador
        if re.match(r'^[-*]\s+', s):
            while i < len(lines) and re.match(r'^[-*]\s+', lines[i].strip()):
                item = re.sub(r'^[-*]\s+','', lines[i].strip())
                item = re.sub(r'\*\*(.+?)\*\*',r'\1', item)
                p = doc.add_paragraph(style='List Bullet')
                r = p.add_run(item); r.font.size=Pt(10)
                p.paragraph_format.left_indent=Cm(0.5)
                p.paragraph_format.space_after=Pt(2)
                i += 1
            continue

        # Listas numeradas
        if re.match(r'^\d+\.\s+', s):
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                item = re.sub(r'^\d+\.\s+','', lines[i].strip())
                item = re.sub(r'\*\*(.+?)\*\*',r'\1', item)
                p = doc.add_paragraph(style='List Number')
                r = p.add_run(item); r.font.size=Pt(10)
                i += 1
            continue

        # Parágrafo normal (com negrito inline)
        if s:
            p = doc.add_paragraph()
            p.paragraph_format.space_after=Pt(4)
            # processar **negrito** inline
            parts = re.split(r'\*\*(.+?)\*\*', s)
            for idx, part in enumerate(parts):
                r = p.add_run(part)
                r.font.size=Pt(10)
                if idx % 2 == 1: r.font.bold=True  # parte dentro de **...**
        i += 1

    flush_table()
    return fotos_inseridas


def make_capa(doc):
    """
    Página de capa:
      • Foto geral F12 no topo
      • Título e subtítulo
      • Nome e endereço do condomínio
      • Tabela de dados identificação
      • Resumo de ocorrências
    """
    # Foto de capa — F12_geral.jpeg
    f12 = os.path.join(_FOTOS, 'F12_geral.jpeg')
    if os.path.exists(f12):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try:
            p.add_run().add_picture(f12, width=Cm(14))
            print("  📸 F12_geral.jpeg (capa)")
        except Exception as e:
            print(f"  ⚠️  foto capa: {e}")
    else:
        print("  ⚠️  F12_geral.jpeg não encontrada — capa sem foto")

    doc.add_paragraph()

    # Título
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('LAUDO TÉCNICO DE VISTORIA PREDIAL')
    r.font.size=Pt(20); r.font.bold=True; r.font.color.rgb=AZUL

    p2 = doc.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run('Autovistoria Predial — Lei Estadual nº 6.400/2013 | Lei Complementar nº 126/2013 | Decreto nº 37.426/2013')
    r2.font.size=Pt(9); r2.font.italic=True; r2.font.color.rgb=CINZA

    doc.add_paragraph()

    # Nome do condomínio
    p3 = doc.add_paragraph(); p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run('Condomínio Jardim das Flores')
    r3.font.size=Pt(17); r3.font.bold=True

    p4 = doc.add_paragraph(); p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run('Rua João Lira, nº 15 — Leblon, Rio de Janeiro / RJ')
    r4.font.size=Pt(11); r4.font.color.rgb=CINZA

    hr(doc)

    # Tabela de identificação
    dados = [
        ('Código do Laudo',       'LTVP-2026-JDF-015'),
        ('Data da Vistoria',      '05 de novembro de 2026'),
        ('Data de Emissão',       '08 de novembro de 2026'),
        ('Responsável Técnico',   'Eng.º Civil Rafael Mendes Cavalcanti'),
        ('CREA-RJ',               '2019114-7'),
        ('ART / RRT',             'XXXX'),
        ('Síndico / Solicitante', 'Marcos Antônio Ferreira da Silva'),
    ]
    table = doc.add_table(rows=len(dados), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (k, v) in enumerate(dados):
        c0, c1 = table.cell(i,0), table.cell(i,1)
        for cell, txt, bold in [(c0, k, True), (c1, v, False)]:
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(txt)
            run.font.size=Pt(10); run.font.bold=bold
        bg = 'DFE6F0' if i%2==0 else 'FFFFFF'
        for c in (c0, c1): set_cell_bg(c, bg); set_cell_borders(c)

    doc.add_paragraph()

    # Resumo de ocorrências
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('🔴 7 ocorrências P1 — CRÍTICO   |   🟠 10 ocorrências P2 — REGULAR   |   🟡 3 ocorrências P3 — MÍNIMO')
    r.font.size=Pt(10); r.font.bold=True


# ══════════════════════════════════════════════════════════════════════════════
# GERAR v6
# ══════════════════════════════════════════════════════════════════════════════
print("─── Gerando Laudo_Jardim_das_Flores_v6.docx ───")

doc = Document()
sec = doc.sections[0]
sec.top_margin    = Cm(2.23)
sec.bottom_margin = Cm(1.65)
sec.left_margin   = Cm(3.0)
sec.right_margin  = Cm(2.0)
doc.styles['Normal'].font.name = 'Calibri'
doc.styles['Normal'].font.size = Pt(10)

setup_header_footer(doc)
make_capa(doc)
doc.add_page_break()

print("  Processando laudo markdown + fotos...")
fotos = process_md(doc, LAUDO_MD)

doc.save(OUT_V6)
size_kb = os.path.getsize(OUT_V6) / 1024
print(f"\n  ✅ {OUT_V6}")
print(f"     Tamanho: {size_kb:.0f} KB")
print(f"     Fotos inseridas: {len(fotos)} / {len(fotos_presentes)} disponíveis")
if size_kb < 200:
    print(f"  ⚠️  AVISO: arquivo parece pequeno — verificar se conteúdo foi carregado")
