# BRIEFING — Conversa com o Engenheiro
## Condomínio Jardim das Flores — Rua João Lira, 15

> **Para a IA (OpenClaw):** Este arquivo orienta a conversa a ser realizada com o engenheiro
> que fez a vistoria presencial. Com base nas respostas, preencher o
> `Laudo/Laudo_Jardim_das_Flores.md` e executar a Etapa 1 (análise fotográfica).

---

## O que já temos ✅

| Item | Situação |
|:---|:---|
| 210 fotos da vistoria | ✅ Em `Fotos_Organizadas/` |
| Metadados do imóvel (pesquisa web) | ✅ `METADADOS_IMOVEL.md` |
| Análise prévia por 4 modelos de IA | ✅ `Previa e Comparacao/` |
| 8 ocorrências identificadas pela IA | ✅ Ver quadro abaixo |
| Esqueleto do laudo em Markdown | ✅ `Laudo/Laudo_Jardim_das_Flores.md` |
| Script de análise fotográfica Bedrock | ✅ `Scripts/01_analisar_fotos_bedrock.py` |
| Script de geração DOCX | ✅ `Scripts/02_gerar_laudo_docx.py` |
| Normas e legislação RJ | ✅ `../Normas para Laudo de Autovistoria no Rio de Janeiro/` |

## O que falta ❌

| Item | Como obter |
|:---|:---|
| Dados do prédio (pavimentos, idade, estrutura) | **Conversa com engenheiro** |
| Anomalias reais observadas em campo | **Conversa com engenheiro** |
| Prioridades definitivas (P1/P2/P3) | **Conversa com engenheiro** |
| Nome do RT, CREA/CAU, ART/RRT | **Conversa com engenheiro** |
| Data da vistoria | **Conversa com engenheiro** |
| Síndico / solicitante | **Conversa com engenheiro** |
| Análise fotográfica Bedrock (nova rodada) | Rodar `Scripts/01_analisar_fotos_bedrock.py` |
| DOCX final | Rodar `Scripts/02_gerar_laudo_docx.py` |

---

## Ocorrências identificadas pela IA (base para a conversa)

A IA processou 210 fotos com 4 modelos diferentes. Estas são as principais flags —
o engenheiro deve confirmar, corrigir ou descartar cada uma.

| Código | Foto | O que a IA viu | Prioridade IA | Confirmar em campo |
|:---|:---|:---|:---:|:---|
| **OC-01** | IMG_1638 | Destacamento de revestimento/concreto no teto (garagem?) | 🟠 P1/P2 | Substrato, armadura exposta, extensão |
| **OC-02** | IMG_1472 | Fissuração vertical na fachada (modelos divergem) | 🟡 P2/IND | Existe a fissura? Material? Ativa? |
| **OC-03** | IMG_1609 | Fissuração em revestimento cerâmico (4 modelos convergem P2) | 🟠 P2 | Extensão, causa, aderência |
| **OC-04** | IMG_1484 | Guarda-corpo deteriorado / descontinuidade (P1 em 2 modelos) | 🔴 P1/P2 | Trecho, altura, fixação, risco de queda |
| **OC-05** | IMG_1669 | Invólucro elétrico corroído (caixa de medição?) | 🟠 P1/P2 | Equipamento, energizado, acesso |
| **OC-06** | IMG_1631 | Abrigo de hidrante com desgaste/sujidade | 🟠 P1/P2 | Sistema operacional? Projeto? |
| **OC-07** | IMG_1560 | Material armazenado junto a porta (rota de saída?) | 🟠 P1 | Porta corta-fogo? Obstrução real? |
| **OC-08** | IMG_1490 | Antenas / torre de telecom na cobertura | 🟡 P2 | Documentação operador, suporte |

**Fotos com P1 em múltiplos modelos (alta atenção):**
- IMG_1482, 1483, 1484 (guarda-corpo/borda)
- IMG_1498–1501, 1503 (cobertura/terraço — múltiplos P1)
- IMG_1507, 1510, 1513–1516, 1522, 1530, 1536, 1555 (verificar em campo)

---

## Perguntas para o engenheiro

### 📋 Dados gerais do prédio
1. Quantos pavimentos tem o prédio (incluindo subsolo, garagem, cobertura)?
2. Qual o ano de construção estimado (ou aparente)?
3. Qual o sistema estrutural: concreto armado convencional, paredes de concreto, alvenaria estrutural?
4. Qual o tipo de revestimento de fachada: cerâmico, argamassa pintada, pastilha, pedra, outro?
5. Quantos elevadores? Tem escada de incêndio? Tem gerador?
6. Tem piscina, sauna, academia em funcionamento?
7. Tem gás encanado (GLP/GN) ou botijão individual?
8. Nome do síndico e CNPJ do condomínio (se souber)?

### 🔴 Estrutura
9. Viu algum pilar ou viga com armadura exposta, fissura, desplacamento?
10. A garagem tem algum ponto de corrosão estrutural ou revestimento caindo?
11. As varandas apresentam infiltração, desplacamento, guarda-corpo corroído?
12. Há sinais de recalque (piso inclinado, fissuras em diagonal nas paredes)?

### 🟠 Fachada
13. O revestimento de fachada está aderente ou tem pontos soando oco?
14. Tem mapeamento de fissuras na fachada?
15. Os peitoris das janelas estão íntegros?
16. A fachada tem sistema de ancoragem para manutenção?

### ⚡ Elétrica / Gás / Incêndio
17. O quadro elétrico geral é moderno ou obsoleto (eletromecânico, sem disjuntores DR)?
18. Tem SPDA (para-raios) instalado e documentado?
19. Os extintores estão dentro da validade?
20. Os hidrantes têm mangueiras e registros em boas condições?
21. A sinalização de emergência está completa e visível?
22. As rotas de saída estão desobstruídas?

### 🛗 Elevadores
23. Quantos elevadores? Empresa mantenedora?
24. Tem relatório de manutenção recente?
25. Cabos, portas, nivelamento — algum problema visível?

### 🏠 Cobertura / terraço
26. A cobertura tem impermeabilização? Está em boas condições?
27. Tem reservatório de água (cisterna/caixa d'água)? Estado?
28. As antenas/torres têm documentação do operador?

### 📝 Dados do laudo
29. Qual é o nome completo do responsável técnico?
30. Qual o número do CREA ou CAU?
31. Qual foi a data da vistoria?
32. Há um número de laudo / documento técnico (ex: TD 071/2026)?

---

## Instruções para a IA após a conversa

1. **Preencher** todas as seções `⚠️ [AGUARDA DESCRIÇÃO DO ENGENHEIRO]` no `Laudo_Jardim_das_Flores.md`
2. **Atualizar** o Quadro Resumo de Ocorrências com as anomalias confirmadas
3. **Definir** as prioridades P1/P2/P3 com base no relato do engenheiro
4. **Rodar** `Scripts/01_analisar_fotos_bedrock.py` para análise completa das 210 fotos
5. **Redigir** o Parecer Técnico e Conclusão com base em tudo
6. **Rodar** `Scripts/02_gerar_laudo_docx.py` para gerar o DOCX final
