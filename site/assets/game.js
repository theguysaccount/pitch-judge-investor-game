// The game: daily (same five pitches for everyone, by UTC date) or practice (ten at random).
(function () {
  "use strict";
  var root = document.getElementById("game");
  if (!root || !window.pjCore) return;
  var C = window.pjCore;
  var mode = root.getAttribute("data-mode"), size = parseInt(root.getAttribute("data-size"), 10);
  var base = root.getAttribute("data-base"), epoch = root.getAttribute("data-epoch");
  var day = C.dayNumber(epoch, new Date());
  var deck = {}, order = [], i = 0, results = [];
  var LABEL = { breakout: "🦄 Breakout", success: "✅ Success", bust: "💥 Bust" };

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function store(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }
  function load(k) { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch (e) { return null; } }
  function track(n, d) { if (window.pjTrack) window.pjTrack(n, d); }

  function dots() {
    var out = "";
    for (var k = 0; k < order.length; k++) {
      var r = results[k];
      out += '<span class="dot ' + (r ? (C.isRight(r.call, r.outcome) ? "ok" : "no") : (k === i ? "now" : "")) + '"></span>';
    }
    return '<div class="dots" aria-hidden="true">' + out + "</div>";
  }

  function header() {
    return '<p class="ghead">' + (mode === "daily" ? "Daily #" + day : "Practice") + " · pitch " + (Math.min(i + 1, order.length)) + " of " + order.length + "</p>" + dots();
  }

  function showPitch() {
    var p = deck[order[i]];
    root.innerHTML = header() + '<article class="card pitchcard"><p class="kicker">' + p.year + " \u00b7 " + esc(p.stage) +
      '</p><p class="hl">' + esc(p.headline) + "</p><p>" + esc(p.pitch) + '</p><ul class="facts">' +
      p.facts.map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("") + "</ul>" +
      '<div class="choices"><button type="button" class="btn invest" data-call="invest">Invest</button>' +
      '<button type="button" class="btn pass" data-call="pass">Pass</button></div></article>';
    root.querySelector(".invest").focus({ preventScroll: true });
  }

  function reveal(call) {
    var p = deck[order[i]];
    var right = C.isRight(call, p.outcome);
    results[i] = { slug: p.slug, call: call, outcome: p.outcome };
    track("call", call + ":" + (right ? "right" : "wrong"));
    var pros = p.kind === "tv" ? "On the TV pitch show: " + p.pros : "At the time: " + p.pros;
    var src = p.sources[0];
    var card = root.querySelector(".pitchcard");
    card.querySelector(".choices").innerHTML = '<p class="yourcall ' + (right ? "ok" : "no") + '">You said <b>' + (call === "invest" ? "invest" : "pass") +
      "</b> — " + (right ? "good call." : "wrong call.") + "</p>";
    card.insertAdjacentHTML("beforeend", '<div class="answer"><p class="verdict-line"><span class="badge o-' + p.outcome + '">' + LABEL[p.outcome] +
      "</span></p><p>It was <b>" + esc(p.name) + "</b>. " + esc(p.outcome_text) + '</p><p class="pros">' + esc(pros) + '</p><p class="fine"><a href="' +
      esc(src.url) + '" target="_blank" rel="noopener">Source</a> · <a href="' + base + "/pitch/" + p.slug + '/">Case file</a></p>' +
      '<button type="button" class="btn next">' + (i + 1 < order.length ? "Next pitch" : "See your score") + "</button></div>");
    root.querySelector(".dots").outerHTML = dots();
    root.querySelector(".next").focus({ preventScroll: true });
    if (mode === "daily") store("pj-daily-" + day, { results: results, done: results.filter(Boolean).length === order.length });
  }

  function countdown() {
    var now = new Date();
    var next = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + 1);
    var mins = Math.round((next - now.getTime()) / 60000);
    return Math.floor(mins / 60) + "h " + (mins % 60) + "m";
  }

  function finish() {
    var right = results.filter(function (r) { return C.isRight(r.call, r.outcome); }).length;
    var unicorns = results.filter(function (r) { return r.call === "invest" && r.outcome === "breakout"; }).length;
    var dodged = results.filter(function (r) { return r.call === "pass" && r.outcome === "bust"; }).length;
    var tv = results.filter(function (r) { return deck[r.slug].kind === "tv"; });
    var prosLine = "";
    if (tv.length) {
      var prosRight = tv.filter(function (r) { return C.isRight(deck[r.slug].pros_call, r.outcome); }).length;
      var youRight = tv.filter(function (r) { return C.isRight(r.call, r.outcome); }).length;
      prosLine = "<li>On TV pitches: you " + youRight + "/" + tv.length + ", the TV investors " + prosRight + "/" + tv.length + "</li>";
    }
    var url = base + (mode === "daily" ? "/" : "/practice/");
    var text = C.shareText(mode, day, results, url);
    var scoreUrl = base + "/score/" + right + "-of-" + results.length + "/";
    var stats = "";
    if (mode === "daily") {
      store("pj-daily-" + day, { results: results, done: true });
      var hist = load("pj-history") || {};
      hist[day] = right;
      store("pj-history", hist);
      var days = Object.keys(hist).length, avg = 0;
      Object.keys(hist).forEach(function (k) { avg += hist[k]; });
      stats = '<p class="fine">Played ' + days + " daily round" + (days === 1 ? "" : "s") + " on this device, average " + (avg / days).toFixed(1) +
        "/" + size + ". Next five in " + countdown() + " (midnight UTC).</p>";
    }
    track("game_complete", mode + ":" + right + "/" + results.length);
    root.innerHTML = header() + '<section class="card score"><p class="kicker">' + (mode === "daily" ? "Daily #" + day : "Practice round") +
      '</p><p class="big">' + right + "<span>/" + results.length + '</span></p><p class="marks">' + results.map(function (r) { return C.mark(r.call, r.outcome); }).join(" ") +
      "</p><ul class=\"tally\"><li>Breakouts you backed: " + unicorns + "</li><li>Busts you dodged: " + dodged + "</li>" + prosLine + "</ul>" +
      '<div class="share-row" data-share-url="' + esc(scoreUrl) + '" data-share-text="' + esc(text) + '" data-slug="score">' +
      '<button type="button" class="btn" data-share="native">Share score</button>' +
      '<button type="button" class="btn ghost" data-copy="' + esc(text) + '">Copy result</button>' +
      '<a class="btn ghost" data-share="x" target="_blank" rel="noopener" href="https://twitter.com/intent/tweet?text=' + encodeURIComponent(text) + '">Post on X</a></div>' +
      stats + '<p><a href="' + base + '/practice/">Play a practice round</a> · <a href="' + base + '/deck/">See every pitch</a></p>' +
      '<details class="review"><summary>Review your calls</summary><ol>' + results.map(function (r) {
        var p = deck[r.slug];
        return '<li>' + C.mark(r.call, r.outcome) + ' <a href="' + base + "/pitch/" + p.slug + '/">' + esc(p.name) + "</a> (" + p.year + "): you said " + r.call + ", " + LABEL[r.outcome] + "</li>";
      }).join("") + "</ol></details></section>";
  }

  root.addEventListener("click", function (ev) {
    var t = ev.target;
    if (t.matches && t.matches("[data-call]") && !results[i]) reveal(t.getAttribute("data-call"));
    else if (t.matches && t.matches(".next")) { i++; if (i < order.length) showPitch(); else finish(); }
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.target.tagName === "TEXTAREA" || ev.target.tagName === "INPUT") return;
    if (!results[i] && order.length && i < order.length && (ev.key === "i" || ev.key === "p")) reveal(ev.key === "i" ? "invest" : "pass");
  });

  fetch(root.getAttribute("data-deck")).then(function (r) { return r.json(); }).then(function (d) {
    d.pitches.forEach(function (p) { deck[p.slug] = p; });
    var slugs = Object.keys(deck), outcomeOf = {};
    slugs.forEach(function (s) { outcomeOf[s] = deck[s].outcome; });
    order = mode === "daily" ? C.dailySet(slugs, day, size, outcomeOf) : C.practiceSet(slugs, size);
    var saved = mode === "daily" ? load("pj-daily-" + day) : null;
    if (saved && saved.results && saved.results.length) {
      results = saved.results.filter(function (r) { return r && deck[r.slug]; });
      i = results.length;
      if (saved.done && results.length === order.length) { finish(); return; }
    }
    track("game_start", mode);
    if (i < order.length) showPitch(); else finish();
  }).catch(function () { root.innerHTML = '<p class="fine">Could not load the pitches. Try again in a moment.</p>'; });
})();
