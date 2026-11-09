# 🔄 Pipeline de Produção do Laudo

## Visão geral

```
Fotos JPEG (iPhone)
        │
        ▼
[00] Preparar fotos      →  redimensionar, renomear, organizar por lote
        │
        ▼
[01] Analisar com IA     →  AWS Bedrock (Claude 3.5 Sonnet) analisa lote a lote
        │                   saída: Analise_Fotografica_Completa.md
        ▼
[02] Revisar análise     →  verificação de qualidade por amostragem
        │                   reprocessar lotes com nota < 7/10
        ▼
[03] Elaborar laudo MD   →  preencher ocorrências, prioridades, recomendações
        │                   Laudo_<Nome>.md (fonte da verdade)
        ▼
[04] Gerar DOCX (gerar_laudo_vN.py)
        │   Base: Model-01.docx (pages 1–2 intactas, dados substituídos)
        │   Conteúdo inserido a partir da Seção 3 (página 3 em diante)
        │   Script gera Laudo_<Nome>_vN.docx — nunca sobrescreve versões anteriores
        ▼
[05] ⚠️  ATUALIZAÇÃO MANUAL OBRIGATÓRIA — ver nota abaixo
        │
        ▼
[06] Revisar e commitar  →  branch dev → revisão → merge main
        │
        ▼
Laudo_<Nome>_vN.docx  ✅  entrega ao cliente
```

> ⚠️ **ATENÇÃO — ETAPA MANUAL OBRIGATÓRIA (Etapa 05)**
>
> O script gera o DOCX automaticamente a partir do Markdown, **mas as páginas 1 e 2
> devem ser revisadas e corrigidas manualmente pelo executor do laudo** antes da entrega.
>
> O script substitui os dados do modelo de referência (Solar Caravelas) pelos dados
> da nova vistoria, mas **não tem como saber** o que mudou no layout, formatação
> ou conteúdo específico das páginas 1 e 2 do Model-01.
>
> **O executor deve abrir o DOCX gerado e verificar manualmente:**
> - Página 1 — capa: nome do condomínio, endereço, código do laudo, data, RT, ART/RRT
> - Página 2 — Seções 1 e 2: tabela de identificação (todos os campos), texto do Objetivo
> - Qualquer dado residual do Solar Caravelas que o script não tenha substituído
> - Número da ART/RRT (sempre `XXXX` até o RT fornecer o número real)
>
> **Nenhuma versão do script substitui essa revisão humana.**

---

## Etapa 00 — Preparar fotos

**Script:** `Scripts/00_preparar_fotos.py`  
**Entrada:** Fotos originais do iPhone (3–6 MB cada, ~4032×3024 px)  
**Saída:** Fotos em `fotos_vistoria/` — 900px no lado maior, JPEG q65

```bash
.venv/bin/python Scripts/00_preparar_fotos.py
```

**Resultado Jardim das Flores:** 210 fotos originais → 12 fotos selecionadas (F01–F12)

---

## Etapa 01 — Análise fotográfica com AWS Bedrock

**Script:** `Scripts/01_analisar_fotos_bedrock.py`  
**Modelo:** `anthropic.claude-3-5-sonnet-20240620-v1:0`  
**Região:** `us-east-1`

O script divide as fotos em **lotes de 10** e envia para o Claude analisar cada sistema construtivo:
- Fachada e revestimentos externos
- Cobertura e impermeabilização
- Elementos de segurança (guarda-corpo, escadas)
- Instalações (gás, elétrica, hidráulica)
- Áreas comuns (garagem, academia, depósito)

**Saída:** `Laudo/Analise_Fotografica_Completa.md` com todas as ocorrências identificadas

### Credenciais AWS
```python
# CORRETO — variável de ambiente
import boto3, os
client = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

# ERRADO — nunca hardcoded
# aws_access_key_id='AKIA...'  ← não fazer isso
```

### Verificação de qualidade por amostragem
Após análise completa, verificar 3–5 lotes por agente paralelo:
- Nota ≥ 7/10 → aprovado
- Nota < 7/10 (ex: iluminação insuficiente) → reprocessar com inferência contextual

**Resultado Jardim das Flores:** 10 lotes verificados, qualidade ~85%, lote 023 (academia) reprocessado

---

## Etapa 02 — Elaborar o laudo Markdown

Arquivo: `Laudo/Laudo_<Nome>.md`

### Estrutura REAL do laudo (seções numeradas)
```
1. IDENTIFICAÇÃO DO IMÓVEL
2. OBJETIVO
3. LEGISLAÇÃO E NORMAS APLICÁVEIS
   3.1 Legislação
   3.2 Normas Técnicas (ABNT)
4. METODOLOGIA
5. SISTEMAS INSPECIONADOS E ANOMALIAS IDENTIFICADAS
   5.1 COBERTURA
   5.2 APARTAMENTO DE COBERTURA
   5.3 FACHADA
   5.4 PRISMA DE VENTILAÇÃO
   5.5 ESCADA DE INCÊNDIO E ROTAS DE SAÍDA
   5.6 SINALIZAÇÃO DE EMERGÊNCIA
   5.7 ELEVADORES E CASAS DE MÁQUINAS
   5.8 PAVIMENTOS 1º AO 3º ANDAR
   5.9 4º ANDAR
   5.10 ACADEMIA E DEPÓSITO
6. QUADRO RESUMO DE OCORRÊNCIAS
7. RECOMENDAÇÕES TÉCNICAS
   7.1 Ações imediatas (antes de qualquer outra providência)
   7.2 Curto prazo (P1) e Médio prazo (P2)
8. PARECER TÉCNICO
9. CONCLUSÃO
10. ENCERRAMENTO
ANEXOS (sem número de seção)
```

### Escala de prioridades (NBR 16747:2020)
| Prioridade | Cor | Prazo | Critério |
|:---|:---:|:---|:---|
| **P1** | 🔴 Vermelho | Imediato (≤ 30 dias) | Risco à segurança / vida |
| **P2** | 🟠 Laranja | Curto prazo (30–90 dias) | Comprometimento funcional |
| **P3** | 🟡 Amarelo | Médio prazo (90–180 dias) | Manutenção preventiva |

### Dados fixos — Jardim das Flores
```
Código do laudo:  LTVP-2026-JDF-015
Data da vistoria: 05/11/2026
Data de emissão:  08/11/2026
RT:               Eng.º Civil Rafael Mendes Cavalcanti
CREA-RJ:          2019114-7
Síndico:          Marcos Antônio Ferreira da Silva
ART/RRT:          XXXX ← preencher com número real
Total ocorrências: 20 (7×P1, 10×P2, 3×P3)
```

---

## Etapa 03 — Gerar DOCX v5 com papel timbrado + fotos

**Script:** `Scripts/gerar_laudo_v5.py`  
**Dependências:** `python-docx`, `Pillow`

```bash
# Rodar no servidor (sempre usar venv)
.venv/bin/python Scripts/gerar_laudo_v5.py
```

### O que o script faz
1. Lê `Laudo/Laudo_<Nome>.md` (fonte da verdade)
2. Cria documento Word com margens do padrão Time Designer:
   - Topo: 2,23 cm | Base: 1,65 cm | Esquerda: 3,0 cm | Direita: 2,0 cm
3. Insere header com `assets/header_logo.png`
4. Insere footer: endereço + paginação automática
5. Processa o Markdown → parágrafos, títulos, tabelas, listas
6. Insere fotos de `fotos_vistoria/` nas seções correspondentes
7. Aplica cores de prioridade (P1=vermelho, P2=laranja, P3=amarelo)
8. Salva em `Laudo/Laudo_<Nome>_v5.docx`

### Fotos incorporadas (Jardim das Flores)
| Arquivo | Sistema | Seção real |
|:---|:---|:---|
| F01_fachada.jpeg | Fachada | 5.3 FACHADA |
| F02_cobertura.jpeg | Cobertura | 5.1 COBERTURA |
| F03_guarda_corpo.jpeg | Guarda-corpo | 5.1 COBERTURA |
| F04_casa_maquinas.jpeg | Casa de máquinas | 5.7 ELEVADORES E CASAS DE MÁQUINAS |
| F05_escada.jpeg | Escadas | 5.5 ESCADA DE INCÊNDIO |
| F06_infiltracao.jpeg | Infiltração | 5.2 APARTAMENTO DE COBERTURA |
| F07_prisma.jpeg | Prisma | 5.4 PRISMA DE VENTILAÇÃO |
| F08_academia.jpeg | Academia/depósito | 5.10 ACADEMIA E DEPÓSITO |
| F09_garagem.jpeg | Garagem | 5.7 ELEVADORES E CASAS DE MÁQUINAS |
| F10_gas.jpeg | Instalações de gás | 5.7 (casa de máquinas / gás) |
| F11_revestimento.jpeg | Revestimentos | 5.3 FACHADA |
| F12_geral.jpeg | Vista geral | Capa / Seção 1 |

---

## Etapa 04 — Revisão e entrega

1. Abrir `Laudo_<Nome>_v5.docx` no Word / LibreOffice
2. Conferir: paginação, fotos, tabelas, dados do RT, ART/RRT
3. Preencher `ART/RRT: XXXX` com o número real
4. Fazer merge da branch `dev` → `main`
5. Entregar DOCX ao cliente + RT para assinatura

---

## Tempos estimados por etapa

| Etapa | Tempo estimado |
|:---|:---|
| Preparar fotos | 2–5 min |
| Análise Bedrock (~210 fotos, 21 lotes) | 15–30 min |
| Revisão análise | 10–15 min |
| Elaborar laudo MD | 60–120 min (com RT) |
| Gerar DOCX v5 | < 1 min |
| Revisão final | 15–30 min |
| **Total** | **~3–4 horas** |
