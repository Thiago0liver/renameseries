#!/usr/bin/env python3
"""
Painel visual para renomear episódios no formato S02E01, S02E02, etc.

Etapa 1: escolher a pasta e a temporada
Etapa 2: ver a prévia e confirmar (Sim / Não)

Uso: python painel_renomear.py
(precisa apenas do Python com tkinter, que já vem instalado no Windows e no macOS)
"""

import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

EXT_MIDIA = {".mkv", ".mp4", ".avi", ".mov", ".m4v", ".wmv", ".ts",
             ".srt", ".ass", ".ssa", ".sub", ".vtt"}

P_SXXEXX = re.compile(r"S(\d{1,2})[\s._-]?E(\d{1,4})(?![0-9])", re.I)
P_NXNN = re.compile(r"(?<![A-Za-z0-9])(\d{1,2})x(\d{2,4})(?![A-Za-z0-9])", re.I)
P_EP = re.compile(
    r"(?<![A-Za-z0-9])(?:epis[oó]dio|episode|ep|cap[ií]tulo|cap|e)[\s._-]*(\d{1,4})(?![A-Za-z0-9])",
    re.I,
)
# trechos que parecem número mas não são episódio (resolução, ano, codec, áudio...)
LIXO = [
    r"\b(?:2160|1080|720|576|480)[pi]\b",
    r"\b[xh]\.?26[45]\b",
    r"\b\d+\s?bit\b",
    r"(?:dd\+?|ddp|aac|ac3|dts|atmos)?[257]\.[01]",
    r"\b(?:19|20)\d{2}\b",
]
P_PARENTESES = re.compile(r"\((\d{1,4})\)")
P_SOLTO = re.compile(r"(?<![A-Za-z0-9])(\d{1,4})(?![A-Za-z0-9])")


def detectar(arquivo, temporada):
    """
    Descobre o número do episódio no nome do arquivo.
    Retorna (episodio, metodo) ou None se não for da temporada / não achar número.
    """
    nome = arquivo.stem

    m = P_SXXEXX.search(nome)
    if m:
        if int(m.group(1)) != temporada:
            return None
        ep = int(m.group(2))
        if ep == 0:
            # caso "S02E00 (15).mkv": o número real do episódio está entre parênteses
            par = P_PARENTESES.findall(nome)
            if par:
                return int(par[-1]), "E00 + (nº)"
        return ep, "SxxExx"

    m = P_NXNN.search(nome)
    if m:
        if int(m.group(1)) != temporada:
            return None
        return int(m.group(2)), "1x01"

    m = P_EP.search(nome)
    if m:
        return int(m.group(1)), "Ep/E01"

    # último recurso: número solto (só em vídeos e legendas)
    if arquivo.suffix.lower() in EXT_MIDIA:
        limpo = nome
        for lixo in LIXO:
            limpo = re.sub(lixo, " ", limpo, flags=re.I)
        limpo = re.sub(r"[._]", " ", limpo)
        m = P_SOLTO.search(limpo)
        if m:
            return int(m.group(1)), "⚠ número solto"

    return None


class Painel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Renomear episódios")
        self.geometry("760x500")
        self.minsize(640, 420)

        self.pasta = tk.StringVar()
        self.temporada = tk.StringVar(value="1")
        self.renomeios = []
        self.metodos = {}

        estilo = ttk.Style(self)
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 15, "bold"))
        estilo.configure("Sub.TLabel", font=("Segoe UI", 10))
        estilo.configure("Grande.TButton", font=("Segoe UI", 11), padding=8)

        self.container = ttk.Frame(self, padding=24)
        self.container.pack(fill="both", expand=True)

        self.etapa1()

    # ---------- utilidades ----------
    def limpar(self):
        for w in self.container.winfo_children():
            w.destroy()

    def escanear(self, pasta, temporada):
        """Retorna lista de (arquivo_antigo, caminho_novo) da temporada escolhida."""
        achados = []
        self.metodos = {}
        for arq in pasta.iterdir():
            if not arq.is_file():
                continue
            r = detectar(arq, temporada)
            if not r:
                continue
            ep, metodo = r
            achados.append((ep, arq))
            self.metodos[arq] = metodo
        if not achados:
            return []
        # 1 a 9 -> E01..E09 | 10 em diante -> sem zero à esquerda (E10, E45, E100)
        achados.sort(key=lambda x: (x[0], x[1].name))
        return [
            (arq, pasta / f"S{temporada:02d}E{ep:02d}{arq.suffix.lower()}")
            for ep, arq in achados
        ]

    # ---------- etapa 1 ----------
    def etapa1(self):
        self.limpar()
        f = self.container

        ttk.Label(f, text="Etapa 1 de 2", style="Sub.TLabel").pack(anchor="w")
        ttk.Label(f, text="Qual temporada você quer renomear?", style="Titulo.TLabel").pack(
            anchor="w", pady=(0, 20)
        )

        ttk.Label(f, text="Pasta dos episódios:").pack(anchor="w")
        linha = ttk.Frame(f)
        linha.pack(fill="x", pady=(4, 16))
        ttk.Entry(linha, textvariable=self.pasta).pack(side="left", fill="x", expand=True)
        ttk.Button(linha, text="Escolher...", command=self.escolher_pasta).pack(
            side="left", padx=(8, 0)
        )

        ttk.Label(f, text="Temporada:").pack(anchor="w")
        ttk.Spinbox(f, from_=1, to=99, width=6, textvariable=self.temporada,
                    font=("Segoe UI", 14)).pack(anchor="w", pady=(4, 24))

        ttk.Button(f, text="Próximo  ›", style="Grande.TButton",
                   command=self.ir_etapa2).pack(anchor="e", side="bottom")

    def escolher_pasta(self):
        p = filedialog.askdirectory(title="Escolha a pasta dos episódios")
        if p:
            self.pasta.set(p)

    def ir_etapa2(self):
        pasta = Path(self.pasta.get())
        if not pasta.is_dir():
            messagebox.showwarning("Pasta inválida", "Escolha uma pasta válida.")
            return
        try:
            temporada = int(self.temporada.get())
        except ValueError:
            messagebox.showwarning("Temporada inválida", "Digite um número para a temporada.")
            return

        self.renomeios = self.escanear(pasta, temporada)
        if not self.renomeios:
            messagebox.showinfo(
                "Nada encontrado",
                f"Nenhum episódio da temporada {temporada:02d} foi encontrado nessa pasta.",
            )
            return

        novos = [n for _, n in self.renomeios]
        if len(novos) != len(set(novos)):
            messagebox.showerror(
                "Conflito",
                "Dois ou mais arquivos resultariam no mesmo nome. Nada foi alterado.",
            )
            return

        self.etapa2(temporada)

    # ---------- etapa 2 ----------
    def etapa2(self, temporada):
        self.limpar()
        f = self.container

        ttk.Label(f, text="Etapa 2 de 2", style="Sub.TLabel").pack(anchor="w")
        ttk.Label(
            f,
            text=f"Renomear todos os {len(self.renomeios)} arquivos da temporada {temporada:02d}?",
            style="Titulo.TLabel",
        ).pack(anchor="w", pady=(0, 12))

        # botões primeiro (ficam sempre visíveis embaixo)
        botoes = ttk.Frame(f)
        botoes.pack(side="bottom", fill="x", pady=(16, 0))
        ttk.Button(botoes, text="Sim, renomear", style="Grande.TButton",
                   command=self.confirmar).pack(side="right")
        ttk.Button(botoes, text="Não, voltar", style="Grande.TButton",
                   command=self.etapa1).pack(side="right", padx=(0, 8))

        colunas = ("antes", "depois", "como")
        tabela = ttk.Treeview(f, columns=colunas, show="headings")
        tabela.heading("antes", text="Nome atual")
        tabela.heading("depois", text="Novo nome")
        tabela.heading("como", text="Detectado por")
        tabela.column("antes", width=380)
        tabela.column("depois", width=110)
        tabela.column("como", width=120)
        for antigo, novo in self.renomeios:
            tabela.insert("", "end", values=(antigo.name, novo.name, self.metodos.get(antigo, "")))

        barra = ttk.Scrollbar(f, orient="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=barra.set)
        tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="left", fill="y")

    def confirmar(self):
        feitos, pulados = 0, []
        for antigo, novo in self.renomeios:
            if novo.exists() and novo != antigo:
                pulados.append(novo.name)
                continue
            try:
                antigo.rename(novo)
                feitos += 1
            except OSError as e:
                pulados.append(f"{antigo.name} ({e})")

        msg = f"{feitos} arquivo(s) renomeado(s) com sucesso."
        if pulados:
            msg += "\n\nNão foi possível renomear:\n" + "\n".join(pulados)
        messagebox.showinfo("Concluído", msg)
        self.etapa1()


if __name__ == "__main__":
    Painel().mainloop()