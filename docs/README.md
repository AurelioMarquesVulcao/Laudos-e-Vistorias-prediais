# 📚 Documentação do Projeto — Laudos e Vistorias Prediais

> **Time Designer** — Rio de Janeiro/RJ  
> Repositório de laudos técnicos de autovistoria predial (NBR 16747:2020)

---

## Índice

| Documento | Descrição |
|:---|:---|
| [ARQUITETURA.md](ARQUITETURA.md) | Estrutura do repositório, convenções e organização de pastas |
| [PIPELINE.md](PIPELINE.md) | Pipeline completo de produção de um laudo (fotos → DOCX) |
| [DESCRICAO_IMOVEL.md](DESCRICAO_IMOVEL.md) | Descrição física completa do imóvel vistoriado |
| [HISTORICO_EXECUCAO.md](HISTORICO_EXECUCAO.md) | Ordem cronológica de todos os passos executados no projeto |
| [ACERTOS.md](ACERTOS.md) | O que funcionou bem — com comandos e contexto para reproduzir |
| [ERROS.md](ERROS.md) | O que não funcionou — causa raiz e o que resolveu |
| [LICOES_APRENDIDAS.md](LICOES_APRENDIDAS.md) | Lições técnicas fixadas para vistorias futuras |
| [MODELO_LAUDO.md](MODELO_LAUDO.md) | Modelo completo do laudo — itens obrigatórios, com e sem laudo anterior |

---

## TL;DR — Como gerar um laudo novo

```bash
# 1. Clonar e entrar na branch dev
git clone https://github.com/AurelioMarquesVulcao/Laudos-e-Vistorias-prediais.git
git checkout dev

# 2. Criar pasta da nova vistoria
cp -r vistorias/joao-lira-15-jardim-das-flores vistorias/<novo-slug>

# 3. Copiar fotos para fotos_vistoria/ (via rsync/Tailscale — não vão ao Git)
rsync -avz -e "ssh -i ~/.ssh/id_ed25519_from_homelab" \
  aureliovemconveniencia@100.100.109.28:/caminho/fotos/ \
  vistorias/<novo-slug>/fotos_vistoria/

# 4. (Opcional) Preparar e redimensionar fotos
../.venv/bin/python vistorias/<novo-slug>/Scripts/00_preparar_fotos.py

# 5. Analisar fotos com Bedrock
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
../.venv/bin/python vistorias/<novo-slug>/Scripts/01_analisar_fotos_bedrock.py

# 6. Editar o laudo Markdown com as ocorrências

# 7. Gerar DOCX com papel timbrado + fotos
../.venv/bin/python vistorias/<novo-slug>/Scripts/gerar_laudo_v5.py

# 7. Commitar na branch dev
git add . && git commit -m "feat(<slug>): laudo vX — descrição"
git push origin dev

# Nota: venv está em ../.venv (um nível acima do repo)
# Fotos ficam locais — não vão ao Git (ver .gitignore em cada pasta de vistoria)
```
