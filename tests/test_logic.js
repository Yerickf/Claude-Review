// Corre com: node tests/test_logic.js
const assert = require("assert");
const L = require("../stage/logic.js");

const temas = [
  { marker: 10, ecras: [{}, {}, {}] },
  { marker: 11, ecras: [{}, {}] },
];
const reduce = L.makeReducer(temas);
const ev = (type, payload) => ({ type, payload });
let s = L.initialState();

s = reduce(s, ev("PIECE_ENTER", { marker: 99 }));            // marcador desconhecido
assert.strictEqual(s.view, "idle");

s = reduce(s, ev("PIECE_ENTER", { marker: 10 }));
assert.strictEqual(s.view, "tema");
assert.strictEqual(s.idx, 0);

s = reduce(s, ev("PIECE_ENTER", { marker: 11 }));            // outro tema com o hub ocupado
assert.strictEqual(s.marker, 10);

s = reduce(s, ev("DIAL_STEP", { steps: 5 }));                // fica no último ecrã
assert.strictEqual(s.idx, 2);
s = reduce(s, ev("DIAL_STEP", { steps: -1 }));
assert.strictEqual(s.idx, 1);

s = reduce(s, ev("PIECE_EXIT", { marker: 11 }));             // outra peça a sair: ignora
assert.strictEqual(s.view, "tema");
s = reduce(s, ev("PIECE_EXIT", { marker: 10 }));
assert.strictEqual(s.view, "idle");

s = reduce(s, ev("PIECE_ENTER", { marker: 10 }));            // retoma onde ficou
assert.strictEqual(s.idx, 1);
s = reduce(s, ev("PIECE_EXIT", {}));

s = reduce(s, ev("PIECE_ENTER", { marker: 11 }));            // 2.º tema visitado
s = reduce(s, ev("PIECE_EXIT", { marker: 11 }));
assert.strictEqual(s.view, "fecho");                         // todos vistos: ecrã de fecho

s = reduce(s, ev("RESET", {}));
assert.deepStrictEqual(s, L.initialState());
console.log("logic.js: ok");
