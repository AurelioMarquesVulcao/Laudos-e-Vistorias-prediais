# 🏗️ Arquitetura do Projeto

## Estrutura de pastas

```
repo_laudos_work/
├── README.md                        ← visão geral do projeto
├── docs/                            ← documentação (esta pasta)
│   ├── README.md                    ← índice da documentação
│   ├── ARQUITETURA.md               ← este arquivo
│   ├── PIPELINE.md                  ← pipeline de produção
│   ├── ACERTOS.md                   ← o que funcionou bem
│   ├── ERROS.md                     ← o que não funcionou
│   ├── LICOES_APRENDIDAS.md         ← lições fixadas para futuras vistorias
│   └── MODELO_LAUDO.md              ← modelo completo do laudo
│
└── vistorias/
    ├── joao-lira-60-solar-caravelas/   ← Vistoria nº 60 (concluída)
    └── joao-lira-15-jardim-das-flores/ ← Vistoria nº 15 (em andamento)
        ├── .gitignore               ← exclui fotos e arquivos pesados
        ├── README.md                ← contexto e status da vistoria
        ├── BRIEFING_ENGENHEIRO.md   ← perguntas para o RT
        ├── assets/
        │   └── header_logo.png      ← logo Time Designer (108 KB)
        ├── fotos_vistoria/          ← fotos locais (NÃO vão ao Git)
        │   ├── F01_fachada.jpeg      ← redimensionadas para embed DOCX: 800×600px, q55
        │   ├── F02_cobertura.jpeg
        │   └── ... (12 fotos, 29–74 KB cada — otimizadas para DOCX)
        ├── Laudo/
        │   ├── Laudo_Jardim_das_Flores.md      ← laudo em Markdown (fonte da verdade)
        │   ├── Laudo_Jardim_das_Flores.docx    ← DOCX v1 (sem papel timbrado)
        │   ├── Laudo_Jardim_das_Flores_v5.docx ← DOCX v5 (com timbrado + fotos) ✅
        │   └── Modelo_Pagina_Timbrada.docx     ← template reutilizável
        └── Scripts/
            ├── 00_preparar_fotos.py            ← redimensiona fotos para análise
            ├── 01_analisar_fotos_bedrock.py    ← análise IA via AWS Bedrock
            ├── 02_gerar_laudo_docx.py          ← geração DOCX simples
            └── gerar_laudo_v5.py               ← geração DOCX com timbrado + fotos ✅
```

---

## Convenções de nomenclatura

### Slugs de vistoria
```
<rua>-<numero>-<nome-condominio>
```
Exemplos:
- `joao-lira-15-jardim-das-flores`
- `joao-lira-60-solar-caravelas`

### Versões do laudo
| Versão | Formato | Descrição |
|:---|:---|:---|
| `.md` | Markdown | Fonte da verdade — editável, versionável |
| `v1.docx` | DOCX | Primeira geração programática (sem timbrado) |
| `v5.docx` | DOCX | Com papel timbrado Time Designer + fotos incorporadas |

### Fotos na vistoria
- Nomenclatura: `F01_fachada.jpeg`, `F02_cobertura.jpeg`, …
- **Originais no Mac:** 3–6 MB cada (~4032×3024 px) — 210 fotos, ~999 MB total
- **Fotos para análise IA (Mac):** 900px no lado maior, qualidade 65–75 — `fotos_small/`
- **Fotos para embed no DOCX (servidor):** 800×600 px máximo, qualidade 55 — `fotos_vistoria/`
- **Nunca vão ao Git** — ficam locais no Mac e no servidor (sincronizadas via rsync/Tailscale)

---

## O que vai e o que não vai ao Git

| Item | Git? | Motivo |
|:---|:---:|:---|
| Laudo `.md` | ✅ | Texto leve, versionável |
| Laudo `.docx` final | ✅ | Artefato de entrega |
| Modelo timbrado | ✅ | Template reutilizável |
| Scripts `.py` | ✅ | Código reproduzível |
| `assets/header_logo.png` | ✅ | 108 KB, necessário para DOCX |
| Fotos originais (Mac) | ❌ | 210 fotos, ~999 MB — ficam no Mac e backup |
| Fotos vistoria no servidor | ❌ | 12 fotos, ~992 KB — excluídas via .gitignore |
| PDFs intermediários | ❌ | Gerados on-demand |
| Credenciais AWS | ❌ | Nunca hardcoded — usar `os.environ.get()` |
