(function () {
  function init() {
    const dataEl = document.getElementById("story-data");
    let story;
    try {
      story = JSON.parse(dataEl.textContent);
    } catch (err) {
      var errEl = document.getElementById("storyTyped") || document.getElementById("storyText");
      if (errEl) {
        errEl.textContent = "Could not load story data. Check the console.";
      }
      console.error(err);
      return;
    }

    const storyTyped = document.getElementById("storyTyped");
    const typeCursor = document.getElementById("typeCursor");
    const typeHint = document.getElementById("typeHint");
    const terminalEl = document.getElementById("terminal");
    const crtFrame = document.getElementById("crtFrame");
    const crtStatic = document.getElementById("crtStatic");
    const sceneTitle = document.getElementById("sceneTitle");
    const choicesEl = document.getElementById("choices");
    const ambient = document.getElementById("ambient");
    const btnMute = document.getElementById("btnMute");

    let currentId = "start";

    /** @type {'off' | 'file' | 'synth'} */
    let soundMode = "off";
    let muted = false;

    /** @type {{ ctx: AudioContext; osc: OscillatorNode; gain: GainNode } | null} */
    let synth = null;

    /** @type {AudioContext | null} */
    let uiAudioCtx = null;

    let typingGeneration = 0;

    /** @type {number | null} */
    let typeTimeout = null;

    /** @type {number | null} */
    let critDelayTimer = null;

    /** @type {number | null} */
    let crtFallbackTimer = null;

    const CRITICAL_PAUSE_MS = 1150;
    const CRT_SHUTDOWN_MS = 1550;

    function clearTypeTimer() {
      if (typeTimeout !== null) {
        window.clearTimeout(typeTimeout);
        typeTimeout = null;
      }
    }

    function clearCritTimer() {
      if (critDelayTimer !== null) {
        window.clearTimeout(critDelayTimer);
        critDelayTimer = null;
      }
    }

    function clearCrtTimer() {
      if (crtFallbackTimer !== null) {
        window.clearTimeout(crtFallbackTimer);
        crtFallbackTimer = null;
      }
    }

    function getAudioContextForUi() {
      if (synth && synth.ctx && synth.ctx.state !== "closed") {
        return synth.ctx;
      }
      if (uiAudioCtx && uiAudioCtx.state !== "closed") {
        return uiAudioCtx;
      }
      try {
        var Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) {
          return null;
        }
        uiAudioCtx = new Ctx();
        uiAudioCtx.resume().catch(function () {});
        return uiAudioCtx;
      } catch (e) {
        return null;
      }
    }

    function resumeAllAudio() {
      var ctx = getAudioContextForUi();
      if (ctx) {
        ctx.resume().catch(function () {});
      }
      if (synth && synth.ctx) {
        synth.ctx.resume().catch(function () {});
      }
    }
    document.addEventListener("pointerdown", resumeAllAudio, { once: true, passive: true });
    document.addEventListener(
      "keydown",
      function k() {
        resumeAllAudio();
        document.removeEventListener("keydown", k);
      },
      true
    );

    /**
     * Quiet CRT/teletype tick while text prints. Throttled; skips spaces.
     */
    function playTypewriterTick(char) {
      if (soundMode !== "off" && muted) {
        return;
      }
      if (char === " " || char === "\t") {
        return;
      }
      var ctx = getAudioContextForUi();
      if (!ctx) {
        return;
      }
      try {
        ctx.resume().catch(function () {});
        var t = ctx.currentTime;
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = "square";
        if (char === "\n") {
          osc.frequency.setValueAtTime(380, t);
          osc.frequency.exponentialRampToValueAtTime(140, t + 0.022);
        } else {
          osc.frequency.setValueAtTime(1320, t);
          osc.frequency.exponentialRampToValueAtTime(980, t + 0.012);
        }
        gain.gain.setValueAtTime(0.0001, t);
        gain.gain.exponentialRampToValueAtTime(0.022, t + 0.0015);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.018);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.02);
      } catch (e) {
        /* ignore */
      }
    }

    function playChoiceSound() {
      if (soundMode !== "off" && muted) {
        return;
      }
      var ctx = getAudioContextForUi();
      if (!ctx) {
        return;
      }
      try {
        ctx.resume().catch(function () {});
        var t = ctx.currentTime;
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = "square";
        osc.frequency.setValueAtTime(880, t);
        osc.frequency.exponentialRampToValueAtTime(420, t + 0.06);
        gain.gain.setValueAtTime(0.0001, t);
        gain.gain.exponentialRampToValueAtTime(0.065, t + 0.004);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.07);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.08);
      } catch (e) {
        /* ignore */
      }
    }

    /** Heavier, lower finale sting for paths into the last act. */
    function playDramaticChoiceSound() {
      if (soundMode !== "off" && muted) {
        return;
      }
      var ctx = getAudioContextForUi();
      if (!ctx) {
        return;
      }
      try {
        ctx.resume().catch(function () {});
        var t = ctx.currentTime;
        var master = ctx.createGain();
        master.gain.setValueAtTime(0.0001, t);
        master.gain.exponentialRampToValueAtTime(0.11, t + 0.02);
        master.gain.exponentialRampToValueAtTime(0.0001, t + 0.55);
        master.connect(ctx.destination);

        var o1 = ctx.createOscillator();
        o1.type = "sawtooth";
        o1.frequency.setValueAtTime(95, t);
        o1.frequency.exponentialRampToValueAtTime(38, t + 0.45);
        var g1 = ctx.createGain();
        g1.gain.value = 0.45;
        o1.connect(g1);
        g1.connect(master);
        o1.start(t);
        o1.stop(t + 0.52);

        var o2 = ctx.createOscillator();
        o2.type = "sine";
        o2.frequency.setValueAtTime(220, t);
        o2.frequency.exponentialRampToValueAtTime(55, t + 0.4);
        var g2 = ctx.createGain();
        g2.gain.value = 0.35;
        o2.connect(g2);
        g2.connect(master);
        o2.start(t);
        o2.stop(t + 0.5);

        var o3 = ctx.createOscillator();
        o3.type = "triangle";
        o3.frequency.setValueAtTime(660, t);
        o3.frequency.exponentialRampToValueAtTime(90, t + 0.12);
        var g3 = ctx.createGain();
        g3.gain.value = 0.08;
        o3.connect(g3);
        g3.connect(master);
        o3.start(t);
        o3.stop(t + 0.15);
      } catch (e) {
        /* ignore */
      }
    }

    /** CRT power-down: electrical crack + collapsing flyback whine. */
    function playCrtShutdownSound() {
      if (soundMode !== "off" && muted) {
        return;
      }
      var ctx = getAudioContextForUi();
      if (!ctx) {
        return;
      }
      try {
        ctx.resume().catch(function () {});
        var t = ctx.currentTime;
        var master = ctx.createGain();
        master.gain.setValueAtTime(0.0001, t);
        master.gain.exponentialRampToValueAtTime(0.14, t + 0.008);
        master.gain.exponentialRampToValueAtTime(0.0001, t + 1.35);
        master.connect(ctx.destination);

        var pop = ctx.createOscillator();
        pop.type = "square";
        pop.frequency.setValueAtTime(1800, t);
        pop.frequency.exponentialRampToValueAtTime(120, t + 0.08);
        var pg = ctx.createGain();
        pg.gain.setValueAtTime(0.12, t);
        pg.gain.exponentialRampToValueAtTime(0.0001, t + 0.1);
        pop.connect(pg);
        pg.connect(master);
        pop.start(t);
        pop.stop(t + 0.11);

        var whine = ctx.createOscillator();
        whine.type = "sawtooth";
        whine.frequency.setValueAtTime(520, t + 0.02);
        whine.frequency.exponentialRampToValueAtTime(40, t + 1.1);
        var wg = ctx.createGain();
        wg.gain.setValueAtTime(0.0001, t + 0.02);
        wg.gain.exponentialRampToValueAtTime(0.06, t + 0.08);
        wg.gain.exponentialRampToValueAtTime(0.0001, t + 1.25);
        whine.connect(wg);
        wg.connect(master);
        whine.start(t + 0.02);
        whine.stop(t + 1.28);
      } catch (e) {
        /* ignore */
      }
    }

    function duckAmbientForShutdown() {
      if (synth && synth.gain && synth.ctx) {
        var g = synth.gain;
        var c = synth.ctx.currentTime;
        try {
          g.gain.cancelScheduledValues(c);
          g.gain.setValueAtTime(g.gain.value, c);
          g.gain.exponentialRampToValueAtTime(0.0001, c + 1.05);
        } catch (e) {
          /* ignore */
        }
      }
      try {
        ambient.volume = Math.min(ambient.volume, 0.22);
      } catch (e) {
        /* ignore */
      }
    }

    function restoreSynthVolumeFromUi() {
      if (!(synth && synth.gain && synth.ctx)) {
        return;
      }
      var c = synth.ctx.currentTime;
      try {
        synth.gain.gain.cancelScheduledValues(c);
        var v = muted ? 0 : 0.045;
        synth.gain.gain.setValueAtTime(v, c);
      } catch (e) {
        /* ignore */
      }
    }

    function resetCrtVisuals() {
      if (crtFrame) {
        crtFrame.classList.remove("crt-frame--poweroff");
      }
      if (crtStatic) {
        crtStatic.classList.remove("crt-static--on");
      }
      if (terminalEl) {
        terminalEl.style.animation = "none";
        terminalEl.offsetHeight;
        terminalEl.style.removeProperty("animation");
        terminalEl.style.removeProperty("opacity");
        terminalEl.style.removeProperty("transform");
        terminalEl.style.removeProperty("filter");
      }
    }

    function setTypingUi(active) {
      if (typeCursor) {
        typeCursor.classList.toggle("type-cursor--on", active);
      }
      if (typeHint) {
        typeHint.classList.toggle("terminal-hint--visible", active);
      }
      if (terminalEl) {
        terminalEl.classList.toggle("terminal--typing", active);
      }
    }

    function choiceUsesDramaticSound(nextId) {
      return nextId === "acceptance";
    }

    function playChoiceSoundForNext(nextId) {
      if (choiceUsesDramaticSound(nextId)) {
        playDramaticChoiceSound();
      } else {
        playChoiceSound();
      }
    }

    function mountChoiceButtons(node, gen) {
      if (gen !== typingGeneration) {
        return;
      }
      const ch = node.choices || [];
      ch.forEach(function (c) {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "choice-btn";
        b.textContent = c.text;
        b.addEventListener("click", function () {
          playChoiceSoundForNext(c.next);
          currentId = c.next;
          render();
        });
        choicesEl.appendChild(b);
      });
    }

    function mountReplayOnly(gen) {
      if (gen !== typingGeneration) {
        return;
      }
      choicesEl.innerHTML = "";
      const replay = document.createElement("button");
      replay.type = "button";
      replay.className = "choice-btn choice-btn--replay";
      replay.textContent = "Play again from the beginning";
      replay.addEventListener("click", function () {
        playDramaticChoiceSound();
        currentId = "start";
        render();
      });
      choicesEl.appendChild(replay);
    }

    function beginCrtShutdown(gen, onDone) {
      if (!crtFrame || !terminalEl) {
        onDone();
        return;
      }
      var finished = false;
      duckAmbientForShutdown();
      if (crtStatic) {
        crtStatic.classList.add("crt-static--on");
      }
      crtFrame.classList.add("crt-frame--poweroff");

      function done() {
        if (finished) {
          return;
        }
        finished = true;
        clearCrtTimer();
        crtFallbackTimer = null;
        if (terminalEl) {
          terminalEl.removeEventListener("animationend", onAnimEnd);
        }
        onDone();
      }

      function onAnimEnd(ev) {
        if (ev.target !== terminalEl) {
          return;
        }
        done();
      }

      terminalEl.addEventListener("animationend", onAnimEnd);
      crtFallbackTimer = window.setTimeout(done, CRT_SHUTDOWN_MS + 200);
    }

    function finishScene(node, gen) {
      if (gen !== typingGeneration) {
        return;
      }
      choicesEl.innerHTML = "";

      const isFinale = Boolean(node.ending && currentId === "acceptance");
      const needsCriticalPause =
        Boolean(node.critical) && !node.ending && !isFinale;

      function proceed() {
        if (gen !== typingGeneration) {
          return;
        }
        if (isFinale) {
          playCrtShutdownSound();
          beginCrtShutdown(gen, function () {
            mountReplayOnly(gen);
          });
          return;
        }
        mountChoiceButtons(node, gen);
      }

      if (needsCriticalPause) {
        critDelayTimer = window.setTimeout(function () {
          critDelayTimer = null;
          proceed();
        }, CRITICAL_PAUSE_MS);
      } else {
        proceed();
      }
    }

    function beginTyping(node) {
      clearTypeTimer();
      var gen = typingGeneration;
      var full = node.text || "";
      storyTyped.textContent = "";
      setTypingUi(true);

      var i = 0;
      var lastTickWallMs = 0;
      var TYPE_TICK_MIN_MS = 22;

      function scheduleNext() {
        typeTimeout = null;
        if (gen !== typingGeneration) {
          return;
        }
        if (i >= full.length) {
          setTypingUi(false);
          finishScene(node, gen);
          return;
        }
        var ch = full.charAt(i);
        storyTyped.textContent += ch;
        i++;
        var now = typeof performance !== "undefined" ? performance.now() : Date.now();
        if (now - lastTickWallMs >= TYPE_TICK_MIN_MS) {
          playTypewriterTick(ch);
          lastTickWallMs = now;
        }
        var prev = full.charAt(i - 1);
        var delay =
          prev === "\n" ? 95 : prev === "." || prev === "!" || prev === "?" ? 42 : 15;
        typeTimeout = window.setTimeout(scheduleNext, delay);
      }

      scheduleNext();
    }

    function skipTypingForCurrentScene() {
      if (!terminalEl.classList.contains("terminal--typing")) {
        return;
      }
      var node = story[currentId];
      if (!node) {
        return;
      }
      clearTypeTimer();
      typingGeneration++;
      var gen = typingGeneration;
      storyTyped.textContent = node.text || "";
      setTypingUi(false);
      finishScene(node, gen);
    }

    function render() {
      clearTypeTimer();
      clearCritTimer();
      clearCrtTimer();
      typingGeneration++;
      resetCrtVisuals();
      restoreSynthVolumeFromUi();

      const node = story[currentId];
      if (!node) {
        sceneTitle.textContent = "—";
        storyTyped.textContent = "[Missing scene: " + currentId + "]";
        setTypingUi(false);
        choicesEl.innerHTML = "";
        return;
      }

      sceneTitle.textContent = node.title || "—";
      choicesEl.innerHTML = "";
      beginTyping(node);
    }

    terminalEl.addEventListener("click", function (ev) {
      if (terminalEl.classList.contains("terminal--typing")) {
        ev.preventDefault();
        skipTypingForCurrentScene();
      }
    });

    document.addEventListener(
      "keydown",
      function (ev) {
        if (!terminalEl.classList.contains("terminal--typing")) {
          return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        skipTypingForCurrentScene();
      },
      true
    );

    function stopSynth() {
      if (!synth) {
        return;
      }
      try {
        synth.osc.stop();
        synth.osc.disconnect();
      } catch (e) {
        /* ignore */
      }
      try {
        synth.ctx.close();
      } catch (e) {
        /* ignore */
      }
      synth = null;
    }

    function startSynth() {
      try {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) {
          return false;
        }
        const ctx = new Ctx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.value = 52;
        gain.gain.value = muted ? 0 : 0.045;
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        synth = { ctx: ctx, osc: osc, gain: gain };
        ctx.resume().catch(function () {});
        return true;
      } catch (e) {
        console.warn("Web Audio unavailable:", e);
        return false;
      }
    }

    function applyMute() {
      if (soundMode === "file") {
        ambient.muted = muted;
      }
      if (synth && synth.gain && synth.ctx) {
        var v = muted ? 0 : 0.045;
        synth.gain.gain.setTargetAtTime(v, synth.ctx.currentTime, 0.05);
      }
    }

    function syncButton() {
      if (soundMode === "off") {
        btnMute.textContent = "🔇";
        btnMute.title = "Click for ambient sound";
        btnMute.setAttribute("aria-pressed", "false");
        btnMute.disabled = false;
        return;
      }
      btnMute.textContent = muted ? "🔇" : "🔈";
      btnMute.title = muted ? "Unmute" : "Mute";
      btnMute.setAttribute("aria-pressed", muted ? "false" : "true");
    }

    function tryUpgradeToFileAudio() {
      ambient.volume = 0.22;
      ambient.muted = false;
      var p = ambient.play();
      if (!p || typeof p.then !== "function") {
        return;
      }
      var timeoutMs = 2000;
      var timeout = new Promise(function (_, reject) {
        window.setTimeout(function () {
          reject(new Error("ambient timeout"));
        }, timeoutMs);
      });
      Promise.race([p, timeout])
        .then(function () {
          stopSynth();
          soundMode = "file";
          muted = false;
          syncButton();
        })
        .catch(function () {
          try {
            ambient.pause();
            ambient.currentTime = 0;
          } catch (e) {
            /* ignore */
          }
        });
    }

    btnMute.addEventListener(
      "click",
      function (ev) {
        ev.preventDefault();
        if (soundMode === "off") {
          stopSynth();
          if (!startSynth()) {
            btnMute.title = "Sound unavailable in this browser";
            btnMute.textContent = "—";
            return;
          }
          soundMode = "synth";
          muted = false;
          syncButton();
          tryUpgradeToFileAudio();
          return;
        }

        muted = !muted;
        applyMute();
        syncButton();
      },
      false
    );

    ambient.muted = true;
    syncButton();
    render();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
