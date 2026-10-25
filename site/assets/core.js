// Shared game logic (daily selection, scoring, share text). Used by game.js and embed.js, and by the Node tests.
(function (root) {
  "use strict";
  function dayNumber(epoch, now) {
    var p = epoch.split("-").map(Number);
    var e = Date.UTC(p[0], p[1] - 1, p[2]);
    var t = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
    return Math.floor((t - e) / 86400000) + 1;
  }
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function shuffle(arr, rnd) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(rnd() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  // Every day in a cycle gets different pitches; each new cycle reshuffles the whole deck.
  function dailySet(slugs, day, size) {
    var sorted = slugs.slice().sort();
    var per = Math.max(1, Math.floor(sorted.length / size));
    var d = Math.max(1, day);
    var cycle = Math.floor((d - 1) / per), pos = (d - 1) % per;
    return shuffle(sorted, mulberry32(1000003 * (cycle + 1))).slice(pos * size, pos * size + size);
  }
  function practiceSet(slugs, size, rnd) {
    return shuffle(slugs, rnd || Math.random).slice(0, size);
  }
  function isRight(call, outcome) {
    return call === "invest" ? outcome !== "bust" : outcome === "bust";
  }
  function mark(call, outcome) {
    if (!isRight(call, outcome)) return "❌";
    return call === "invest" && outcome === "breakout" ? "🦄" : "✅";
  }
  function shareText(mode, day, results, url) {
    var right = results.filter(function (r) { return isRight(r.call, r.outcome); }).length;
    var head = mode === "daily" ? "Would You Fund It? #" + day + " " + right + "/" + results.length
                                : "Would You Fund It? practice " + right + "/" + results.length;
    return head + "\n" + results.map(function (r) { return mark(r.call, r.outcome); }).join("") + "\n" + url;
  }
  root.pjCore = { dayNumber: dayNumber, dailySet: dailySet, practiceSet: practiceSet, isRight: isRight, mark: mark,
                  shareText: shareText, mulberry32: mulberry32 };
})(typeof window !== "undefined" ? window : globalThis);
