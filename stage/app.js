// Palco: desenha o estado e liga teclado + servidor. Funciona também sem servidor (só teclado).
(function () {
  "use strict";

  var TEMAS = window.CONTENT || [];
  var logic = window.StageLogic;
  var reduce = logic.makeReducer(TEMAS);
  var state = logic.initialState();
  var lastSeq = 0;
  var ws = null;
  var wsOpen = false;

  var screen = document.getElementById("screen");
  var statusEl = document.getElementById("status");
  var byMarker = {};
  TEMAS.forEach(function (t) { byMarker[t.marker] = t; });

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
  }

  function hostOf(url) {
    try { return new URL(url).hostname.replace(/^www\./, ""); } catch (e) { return url; }
  }

  function dots() {
    var wrap = el("div", "dots");
    TEMAS.forEach(function (t) {
      wrap.appendChild(el("span", "dot" + (state.visited.indexOf(t.marker) !== -1 ? " on" : "")));
    });
    return wrap;
  }

  function renderIdle() {
    screen.className = "screen idle";
    screen.appendChild(el("h1", "title", "Magnus Carlsen"));
    screen.appendChild(el("p", "hint", "Põe uma peça no centro do tabuleiro"));
    screen.appendChild(dots());
  }

  function renderTema() {
    var t = byMarker[state.marker];
    var e = t.ecras[state.idx];
    screen.className = "screen tema tipo-" + (e.tipo || "facto");
    var head = el("div", "head");
    head.appendChild(el("span", "tema-nome", t.tema));
    head.appendChild(el("span", "pos", (state.idx + 1) + " / " + t.ecras.length));
    screen.appendChild(head);

    var body = el("div", "body");
    if (e.tipo === "pergunta") body.appendChild(el("div", "tag", "Pergunta"));
    if (e.tipo === "resposta") body.appendChild(el("div", "tag", "Resposta"));
    if (e.titulo) body.appendChild(el("h2", "titulo", e.titulo));
    if (e.texto) body.appendChild(el("p", "texto", e.texto));
    if (e.imagem) {
      var img = el("img", "foto");
      img.src = e.imagem;
      img.alt = "";
      body.appendChild(img);
    }
    screen.appendChild(body);
    if (e.fonte) screen.appendChild(el("div", "fonte", "Fonte: " + hostOf(e.fonte)));
  }

  function renderFecho() {
    screen.className = "screen fecho";
    screen.appendChild(el("h1", "title", "Obrigado!"));
    var seen = {};
    var hosts = [];
    TEMAS.forEach(function (t) {
      (t.ecras || []).forEach(function (e) {
        if (e.fonte) {
          var h = hostOf(e.fonte);
          if (!seen[h]) { seen[h] = true; hosts.push(h); }
        }
      });
    });
    if (hosts.length) screen.appendChild(el("p", "fontes", "Fontes: " + hosts.join(", ")));
  }

  function render() {
    screen.textContent = "";
    if (!TEMAS.length) {
      screen.className = "screen idle";
      screen.appendChild(el("p", "hint", "Sem conteúdo. Corre: uv run python tools/build_content.py"));
    } else if (state.view === "tema") {
      renderTema();
    } else if (state.view === "fecho") {
      renderFecho();
    } else {
      renderIdle();
    }
    updateStatus();
  }

  function updateStatus() {
    statusEl.textContent = "servidor: " + (wsOpen ? "ligado" : "desligado (so teclado)") +
      " | seq " + lastSeq + " | " + state.view +
      (state.marker !== null ? " marcador " + state.marker + " ecra " + (state.idx + 1) : "");
  }

  function apply(ev) {
    state = reduce(state, ev);
    render();
  }

  // Com servidor: manda para lá e espera pelo eco (uma só fonte de verdade).
  // Sem servidor: aplica localmente.
  function emit(type, payload) {
    var ev = { type: type, payload: payload || {}, source: "stage" };
    if (wsOpen) {
      try { ws.send(JSON.stringify(ev)); return; } catch (e) { /* cai para local */ }
    }
    apply(ev);
  }

  function connect() {
    var url = (location.protocol === "https:" ? "wss://" : "ws://") + (location.host || "localhost:8000") + "/ws";
    try { ws = new WebSocket(url); } catch (e) { setTimeout(connect, 2000); return; }
    ws.onopen = function () { wsOpen = true; updateStatus(); };
    ws.onclose = function () { wsOpen = false; updateStatus(); setTimeout(connect, 2000); };
    ws.onerror = function () { try { ws.close(); } catch (e) { /* ignora */ } };
    ws.onmessage = function (m) {
      var msg;
      try { msg = JSON.parse(m.data); } catch (e) { return; }
      if (msg.kind === "snapshot") {
        state = logic.initialState();
        lastSeq = 0;
        msg.events.forEach(function (ev) {
          state = reduce(state, ev);
          lastSeq = Math.max(lastSeq, ev.seq || 0);
        });
        render();
      } else if (msg.kind === "event" && msg.event.seq > lastSeq) {
        lastSeq = msg.event.seq;
        apply(msg.event);
      }
    };
  }

  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey || e.altKey || e.metaKey) return;
    var k = e.key;
    if (k >= "1" && k <= "7") {
      emit("PIECE_ENTER", { marker: 9 + parseInt(k, 10) });   // tecla 1 = marcador 10 ... 7 = 16
    } else if (k === "0" || k === "Backspace" || k === "Escape") {
      emit("PIECE_EXIT", { marker: state.marker });
    } else if (k === "ArrowRight" || k === "PageDown" || k === " ") {
      emit("DIAL_STEP", { steps: 1 });
    } else if (k === "ArrowLeft" || k === "PageUp") {
      emit("DIAL_STEP", { steps: -1 });
    } else if (k === "r" || k === "R") {
      emit("RESET", {});
    } else if (k === "f" || k === "F") {
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
    } else if (k === "d" || k === "D") {
      statusEl.classList.toggle("show");
    } else {
      return;
    }
    e.preventDefault();
  });

  render();
  connect();
})();
