#!/usr/bin/env python3
"""
Cria:
  1. Modelo_Pagina_Timbrada.docx — capa + pág em branco timbrada
  2. Laudo_Jardim_das_Flores_v5.docx — laudo completo com fotos
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re, os, copy

# ─── Caminhos ─────────────────────────────────────────────────────────────────
TIMBRADO_BASE = "/tmp/ref_laudo60/PAPEL_TIMBRADO.docx"
LOGO_PNG      = "/tmp/ref_assets/header_logo.png"
FOTOS_DIR = "/tmp/fotos_docx"
LAUDO_MD = "/tmp/repo_laudos_mac/vistorias/joao-lira-15-jardim-das-flores/Laudo/Laudo_Jardim_das_Flores.md"

OUT_MODELO = "/tmp/repo_laudos_mac/vistorias/joao-lira-15-jardim-das-flores/Laudo/Modelo_Pagina_Timbrada.docx"
OUT_V5 = "/tmp/repo_laudos_mac/vistorias/joao-lira-15-jardim-das-flores/Laudo/Laudo_Jardim_das_Flores_v5.docx"

# ─── Cores ────────────────────────────────────────────────────────────────────
AZUL  = RGBColor(0x1F, 0x49, 0x7D)
P1    = RGBColor(0xC0, 0x00, 0x00)
P2    = RGBColor(0xED, 0x7D, 0x31)
P3    = RGBColor(0x7F, 0x6B, 0x00)
CINZA = RGBColor(0x60, 0x60, 0x60)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def set_cell_bg(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)

def set_cell_borders(cell):
    tc      = cell._tc
    tcPr    = tc.get_or_add_tcPr()
    tcBords = OxmlElement('w:tcBorders')
    for side in ['top', 'left', 'bottom', 'right']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'),   'single')
        b.set(qn('w:sz'),    '4')
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), 'BFBFBF')
        tcBords.append(b)
    tcPr.append(tcBords)

def hr(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    '6')
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), '2E74B5')
    pBdr.append(bot)
    pPr.append(pBdr)

def page_num_run(para):
    """Adiciona campo PAGE / NUMPAGES num parágrafo."""
    def fld(instrText):
        fc1 = OxmlElement('w:fldChar');  fc1.set(qn('w:fldCharType'), 'begin')
        it  = OxmlElement('w:instrText'); it.text = instrText
        fc2 = OxmlElement('w:fldChar');  fc2.set(qn('w:fldCharType'), 'end')
        r   = para.add_run()
        r._r.append(fc1); r._r.append(it); r._r.append(fc2)
        r.font.size = Pt(8); r.font.color.rgb = CINZA
        return r
    fld(' PAGE ');   para.add_run(' de ').font.size = Pt(8)
    fld(' NUMPAGES ')

def setup_header_footer(doc, logo_path, include_logo=True):
    """Header com logo; footer com endereço + paginação."""
    sec = doc.sections[0]
    sec.different_first_page_header_footer = False

    # ── HEADER ──────────────────────────────────────────────────────────────
    header = sec.header
    for p in list(header.paragraphs):
        p._p.getparent().remove(p._p)

    hp = header.add_paragraph()
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT

    if include_logo and os.path.exists(logo_path):
        run = hp.add_run()
        try:
            run.add_picture(logo_path, height=Cm(1.6))
        except Exception as e:
            print(f"  ⚠️  logo: {e}")
            run.text = "TIME DESIGNER"
            run.font.bold = True; run.font.size = Pt(13)
            run.font.color.rgb = AZUL
    else:
        r = hp.add_run("TIME DESIGNER")
        r.font.bold = True; r.font.size = Pt(13); r.font.color.rgb = AZUL

    # linha azul abaixo do header
    pPr = hp._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single'); bot.set(qn('w:sz'),    '8')
    bot.set(qn('w:space'), '1');      bot.set(qn('w:color'), '1F497D')
    pBdr.append(bot); pPr.append(pBdr)

    # ── FOOTER ──────────────────────────────────────────────────────────────
    footer = sec.footer
    for p in list(footer.paragraphs):
        p._p.getparent().remove(p._p)

    def fp(text, sz=8, color=None, align=WD_ALIGN_PARAGRAPH.CENTER):
        p = footer.add_paragraph(); p.alignment = align
        r = p.add_run(text)
        r.font.size = Pt(sz)
        r.font.color.rgb = color or CINZA
        return p

    fp("Rua Marechal Floriano, 38 – sala 610 – Centro")
    fp("Rio de Janeiro RJ  |  cesar@timedesigner.com.br  |  timedesigner.com.br")

    pg = footer.add_paragraph(); pg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r  = pg.add_run("LTVP-2026-JDF-015   |   Pág. ")
    r.font.size = Pt(8); r.font.color.rgb = CINZA
    page_num_run(pg)


def add_table(doc, headers, rows):
    if not headers: return
    table = doc.add_table(rows=len(rows)+1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
        if cell.paragraphs[0].runs:
            run = cell.paragraphs[0].runs[0]
        else:
            run = cell.paragraphs[0].add_run(cell.text); cell.text = ''
        run.font.bold = True; run.font.color.rgb = RGBColor(255,255,255)
        run.font.size = Pt(9)
        set_cell_bg(cell, '2E74B5'); set_cell_borders(cell)
    for i, row in enumerate(rows):
        bg = 'DFE6F0' if i%2==0 else 'FFFFFF'
        for j in range(len(headers)):
            cell = table.cell(i+1, j)
            txt  = row[j] if j < len(row) else ''
            txt  = re.sub(r'\*\*(.+?)\*\*', r'\1', txt)
            cell.text = txt
            if cell.paragraphs[0].runs:
                run = cell.paragraphs[0].runs[0]
            else:
                run = cell.paragraphs[0].add_run(txt); cell.text = ''
            run.font.size = Pt(9)
            if '🔴' in txt or txt.strip()=='P1': run.font.color.rgb=P1; run.font.bold=True
            elif '🟠' in txt or txt.strip()=='P2': run.font.color.rgb=P2; run.font.bold=True
            set_cell_bg(cell, bg); set_cell_borders(cell)
    doc.add_paragraph()


def process_md(doc, md_path, fotos_dir):
    """Converte MD para DOCX, inserindo fotos nos pontos certos."""
    with open(md_path) as f:
        lines = f.readlines()

    # Mapeamento: keyword no MD → arquivo de foto
    foto_map = {
        'FACHADA':         'F01_fachada.jpeg',
        'COBERTURA':       'F02_cobertura.jpeg',
        'GUARDA-CORPO':    'F03_guarda_corpo.jpeg',
        'CASAS DE MÁQUINAS':'F04_casa_maquinas.jpeg',
        'ESCADA DE INC':   'F05_escada.jpeg',
        'INFILTRACAO':     'F06_infiltracao.jpeg',
        'PRISMA DE VENTIL':'F07_prisma.jpeg',
        'ACADEMIA':        'F08_academia.jpeg',
        'GARAGEM':         'F09_garagem.jpeg',
        'GÁS':             'F10_gas.jpeg',
        'REVESTIMENTO CER':'F11_revestimento.jpeg',
    }
    fotos_inseridas = set()

    def maybe_insert_foto(titulo):
        """Insere foto relacionada ao título (1x por seção)."""
        tu = titulo.upper()
        for kw, fname in foto_map.items():
            if kw in tu and fname not in fotos_inseridas:
                fpath = os.path.join(fotos_dir, fname)
                if os.path.exists(fpath):
                    try:
                        p = doc.add_paragraph()
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        run = p.add_run()
                        run.add_picture(fpath, width=Cm(14))
                        cap = doc.add_paragraph()
                        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        r   = cap.add_run(f"Foto: {titulo}")
                        r.font.size = Pt(8.5); r.font.italic = True
                        r.font.color.rgb = CINZA
                        fotos_inseridas.add(fname)
                    except Exception as e:
                        print(f"  ⚠️  foto {fname}: {e}")
                break

    i = 0
    table_buf = []

    def flush_table():
        nonlocal table_buf
        if not table_buf: return
        headers, rows = [], []
        for tl in table_buf:
            tl = tl.strip()
            if re.match(r'^\|[\s\-:|]+\|', tl): continue
            cells = [c.strip() for c in tl.split('|') if c.strip()!='']
            if not headers: headers = cells
            else: rows.append(cells)
        add_table(doc, headers, rows)
        table_buf.clear()

    while i < len(lines):
        s = lines[i].strip()
        if s.startswith('|'):
            table_buf.append(s); i+=1; continue
        else:
            flush_table()

        if not s:                      i+=1; continue
        if re.match(r'^---+$', s):     hr(doc); i+=1; continue

        m = re.match(r'^(#{1,4})\s+(.+)', s)
        if m:
            lvl = len(m.group(1))
            txt = re.sub(r'\*\*(.+?)\*\*', r'\1', m.group(2))
            p   = doc.add_paragraph()
            run = p.add_run(txt)
            if lvl==1:
                run.font.size=Pt(15); run.font.bold=True; run.font.color.rgb=AZUL
                p.paragraph_format.space_before=Pt(18)
            elif lvl==2:
                run.font.size=Pt(12); run.font.bold=True; run.font.color.rgb=AZUL
                p.paragraph_format.space_before=Pt(12)
            elif lvl==3:
                run.font.size=Pt(10.5); run.font.bold=True
                p.paragraph_format.space_before=Pt(10)
                maybe_insert_foto(txt)   # ← foto após título de seção
            else:
                run.font.size=Pt(10); run.font.bold=True; run.font.italic=True
                p.paragraph_format.space_before=Pt(8)
                maybe_insert_foto(txt)   # ← foto após título de subseção
            i+=1; continue

        if re.search(r'Prioridade:\s*\d', s) or '**Prioridade' in s:
            txt = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
            p   = doc.add_paragraph()
            run = p.add_run(txt); run.font.bold=True; run.font.size=Pt(10)
            if 'P1' in txt or '1 —' in txt: run.font.color.rgb=P1
            elif 'P2' in txt:               run.font.color.rgb=P2
            else:                           run.font.color.rgb=P3
            i+=1; continue

        if s.startswith('>'):
            txt = re.sub(r'^>\s*','',s); txt=re.sub(r'\*\*(.+?)\*\*',r'\1',txt)
            p   = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(1)
            run = p.add_run(txt); run.font.size=Pt(9.5); run.font.italic=True
            run.font.color.rgb = RGBColor(0x40,0x40,0x60)
            i+=1; continue

        if re.match(r'^[-*]\s+', s):
            items=[]
            while i<len(lines) and re.match(r'^[-*]\s+',lines[i].strip()):
                item=re.sub(r'^[-*]\s+','',lines[i].strip())
                item=re.sub(r'\*\*(.+?)\*\*',r'\1',item)
                items.append(item); i+=1
            for item in items:
                p=doc.add_paragraph(style='List Bullet')
                r=p.add_run(item); r.font.size=Pt(10)
                p.paragraph_format.left_indent=Cm(0.5)
                p.paragraph_format.space_after=Pt(2)
            continue

        if re.match(r'^\d+\.\s+', s):
            items=[]
            while i<len(lines) and re.match(r'^\d+\.\s+',lines[i].strip()):
                item=re.sub(r'^\d+\.\s+','',lines[i].strip())
                item=re.sub(r'\*\*(.+?)\*\*',r'\1',item)
                items.append(item); i+=1
            for item in items:
                p=doc.add_paragraph(style='List Number')
                r=p.add_run(item); r.font.size=Pt(10)
            continue

        txt=re.sub(r'\*\*(.+?)\*\*',r'\1',s); txt=re.sub(r'_(.+?)_',r'\1',txt)
        if txt:
            p=doc.add_paragraph()
            r=p.add_run(txt); r.font.size=Pt(10)
            p.paragraph_format.space_after=Pt(4)
        i+=1
    flush_table()


def make_capa(doc, is_modelo=False):
    """Insere capa no documento."""
    for _ in range(3): doc.add_paragraph()
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run('LAUDO TÉCNICO DE VISTORIA PREDIAL')
    r.font.size=Pt(20); r.font.bold=True; r.font.color.rgb=AZUL

    p2=doc.add_paragraph(); p2.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r2=p2.add_run('Autovistoria Predial — Lei Estadual nº 6.400/2013')
    r2.font.size=Pt(11); r2.font.italic=True; r2.font.color.rgb=CINZA

    doc.add_paragraph()
    p3=doc.add_paragraph(); p3.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r3=p3.add_run('Condomínio Jardim das Flores')
    r3.font.size=Pt(17); r3.font.bold=True

    p4=doc.add_paragraph(); p4.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r4=p4.add_run('Rua João Lira, nº 15 — Leblon, Rio de Janeiro / RJ')
    r4.font.size=Pt(11); r4.font.color.rgb=CINZA

    doc.add_paragraph(); hr(doc); doc.add_paragraph()

    dados=[
        ('Código do Laudo',      'LTVP-2026-JDF-015'),
        ('Data da Vistoria',     '05 de novembro de 2026'),
        ('Data de Emissão',      '08 de novembro de 2026'),
        ('Responsável Técnico',  'Eng.º Civil Rafael Mendes Cavalcanti'),
        ('CREA-RJ',              '2019114-7'),
        ('ART / RRT',            'XXXX'),
        ('Síndico / Solicitante','Marcos Antônio Ferreira da Silva'),
    ]
    table=doc.add_table(rows=len(dados), cols=2)
    table.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,(k,v) in enumerate(dados):
        c0,c1=table.cell(i,0),table.cell(i,1)
        c0.text=k; c1.text=v
        for c in [c0,c1]:
            if c.paragraphs[0].runs: c.paragraphs[0].runs[0].font.size=Pt(10)
        if c0.paragraphs[0].runs: c0.paragraphs[0].runs[0].font.bold=True
        bg='DFE6F0' if i%2==0 else 'FFFFFF'
        for c in [c0,c1]: set_cell_bg(c,bg); set_cell_borders(c)

    doc.add_paragraph()
    pr=doc.add_paragraph(); pr.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr=pr.add_run('🔴 7 P1 — CRÍTICO   |   🟠 9 P2 — REGULAR   |   🟡 4 P3 — MÍNIMO')
    rr.font.size=Pt(10); rr.font.bold=True

    if is_modelo:
        nota=doc.add_paragraph()
        nota.alignment=WD_ALIGN_PARAGRAPH.CENTER
        rn=nota.add_run('[PÁGINA MODELO — substituir conteúdo a partir daqui]')
        rn.font.size=Pt(9); rn.font.italic=True; rn.font.color.rgb=CINZA


# ══════════════════════════════════════════════════════════════════════════════
# 1. MODELO DE PÁGINA TIMBRADA
# ══════════════════════════════════════════════════════════════════════════════
print("─── Criando Modelo_Pagina_Timbrada.docx ───")
doc_modelo = Document()
sec = doc_modelo.sections[0]
sec.top_margin    = Cm(2.23)
sec.bottom_margin = Cm(1.65)
sec.left_margin   = Cm(3.0)
sec.right_margin  = Cm(2.0)
doc_modelo.styles['Normal'].font.name = 'Calibri'
doc_modelo.styles['Normal'].font.size = Pt(10)

setup_header_footer(doc_modelo, LOGO_PNG)
make_capa(doc_modelo, is_modelo=True)
doc_modelo.add_page_break()
# Página 2 — em branco (só timbrada)
doc_modelo.add_paragraph()

doc_modelo.save(OUT_MODELO)
print(f"  ✅ {OUT_MODELO}  ({os.path.getsize(OUT_MODELO)/1024:.0f} KB)")


# ══════════════════════════════════════════════════════════════════════════════
# 2. LAUDO V5 COMPLETO
# ══════════════════════════════════════════════════════════════════════════════
print("─── Criando Laudo_Jardim_das_Flores_v5.docx ───")
doc_v5 = Document()
sec = doc_v5.sections[0]
sec.top_margin    = Cm(2.23)
sec.bottom_margin = Cm(1.65)
sec.left_margin   = Cm(3.0)
sec.right_margin  = Cm(2.0)
doc_v5.styles['Normal'].font.name = 'Calibri'
doc_v5.styles['Normal'].font.size = Pt(10)

setup_header_footer(doc_v5, LOGO_PNG)
make_capa(doc_v5)
doc_v5.add_page_break()

print("  Processando laudo markdown + fotos...")
process_md(doc_v5, LAUDO_MD, FOTOS_DIR)

doc_v5.save(OUT_V5)
print(f"  ✅ {OUT_V5}  ({os.path.getsize(OUT_V5)/1024:.0f} KB)")
print("Concluído.")
