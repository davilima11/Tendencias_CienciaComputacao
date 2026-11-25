/* Versão web do DecifraBot: roda o mesmo código Python do projeto no navegador, com o Pyodide. */
(function () {
  "use strict";

  const $ = (seletor) => document.querySelector(seletor);
  const reduzirMovimento = window.matchMedia("(prefers-reduced-motion: reduce)");

  // ---------- Markdown seguro ----------
  const escaparHtml = (texto) => String(texto).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // respostas do bot podem ter pedaços do código do usuário: HTML vira texto, link só http(s), imagem não
  const markdownDoChat = new marked.Marked({
    renderer: {
      html(html) { return escaparHtml(typeof html === "string" ? html : html.text); },
      link(href, titulo, texto) { return /^https?:\/\//.test(href || "") ? false : texto; },
      image(href, titulo, texto) { return escaparHtml(texto || ""); },
    },
  });
  const markdownDosDocs = new marked.Marked();

  // texto com `código` entre crases, montado só com textContent (nunca vira HTML)
  function textoComCodigo(texto) {
    const fragmento = document.createDocumentFragment();
    for (const parte of String(texto).split(/(``.+?``|`[^`]+`)/)) {
      if (!parte) continue;
      const codigo = parte.match(/^``\s?(.+?)\s?``$/) || parte.match(/^`([^`]+)`$/);
      if (codigo) {
        const el = document.createElement("code");
        el.textContent = codigo[1];
        fragmento.append(el);
      } else {
        fragmento.append(document.createTextNode(parte));
      }
    }
    return fragmento;
  }

  // ---------- abas ----------
  const abas = [...document.querySelectorAll('[role="tab"]')];
  let docAtual = null;

  function selecionarAba(aba, focar) {
    for (const a of abas) {
      const ativa = a === aba;
      a.setAttribute("aria-selected", String(ativa));
      a.tabIndex = ativa ? 0 : -1;
      document.getElementById(a.dataset.painel).hidden = !ativa;
    }
    if (focar) aba.focus();
    if (aba.id === "aba-docs" && !docAtual) abrirDoc("1-especificacao");
  }

  abas.forEach((aba, i) => {
    aba.addEventListener("click", () => selecionarAba(aba));
    aba.addEventListener("keydown", (evento) => {
      const destino = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: abas.length - 1 }[evento.key];
      if (destino === undefined) return;
      evento.preventDefault();
      selecionarAba(abas[(destino + abas.length) % abas.length], true);
    });
  });

  // ---------- conversa ----------
  const log = $("#mensagens");
  const form = $("#form-chat");
  const campo = $("#campo");
  let ponte = null;

  function rolarParaFim() {
    log.scrollTo({ top: log.scrollHeight, behavior: reduzirMovimento.matches ? "auto" : "smooth" });
  }

  function novaMensagem(autor) {
    const mensagem = document.createElement("div");
    mensagem.className = autor === "bot" ? "msg msg-bot" : "msg msg-voce";
    const quem = document.createElement("span");
    quem.className = "quem";
    quem.textContent = autor === "bot" ? "DecifraBot" : "Você";
    const corpo = document.createElement("div");
    corpo.className = "corpo";
    mensagem.append(quem, corpo);
    log.append(mensagem);
    return corpo;
  }

  function caixa(classe, rotulo, texto) {
    const el = document.createElement("div");
    el.className = "caixa " + classe;
    if (rotulo) {
      const forte = document.createElement("strong");
      forte.textContent = rotulo + " ";
      el.append(forte);
    }
    el.append(textoComCodigo(texto));
    return el;
  }

  function mostrarDoUsuario(texto, resposta) {
    const corpo = novaMensagem("voce");
    if (resposta.acao === "bloquear_dado") {
      corpo.classList.add("apagada");
      corpo.textContent = "[mensagem apagada: tinha um dado sensível]";
    } else if (resposta.codigo_exibido) {
      // o que aparece na tela é o código já com as senhas escondidas
      const pre = document.createElement("pre");
      const code = document.createElement("code");
      code.textContent = resposta.codigo_exibido;
      pre.append(code);
      corpo.append(pre);
    } else {
      const p = document.createElement("p");
      p.textContent = texto;
      corpo.append(p);
    }
  }

  function mostrarDoBot(resposta) {
    const corpo = novaMensagem("bot");
    for (const aviso of resposta.avisos || []) corpo.append(caixa("info", "", aviso));

    if (resposta.tipo === "explicacao") {
      const resumo = document.createElement("p");
      resumo.className = "resumo";
      resumo.append(textoComCodigo(resposta.texto));
      corpo.append(resumo);

      const lista = document.createElement("ul");
      lista.className = "linhas";
      for (const linha of resposta.linhas) {
        const item = document.createElement("li");
        item.style.setProperty("--nivel", linha.nivel);
        if (linha.nivel > 0) item.classList.add("dentro");
        const numero = document.createElement("span");
        numero.className = "num";
        numero.textContent = `Linha ${linha.numero}:`;
        item.append(numero, " ", textoComCodigo(linha.texto));
        lista.append(item);
      }
      corpo.append(lista);

      for (const alerta of resposta.alertas) {
        corpo.append(caixa("alerta", `Atenção (linha ${alerta.numero}):`, alerta.texto + "."));
      }
      if (resposta.conceitos.length) {
        const conceitos = document.createElement("p");
        conceitos.className = "conceitos";
        conceitos.textContent = `Conceitos usados: ${resposta.conceitos.join(", ")}. Pergunte sobre qualquer um deles, ou peça "explica a linha 3".`;
        corpo.append(conceitos);
      }
    } else {
      const texto = document.createElement("div");
      texto.innerHTML = markdownDoChat.parse(resposta.texto);
      corpo.append(texto);
    }

    if (resposta.explicacao) {
      const detalhes = document.createElement("details");
      detalhes.className = "porque";
      const resumo = document.createElement("summary");
      resumo.textContent = "Por que o DecifraBot respondeu isso?";
      const explicacao = document.createElement("p");
      explicacao.textContent = resposta.explicacao;
      detalhes.append(resumo, explicacao);
      corpo.append(detalhes);
    }
  }

  // ---------- seletor de linguagem ----------
  const seletor = $("#seletor");
  const opcoes = [...seletor.querySelectorAll('input[name="linguagem"]')];

  // a tela sempre mostra a linguagem que o agente tem guardada (o "é javascript" também troca)
  function sincronizarSeletor(linguagem) {
    for (const opcao of opcoes) opcao.checked = opcao.value === linguagem;
    campo.placeholder = `Cole um código em ${linguagem} ou faça uma pergunta...`;
  }

  opcoes.forEach((opcao) => opcao.addEventListener("change", () => {
    if (!opcao.checked || !ponte) return;
    const resposta = JSON.parse(ponte.escolher_linguagem(opcao.value));
    sincronizarSeletor(opcao.value);
    if (resposta) {
      mostrarDoBot(resposta);
      rolarParaFim();
    }
  }));

  function enviar(texto) {
    if (!ponte || !texto.trim()) return;
    const resposta = JSON.parse(ponte.responder(texto));
    mostrarDoUsuario(texto, resposta);
    mostrarDoBot(resposta);
    if (resposta.linguagem_escolhida) sincronizarSeletor(resposta.linguagem_escolhida);
    rolarParaFim();
  }

  function mensagemSimples(texto) {
    mostrarDoBot({ tipo: "texto", texto, avisos: [] });
  }

  form.addEventListener("submit", (evento) => {
    evento.preventDefault();
    const texto = campo.value;
    campo.value = "";
    ajustarAltura();
    enviar(texto);
    campo.focus();
  });

  // o campo cresce conforme o texto (até quase metade do chat), em vez de mostrar barra de rolagem
  function ajustarAltura() {
    campo.style.height = "auto";
    const limite = document.querySelector(".chat").clientHeight * 0.45;
    campo.style.height = Math.min(campo.scrollHeight + 2, limite) + "px";
  }
  campo.addEventListener("input", ajustarAltura);

  campo.addEventListener("keydown", (evento) => {
    if (evento.key === "Enter" && !evento.shiftKey && !evento.isComposing) {
      evento.preventDefault();
      form.requestSubmit();
    }
  });

  $("#limpar").addEventListener("click", () => {
    ponte.limpar();
    log.replaceChildren();
    mensagemSimples(ponte.mensagem_inicial());
    campo.focus();
  });

  // ---------- carregar o Python no navegador ----------
  async function baixarTexto(caminho) {
    const resposta = await fetch(caminho);
    if (!resposta.ok) throw new Error(`${caminho}: ${resposta.status}`);
    return resposta.text();
  }

  async function iniciarPython() {
    const pyodide = await loadPyodide({ indexURL: new URL("pagina/bibliotecas/pyodide/", location.href).href });
    const arquivos = JSON.parse(await baixarTexto("pagina/arquivos.json"));
    const conteudos = await Promise.all(arquivos.map(async (caminho) => [caminho, await baixarTexto(caminho)]));
    for (const [caminho, texto] of conteudos) {
      const destino = caminho.startsWith("pagina/bibliotecas/")
        ? "/home/pyodide/bibliotecas/" + caminho.slice("pagina/bibliotecas/".length)
        : "/home/pyodide/app/" + caminho;
      pyodide.FS.mkdirTree(destino.slice(0, destino.lastIndexOf("/")));
      pyodide.FS.writeFile(destino, texto);
    }
    pyodide.runPython('import sys\nsys.path.insert(0, "/home/pyodide/app")\nsys.path.insert(0, "/home/pyodide/bibliotecas")');
    return pyodide.pyimport("decifra.ponte");
  }

  function montarExemplos() {
    const lugar = $("#exemplos");
    const exemplos = JSON.parse(ponte.exemplos());
    exemplos.push({ titulo: "o que é uma lista?", linguagem: null, codigo: "o que é uma lista?" });
    for (const exemplo of exemplos) {
      const botao = document.createElement("button");
      botao.type = "button";
      botao.textContent = exemplo.titulo;
      botao.addEventListener("click", () => {
        // o exemplo troca a linguagem antes de mandar o código
        if (exemplo.linguagem) {
          ponte.escolher_linguagem(exemplo.linguagem, false);
          sincronizarSeletor(exemplo.linguagem);
        }
        enviar(exemplo.codigo);
      });
      lugar.append(botao);
    }
  }

  mensagemSimples("Carregando o DecifraBot... Na primeira vez pode levar alguns segundos, porque o Python está sendo carregado no seu navegador.");
  iniciarPython()
    .then((modulo) => {
      ponte = modulo;
      log.replaceChildren();
      mensagemSimples(ponte.mensagem_inicial());
      montarExemplos();
      form.querySelectorAll("textarea, button, fieldset").forEach((el) => (el.disabled = false));
      sincronizarSeletor(ponte.linguagem_escolhida());
      $("#limpar").disabled = false;
    })
    .catch((erro) => {
      log.replaceChildren();
      mensagemSimples("Não consegui carregar o DecifraBot neste navegador. Se você abriu o arquivo direto do computador, rode `python -m http.server` na pasta do projeto e abra http://localhost:8000.");
      console.error(erro);
    });

  // ---------- documentação ----------
  const visor = $("#visor");
  const linksDocs = [...document.querySelectorAll("[data-doc]")];
  const DOCS = linksDocs.map((link) => link.dataset.doc);

  // os diagramas são escritos em mermaid, igual o GitHub mostra. A biblioteca (2,5 MB) só é
  // baixada quando a pessoa abre a documentação, para não atrasar o chat.
  let mermaidPronto = null;
  let contadorDiagramas = 0;
  function carregarMermaid() {
    if (!mermaidPronto) {
      mermaidPronto = new Promise((ok, falhou) => {
        const script = document.createElement("script");
        script.src = "pagina/bibliotecas/mermaid/mermaid.min.js";
        script.onload = () => {
          const cor = (nome) => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
          window.mermaid.initialize({
            startOnLoad: false,
            securityLevel: "strict",
            theme: "base",
            fontFamily: getComputedStyle(document.body).fontFamily,
            themeVariables: {
              darkMode: true,
              background: cor("--superficie"),
              primaryColor: cor("--elevado"),
              primaryTextColor: cor("--texto"),
              primaryBorderColor: cor("--destaque"),
              lineColor: cor("--texto-suave"),
              textColor: cor("--texto"),
              edgeLabelBackground: cor("--superficie"),
              actorBkg: cor("--elevado"),
              actorBorder: cor("--destaque"),
              actorTextColor: cor("--texto"),
              signalColor: cor("--texto-suave"),
              signalTextColor: cor("--texto"),
              noteBkgColor: cor("--tinta-fundo"),
              noteTextColor: cor("--tinta"),
              noteBorderColor: cor("--destaque"),
            },
          });
          ok(window.mermaid);
        };
        script.onerror = () => { mermaidPronto = null; falhou(new Error("mermaid não carregou")); };
        document.head.append(script);
      });
    }
    return mermaidPronto;
  }

  async function desenharDiagramas(id) {
    for (const codigo of visor.querySelectorAll("code.language-mermaid")) {
      const bloco = codigo.parentElement;
      try {
        const mermaid = await carregarMermaid();
        const { svg } = await mermaid.render(`diagrama-${++contadorDiagramas}`, codigo.textContent);
        if (docAtual !== id || !bloco.isConnected) return; // a pessoa já trocou de documento
        const figura = document.createElement("figure");
        figura.className = "diagrama";
        figura.innerHTML = svg;
        bloco.replaceWith(figura);
      } catch (erro) {
        // sem a biblioteca, o diagrama continua aparecendo como texto, que ainda dá para ler
        bloco.classList.add("diagrama-texto");
      }
    }
  }

  async function abrirDoc(id) {
    if (!DOCS.includes(id)) id = DOCS[0];
    docAtual = id;
    linksDocs.forEach((link) => {
      if (link.dataset.doc === id) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    try {
      const texto = await baixarTexto(`documentacao/${id}.md`);
      if (docAtual !== id) return; // a pessoa já clicou em outro documento
      visor.innerHTML = markdownDosDocs.parse(texto);
    } catch (erro) {
      visor.textContent = "Não consegui carregar este documento.";
      return;
    }
    visor.querySelectorAll("table").forEach((tabela) => {
      const caixaTabela = document.createElement("div");
      caixaTabela.className = "tabela";
      tabela.before(caixaTabela);
      caixaTabela.append(tabela);
    });
    visor.querySelectorAll("a[href]").forEach((link) => {
      const href = link.getAttribute("href");
      const outroDoc = href.match(/^(?:\.\/)?([\w-]+)\.md$/);
      if (outroDoc && DOCS.includes(outroDoc[1])) link.setAttribute("href", `#doc/${outroDoc[1]}`);
      else if (/^https?:/.test(href)) { link.target = "_blank"; link.rel = "noopener"; }
    });
    await desenharDiagramas(id);
  }

  function seguirEndereco() {
    const doc = location.hash.match(/^#doc\/([\w-]+)$/);
    if (!doc) return;
    docAtual = doc[1];
    selecionarAba($("#aba-docs"));
    abrirDoc(doc[1]).then(() => {
      visor.focus({ preventScroll: true });
      visor.scrollIntoView({ block: "start", behavior: reduzirMovimento.matches ? "auto" : "smooth" });
    });
  }

  window.addEventListener("hashchange", seguirEndereco);
  seguirEndereco();
})();
