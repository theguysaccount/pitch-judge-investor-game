// Embeddable widget: today's first pitch, linking to the game.
(function () {
  "use strict";
  var w = document.getElementById("ewidget");
  if (!w || !window.pjCore) return;
  var C = window.pjCore;
  var day = C.dayNumber(w.getAttribute("data-epoch"), new Date());
  fetch(w.getAttribute("data-deck")).then(function (r) { return r.json(); }).then(function (d) {
    var by = {}, outcomeOf = {};
    d.pitches.forEach(function (p) { by[p.slug] = p; outcomeOf[p.slug] = p.outcome; });
    var first = by[C.dailySet(Object.keys(by), day, parseInt(w.getAttribute("data-size"), 10), outcomeOf)[0]];
    w.querySelector(".ep").innerHTML = "Daily #" + day + " · " + first.year + " · " + first.stage + ": <b>" +
      String(first.headline).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }) + "</b>. Would you fund it?";
  }).catch(function () { /* the play button still works */ });
})();
