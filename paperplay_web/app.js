/**
 * PaperPlay Web — browser port of the PaperPlay game suite (parity with desktop catalog).
 */
(function () {
  "use strict";

  const CATALOG = [
    {
      id: "tictactoe",
      title: "Tic-Tac-Toe",
      category: "Classic",
      description: "3×3 — three in a row. 1P vs AI or 2P local.",
    },
    {
      id: "connect4",
      title: "Connect 4",
      category: "Classic",
      description: "Drop discs into a 7×6 grid. 1P vs AI or 2P local.",
    },
    {
      id: "nim",
      title: "Nim",
      category: "Math",
      description: "Take 1..k from a pile; last move wins. Optimal AI available.",
    },
    {
      id: "hangman",
      title: "Hangman",
      category: "Word",
      description: "Guess the word one letter at a time before lives run out.",
    },
    {
      id: "dotsboxes",
      title: "Dots and Boxes",
      category: "Classic",
      description: "Draw lines; complete a box to score — and go again.",
    },
    {
      id: "sudoku",
      title: "Sudoku",
      category: "Puzzle",
      description: "Fill the 9×9 grid: rows, columns, and 3×3 boxes use 1–9 once each.",
    },
    {
      id: "nonogram",
      title: "Nonogram (Picross)",
      category: "Puzzle",
      description: "Use row/column clues to fill cells and match the picture.",
    },
    {
      id: "crossword",
      title: "Crossword",
      category: "Word",
      description: "Small sample puzzle — same spirit as the desktop JSON crosswords.",
    },
  ];

  const WORDS_EASY = [
    "paper",
    "pencil",
    "game",
    "board",
    "mouse",
    "apple",
    "train",
    "house",
    "music",
    "river",
  ];

  const SUDOKU_PUZZLES = [
    [
      [5, 3, 0, 0, 7, 0, 0, 0, 0],
      [6, 0, 0, 1, 9, 5, 0, 0, 0],
      [0, 9, 8, 0, 0, 0, 0, 6, 0],
      [8, 0, 0, 0, 6, 0, 0, 0, 3],
      [4, 0, 0, 8, 0, 3, 0, 0, 1],
      [7, 0, 0, 0, 2, 0, 0, 0, 6],
      [0, 6, 0, 0, 0, 0, 2, 8, 0],
      [0, 0, 0, 4, 1, 9, 0, 0, 5],
      [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
  ];

  const NONO_SOLUTION = [
    [0, 1, 0, 1, 0],
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0],
  ];

  /** ---------- Shared DOM ---------- */
  const elMenu = document.getElementById("viewMenu");
  const elGame = document.getElementById("viewGame");
  const elCards = document.getElementById("gameCards");
  const elMount = document.getElementById("gameMount");
  const elTitle = document.getElementById("gameTitle");
  const elDesc = document.getElementById("gameDesc");
  const btnHome = document.getElementById("btnHome");
  const btnReset = document.getElementById("btnReset");
  const chkDark = document.getElementById("themeDark");

  let activeId = null;
  let activeCleanup = null;

  function setTheme(dark) {
    document.body.classList.toggle("theme-dark", dark);
    localStorage.setItem("paperplay-theme", dark ? "dark" : "light");
  }

  chkDark.checked = localStorage.getItem("paperplay-theme") === "dark";
  setTheme(chkDark.checked);
  chkDark.addEventListener("change", () => setTheme(chkDark.checked));

  function showMenu() {
    if (activeCleanup) {
      activeCleanup();
      activeCleanup = null;
    }
    activeId = null;
    elMenu.hidden = false;
    elGame.hidden = true;
    btnHome.hidden = true;
  }

  function showGame(id) {
    const meta = CATALOG.find((g) => g.id === id);
    if (!meta) return;
    if (activeCleanup) {
      activeCleanup();
      activeCleanup = null;
    }
    activeId = id;
    elTitle.textContent = meta.title;
    elDesc.textContent = meta.description;
    elMount.innerHTML = "";
    elMenu.hidden = true;
    elGame.hidden = false;
    btnHome.hidden = false;

    const handlers = {
      tictactoe: mountTicTacToe,
      connect4: mountConnect4,
      nim: mountNim,
      hangman: mountHangman,
      dotsboxes: mountDots,
      sudoku: mountSudoku,
      nonogram: mountNonogram,
      crossword: mountCrossword,
    };
    activeCleanup = handlers[id](elMount) || (() => {});
  }

  btnHome.addEventListener("click", showMenu);
  btnReset.addEventListener("click", () => {
    if (activeId) showGame(activeId);
  });

  CATALOG.forEach((g) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "game-card";
    card.innerHTML = `<div class="cat">${escapeHtml(g.category)}</div><h3>${escapeHtml(g.title)}</h3><p>${escapeHtml(g.description)}</p>`;
    card.addEventListener("click", () => showGame(g.id));
    elCards.appendChild(card);
  });

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  /** ---------- Tic-tac-toe ---------- */
  function mountTicTacToe(root) {
    const board = Array(9).fill(null);
    let turn = "X";
    let mode = "ai"; // ai | p2

    const status = el("div", "status");
    const row = el("div", "row");
    row.innerHTML =
      '<label class="inline">Mode <select class="select" id="tttMode"><option value="ai">1P vs AI</option><option value="p2">2P local</option></select></label>';
    root.appendChild(row);
    root.appendChild(status);

    const grid = el("div", "grid-ttt");
    const cells = [];
    for (let i = 0; i < 9; i++) {
      const b = document.createElement("button");
      b.type = "button";
      b.dataset.i = String(i);
      b.addEventListener("click", () => onClick(i));
      cells.push(b);
      grid.appendChild(b);
    }
    root.appendChild(grid);

    const selMode = row.querySelector("#tttMode");
    selMode.value = mode;
    selMode.addEventListener("change", () => {
      mode = selMode.value;
      reset();
    });

    function winner() {
      const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
      ];
      for (const [a, b, c] of lines) {
        if (board[a] && board[a] === board[b] && board[a] === board[c]) return board[a];
      }
      return null;
    }

    function draw() {
      return !winner() && board.every((x) => x !== null);
    }

    function reset() {
      board.fill(null);
      turn = "X";
      sync();
    }

    function sync() {
      cells.forEach((btn, i) => {
        btn.textContent = board[i] || "";
        btn.disabled = board[i] !== null || !!winner() || draw();
      });
      const w = winner();
      if (w) status.textContent = `Winner: ${w}`;
      else if (draw()) status.textContent = "Draw.";
      else status.textContent = mode === "p2" ? `Turn: ${turn}` : turn === "X" ? "Your turn (X)" : "AI thinking…";
    }

    function onClick(i) {
      if (board[i] || winner() || draw()) return;
      if (mode === "ai" && turn === "O") return;
      board[i] = turn;
      if (winner() || draw()) {
        sync();
        return;
      }
      turn = turn === "X" ? "O" : "X";
      sync();
      if (mode === "ai" && turn === "O" && !winner() && !draw()) {
        setTimeout(() => {
          const mv = tttAiMove(board, "O", "X");
          if (mv >= 0) {
            board[mv] = "O";
            turn = "X";
          }
          sync();
        }, 200);
      }
    }

    function tttAiMove(b, ai, human) {
      function scoreState(nb, nt) {
        const w = winnerOf(nb);
        if (w === ai) return 1;
        if (w) return -1;
        if (nb.every((x) => x !== null)) return 0;
        const maximizing = nt === ai;
        let best = maximizing ? -2 : 2;
        for (let m = 0; m < 9; m++) {
          if (nb[m] !== null) continue;
          const next = nb.slice();
          next[m] = nt;
          const nt2 = nt === "X" ? "O" : "X";
          const v = scoreState(next, nt2);
          if (maximizing) {
            best = Math.max(best, v);
            if (best === 1) break;
          } else {
            best = Math.min(best, v);
            if (best === -1) break;
          }
        }
        return best;
      }

      function winnerOf(nb) {
        const lines = [
          [0, 1, 2],
          [3, 4, 5],
          [6, 7, 8],
          [0, 3, 6],
          [1, 4, 7],
          [2, 5, 8],
          [0, 4, 8],
          [2, 4, 6],
        ];
        for (const [a, b, c] of lines) {
          if (nb[a] && nb[a] === nb[b] && nb[a] === nb[c]) return nb[a];
        }
        return null;
      }

      let bestM = -1;
      let bestV = -2;
      for (let m = 0; m < 9; m++) {
        if (b[m] !== null) continue;
        const nb = b.slice();
        nb[m] = ai;
        const v = scoreState(nb, human);
        if (v > bestV) {
          bestV = v;
          bestM = m;
        }
      }
      return bestM;
    }

    sync();
    return reset;
  }

  function el(tag, cls) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    return e;
  }

  /** ---------- Connect 4 ---------- */
  function mountConnect4(root) {
    const ROWS = 6;
    const COLS = 7;
    let board = zeros2d(ROWS, COLS);
    let turn = 1;
    let mode = "ai";

    const status = el("div", "status");
    const row = el("div", "row");
    row.innerHTML =
      '<label class="inline">Mode <select class="select" id="c4Mode"><option value="ai">1P vs AI</option><option value="p2">2P local</option></select></label>';
    root.appendChild(row);
    root.appendChild(status);

    const wrap = el("div", "grid-c4");
    const dropRow = el("div", "drop-row");
    const dropBtns = [];
    for (let c = 0; c < COLS; c++) {
      const db = document.createElement("button");
      db.type = "button";
      db.className = "col-btn";
      db.textContent = "▼";
      db.dataset.col = String(c);
      dropBtns.push(db);
      dropRow.appendChild(db);
    }
    wrap.appendChild(dropRow);
    const cellsEl = el("div", "cells");
    const cells = zeros2d(ROWS, COLS);
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const cell = el("div", "cell");
        cells[r][c] = cell;
        cellsEl.appendChild(cell);
      }
    }
    wrap.appendChild(cellsEl);
    root.appendChild(wrap);

    const sel = row.querySelector("#c4Mode");
    sel.addEventListener("change", () => {
      mode = sel.value;
      reset();
    });

    function zeros2d(r, c) {
      return Array.from({ length: r }, () => Array(c).fill(0));
    }

    function winner() {
      const dirs = [
        [0, 1],
        [1, 0],
        [1, 1],
        [1, -1],
      ];
      for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
          const p = board[r][c];
          if (!p) continue;
          for (const [dr, dc] of dirs) {
            let ok = true;
            for (let k = 1; k < 4; k++) {
              const rr = r + dr * k;
              const cc = c + dc * k;
              if (rr < 0 || rr >= ROWS || cc < 0 || cc >= COLS || board[rr][cc] !== p) {
                ok = false;
                break;
              }
            }
            if (ok) return p;
          }
        }
      }
      return null;
    }

    function draw() {
      return !winner() && board[0].every((x) => x !== 0);
    }

    function legalCols() {
      return Array.from({ length: COLS }, (_, c) => c).filter((c) => board[0][c] === 0 && !winner());
    }

    function drop(col) {
      for (let r = ROWS - 1; r >= 0; r--) {
        if (board[r][col] === 0) {
          board[r][col] = turn;
          return [r, col];
        }
      }
      return null;
    }

    function other(p) {
      return p === 1 ? 2 : 1;
    }

    function aiMove(ai) {
      const legal = legalCols();
      if (!legal.length) return -1;

      function wouldWin(col, p) {
        const b = board.map((row) => row.slice());
        let tr = turn;
        turn = p;
        const placed = dropAt(b, col, p);
        turn = tr;
        return placed && winnerOfBoard(b) === p;
      }

      function dropAt(b, col, p) {
        for (let r = ROWS - 1; r >= 0; r--) {
          if (b[r][col] === 0) {
            b[r][col] = p;
            return true;
          }
        }
        return false;
      }

      function winnerOfBoard(b) {
        const dirs = [
          [0, 1],
          [1, 0],
          [1, 1],
          [1, -1],
        ];
        for (let r = 0; r < ROWS; r++) {
          for (let c = 0; c < COLS; c++) {
            const p = b[r][c];
            if (!p) continue;
            for (const [dr, dc] of dirs) {
              let ok = true;
              for (let k = 1; k < 4; k++) {
                const rr = r + dr * k;
                const cc = c + dc * k;
                if (rr < 0 || rr >= ROWS || cc < 0 || cc >= COLS || b[rr][cc] !== p) {
                  ok = false;
                  break;
                }
              }
              if (ok) return p;
            }
          }
        }
        return null;
      }

      for (const c of legal) {
        if (wouldWin(c, ai)) return c;
      }
      const opp = other(ai);
      for (const c of legal) {
        if (wouldWin(c, opp)) return c;
      }
      const center = Math.floor(COLS / 2);
      return legal.sort((a, b) => Math.abs(a - center) - Math.abs(b - center) || a - b)[0];
    }

    function paint() {
      for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
          const v = board[r][c];
          const cell = cells[r][c];
          cell.className = "cell" + (v === 1 ? " p1" : v === 2 ? " p2" : "");
        }
      }
      const w = winner();
      if (w) status.textContent = `Player ${w} wins!`;
      else if (draw()) status.textContent = "Draw.";
      else if (mode === "p2") status.textContent = `Player ${turn}'s turn`;
      else status.textContent = turn === 1 ? "Your turn (yellow)" : "AI thinking…";
    }

    function reset() {
      board = zeros2d(ROWS, COLS);
      turn = 1;
      paint();
    }

    dropBtns.forEach((db) => {
      db.addEventListener("click", () => {
        const col = +db.dataset.col;
        if (winner() || draw()) return;
        if (mode === "ai" && turn === 2) return;
        if (board[0][col] !== 0) return;
        drop(col);
        if (winner() || draw()) {
          paint();
          return;
        }
        turn = other(turn);
        paint();
        if (mode === "ai" && turn === 2 && !winner() && !draw()) {
          setTimeout(() => {
            const mv = aiMove(2);
            if (mv >= 0) drop(mv);
            if (!winner() && !draw()) turn = 1;
            paint();
          }, 250);
        }
      });
    });

    paint();
    return reset;
  }

  /** ---------- Nim ---------- */
  function mountNim(root) {
    let pile = 21;
    const maxTake = 3;
    let turn = 1;
    let vsAi = true;

    const status = el("div", "status");
    const row = el("div", "row");
    row.innerHTML =
      '<label class="inline"><input type="checkbox" id="nimAi" checked /> vs optimal AI</label>';
    root.appendChild(row);
    root.appendChild(status);

    const pileEl = el("div", "nim-pile");
    const btns = el("div", "nim-btns");
    root.appendChild(pileEl);
    root.appendChild(btns);

    const chk = row.querySelector("#nimAi");
    chk.addEventListener("change", () => {
      vsAi = chk.checked;
      reset();
    });

    function optimalTake(p) {
      const k = maxTake + 1;
      const r = p % k;
      if (r === 0) return 1;
      return Math.min(r, maxTake);
    }

    function renderPile() {
      pileEl.textContent = "●".repeat(Math.min(pile, 40)) + (pile > 40 ? " +" + (pile - 40) : "");
    }

    function sync() {
      renderPile();
      btns.innerHTML = "";
      if (pile === 0) {
        const lastWinner = turn === 1 ? 2 : 1;
        status.textContent = `Player ${lastWinner} took the last counter and wins.`;
        return;
      }
      status.textContent = vsAi
        ? turn === 1
          ? `Your turn — ${pile} left`
          : `AI's turn — ${pile} left`
        : `Player ${turn}'s turn — ${pile} left`;
      const max = Math.min(maxTake, pile);
      for (let n = 1; n <= max; n++) {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "btn";
        b.textContent = `Take ${n}`;
        b.addEventListener("click", () => take(n));
        btns.appendChild(b);
      }
    }

    function take(n) {
      if (pile === 0) return;
      if (vsAi && turn === 2) return;
      pile -= n;
      turn = turn === 1 ? 2 : 1;
      sync();
      if (pile === 0) return;
      if (vsAi && turn === 2) {
        setTimeout(() => {
          const n2 = optimalTake(pile);
          pile -= n2;
          turn = 1;
          sync();
        }, 350);
      }
    }

    function reset() {
      pile = 21;
      turn = 1;
      sync();
    }

    sync();
    return reset;
  }

  /** ---------- Hangman ---------- */
  function mountHangman(root) {
    let word = "";
    let lives = 6;
    let guessed = new Set();
    const status = el("div", "status");
    const maskEl = el("div", "word-mask");
    const keys = el("div", "keygrid");
    root.appendChild(status);
    root.appendChild(maskEl);
    root.appendChild(keys);

    function newWord() {
      word = WORDS_EASY[(Math.random() * WORDS_EASY.length) | 0];
      lives = 6;
      guessed = new Set();
      sync();
    }

    function mask() {
      return word
        .split("")
        .map((ch) => (guessed.has(ch) ? ch : "_"))
        .join(" ");
    }

    function sync() {
      maskEl.textContent = mask();
      keys.innerHTML = "";
      if (won()) {
        status.textContent = "You got it!";
        return;
      }
      if (lost()) {
        status.textContent = `Out of lives — the word was "${word}".`;
        return;
      }
      status.textContent = `${lives} lives left`;
      for (let i = 0; i < 26; i++) {
        const ch = String.fromCharCode(97 + i);
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = ch.toUpperCase();
        b.disabled = guessed.has(ch);
        b.addEventListener("click", () => guess(ch));
        keys.appendChild(b);
      }
    }

    function won() {
      return word.split("").every((c) => guessed.has(c));
    }

    function lost() {
      return lives <= 0 && !won();
    }

    function guess(ch) {
      if (won() || lost() || guessed.has(ch)) return;
      guessed.add(ch);
      if (!word.includes(ch)) lives -= 1;
      sync();
    }

    function reset() {
      newWord();
    }

    newWord();
    return reset;
  }

  /** ---------- Dots and boxes ---------- */
  function mountDots(root) {
    let dr = 5;
    let dc = 5;
    let state = newDab(dr, dc);

    const status = el("div", "status");
    root.appendChild(status);

    const boardEl = el("div", "dab-wrap");
    root.appendChild(boardEl);

    function newDab(dotsR, dotsC) {
      const h = Array.from({ length: dotsR }, () => Array(dotsC - 1).fill(0));
      const v = Array.from({ length: dotsR - 1 }, () => Array(dotsC).fill(0));
      const boxes = Array.from({ length: dotsR - 1 }, () => Array(dotsC - 1).fill(0));
      return {
        dots_rows: dotsR,
        dots_cols: dotsC,
        h,
        v,
        boxes,
        turn: 1,
        score1: 0,
        score2: 0,
      };
    }

    function isOver(s) {
      return s.h.every((row) => row.every((e) => e !== 0)) && s.v.every((row) => row.every((e) => e !== 0));
    }

    function playEdge(s, kind, r, c) {
      const pl = s.turn;
      if (kind === "h") {
        if (s.h[r][c] !== 0) return 0;
        s.h[r][c] = pl;
      } else {
        if (s.v[r][c] !== 0) return 0;
        s.v[r][c] = pl;
      }
      let completed = 0;
      for (const [br, bc] of affectedBoxes(kind, r, c, s)) {
        if (s.boxes[br][bc] === 0 && isBoxComplete(s, br, bc)) {
          s.boxes[br][bc] = pl;
          completed++;
          if (pl === 1) s.score1++;
          else s.score2++;
        }
      }
      if (completed === 0) s.turn = s.turn === 1 ? 2 : 1;
      return completed;
    }

    function affectedBoxes(kind, r, c, s) {
      const out = [];
      if (kind === "h") {
        if (r < s.dots_rows - 1) out.push([r, c]);
        if (r > 0) out.push([r - 1, c]);
      } else {
        if (c < s.dots_cols - 1) out.push([r, c]);
        if (c > 0) out.push([r, c - 1]);
      }
      return out;
    }

    function isBoxComplete(s, br, bc) {
      return (
        s.h[br][bc] !== 0 &&
        s.h[br + 1][bc] !== 0 &&
        s.v[br][bc] !== 0 &&
        s.v[br][bc + 1] !== 0
      );
    }

    function rebuild() {
      boardEl.innerHTML = "";
      const s = state;
      const grid = document.createElement("div");
      grid.style.display = "grid";
      grid.style.gridTemplateColumns = `repeat(${2 * s.dots_cols - 1}, auto)`;
      for (let rr = 0; rr < 2 * s.dots_rows - 1; rr++) {
        for (let cc = 0; cc < 2 * s.dots_cols - 1; cc++) {
          if (rr % 2 === 0 && cc % 2 === 0) {
            const dot = el("div", "dab-dot");
            grid.appendChild(dot);
          } else if (rr % 2 === 0 && cc % 2 === 1) {
            const r = rr / 2;
            const c = (cc - 1) / 2;
            const eb = el("div", "dab-h");
            const val = s.h[r][c];
            if (val) eb.classList.add(val === 1 ? "p1" : "p2");
            else
              eb.addEventListener("click", () => {
                if (isOver(s)) return;
                playEdge(s, "h", r, c);
                rebuild();
              });
            grid.appendChild(eb);
          } else if (rr % 2 === 1 && cc % 2 === 0) {
            const r = (rr - 1) / 2;
            const c = cc / 2;
            const eb = el("div", "dab-v");
            const val = s.v[r][c];
            if (val) eb.classList.add(val === 1 ? "p1" : "p2");
            else
              eb.addEventListener("click", () => {
                if (isOver(s)) return;
                playEdge(s, "v", r, c);
                rebuild();
              });
            grid.appendChild(eb);
          } else {
            const br = (rr - 1) / 2;
            const bc = (cc - 1) / 2;
            const bx = el("div", "dab-gap");
            const o = s.boxes[br][bc];
            bx.textContent = o === 1 ? "1" : o === 2 ? "2" : "";
            grid.appendChild(bx);
          }
        }
      }
      boardEl.appendChild(grid);

      if (isOver(s)) {
        let msg = `Final: P1 ${s.score1} — P2 ${s.score2}. `;
        if (s.score1 > s.score2) msg += "Player 1 wins.";
        else if (s.score2 > s.score1) msg += "Player 2 wins.";
        else msg += "Tie.";
        status.textContent = msg;
      } else {
        status.textContent = `Player ${s.turn} — scores P1 ${s.score1} · P2 ${s.score2}`;
      }
    }

    function reset() {
      state = newDab(dr, dc);
      rebuild();
    }

    rebuild();
    return reset;
  }

  /** ---------- Sudoku ---------- */
  function mountSudoku(root) {
    const given = SUDOKU_PUZZLES[0].map((r) => r.slice());
    let grid = given.map((r) => r.slice());
    const status = el("div", "status");
    root.appendChild(status);

    const wrap = el("div", "sudoku-grid");
    const inputs = [];
    for (let r = 0; r < 9; r++) {
      inputs[r] = [];
      for (let c = 0; c < 9; c++) {
        const inp = document.createElement("input");
        inp.type = "text";
        inp.maxLength = 1;
        inp.inputMode = "numeric";
        if (given[r][c]) {
          inp.value = String(given[r][c]);
          inp.readOnly = true;
          inp.classList.add("given");
        }
        const thickR = c === 2 || c === 5;
        const thickB = r === 2 || r === 5;
        if (thickR) inp.classList.add("thick-r");
        if (thickB) inp.classList.add("thick-b");
        inp.dataset.r = String(r);
        inp.dataset.c = String(c);
        inp.addEventListener("input", () => {
          const v = inp.value.replace(/\D/g, "").slice(0, 1);
          inp.value = v;
          const n = v ? parseInt(v, 10) : 0;
          grid[r][c] = given[r][c] || n;
          if (!validGrid(grid)) {
            inp.value = "";
            grid[r][c] = 0;
          }
          if (solved(grid)) status.textContent = "Solved — nice!";
          else status.textContent = "";
        });
        inputs[r][c] = inp;
        wrap.appendChild(inp);
      }
    }
    root.appendChild(wrap);

    function validGrid(g) {
      function validUnit(nums) {
        const seen = new Set();
        for (const n of nums) {
          if (n === 0) continue;
          if (n < 1 || n > 9 || seen.has(n)) return false;
          seen.add(n);
        }
        return true;
      }
      for (let r = 0; r < 9; r++) if (!validUnit(g[r])) return false;
      for (let c = 0; c < 9; c++) {
        const col = [];
        for (let r = 0; r < 9; r++) col.push(g[r][c]);
        if (!validUnit(col)) return false;
      }
      for (let br = 0; br < 9; br += 3) {
        for (let bc = 0; bc < 9; bc += 3) {
          const u = [];
          for (let r = br; r < br + 3; r++) for (let c = bc; c < bc + 3; c++) u.push(g[r][c]);
          if (!validUnit(u)) return false;
        }
      }
      return true;
    }

    function solved(g) {
      return validGrid(g) && g.every((row) => row.every((n) => n !== 0));
    }

    function reset() {
      grid = given.map((r) => r.slice());
      for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
          if (!given[r][c]) {
            inputs[r][c].value = "";
            grid[r][c] = 0;
          }
        }
      }
      status.textContent = "";
    }

    status.textContent = "Fill empty cells — given numbers stay fixed.";
    return reset;
  }

  /** ---------- Nonogram ---------- */
  function mountNonogram(root) {
    const sol = NONO_SOLUTION.map((r) => r.slice());
    const h = sol.length;
    const w = sol[0].length;

    function lineClues(bits) {
      const clues = [];
      let run = 0;
      for (const b of bits) {
        if (b) run++;
        else {
          if (run) clues.push(run);
          run = 0;
        }
      }
      if (run) clues.push(run);
      return clues.length ? clues : [0];
    }

    const rowClues = sol.map(lineClues);
    const colClues = [];
    for (let c = 0; c < w; c++) {
      const bits = [];
      for (let r = 0; r < h; r++) bits.push(sol[r][c]);
      colClues.push(lineClues(bits));
    }

    const marks = Array.from({ length: h }, () => Array(w).fill(0));

    const status = el("div", "status");
    root.appendChild(status);

    const table = document.createElement("table");
    table.className = "nono-table";

    const thead = document.createElement("thead");
    const trHead = document.createElement("tr");
    const corner = document.createElement("th");
    corner.className = "corner";
    trHead.appendChild(corner);
    for (let c = 0; c < w; c++) {
      const th = document.createElement("th");
      const div = el("div", "colclue");
      div.textContent = colClues[c].join("\n");
      th.appendChild(div);
      trHead.appendChild(th);
    }
    thead.appendChild(trHead);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    for (let r = 0; r < h; r++) {
      const tr = document.createElement("tr");
      const rclue = document.createElement("td");
      rclue.className = "rowclue";
      rclue.textContent = rowClues[r].join(" ");
      tr.appendChild(rclue);
      for (let c = 0; c < w; c++) {
        const td = document.createElement("td");
        td.className = "cell play";
        td.dataset.r = String(r);
        td.dataset.c = String(c);
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);

    const wrap = el("div", "nonogram-wrap");
    wrap.appendChild(table);
    root.appendChild(wrap);

    function paintCell(td, r, c) {
      td.className = "cell play";
      const m = marks[r][c];
      if (m === 1) td.classList.add("filled");
      else if (m === -1) td.classList.add("mark-x");
    }

    function solved() {
      for (let r = 0; r < h; r++) {
        for (let c = 0; c < w; c++) {
          const want = sol[r][c] ? 1 : 0;
          const have = marks[r][c] === 1 ? 1 : 0;
          if (want !== have) return false;
        }
      }
      return true;
    }

    table.querySelectorAll(".cell.play").forEach((td) => {
      const r = +td.dataset.r;
      const c = +td.dataset.c;
      td.addEventListener("click", () => {
        marks[r][c] = marks[r][c] === 0 ? 1 : marks[r][c] === 1 ? -1 : 0;
        paintCell(td, r, c);
        status.textContent = solved() ? "Matched the picture — solved!" : "";
      });
      paintCell(td, r, c);
    });

    status.textContent = "Click: empty → fill → mark X → empty.";

    function reset() {
      for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) marks[r][c] = 0;
      table.querySelectorAll(".cell.play").forEach((td) => {
        const r = +td.dataset.r;
        const c = +td.dataset.c;
        paintCell(td, r, c);
      });
      status.textContent = "Click: empty → fill → mark X → empty.";
    }

    return reset;
  }

  /** ---------- Crossword mini ---------- */
  function mountCrossword(root) {
    /* 3×3: DOG across, DAY down, D shared */
    const solution = [
      ["D", "O", "G"],
      ["A", null, null],
      ["Y", null, null],
    ];
    const blocks = [
      [false, false, false],
      [false, true, true],
      [false, true, true],
    ];
    const nums = [
      [1, 0, 0],
      [0, 0, 0],
      [0, 0, 0],
    ];

    const status = el("div", "status");
    const clues = el("div", "clue-list");
    clues.innerHTML =
      "<h4>Across</h4><p><strong>1</strong> Man's best friend, three letters</p>" +
      "<h4>Down</h4><p><strong>1</strong> A 24-hour period; three letters</p>";
    root.appendChild(clues);
    root.appendChild(status);

    const tbl = document.createElement("table");
    tbl.className = "xword-table";
    const inputs = [];
    for (let r = 0; r < 3; r++) {
      inputs[r] = [];
      const tr = document.createElement("tr");
      for (let c = 0; c < 3; c++) {
        const td = document.createElement("td");
        if (blocks[r][c]) {
          td.className = "block";
          td.innerHTML = "&nbsp;";
        } else {
          const n = nums[r][c];
          if (n) {
            const sp = el("span", "num");
            sp.textContent = String(n);
            td.appendChild(sp);
          }
          const inp = document.createElement("input");
          inp.maxLength = 1;
          inp.dataset.r = String(r);
          inp.dataset.c = String(c);
          inputs[r][c] = inp;
          td.appendChild(inp);
        }
        tr.appendChild(td);
      }
      tbl.appendChild(tr);
    }
    root.appendChild(tbl);

    const btn = el("button", "btn primary");
    btn.type = "button";
    btn.textContent = "Check";
    btn.addEventListener("click", () => {
      let ok = true;
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          if (blocks[r][c]) continue;
          const want = solution[r][c];
          if (want === null) continue;
          const got = (inputs[r][c].value || "").toUpperCase();
          if (got !== want) ok = false;
        }
      }
      status.textContent = ok ? "Perfect — all letters match." : "Some letters differ — keep trying.";
    });
    root.appendChild(btn);

    function reset() {
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          if (!blocks[r][c] && inputs[r][c]) inputs[r][c].value = "";
        }
      }
      status.textContent = "";
    }

    return reset;
  }
})();
