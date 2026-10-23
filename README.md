# 🎬 Renomeador de Episódios

Painel visual em Python para renomear episódios de séries no padrão **`S02E01`, `S02E02`, `S02E03`…**, a partir de nomes bagunçados como:

```
The.Paper.S02E01.The.Best.of.Us.2160p.10bit.AMZN.WEB-DL.DDP5.1.HEVC-Vyndros.mkv
```

que viram simplesmente:

```
S02E01.mkv
```

Sem dependências externas: usa apenas a biblioteca padrão do Python (`tkinter`).

<!-- Adicione aqui um print da tela: ![Painel](docs/screenshot.png) -->

## ✨ Recursos

- Interface gráfica simples, em duas etapas:
  1. Escolher a **pasta** e a **temporada**
  2. Conferir a prévia e confirmar com **Sim / Não**
- Renomeia **apenas** os arquivos da temporada escolhida (os de outras temporadas não são tocados)
- Reconhece vários formatos de nome (veja a tabela abaixo)
- Mantém a extensão do arquivo, então funciona com vídeos e legendas (`.mkv`, `.mp4`, `.srt`…)
- Mostra uma tabela com **nome atual → novo nome** e como o episódio foi detectado
- Protege contra conflitos: se dois arquivos resultarem no mesmo nome, nada é alterado

## 📋 Requisitos

- Python 3.8 ou superior
- `tkinter` (já vem com o Python no Windows e no macOS)

No Linux, se necessário:

```bash
sudo apt install python3-tk
```

## 🚀 Como usar

```bash
git clone https://github.com/Thiago0liver/renameseries.git
cd renameseries
python rename.py
```

No Windows também é possível dar dois cliques no arquivo `rename.py`.

1. Clique em **Escolher...** e selecione a pasta dos episódios
2. Informe o número da temporada e clique em **Próximo**
3. Confira a prévia e clique em **Sim, renomear** (ou **Não, voltar** para ajustar)

## 🔎 Formatos reconhecidos

Exemplos usando a temporada **2**:

| Nome do arquivo | Resultado | Detectado por |
|---|---|---|
| `The.Paper.S02E01.The.Best.of.Us.2160p...mkv` | `S02E01.mkv` | `SxxExx` |
| `abracadabraS02E05.mkv` (texto colado antes) | `S02E05.mkv` | `SxxExx` |
| `The Paper 2x03.mkv` | `S02E03.mkv` | `1x01` |
| `The Paper - Episode 4.mp4` | `S02E04.mp4` | `Ep/E01` |
| `Show Ep05 1080p.mkv` / `E06.mkv` | `S02E05.mkv` / `S02E06.mkv` | `Ep/E01` |
| `S02E00 (15).mkv` | `S02E15.mkv` | `E00 + (nº)` |
| `07.mkv` / `The.Paper.08.2160p.x265.mkv` | `S02E07.mkv` / `S02E08.mkv` | `⚠ número solto` |

### Regras de numeração

- Episódios de **1 a 9** recebem zero à esquerda: `E01` … `E09`
- Do **10 em diante** o número fica sem zero extra: `E10`, `E45`, `E100`
- Quando o nome já traz a temporada (`S01E02`, `1x02`), o arquivo só é incluído se for a temporada escolhida
- No caso de **número solto**, o script ignora resolução (`2160p`), ano, codec (`x265`), `10bit` e canais de áudio (`5.1`). Esse método só vale para vídeos e legendas, e aparece marcado com `⚠` na prévia para você conferir

## ⚠️ Avisos

- A renomeação é feita direto no disco e **não tem desfazer**. Sempre confira a prévia antes de confirmar.
- Subpastas não são processadas, apenas os arquivos do nível da pasta escolhida.
- Se o nome do arquivo de destino já existir na pasta, aquele arquivo é pulado e listado no final.

## 🛠️ Estrutura

```
.
├── rename.py   # aplicação (interface + lógica de detecção)
└── README.md
```

## 🤝 Contribuindo

Encontrou um padrão de nome que não é reconhecido? Abra uma *issue* com o nome do arquivo de exemplo (ou um *pull request* adicionando o padrão na função `detectar`).

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
