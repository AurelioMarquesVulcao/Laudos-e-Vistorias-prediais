#!/usr/bin/env python3
"""
ETAPA 2 — Gera laudo.docx a partir do Laudo/Laudo_Jardim_das_Flores.md
Insere imagens de Fotos_Organizadas/ nos tópicos correspondentes.
Formatação: Tahoma, margens 2.5cm, capa, tabelas, listas.

Dependências: pip3 install python-docx Pillow
"""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import re, os, io, glob

BASE      = os.path.dirname(os.path.abspath(__file__))
RAIZ      = os.path.abspath(os.path.join(BASE, ".."))
MD_FILE   = os.path.join(RAIZ, "Laudo", "Laudo_Jardim_das_Flores.md")
FOTO_DIR  = os.path.join(RAIZ, "Fotos_Organizadas")
OUT_DOCX  = os.path.join(RAIZ, "Saida", "laudo_jardim_das_flores.docx")
OUT_DOCX2 = os.path.join(RAIZ, "Saida", "laudo_jardim_das_flores_v2.docx")

FONT_NAME  = "Tahoma"
FONT_BODY  = Pt(10)
FONT_H1    = Pt(14)
FONT_H2    = Pt(12)
FONT_H3    = Pt(11)
FONT_H4    = Pt(10)
LINE_SPACE = Pt(14)

# Mapa seção → lista de fotos (preenchido após análise + conversa com engenheiro)
# Formato: { "5.1.1": ["IMG_1638.jpeg", "IMG_1522.jpeg"], ... }
# Deixe vazio para gerar sem imagens e adicionar depois
SECTION_FOTO_MAP = {
    # "5.1":   [],  # Estrutura
    # "5.2":   [],  # Fachada
    # "5.3":   [],  # Elétrica
    # "5.4":   [],  # Gás
    # "5.5":   [],  # Incêndio
    # "5.6":   [],  # Rotas de saída
    # "5.7":   [],  # Elevadores
    # "5.8":   [],  # Cobertura/antenas
    # "5.9":   [],  # Garagem
    # "5.10":  [],  # Áreas comuns
}


def set_font(run, bold=False, size=FONT_BODY, color=None):
    run.font.name = FONT_NAME
    run.font.size = size
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = run._element.makeelement(qn('w:rFonts'), {})
        rPr.insert(0, rFonts)
    for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rFonts.set(qn(attr), FONT_NAME)


def add_para(doc, text, bold=False, size=FONT_BODY, align=None, color=None):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.line_spacing = LINE_SPACE
    r = p.add_run(text)
    set_font(r, bold=bold, size=size, color=color)
    return p


def add_image(doc, path, width=Inches(4.5)):
    doc.add_picture(path, width=width)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


def insert_section_images(doc, section_key, inserted):
    if section_key in SECTION_FOTO_MAP and section_key not in inserted:
        inserted.add(section_key)
        for fname in SECTION_FOTO_MAP[section_key][:4]:
            fpath = os.path.join(FOTO_DIR, fname)
            if os.path.exists(fpath):
                add_image(doc, fpath)
            else:
                add_para(doc, f"[foto não encontrada: {fname}]", size=Pt(8))


def build_docx(md_file, out_file):
    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = Document()
    for sec in doc.sections:
        for attr in ("top_margin","bottom_margin","left_margin","right_margin"):
            setattr(sec, attr, Cm(2.5))

    # ── CAPA ──
    add_para(doc, "", size=Pt(12))
    add_para(doc, "AUTOVISTORIA PREDIAL", bold=True, size=Pt(16), align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "", size=Pt(8))
    add_para(doc, "CONDOMÍNIO JARDIM DAS FLORES", bold=True, size=Pt(13), align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "Rua João Lira, 15 — Leblon — Rio de Janeiro/RJ", size=Pt(10), align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "", size=Pt(12))
    add_para(doc, "Rio de Janeiro, Novembro de 2026.", size=Pt(10), align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_page_break()

    # ── CORPO ──
    current_section = ""
    inserted = set()
    skip_h1 = True
    i = 0

    while i < len(lines):
        line = lines[i].rstrip("\n")

        # Obsidian embed ![[...]]
        if line.strip().startswith("![["):
            i += 1; continue
        # Nota callout Obsidian > [!...]
        if line.strip().startswith("> [!"):
            i += 1; continue
        # Separador
        if line.strip() == "---":
            i += 1; continue

        # H1
        if line.startswith("# ") and not line.startswith("##"):
            if skip_h1:
                skip_h1 = False; i += 1; continue
            add_para(doc, line[2:].strip(), bold=True, size=FONT_H1)
            i += 1; continue

        # H2
        if line.startswith("## ") and not line.startswith("###"):
            text = line[3:].strip()
            add_para(doc, "", size=Pt(4))
            add_para(doc, text, bold=True, size=FONT_H2)
            for key in ("5.1","5.2","5.3","5.4","5.5","5.6","5.7","5.8","5.9","5.10"):
                if key in text:
                    current_section = key; break
            i += 1; continue

        # H3
        if line.startswith("### ") and not line.startswith("####"):
            add_para(doc, line[4:].strip(), bold=True, size=FONT_H3)
            i += 1; continue

        # H4 — insere imagens depois do título
        if line.startswith("#### "):
            text = line[5:].strip()
            add_para(doc, "", size=Pt(3))
            add_para(doc, text, bold=True, size=FONT_H4)
            for key in ("5.1.1","5.1.2","5.1.3","5.2.1","5.2.2","5.2.3",
                        "5.3","5.4","5.5","5.6","5.7","5.8","5.9","5.10"):
                if key in text:
                    insert_section_images(doc, key, inserted)
                    break
            i += 1; continue

        # Tabela |
        if line.strip().startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i].strip()); i += 1
            if len(tbl) >= 2:
                header = [c.strip() for c in tbl[0].split("|")[1:-1]]
                data   = [l for l in tbl[1:] if not re.match(r"^\|[\s:-]+\|$", l)]
                if header and data:
                    t = doc.add_table(rows=1+len(data), cols=len(header))
                    t.style = "Table Grid"
                    for j, h in enumerate(header):
                        r = t.rows[0].cells[j].paragraphs[0].add_run(h.replace("**",""))
                        set_font(r, bold=True, size=Pt(9))
                    for ri, dl in enumerate(data):
                        cells = [c.strip() for c in dl.split("|")[1:-1]]
                        for j, ct in enumerate(cells[:len(header)]):
                            r = t.rows[ri+1].cells[j].paragraphs[0].add_run(ct.replace("**",""))
                            set_font(r, size=Pt(8))
            continue

        # Blockquote >
        if line.strip().startswith(">"):
            text = line.strip()[1:].strip().replace("**","")
            p = add_para(doc, text, size=FONT_BODY)
            p.paragraph_format.left_indent = Cm(1)
            i += 1; continue

        # Bullet
        if re.match(r"^[\s]*[-*] ", line):
            text = re.sub(r"^[\s]*[-*] ", "", line).replace("**","")
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text); set_font(r, size=FONT_BODY)
            i += 1; continue

        # Numbered list
        if re.match(r"^[\s]*\d+\.\s", line.strip()):
            text = re.sub(r"^\d+\.\s", "", line.strip()).replace("**","")
            p = doc.add_paragraph(style="List Number")
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text); set_font(r, size=FONT_BODY)
            i += 1; continue

        # Texto normal
        if line.strip():
            text = line.strip()
            if "**" in text:
                p = doc.add_paragraph()
                p.paragraph_format.space_after  = Pt(4)
                p.paragraph_format.line_spacing = LINE_SPACE
                for idx, part in enumerate(text.split("**")):
                    if part:
                        r = p.add_run(part)
                        set_font(r, bold=(idx % 2 == 1), size=FONT_BODY)
            else:
                add_para(doc, text, size=FONT_BODY)

        i += 1

    doc.save(out_file)
    print(f"✅ Salvo: {out_file}  ({os.path.getsize(out_file)//1024} KB)")


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT_DOCX), exist_ok=True)
    if not os.path.exists(MD_FILE):
        print(f"❌ Laudo Markdown não encontrado: {MD_FILE}")
        print("   Crie primeiro o arquivo Laudo/Laudo_Jardim_das_Flores.md")
    else:
        build_docx(MD_FILE, OUT_DOCX)
