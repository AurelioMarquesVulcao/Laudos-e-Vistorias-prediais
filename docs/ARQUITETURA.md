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
        │   ├── header_logo.png      ← logo Time Designer (108 KB)
        │   └── Model-01.docx        ← ⚠️ BASE DO DOCX FINAL — ver nota abaixo
        ├── fotos_vistoria/          ← fotos locais (NÃO vão ao Git)
        │   ├── F01_fachada.jpeg     ← redimensionadas para embed DOCX: 800×600px, q55
        │   ├── F02_cobertura.jpeg
        │   └── ... (12 fotos, 29–74 KB cada — otimizadas para DOCX)
        ├── Laudo/
        │   ├── Laudo_Jardim_das_Flores.md      ← laudo em Markdown (fonte da verdade)
        │   ├── Laudo_Jardim_das_Flores.docx    ← DOCX v1 (sem papel timbrado, histórico)
        │   ├── Laudo_Jardim_das_Flores_v5.docx ← DOCX v5 (histórico)
        │   ├── Laudo_Jardim_das_Flores_v6.docx ← DOCX v6 (histórico)
        │   ├── Laudo_Jardim_das_Flores_v7.docx ← DOCX v7 ✅ versão atual
        │   └── Modelo_Pagina_Timbrada.docx     ← template auxiliar
        └── Scripts/
            ├── 00_preparar_fotos.py            ← redimensiona fotos para análise
            ├── 01_analisar_fotos_bedrock.py    ← análise IA via AWS Bedrock
            ├── 02_gerar_laudo_docx.py          ← geração DOCX simples (v1)
            ├── gerar_laudo_v5.py               ← histórico
            ├── gerar_laudo_v6.py               ← histórico
            └── gerar_laudo_v7.py               ← geração DOCX atual ✅
```

---

## ⚠️ Model-01.docx — base do DOCX final (atualização manual obrigatória)

O arquivo `assets/Model-01.docx` é o **modelo de referência oficial** da Time Designer.
Ele contém as **2 primeiras páginas do laudo** com:
- Papel timbrado completo (header com logo, footer com endereço e paginação)
- Estilos tipográficos oficiais (Heading 1/2/3, cores, margens)
- Página 1 — capa: código do laudo, data, RT, ART/RRT, síndico
- Página 2 — Seções 1 e 2: Identificação do Imóvel + Objetivo

O script `gerar_laudo_vN.py` abre esse arquivo como base, **substitui automaticamente**
os dados do modelo de referência (Solar Caravelas) pelos dados da nova vistoria,
e **acrescenta o conteúdo a partir da Seção 3** (página 3 em diante).

### 🔴 ATENÇÃO — O executor do laudo DEVE revisar manualmente o DOCX gerado

> **O script não substitui a revisão humana das páginas 1 e 2.**
>
> Após rodar `gerar_laudo_vN.py`, o executor obrigatoriamente deve:
>
> 1. **Abrir o DOCX gerado** no Word ou LibreOffice
> 2. **Página 1 — verificar e corrigir:**
>    - Nome do condomínio e endereço
>    - Código do laudo (formato `LTVP-AAAA-XXX-NNN`)
>    - Data de emissão
>    - Nome e CREA/CAU do Responsável Técnico
>    - **Número da ART/RRT** — sempre fica `XXXX` até o RT fornecer o número real
> 3. **Página 2 — verificar e corrigir:**
>    - Tabela de Identificação do Imóvel (todos os campos)
>    - Texto da Seção 2 — Objetivo
>    - Qualquer dado residual do modelo de referência que o script não tenha substituído
> 4. **Salvar como nova versão** (`_v8`, `_v9`, etc.) — **nunca sobrescrever** a versão anterior
>
> Esse passo é manual, intencional e insubstituível. Nenhuma versão futura do script
> poderá garantir que todas as variações entre vistorias sejam capturadas automaticamente.

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
