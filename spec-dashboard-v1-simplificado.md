# Spec v1 (simplificado): Dashboard Streamlit com Sincronização via GitHub

## Objetivo

Versão inicial e enxuta do sistema, focada só no essencial: manter um dashboard Streamlit sempre atualizado com os dados de uma planilha Google Sheets, sincronizando automaticamente 1x por semana, com opção de forçar a sincronização manualmente pelo próprio dashboard.

**Fora de escopo nesta versão** (planejado para depois, em versões futuras):
- Geração de PDF (manual ou automática)
- Análise de dados com IA (Gemini)
- Upload de arquivos para o Google Drive
- GitHub Actions / Service Account do Google Cloud

---

## Arquitetura

```
┌───────────────────────┐
│    Google Sheets        │
│    (fonte de dados)     │
└───────────┬─────────────┘
            │ Apps Script
            │  - trigger semanal (segunda-feira)
            │  - Web App (doGet) p/ disparo manual
            ▼
┌───────────────────────┐
│   Repositório GitHub    │
│   /dados/planilha.csv   │
└───────────┬─────────────┘
            │ lido via raw.githubusercontent.com
            ▼
┌───────────────────────┐
│  Streamlit Community    │
│  Cloud (dashboard)      │
│  - exibe os dados        │
│  - botão "Sincronizar    │
│    agora" → chama o      │
│    Web App do Apps Script│
└───────────────────────┘
```

Duas formas de a planilha chegar até o dashboard:
1. **Automática**: toda segunda-feira, o Apps Script roda sozinho (trigger de tempo) e atualiza o CSV no GitHub.
2. **Manual**: alguém no dashboard clica em "Sincronizar agora" → isso chama uma URL (Web App do Apps Script) → o Apps Script atualiza o CSV no GitHub → o dashboard limpa o cache e recarrega os dados.

---

## Componente 1 — Google Apps Script

### Responsabilidades
- Exportar uma aba da planilha como CSV
- Criar ou atualizar esse CSV no repositório GitHub via API (commit direto)
- Expor uma URL (Web App) protegida por token, que permite disparar essa sincronização manualmente
- Rodar automaticamente 1x por semana via trigger de tempo

### Arquivo: `Code.gs`

```javascript
// ===== CONFIGURAÇÃO =====
// Rodar salvarConfiguracoes() UMA vez, com os valores corretos preenchidos abaixo
function salvarConfiguracoes() {
  const props = PropertiesService.getScriptProperties();
  props.setProperties({
    GITHUB_TOKEN: 'SEU_GITHUB_TOKEN_AQUI',
    GITHUB_REPO: 'usuario/nome-do-repo',
    GITHUB_BRANCH: 'main',
    CAMINHO_ARQUIVO: 'dados/planilha.csv',
    NOME_ABA: 'Sheet1',
    WEBHOOK_TOKEN: 'escolha-uma-senha-aleatoria-forte-aqui'
  });
}

// ===== FUNÇÃO PRINCIPAL: exporta a aba e envia pro GitHub =====
function enviarPlanilhaParaGitHub() {
  const props = PropertiesService.getScriptProperties();
  const TOKEN = props.getProperty('GITHUB_TOKEN');
  const REPO = props.getProperty('GITHUB_REPO');
  const BRANCH = props.getProperty('GITHUB_BRANCH');
  const CAMINHO_ARQUIVO = props.getProperty('CAMINHO_ARQUIVO');
  const NOME_ABA = props.getProperty('NOME_ABA');

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(NOME_ABA);
  const dados = sheet.getDataRange().getValues();

  const csv = dados.map(row =>
    row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
  ).join('\n');

  const conteudoBase64 = Utilities.base64Encode(csv, Utilities.Charset.UTF_8);
  const urlBase = `https://api.github.com/repos/${REPO}/contents/${CAMINHO_ARQUIVO}`;

  // Verifica se o arquivo já existe (necessário pegar o SHA para poder atualizar)
  let sha = null;
  try {
    const respGet = UrlFetchApp.fetch(urlBase, {
      headers: { Authorization: `token ${TOKEN}` },
      muteHttpExceptions: true
    });
    if (respGet.getResponseCode() === 200) {
      sha = JSON.parse(respGet.getContentText()).sha;
    }
  } catch (e) {
    // arquivo ainda não existe — sem problema, será criado
  }

  const payload = {
    message: `Sincronização automática - ${new Date().toISOString()}`,
    content: conteudoBase64,
    branch: BRANCH
  };
  if (sha) payload.sha = sha;

  const resp = UrlFetchApp.fetch(urlBase, {
    method: 'put',
    contentType: 'application/json',
    headers: { Authorization: `token ${TOKEN}` },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });

  Logger.log(resp.getContentText());
  return resp.getResponseCode();
}

// ===== WEB APP: permite disparo manual via URL (chamado pelo botão no Streamlit) =====
function doGet(e) {
  const TOKEN_SEGURANCA = PropertiesService.getScriptProperties().getProperty('WEBHOOK_TOKEN');

  if (!e.parameter.token || e.parameter.token !== TOKEN_SEGURANCA) {
    return ContentService.createTextOutput(
      JSON.stringify({ status: 'erro', mensagem: 'não autorizado' })
    ).setMimeType(ContentService.MimeType.JSON);
  }

  try {
    enviarPlanilhaParaGitHub();
    return ContentService.createTextOutput(
      JSON.stringify({ status: 'ok', mensagem: 'sincronizado', hora: new Date().toISOString() })
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ status: 'erro', mensagem: err.toString() })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}
```

### Configuração manual (feita na interface do Google, não é código)

1. Na planilha: **Extensões → Apps Script**, colar o código acima em `Code.gs`
2. Editar os valores dentro de `salvarConfiguracoes()` e rodar essa função **uma vez**
3. **Deploy → New deployment → Web app**
   - Execute as: `Me`
   - Who has access: `Anyone` (o token no parâmetro `?token=...` já protege o endpoint)
   - Copiar a URL gerada (termina em `.../exec`)
4. **Triggers (ícone de relógio) → Add Trigger**
   - Function: `enviarPlanilhaParaGitHub`
   - Event source: `Time-driven`
   - Type: `Week timer` → `Every Monday`, horário à escolha

---

## Componente 2 — Repositório GitHub

### Estrutura de pastas

```
repo/
├── dados/
│   └── planilha.csv        # atualizado pelo Apps Script (commit automático)
├── dashboard/
│   └── app.py               # app Streamlit
├── requirements.txt
└── .gitignore
```

### `.gitignore`

```
.streamlit/secrets.toml
__pycache__/
```

### Pré-requisito: Personal Access Token do GitHub

- GitHub → Settings → Developer settings → **Fine-grained tokens**
- Repository access: restrito só ao repositório usado neste projeto
- Permissão: **Contents: Read and write**
- Expiration: **1 ano** (máximo permitido em fine-grained tokens) — anotar a data de expiração em algum lembrete, pois não é possível criar token sem expiração

---

## Componente 3 — Dashboard Streamlit

### Responsabilidades
- Ler o CSV direto do GitHub (raw), com cache curto
- Exibir os dados/visualizações
- Botão "Sincronizar agora" → chama o Web App do Apps Script → limpa cache → recarrega os dados

### Arquivo: `dashboard/app.py`

```python
import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Dashboard", layout="wide")

REPO_RAW_URL = "https://raw.githubusercontent.com/usuario/repo/main/dados/planilha.csv"


@st.cache_data(ttl=60)
def carregar_dados():
    url = f"{REPO_RAW_URL}?t={int(time.time())}"  # evita servir versão em cache do CDN do GitHub
    return pd.read_csv(url)


st.title("Dashboard")

if st.button("🔄 Sincronizar agora"):
    with st.spinner("Sincronizando dados da planilha..."):
        try:
            resp = requests.get(
                st.secrets["APPS_SCRIPT_URL"],
                params={"token": st.secrets["APPS_SCRIPT_TOKEN"]},
                timeout=30
            )
            resultado = resp.json()
            if resultado.get("status") == "ok":
                st.cache_data.clear()
                st.success("Sincronizado! Atualizando...")
                st.rerun()
            else:
                st.error(f"Erro: {resultado.get('mensagem')}")
        except Exception as e:
            st.error(f"Falha na sincronização: {e}")

st.divider()

df = carregar_dados()
st.dataframe(df)

# TODO (próxima versão): gráficos com st.line_chart / st.bar_chart / plotly, etc.
```

### `.streamlit/secrets.toml` (configurar via "Secrets" no Streamlit Community Cloud — não versionar no Git)

```toml
APPS_SCRIPT_URL = "https://script.google.com/macros/s/XXXXX/exec"
APPS_SCRIPT_TOKEN = "escolha-uma-senha-aleatoria-forte-aqui"
```

---

## `requirements.txt`

```
streamlit
pandas
requests
```

---

## Checklist de configuração (ordem recomendada)

1. [ ] Criar repositório no GitHub com a estrutura de pastas acima
2. [ ] Gerar Personal Access Token do GitHub (fine-grained, `Contents: Read and write`, expiração de 1 ano)
3. [ ] Colar o código `Code.gs` no Apps Script da planilha
4. [ ] Rodar `salvarConfiguracoes()` uma vez, com os valores corretos
5. [ ] Publicar como Web App (Deploy → New deployment) e copiar a URL `.../exec`
6. [ ] Criar o trigger semanal (Time-driven → Week timer → Every Monday)
7. [ ] Testar `enviarPlanilhaParaGitHub()` manualmente pelo editor do Apps Script, conferir se o CSV aparece no repositório
8. [ ] Testar a URL do Web App direto no navegador (`.../exec?token=SEU_TOKEN`), conferir resposta `{"status":"ok",...}`
9. [ ] Publicar o app no Streamlit Community Cloud, apontando pra `dashboard/app.py`
10. [ ] Configurar Secrets no Streamlit Cloud: `APPS_SCRIPT_URL`, `APPS_SCRIPT_TOKEN`
11. [ ] Testar o botão "Sincronizar agora" no dashboard publicado

---

## O que fica de fora por enquanto (adicionar em versões futuras)

- Geração de PDF do dashboard (manual, via botão)
- Geração de PDF automático semanal
- Análise de dados com IA (Gemini) no relatório semanal
- Upload de relatórios para uma pasta do Google Drive
- Service Account do Google Cloud e GitHub Actions (só voltam a ser necessários quando o PDF/IA/Drive entrarem em cena)

Nenhuma etapa desta versão exige cartão de crédito — Apps Script, GitHub (conta free) e Streamlit Community Cloud cobrem tudo sem custo.
