"""Interface do DecifraBot em Streamlit. Para rodar: streamlit run app.py"""
import json
import re
from pathlib import Path

import streamlit as st

from decifra.agente import Agente

st.set_page_config(page_title="DecifraBot")
EXEMPLOS = json.loads((Path(__file__).parent / "dados" / "exemplos.json").read_text(encoding="utf-8"))
CODIGO_ENTRE_CRASES = re.compile(r"(``.+?``|`[^`]+`)")


def escapar(texto):
    """Evita que * e _ de dentro do texto virem negrito/itálico, sem mexer no que está entre crases."""
    partes = CODIGO_ENTRE_CRASES.split(texto)
    return "".join(p if CODIGO_ENTRE_CRASES.fullmatch(p) else re.sub(r"([*_])", r"\\\1", p) for p in partes)


def iniciar():
    st.session_state.agente = Agente()
    st.session_state.historico = [{"autor": "assistant", "resposta": {"tipo": "texto", "texto": st.session_state.agente.msgs["inicial"], "avisos": []}}]


def trocar_linguagem():
    """Seletor da lateral: se tinha código esperando a troca, ele é explicado agora."""
    resposta = st.session_state.agente.escolher_linguagem(st.session_state.seletor)
    if resposta:
        st.session_state.historico.append({"autor": "assistant", "resposta": resposta})


def enviar(texto):
    resposta = st.session_state.agente.responder(texto)
    if resposta["acao"] == "bloquear_dado":
        mensagem = {"autor": "user", "texto": "[mensagem apagada: tinha um dado sensível]", "codigo": None}
    elif resposta.get("codigo_exibido"):
        # o que aparece na tela é o código já com as senhas escondidas
        mensagem = {"autor": "user", "texto": None, "codigo": resposta["codigo_exibido"], "linguagem": resposta["linguagem"]}
    else:
        mensagem = {"autor": "user", "texto": texto, "codigo": None}
    st.session_state.historico += [mensagem, {"autor": "assistant", "resposta": resposta}]


def mostrar_resposta(r):
    for aviso in r.get("avisos", []):
        st.info(aviso)
    if r["tipo"] == "texto":
        st.markdown(r["texto"])
    else:
        st.markdown(f"**{escapar(r['texto'])}**")
        linhas = []
        for linha in r["linhas"]:
            recuo = "&nbsp;" * 6 * linha.nivel + ("↳ " if linha.nivel else "")
            linhas.append(f"{recuo}**Linha {linha.numero}:** {escapar(linha.texto)}")
        st.markdown("  \n".join(linhas))
        for numero, texto in r["resultado"].alertas:
            st.warning(f"**Atenção (linha {numero}):** {escapar(texto)}.")
        conceitos = [st.session_state.agente.conceitos[c]["titulo"] for c in r["resultado"].conceitos
                     if c in st.session_state.agente.conceitos]
        if conceitos:
            st.caption("Conceitos usados: " + ", ".join(conceitos) + ". Pergunte sobre qualquer um deles, "
                       "ou peça \"explica a linha 3\".")
    if r.get("explicacao"):
        with st.expander("Por que o DecifraBot respondeu isso?"):
            st.write(r["explicacao"])


if "agente" not in st.session_state:
    iniciar()

# o seletor sempre mostra a linguagem guardada no agente (o "é javascript" também troca)
st.session_state.seletor = st.session_state.agente.memoria.linguagem_escolhida

with st.sidebar:
    st.header("DecifraBot")
    st.write("Explica código em português, linha por linha, para quem está começando ou para quem recebeu "
             "um código pronto e quer entender o que ele faz.")
    st.radio("Linguagem do código", ["Python", "JavaScript"], key="seletor", horizontal=True,
             on_change=trocar_linguagem)
    st.write("**Eu não escrevo nem corrijo código.** Meu papel é te ajudar a entender.")
    st.subheader("Experimente")
    for exemplo in EXEMPLOS:
        if st.button(exemplo["titulo"], use_container_width=True):
            # o exemplo troca a linguagem antes de mandar o código
            st.session_state.agente.escolher_linguagem(exemplo["linguagem"], explicar_pendente=False)
            enviar(exemplo["codigo"])
            st.rerun()
    if st.button("o que é uma lista?", use_container_width=True):
        enviar("o que é uma lista?")
        st.rerun()
    st.caption("Senhas e chaves que estiverem no código são escondidas antes da análise. "
               "Nada fica salvo: ao fechar a página ou limpar a conversa, tudo é apagado.")
    if st.button("Limpar conversa"):
        iniciar()
        st.rerun()

st.title("DecifraBot")

for mensagem in st.session_state.historico:
    with st.chat_message(mensagem["autor"]):
        if mensagem["autor"] == "user":
            if mensagem.get("codigo"):
                st.code(mensagem["codigo"], language=(mensagem.get("linguagem") or "").lower() or None)
            else:
                st.markdown(escapar(mensagem["texto"]))
        else:
            mostrar_resposta(mensagem["resposta"])

entrada = st.chat_input("Cole um código ou faça uma pergunta...")
if entrada:
    enviar(entrada)
    st.rerun()
