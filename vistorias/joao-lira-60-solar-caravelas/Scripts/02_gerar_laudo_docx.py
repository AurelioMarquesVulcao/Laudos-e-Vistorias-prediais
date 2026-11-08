#!/usr/bin/env python3
"""
Gera laudo-04.docx:
- Texto do 'Laudo de vistoria v2.md'
- Imagens do laudo-03.docx nos tópicos correspondentes
- Formatação padronizada: Tahoma, tamanhos consistentes
"""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from copy import deepcopy
import re, os, io

BASE = os.path.dirname(os.path.abspath(__file__))
MD_FILE = os.path.join(BASE, "Laudo de vistoria v2.md")
SRC_DOCX = os.path.join(BASE, "laudo-03.docx")
OUT_DOCX = os.path.join(BASE, "laudo-04.docx")

FONT_NAME = "Tahoma"
FONT_BODY = Pt(10)
FONT_H1 = Pt(14)
FONT_H2 = Pt(12)
FONT_H3 = Pt(11)
FONT_H4 = Pt(10)
LINE_SPACING = Pt(14)

# === EXTRAIR IMAGENS DO LAUDO-03 ===
def extract_images_with_context(docx_path):
    """Extrai imagens do docx com contexto textual para mapeamento."""
    doc = Document(docx_path)
    images = []
    for i, para in enumerate(doc.paragraphs):
        for run in para.runs:
            drawings = run._element.findall('.//' + qn('wp:inline')) + run._element.findall('.//' + qn('wp:anchor'))
            for drawing in drawings:
                # Extrair blob da imagem
                blip = drawing.find('.//' + qn('a:blip'))
                if blip is not None:
                    rId = blip.get(qn('r:embed'))
                    if rId:
                        part = doc.part.related_parts.get(rId)
                        if part:
                            # Contexto: texto anterior
                            context = ''
                            for j in range(i-1, max(0, i-10), -1):
                                t = doc.paragraphs[j].text.strip()
                                if t and len(t) > 5:
                                    context = t
                                    break
                            images.append({
                                'blob': part.blob,
                                'content_type': part.content_type,
                                'context': context,
                                'para_idx': i
                            })
    return images

# === MAPEAR IMAGENS POR SEÇÃO ===
def map_images_to_sections(images):
    """Mapeia imagens para seções do laudo baseado no contexto."""
    section_map = {}
    for img in images:
        ctx = img['context'].lower()
        # Determinar seção baseado no contexto
        if '5.1.1' in ctx or 'pilar' in ctx or 'fissura estrutural' in ctx:
            key = '5.1.1'
        elif '5.1.2' in ctx or 'pórtico' in ctx or 'portão' in ctx:
            key = '5.1.2'
        elif '5.1.3' in ctx or 'varanda' in ctx and 'marquise' in ctx:
            key = '5.1.3'
        elif '5.2.2' in ctx or 'peitoril' in ctx:
            key = '5.2.2'
        elif '5.2.3' in ctx or 'guarda-corpo' in ctx or 'guardacorpo' in ctx:
            key = '5.2.3'
        elif '5.2.4' in ctx or ('armadura' in ctx and 'fachada' in ctx):
            key = '5.2.4'
        elif '5.2.5' in ctx or ('laje' in ctx and 'varanda' in ctx):
            key = '5.2.5'
        elif '5.8.1' in ctx or 'infiltra' in ctx and 'apto' in ctx:
            key = '5.8.1'
        elif '5.2.1' in ctx or 'mármore' in ctx or 'fixação mecânica' in ctx:
            key = '5.2.1'
        elif '5.3' in ctx or 'disjuntor' in ctx or 'elétric' in ctx:
            key = '5.3'
        elif '5.4' in ctx or 'gás' in ctx or 'tubulação' in ctx:
            key = '5.4'
        elif '5.5' in ctx or 'hidrante' in ctx or 'extintor' in ctx or 'mangueira' in ctx:
            key = '5.5'
        elif '5.6' in ctx or 'rota' in ctx or 'fuga' in ctx or 'sinalização' in ctx:
            key = '5.6'
        elif '5.7' in ctx or 'elevador' in ctx or 'máquina' in ctx or 'cabo' in ctx:
            key = '5.7'
        elif 'quadro resumo' in ctx or 'total' in ctx:
            key = 'quadro'
        elif 'recomend' in ctx:
            key = 'recomendacoes'
        elif 'parecer' in ctx or 'conclusão' in ctx:
            key = 'parecer'
        else:
            key = 'outros'
        
        if key not in section_map:
            section_map[key] = []
        section_map[key].append(img)
    
    return section_map

# === FORMATAR PARÁGRAFO ===
def set_font(run, bold=False, size=FONT_BODY, color=None):
    run.font.name = FONT_NAME
    run.font.size = size
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    # Forçar Tahoma para caracteres asiáticos também
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = run._element.makeelement(qn('w:rFonts'), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:ascii'), FONT_NAME)
    rFonts.set(qn('w:hAnsi'), FONT_NAME)
    rFonts.set(qn('w:cs'), FONT_NAME)

def add_paragraph(doc, text, bold=False, size=FONT_BODY, alignment=None, color=None):
    para = doc.add_paragraph()
    if alignment:
        para.alignment = alignment
    para.paragraph_format.space_after = Pt(4)
    para.paragraph_format.space_before = Pt(2)
    para.paragraph_format.line_spacing = LINE_SPACING
    run = para.add_run(text)
    set_font(run, bold=bold, size=size, color=color)
    return para

def add_image_from_blob(doc, blob, content_type, width=Inches(5)):
    """Insere imagem a partir de blob."""
    stream = io.BytesIO(blob)
    doc.add_picture(stream, width=width)
    # Centralizar
    last_para = doc.paragraphs[-1]
    last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# === PARSEAR MARKDOWN ===
def parse_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines

# === GERAR DOCUMENTO ===
def generate_docx():
    print("Extraindo imagens do laudo-03...")
    images = extract_images_with_context(SRC_DOCX)
    print(f"  {len(images)} imagens extraídas")
    
    section_map = map_images_to_sections(images)
    print(f"  Seções com imagens: {list(section_map.keys())}")
    
    print("Parseando Markdown v2...")
    lines = parse_md(MD_FILE)
    
    print("Gerando laudo-04.docx...")
    doc = Document()
    
    # Configurar margens
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
    
    # === CAPA ===
    add_paragraph(doc, "", size=Pt(12))
    add_paragraph(doc, "AUTOVISTORIA PREDIAL", bold=True, size=Pt(16), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "TD 071/2026", bold=True, size=Pt(14), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "", size=Pt(12))
    add_paragraph(doc, "Aos Cuidados do Síndico CONDOMINIO DO EDIFICIO SOLAR CARAVELAS", size=Pt(10), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "Endereço: Rua João Lira, 60 Leblon – Rio de Janeiro - RJ", size=Pt(10), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "Rio de Janeiro, 29 de Março de 2026.", size=Pt(10), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "", size=Pt(12))
    add_paragraph(doc, "©TIME DESIGNER 2019", size=Pt(8), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "Todos os direitos reservados.", size=Pt(8), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "", size=Pt(8))
    add_paragraph(doc, "TIME DESIGNER", bold=True, size=Pt(10), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "Rua Marechal Floriano, 38, sala 610", size=Pt(9), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "20080-007 - Rio de Janeiro – RJ", size=Pt(9), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "Fone / Fax: (21) 2223-1617", size=Pt(9), alignment=WD_ALIGN_PARAGRAPH.CENTER)
    
    doc.add_page_break()
    
    # === CORPO DO LAUDO (do Markdown) ===
    current_section = ''
    images_inserted = set()
    skip_first_heading = True  # Pular o título principal (já na capa)
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        
        # Pular linhas de imagem obsidian ![[...]]
        if line.strip().startswith('![['):
            i += 1
            continue
        
        # Pular nota de revisão (> **Revisão...)
        if line.strip().startswith('> **Revisão'):
            i += 1
            continue
            
        # Heading 1: # 
        if line.startswith('# ') and not line.startswith('##'):
            if skip_first_heading:
                skip_first_heading = False
                i += 1
                continue
            text = line[2:].strip()
            add_paragraph(doc, text, bold=True, size=FONT_H1)
            i += 1
            continue
        
        # Heading 2: ##
        if line.startswith('## ') and not line.startswith('###'):
            text = line[3:].strip()
            add_paragraph(doc, "", size=Pt(6))
            add_paragraph(doc, text, bold=True, size=FONT_H2)
            # Track section for image insertion
            if '5.1' in text and 'ESTRUTURA' in text.upper():
                current_section = '5.1'
            elif '5.2' in text and 'FACHADA' in text.upper():
                current_section = '5.2'
            elif '5.3' in text:
                current_section = '5.3'
            elif '5.4' in text:
                current_section = '5.4'
            elif '5.5' in text:
                current_section = '5.5'
            elif '5.6' in text:
                current_section = '5.6'
            elif '5.7' in text:
                current_section = '5.7'
            elif '6.' in text and 'QUADRO' in text.upper():
                current_section = 'quadro'
            elif '7.' in text:
                current_section = 'recomendacoes'
            elif '8.' in text:
                current_section = 'parecer'
            i += 1
            continue
        
        # Heading 3: ###
        if line.startswith('### ') and not line.startswith('####'):
            text = line[4:].strip()
            add_paragraph(doc, text, bold=True, size=FONT_H3)
            i += 1
            continue
        
        # Heading 4: ####
        if line.startswith('#### '):
            text = line[5:].strip()
            add_paragraph(doc, "", size=Pt(4))
            add_paragraph(doc, text, bold=True, size=FONT_H4)
            
            # Inserir imagens correspondentes após o título da subseção
            section_key = None
            if '5.1.1' in text:
                section_key = '5.1.1'
            elif '5.1.2' in text:
                section_key = '5.1.2'
            elif '5.1.3' in text:
                section_key = '5.1.3'
            elif '5.2.1' in text:
                section_key = '5.2.1'
            elif '5.2.2' in text:
                section_key = '5.2.2'
            elif '5.2.3' in text:
                section_key = '5.2.3'
            elif '5.2.4' in text:
                section_key = '5.2.4'
            elif '5.2.5' in text:
                section_key = '5.2.5'
            elif '5.8.1' in text:
                section_key = '5.8.1'
            elif '5.3.1' in text:
                section_key = '5.3'
            elif '5.4.1' in text:
                section_key = '5.4'
            elif '5.5.1' in text:
                section_key = '5.5'
            elif '5.6.1' in text:
                section_key = '5.6'
            elif '5.7.1' in text:
                section_key = '5.7'
            
            if section_key and section_key in section_map and section_key not in images_inserted:
                images_inserted.add(section_key)
                for img in section_map[section_key][:4]:
                    add_image_from_blob(doc, img['blob'], img['content_type'], width=Inches(4.5))
            
            i += 1
            continue
        
        # Separador ---
        if line.strip() == '---':
            i += 1
            continue
        
        # Tabela (|)
        if line.strip().startswith('|'):
            # Coletar todas as linhas da tabela
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            
            # Parsear tabela
            if len(table_lines) >= 2:
                # Remover linha separadora (|:---|)
                header = [c.strip() for c in table_lines[0].split('|')[1:-1]]
                data_lines = [l for l in table_lines[1:] if not re.match(r'^\|[\s:-]+\|$', l)]
                
                if header and data_lines:
                    cols = len(header)
                    table = doc.add_table(rows=1 + len(data_lines), cols=cols)
                    table.style = 'Table Grid'
                    
                    # Header
                    for j, h in enumerate(header):
                        cell = table.rows[0].cells[j]
                        cell.text = ''
                        run = cell.paragraphs[0].add_run(h.replace('**', ''))
                        set_font(run, bold=True, size=Pt(9))
                    
                    # Data
                    for row_idx, dl in enumerate(data_lines):
                        cells_text = [c.strip() for c in dl.split('|')[1:-1]]
                        for j, ct in enumerate(cells_text[:cols]):
                            cell = table.rows[row_idx + 1].cells[j]
                            cell.text = ''
                            run = cell.paragraphs[0].add_run(ct.replace('**', '').replace('🔴', '🔴').replace('🟠', '🟠'))
                            set_font(run, size=Pt(8))
            continue
        
        # Blockquote >
        if line.strip().startswith('>'):
            text = line.strip()[1:].strip().replace('**', '')
            para = add_paragraph(doc, text, bold=True, size=FONT_BODY)
            para.paragraph_format.left_indent = Cm(1)
            i += 1
            continue
        
        # Bullet point -
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            text = line.strip()[2:].replace('**', '')
            para = doc.add_paragraph(style='List Bullet')
            para.paragraph_format.space_after = Pt(2)
            run = para.add_run(text)
            set_font(run, size=FONT_BODY)
            i += 1
            continue
        
        # Numbered list
        if re.match(r'^\d+\.\s', line.strip()):
            text = re.sub(r'^\d+\.\s', '', line.strip()).replace('**', '')
            para = doc.add_paragraph(style='List Number')
            para.paragraph_format.space_after = Pt(2)
            run = para.add_run(text)
            set_font(run, size=FONT_BODY)
            i += 1
            continue
        
        # Bold paragraph **text**
        if line.strip().startswith('**') and line.strip().endswith('**'):
            text = line.strip()[2:-2]
            add_paragraph(doc, text, bold=True, size=FONT_BODY)
            i += 1
            continue
        
        # Regular text with possible bold markers
        if line.strip():
            text = line.strip()
            # Simple bold handling
            if '**' in text:
                para = doc.add_paragraph()
                para.paragraph_format.space_after = Pt(4)
                para.paragraph_format.line_spacing = LINE_SPACING
                parts = text.split('**')
                for idx, part in enumerate(parts):
                    if part:
                        run = para.add_run(part)
                        set_font(run, bold=(idx % 2 == 1), size=FONT_BODY)
            else:
                add_paragraph(doc, text, size=FONT_BODY)
            
            # Check if this is a "Prioridade" line — insert images after
            if 'Prioridade:' in text and 'CRÍTICO' in text:
                # Determine which section we're in and insert images
                for key in section_map:
                    if key == current_section or (key.startswith(current_section) if current_section else False):
                        if key not in images_inserted:
                            images_inserted.add(key)
                            for img in section_map[key][:3]:  # Max 3 images per section
                                add_image_from_blob(doc, img['blob'], img['content_type'], width=Inches(4.5))
                            break
        
        i += 1
    
    # Inserir imagens restantes que não foram colocadas
    remaining = []
    for key, imgs in section_map.items():
        if key not in images_inserted and key not in ('outros', 'quadro', 'recomendacoes', 'parecer'):
            remaining.extend(imgs[:2])
    
    print(f"  Imagens inseridas em seções: {len(images_inserted)}")
    print(f"  Imagens restantes não mapeadas: {len(remaining)}")
    
    doc.save(OUT_DOCX)
    print(f"\n✅ Salvo: {OUT_DOCX}")
    print(f"   Tamanho: {os.path.getsize(OUT_DOCX)/1024:.0f}KB")


if __name__ == "__main__":
    generate_docx()
