// Lógica pura do palco: estado = reduce(eventos). Sem DOM, por isso é testável em Node.
(function (root) {
  "use strict";

  function initialState() {
    return { view: "idle", marker: null, idx: 0, visited: [], lastIdx: {} };
  }

  function makeReducer(temas) {
    var byMarker = {};
    temas.forEach(function (t) { byMarker[t.marker] = t; });
    function size(marker) {
      var t = byMarker[marker];
      return t && t.ecras ? t.ecras.length : 0;
    }

    return function reduce(state, ev) {
      var p = ev.payload || {};
      switch (ev.type) {
        case "RESET":
          return initialState();

        case "PIECE_ENTER": {
          if (state.view === "tema") return state;               // só entra com o hub livre
          if (!byMarker[p.marker] || size(p.marker) === 0) return state;
          var visited = state.visited.indexOf(p.marker) === -1
            ? state.visited.concat([p.marker]) : state.visited;
          return {
            view: "tema", marker: p.marker, idx: state.lastIdx[p.marker] || 0,
            visited: visited, lastIdx: state.lastIdx
          };
        }

        case "PIECE_EXIT": {
          if (state.view !== "tema") return state;
          if (p.marker !== undefined && p.marker !== null && p.marker !== state.marker) return state;
          var last = Object.assign({}, state.lastIdx);
          last[state.marker] = state.idx;                        // voltar ao tema retoma onde ficou
          var done = temas.length > 0 && state.visited.length >= temas.length;
          return {
            view: done ? "fecho" : "idle", marker: null, idx: 0,
            visited: state.visited, lastIdx: last
          };
        }

        case "DIAL_STEP": {
          if (state.view !== "tema") return state;
          var n = size(state.marker);
          var next = Math.max(0, Math.min(n - 1, state.idx + (p.steps | 0)));
          if (next === state.idx) return state;                  // sem dar a volta nos extremos
          return {
            view: "tema", marker: state.marker, idx: next,
            visited: state.visited, lastIdx: state.lastIdx
          };
        }

        default:
          return state;
      }
    };
  }

  var api = { initialState: initialState, makeReducer: makeReducer };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.StageLogic = api;
})(typeof window !== "undefined" ? window : this);
