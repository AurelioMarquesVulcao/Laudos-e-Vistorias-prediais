# Laudos e Vistorias Prediais
## Time Designer — Rio de Janeiro/RJ

Repositório de laudos técnicos de autovistoria predial (NBR 16747:2020).  
Cada vistoria tem sua própria pasta em `vistorias/`.

---

## Vistorias

| Pasta | Imóvel | Status | Laudo final |
|:---|:---|:---|:---|
| `joao-lira-60-solar-caravelas` | Edifício Solar Caravelas — Rua João Lira, 60 — Leblon/RJ | ✅ Concluído (Mai/2026) | `Saida/laudo-05.docx` |
| `joao-lira-15-jardim-das-flores` | Condomínio Jardim das Flores — Rua João Lira, 15 — Leblon/RJ | 🔄 Em elaboração | Aguarda conversa com RT |

---

## Estrutura padrão de cada vistoria

```
vistorias/<slug>/
├── README.md                    ← contexto e status da vistoria
├── BRIEFING_ENGENHEIRO.md       ← perguntas para o responsável técnico
├── Laudo/
│   ├── Laudo_<Nome>.md          ← laudo técnico em Markdown
│   ├── Analise_Fotografica_Completa.md  ← saída da análise IA
│   └── Comparativo_*.md         ← comparativo com laudo anterior (se houver)
├── Scripts/
│   ├── 01_analisar_fotos_bedrock.py  ← análise IA das fotos via AWS Bedrock
│   └── 02_gerar_laudo_docx.py        ← geração do DOCX final
└── Saida/
    └── laudo-XX.docx            ← versão final publicada
```

> **Fotos e PDFs pesados** ficam localmente no Obsidian vault — não são versionados aqui.

---

## Pipeline de produção

```
Fotos JPEG
    │
    ▼
01_analisar_fotos_bedrock.py  →  Analise_Fotografica_Completa.md
    │
    ▼
Conversa com engenheiro  →  Laudo_<Nome>.md (preenchido)
    │
    ▼
02_gerar_laudo_docx.py  →  Saida/laudo-XX.docx
```

---

## Legislação base (Rio de Janeiro)

- Lei Estadual nº 6.400/2013
- Lei Complementar Municipal nº 126/2013
- Decreto Municipal nº 37.426/2013
- ABNT NBR 16747:2020 — Inspeção predial
