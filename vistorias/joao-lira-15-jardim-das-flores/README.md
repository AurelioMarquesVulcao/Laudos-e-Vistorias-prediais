# Openclaw_Laudo — Condomínio Jardim das Flores
## Rua João Lira, 15 — Leblon/RJ

Pasta criada em 08/11/2026 pela OpenClaw para produção do laudo de autovistoria predial.

---

## Estrutura

```
Openclaw_Laudo/
├── README.md                    ← Este arquivo
├── BRIEFING_ENGENHEIRO.md       ← Roteiro de perguntas para a conversa com o RT
│
├── Fotos_Organizadas/           ← 210 fotos da vistoria (prontas para o script)
│   └── IMG_1472.jpeg … IMG_1681.jpeg
│
├── Laudo/
│   ├── Laudo_Jardim_das_Flores.md   ← Esqueleto do laudo (preencher após conversa)
│   └── Analise_Fotografica_Completa.md  ← Gerado pelo Script 01
│
├── Scripts/
│   ├── 00_preparar_fotos.py     ← Opcional: converter HEIC, reorganizar
│   ├── 01_analisar_fotos_bedrock.py  ← Análise IA das 210 fotos via AWS Bedrock
│   └── 02_gerar_laudo_docx.py   ← Gera laudo.docx a partir do Markdown
│
└── Saida/
    └── laudo_jardim_das_flores.docx  ← Gerado pelo Script 02
```

---

## Workflow — 3 etapas

### Etapa 0 — Conversa com o engenheiro (PRÓXIMO PASSO)
Abrir `BRIEFING_ENGENHEIRO.md` e fazer as perguntas ao responsável técnico.
Com as respostas, preencher as seções `⚠️` no `Laudo/Laudo_Jardim_das_Flores.md`.

### Etapa 1 — Análise fotográfica via IA
```bash
cd Scripts
python3 01_analisar_fotos_bedrock.py
```
- Lê todas as fotos de `Fotos_Organizadas/`
- Envia em lotes de 5 para o Claude via AWS Bedrock
- Salva resultado em `Laudo/Analise_Fotografica_Completa.md`
- **Pré-requisito:** credenciais AWS configuradas (ver o script)

### Etapa 2 — Geração do DOCX
```bash
cd Scripts
python3 02_gerar_laudo_docx.py
```
- Lê `Laudo/Laudo_Jardim_das_Flores.md`
- Insere imagens nos tópicos (configurar `SECTION_FOTO_MAP` no script)
- Salva `Saida/laudo_jardim_das_flores.docx`
- **Pré-requisito:** `pip3 install python-docx Pillow`

---

## Diferenças em relação ao Vistoria--60 (nº 60)

| Vistoria--60 | Jardim das Flores (nº 15) |
|:---|:---|
| 229 fotos | 210 fotos |
| Laudo anterior (2019) disponível | **Sem laudo anterior** — primeira vistoria |
| Imagens do DOCX extraídas do laudo-03 | Imagens direto de `Fotos_Organizadas/` |
| Script `gerar_laudo04.py` | Script `02_gerar_laudo_docx.py` (adaptado) |
| Fachada em mármore confirmada | Tipo de revestimento a confirmar em campo |
| Problema crítico: 7 anos sem correção | Situação atual desconhecida, sem histórico |

---

## O que os agentes de IA já fizeram antes desta pasta

Em outubro/2026, agentes processaram as 210 fotos com 4 modelos (Sonnet 4.5, Sonnet 4.6,
Nova Pro, Nova 2 Lite) em duas versões (V1 e V2). Resultados disponíveis em:

- `../Previa e Comparacao/RELATORIO_AUTOVISTORIA_JARDIM_DAS_FLORES_V02.md` — melhor consolidação
- `../Previa e Comparacao/MATRIZ_210_FOTOS.md` — prioridade foto a foto
- `../comparacao_modelos/` e `../comparacao_checklist_v2/` — dados brutos

**8 ocorrências foram pré-identificadas pela IA** (OC-01 a OC-08).
O engenheiro deve confirmar, expandir ou descartar cada uma.

---

## Status atual

- [x] Fotos organizadas (210 imagens)
- [x] Esqueleto do laudo criado
- [x] Scripts prontos (análise + DOCX)
- [x] Briefing de perguntas para o engenheiro
- [ ] **PRÓXIMO: Conversa com o engenheiro → preencher laudo**
- [ ] Rodar análise fotográfica Bedrock
- [ ] Revisar e completar laudo Markdown
- [ ] Gerar DOCX final
