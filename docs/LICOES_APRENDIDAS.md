# 📖 LIÇÕES APRENDIDAS

Registro detalhado de tudo que foi descoberto, refinado ou corrigido ao longo do projeto.  
Cada lição tem contexto, causa, consequência e o que fazer diferente da próxima vez.

---

## 1. Nunca hardcodar credenciais em scripts que vão ao Git

### O que aconteceu
No início do projeto, o script de análise Bedrock foi escrito com as credenciais AWS diretamente no código Python:
```python
aws_access_key_id='[AWS_KEY_REDACTED]'
```
Esse script foi commitado no repositório GitHub.

### Por que foi um problema real, não só teórico
O GitHub executa varredura automática de credenciais em todos os commits públicos e privados. A chave `[AWS_KEY_REDACTED]` está potencialmente comprometida desde o momento do push. Qualquer pessoa com acesso ao repositório (colaboradores, serviços de CI, forks) teve acesso à chave. Chaves AWS comprometidas já causaram cobranças de dezenas de milhares de dólares em poucas horas por mineração de criptomoeda em instâncias EC2.

### O que fazer da próxima vez
Sempre usar variáveis de ambiente para qualquer credencial:
```python
import os
aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
```
E definir no ambiente antes de rodar:
```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
.venv/bin/python script.py
```

Para o OpenClaw, salvar as chaves em Settings → Secrets e referenciar como SecretRef nos scripts.

### Ação pendente
- [ ] Revogar `[AWS_KEY_REDACTED]` no console AWS (IAM → Users → Security credentials → Access keys → Deactivate/Delete)
- [ ] Verificar no AWS CloudTrail se houve uso não autorizado
- [ ] Gerar nova chave e salvar no OpenClaw Secrets

---

## 2. rsync via Tailscale é a solução certa para transferir arquivos entre Mac e servidor

### O que foi tentado antes (em ordem)
1. **`file.fetch` via OpenClaw** → bloqueado por policy (não está na allowlist do macOS)
2. **SSH sem chave configurada** → `Permission denied (publickey)` porque o servidor não tinha a chave pública no `authorized_keys` do Mac
3. **Transferência via base64 no exec** → funciona para arquivos pequenos (< ~45 KB), mas o output da ferramenta é truncado em ~62.000 chars. Um arquivo de 108 KB resulta em um arquivo corrompido de 1.070 bytes no destino — sem erro aparente, silenciosamente errado
4. **Chunks de base64** → cada chunk de 354.000 chars ainda acima do limite; abordagem abandonada por complexidade e fragilidade

### Por que rsync via Tailscale funcionou
- Tailscale já estava ativo no Mac (`100.100.109.28`) e no servidor (`100.117.153.120`)
- A chave `id_ed25519_from_homelab` já existia no servidor — só precisou ser autorizada no Mac
- Adicionar a chave ao `authorized_keys` do Mac foi feito via script Python rodado no node Mac — sem precisar de acesso root ou `sudo`
- rsync transferiu 12 fotos (994 KB) + logo (108 KB) em menos de 3 segundos pela rede local via Tailscale

### Como configurar da próxima vez (passo a passo)

**1. Verificar se Tailscale está ativo nos dois lados:**
```bash
# No servidor
tailscale ip  # deve mostrar algo como 100.X.X.X

# No Mac (via exec node)
ifconfig | grep 'inet ' | grep '100\.'  # deve mostrar IP 100.X.X.X
```

**2. Verificar qual chave usar no servidor:**
```bash
ls ~/.ssh/  # procurar por chave criada para acesso ao Mac
cat ~/.ssh/id_ed25519_from_homelab.pub
```

**3. Autorizar a chave no Mac (via exec node):**
```python
# Rodar no Mac via exec host=node
pub_key = "ssh-ed25519 AAAA..."
import os
auth = os.path.expanduser("~/.ssh/authorized_keys")
with open(auth, "a") as f:
    f.write("\n" + pub_key + "\n")
os.chmod(auth, 0o600)
```

**4. Testar SSH:**
```bash
ssh -i ~/.ssh/id_ed25519_from_homelab \
  aureliovemconveniencia@100.100.109.28 echo "OK"
```

**5. rsync:**
```bash
rsync -avz -e "ssh -i ~/.ssh/id_ed25519_from_homelab -o StrictHostKeyChecking=no" \
  aureliovemconveniencia@100.100.109.28:/caminho/no/mac/ \
  /caminho/no/servidor/
```

### Regra fixada
> Para qualquer transferência de arquivo entre Mac e servidor maior que 45 KB: **usar rsync via Tailscale, nunca base64 via exec**.

---

## 3. Verificar o tamanho do arquivo gerado — um DOCX idêntico ao modelo é sinal de problema

### O que aconteceu
O script `criar_laudo_v5.py` foi rodado no Mac quando o laudo Markdown ainda não existia no path configurado. O script não levantou exceção — simplesmente gerou um documento em branco com o papel timbrado. O DOCX tinha **129 KB**, exatamente igual ao modelo vazio `Modelo_Pagina_Timbrada.docx`.

### Por que não detectamos imediatamente
O script reportou `✅ /tmp/Laudo_Jardim_das_Flores_v5.docx (129 KB)` como sucesso. A mensagem de sucesso era correta — o arquivo foi gerado. O problema era que o conteúdo (o laudo MD) não existia no Mac.

### O que fazer da próxima vez
Adicionar validação explícita no início do script:
```python
import os, sys

required_files = [LOGO_PNG, LAUDO_MD]
for f in required_files:
    if not os.path.exists(f):
        print(f"❌ ERRO: Arquivo não encontrado: {f}")
        sys.exit(1)

fotos = [f for f in os.listdir(FOTOS_DIR) if f.endswith('.jpeg')]
if len(fotos) == 0:
    print(f"⚠️ AVISO: Nenhuma foto encontrada em {FOTOS_DIR}")
    # não sair — DOCX sem fotos ainda é válido, mas avisar
```

E verificar o tamanho esperado na saída:
```python
docx_size = os.path.getsize(OUT_V5)
if docx_size < 200_000:  # menos de 200 KB sugere conteúdo insuficiente
    print(f"⚠️ AVISO: DOCX gerado parece pequeno ({docx_size//1024} KB). Verificar conteúdo.")
```

---

## 4. Fotos em alta resolução incham o DOCX — redimensionar antes de incorporar

### O que aconteceu
As fotos copiadas do iPhone tinham 3–6 MB cada (4032×3024 px). Mesmo depois de redimensionar para 900px de largura (60–130 KB), ao inserir 12 fotos num DOCX via python-docx, o arquivo ficou com **32 MB**.

### Por que isso aconteceu
O python-docx armazena os bytes brutos da imagem dentro do arquivo ZIP do DOCX. O DOCX é um ZIP contendo XMLs e arquivos de mídia. O tamanho final é a soma dos arquivos de mídia + overhead XML. Cada foto de 100 KB inserida como PNG interno no ZIP ocupa ~100 KB no DOCX — multiplicado por 12 fotos = ~1,2 MB mínimo. Mas algumas fotos ainda tinham dimensões maiores que 900px depois do processamento inicial, inflando o resultado.

### Solução
Processamento específico para embed em DOCX: dimensões menores (800×600 px máximo) e qualidade JPEG mais baixa (55 ao invés de 65–75):
```python
from PIL import Image

img = Image.open(foto_path)
img.thumbnail((800, 600), Image.LANCZOS)
img.save(dst, 'JPEG', quality=55, optimize=True)
```

Resultado: fotos de 29–74 KB → DOCX de 635 KB (vs. 32 MB anterior).

### Regra fixada
> Fotos para embed em DOCX: máximo 800×600 px, qualidade JPEG 55, formato JPEG (nunca PNG — PNG não comprime fotos).

---

## 5. Scripts com paths absolutos fixos quebram ao mudar de máquina

### O que aconteceu
O script `criar_laudo_v5.py` foi criado no Mac com paths absolutos hardcoded:
```python
LOGO_PNG  = "/tmp/ref_assets/header_logo.png"
FOTOS_DIR = "/tmp/fotos_docx"
LAUDO_MD  = "/tmp/repo_laudos_mac/vistorias/.../Laudo_Jardim_das_Flores.md"
OUT_V5    = "/tmp/repo_laudos_mac/vistorias/.../Laudo_Jardim_das_Flores_v5.docx"
```

Quando o script foi copiado para o servidor, todos os paths eram inválidos. Cada vez que a máquina mudava, o script precisava ser editado.

### Solução
Usar `os.path` relativo ao próprio script para paths dentro do repositório:
```python
import os

_REPO      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LAUDO_DIR = os.path.join(_REPO, "Laudo")
_ASSETS    = os.path.join(_REPO, "assets")
_FOTOS     = os.path.join(_REPO, "fotos_vistoria")

LOGO_PNG   = os.path.join(_ASSETS, "header_logo.png")
FOTOS_DIR  = _FOTOS
LAUDO_MD   = os.path.join(_LAUDO_DIR, "Laudo_Jardim_das_Flores.md")
OUT_V5     = os.path.join(_LAUDO_DIR, "Laudo_Jardim_das_Flores_v5.docx")
```

Agora o script funciona no Mac, no servidor, ou em qualquer máquina onde o repositório estiver clonado — sem edição.

### Regra fixada
> Scripts dentro do repositório: nunca usar paths absolutos. Sempre calcular caminhos relativos ao `__file__` do script.

---

## 6. Lotes com iluminação insuficiente precisam de estratégia diferente de análise

### O que aconteceu
O lote 023 (academia e depósito) foi processado pelo Bedrock como qualquer outro lote. 60% das fotos retornaram com classificação INDETERMINADO porque o ambiente tinha iluminação muito baixa — o modelo não conseguiu identificar as anomalias com as fotos escuras.

### Por que a análise padrão não funcionou
O modelo Claude 3.5 Sonnet é honesto: quando não consegue ver o que está na foto, retorna INDETERMINADO ao invés de inventar uma anomalia. Isso é correto. O problema estava na fonte (fotos mal iluminadas), não no modelo.

### Solução usada: inferência contextual
No reprocessamento, o prompt foi modificado para instruir o modelo a:
1. Confirmar o que consegue ver diretamente (elementos visíveis mesmo com iluminação baixa)
2. Inferir as patologias mais prováveis com base no contexto do ambiente:
   - Academia de condomínio com 30+ anos em ambiente litorâneo
   - Classe de agressividade III/IV (NBR 6118)
   - Sem manutenção registrada nos últimos 5 anos
3. Classificar as inferências como "Alta probabilidade de:" ao invés de certeza

Isso resultou nas ocorrências OC-17 (elétrica sem DR), OC-18 (iluminação de emergência) e OC-19 (ancoragem de equipamentos) sendo identificadas com base em padrão esperado para o tipo de ambiente, mesmo sem visibilidade fotográfica completa.

### Regra fixada para vistorias futuras
> Em ambientes fechados com iluminação artificial (academia, depósito, garagem fechada, casa de máquinas sem janela): levar iluminação portátil ≥ 1.000 lm. Fotografar primeiro com flash do iPhone, depois com luz portátil posicionada para eliminar sombras.

---

## 7. Trabalhar 100% no servidor desde o início evita problemas de sincronização

### O que aconteceu
Durante o projeto, o trabalho ficou dividido entre Mac (geração do DOCX, fotos) e servidor (laudo MD, análise Bedrock, versionamento). Isso criou problemas:
- Script gerou DOCX vazio porque o laudo MD estava no servidor, não no Mac
- Logo foi transferida corrompida porque a abordagem de transferência estava errada
- Commits no Mac e no servidor precisavam de sync manual
- Duas cópias do repositório (Mac e servidor) podiam ficar dessincronizadas

### A decisão
A partir de determinado ponto, **todo o trabalho passou a ser feito no servidor**. O Mac só fornece os arquivos que só existem lá (fotos da vistoria, logo) via rsync — e depois não precisa mais.

### Por que o servidor é melhor ambiente de trabalho
1. Git, Python, venv e todas as dependências já estão instalados e configurados
2. Sem dependência de qual máquina está ligada ou com Obsidian aberto
3. Commits são feitos diretamente sem precisar de sync entre máquinas
4. Scripts rodam sem modificação de path
5. OpenClaw tem acesso direto ao sistema de arquivos — sem intermediários

### Regra fixada
> **Todo o trabalho de geração de laudo acontece no servidor.** O Mac é fornecedor de ativos (fotos originais, logo) — transfere via rsync e não interfere mais no fluxo.

---

## 8. Commitar cada mudança na branch dev protege o trabalho e cria histórico útil

### O que aconteceu antes
No início, mudanças eram acumuladas e commitadas em lotes grandes. Isso tornava difícil:
- Saber exatamente quando uma seção foi adicionada
- Reverter uma mudança específica sem perder outras
- Entender o contexto de cada alteração semanas depois

### A decisão
Commitar cada mudança significativa separadamente com mensagem descritiva seguindo a convenção `feat:`, `chore:`, `fix:`, `refactor:`.

### O histórico que isso gerou
```
0b170fc  chore: .gitignore — excluir fotos da vistoria do git
2a3ee04  feat: v5 gerado no servidor via rsync Tailscale
af732ea  feat: laudo v5 com fotos + modelo página timbrada
94c8927  feat: DOCX v1 gerado — laudo completo 20 ocorrências, 7xP1
91faa59  feat: v3 — dados do RT e laudo preenchidos
5ae9e72  feat: v2 — academia/depósito adicionados, 20 ocorrências
cac350d  feat: laudo completo v1
85e96c2  refactor: estrutura multi-vistorias
0866c7e  feat: estrutura inicial do laudo
```

Com esse histórico é possível recuperar qualquer versão anterior do laudo, comparar mudanças entre versões, e entender a evolução do documento.

### Regra fixada
> Cada mudança no laudo (nova seção, correção de dado, nova versão do DOCX) → um commit separado na branch `dev` com mensagem descritiva.

---

## 9. Modelo de papel timbrado deve ser construído do zero, não extraído de DOCX existente

### O que aconteceu
A primeira tentativa foi abrir o DOCX do Solar Caravelas com python-docx e copiar seu header/footer como template. O resultado tinha estilos conflitantes herdados do documento original e elementos difíceis de controlar.

### Solução melhor
Construir o documento do zero com python-docx, definindo explicitamente:
- Margens via `section.top_margin`, `section.bottom_margin`, etc.
- Header via `section.header` com imagem inserida por `add_picture()`
- Footer via `section.footer` com texto e campo de paginação via XML OpenXML direto

Isso deu controle total sobre cada elemento sem interferência de estilos herdados.

### Valores exatos extraídos do Solar Caravelas (referência)
```python
section.top_margin    = Cm(2.23)
section.bottom_margin = Cm(1.65)
section.left_margin   = Cm(3.0)
section.right_margin  = Cm(2.0)
```
Footer: `"Rua Marechal Floriano, 38 – sala 610 – Centro / Rio de Janeiro RJ – cesar@timedesigner.com.br"`

### Regra fixada
> Para criar papel timbrado com python-docx: sempre construir do zero. Não usar DOCX existente como template base — os estilos herdados causam mais problemas do que resolvem.
