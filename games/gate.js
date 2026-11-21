/* Jay's Studio game gate.
   Each game is free for one round. When that round ends, this asks for an email
   (sent to Jay's Kit form through SITE_SUBSCRIBE in site-data.js) before the next one.
   Signing up once unlocks every game on this device. It's a friendly gate, not a lock:
   it lives in the browser, so anyone who clears their storage gets another free round.
   Each game calls window.JS_ROUND_OVER() when a round (or match) ends. */
(function () {
  var me = document.currentScript;
  var GAME = (me && me.getAttribute("data-game")) || location.pathname;
  var NAME = (me && me.getAttribute("data-title")) || document.title || "this game";
  var KEY_IN = "jaysstudio_signedup", KEY_USED = "jaysstudio_round_used_" + GAME;
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode: gate still works for this visit */ } }
  var usedThisVisit = false;
  function signedUp() { return get(KEY_IN) === "1"; }
  function used() { return usedThisVisit || get(KEY_USED) === "1"; }

  var css = "" +
    ".jsg{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:center;justify-content:center;padding:16px;" +
    "background:rgba(20,20,18,.82);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);font-family:'Instrument Sans',system-ui,-apple-system,'Segoe UI',sans-serif;color:#f3efe4}" +
    ".jsg[hidden]{display:none}" +
    ".jsg .c{width:100%;max-width:380px;background:#262724;border:1px solid rgba(243,239,228,.14);border-radius:16px;padding:22px;box-shadow:0 20px 60px rgba(0,0,0,.6)}" +
    ".jsg .k{margin:0 0 6px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#FFC857}" +
    ".jsg h2{margin:0 0 8px;font:700 22px/1.2 'Unbounded','Arial Black',system-ui,sans-serif}" +
    ".jsg p{margin:0 0 14px;font-size:15px;line-height:1.45;color:#d9d6ca}" +
    ".jsg label{display:block;font-size:13px;margin-bottom:6px;color:#b9b7ab}" +
    ".jsg input{width:100%;box-sizing:border-box;font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid rgba(243,239,228,.25);background:#1b1c1a;color:#f3efe4}" +
    ".jsg input:focus{outline:2px solid #FFC857;outline-offset:1px}" +
    ".jsg button{width:100%;margin-top:10px;font:600 16px/1 'Instrument Sans',system-ui,sans-serif;padding:14px;border:0;border-radius:10px;background:#508B3F;color:#fff;cursor:pointer}" +
    ".jsg button:disabled{opacity:.6;cursor:default}" +
    ".jsg .n{min-height:1.2em;margin:10px 0 0;font-size:14px;color:#FFC857}" +
    ".jsg .s{margin:12px 0 0;font-size:12.5px;color:#b9b7ab;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}" +
    ".jsg .s a{color:#b9b7ab}" +
    ".jst{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:2147483001;background:#508B3F;color:#fff;font:600 15px/1.3 'Instrument Sans',system-ui,sans-serif;padding:12px 16px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.5);max-width:calc(100% - 32px);text-align:center}";

  var root, input, btn, note, open = false;
  function build() {
    if (root) return;
    var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
    root = document.createElement("div"); root.className = "jsg"; root.hidden = true;
    root.setAttribute("role", "dialog"); root.setAttribute("aria-modal", "true"); root.setAttribute("aria-labelledby", "jsgT");
    root.innerHTML =
      '<form class="c" novalidate>' +
      '<p class="k">Free round done</p>' +
      '<h2 id="jsgT">Keep playing</h2>' +
      '<p>Drop your email to unlock every game on Jay\'s Studio. You also get my free ebook, AI for Normies.</p>' +
      '<label for="jsgE">Your email</label>' +
      '<input id="jsgE" type="email" autocomplete="email" inputmode="email" placeholder="you@example.com">' +
      '<button type="submit">Unlock the games</button>' +
      '<p class="n" role="status"></p>' +
      '<p class="s"><span>No spam. Unsubscribe anytime.</span><a href="../">Back to the arcade</a></p>' +
      '</form>';
    document.body.appendChild(root);
    input = root.querySelector("input"); btn = root.querySelector("button"); note = root.querySelector(".n");
    /* keep taps and keys inside the card from reaching the game underneath */
    ["pointerdown", "pointerup", "mousedown", "mouseup", "touchstart", "touchend", "click", "keydown", "keyup", "keypress", "wheel"].forEach(function (t) {
      root.addEventListener(t, function (e) { e.stopPropagation(); }, false);
    });
    root.querySelector("form").addEventListener("submit", submit);
    /* inside the 3D studio's arcade screen, this link closes the game there instead */
    if (window.parent !== window) {
      var back = root.querySelector(".s a"); back.textContent = "Exit game";
      back.addEventListener("click", function (e) {
        e.preventDefault(); try { window.parent.postMessage({ type: "jaysstudio-exit-game" }, location.origin); } catch (err) {}
      });
    }
  }
  /* while the card is open, keys pressed anywhere else don't reach the game */
  ["keydown", "keyup", "keypress"].forEach(function (t) {
    window.addEventListener(t, function (e) {
      if (open && !(root && e.target && e.target.nodeType && root.contains(e.target))) { e.stopImmediatePropagation(); e.preventDefault(); if (input) input.focus(); }
    }, true);
  });

  function show() {
    if (signedUp() || open) return;
    build(); root.hidden = false; open = true; note.textContent = "";
    setTimeout(function () { try { input.focus({ preventScroll: true }); } catch (e) { input.focus(); } }, 50);
  }
  function hide() { if (root) root.hidden = true; open = false; }
  function toast(t) {
    var d = document.createElement("div"); d.className = "jst"; d.setAttribute("role", "status"); d.textContent = t;
    document.body.appendChild(d); setTimeout(function () { d.remove(); }, 5000);
  }
  function submit(e) {
    e.preventDefault();
    var v = input.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) { note.textContent = "Enter an email address like name@example.com."; input.focus(); return; }
    if (!window.SITE_SUBSCRIBE) { note.textContent = "Signup isn't connected right now, so nothing was saved. Try again later."; return; }
    btn.disabled = true; note.textContent = "Sending…";
    window.SITE_SUBSCRIBE(v).then(function (how) {
      set(KEY_IN, "1"); hide();
      toast(how === "fallback" ? "Finish signing up in the tab that just opened. The games are unlocked." : "You're in! Check your inbox to confirm, and the ebook follows.");
    }, function (why) {
      note.textContent = why === "invalid" ? "Kit didn't accept that address. Check it and try again." : "Couldn't reach the signup just now. Try again in a moment.";
    }).then(function () { btn.disabled = false; });
  }

  window.JS_ROUND_OVER = function () {
    if (signedUp()) return;
    if (!used()) { usedThisVisit = true; set(KEY_USED, "1"); }
    setTimeout(show, 1400);                 // let the game-over screen land first
  };
  /* came back after the free round: ask before the next one */
  function onReady() { if (!signedUp() && get(KEY_USED) === "1") show(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", onReady); else onReady();
})();
