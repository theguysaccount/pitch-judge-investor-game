// Share buttons, case-file reveal and cookieless counting (only when the operator sets a GoatCounter endpoint;
// Do Not Track and Global Privacy Control switch it off).
(function () {
  "use strict";
  var queue = (window.__pjEvents = window.__pjEvents || []);
  var meta = document.querySelector('meta[name="pj-goatcounter"]');
  var endpoint = meta && meta.content;
  var optedOut = navigator.doNotTrack === "1" || window.doNotTrack === "1" || navigator.globalPrivacyControl === true;
  function count(path, title, isEvent) {
    if (!endpoint || optedOut) return;
    try {
      var img = new Image();
      img.src = endpoint + "?p=" + encodeURIComponent(path) + "&t=" + encodeURIComponent(title || "") + (isEvent ? "&e=true" : "") +
        "&r=" + encodeURIComponent(document.referrer || "") + "&rnd=" + Math.random();
    } catch (e) { /* never break the page */ }
  }
  window.pjTrack = function (name, detail) {
    queue.push({ name: name, detail: detail || null, at: new Date().toISOString() });
    count(name, detail ? String(detail) : name, true);
  };
  count(location.pathname, document.title, false);

  function copy(text, btn) {
    var done = function () { if (btn) { var o = btn.textContent; btn.textContent = "Copied"; setTimeout(function () { btn.textContent = o; }, 1400); } };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, done); else done();
  }

  document.addEventListener("click", function (ev) {
    var t = ev.target;
    // Case-file pages: decide, then the outcome opens.
    var choice = t.closest ? t.closest(".case .choices [data-call]") : null;
    if (choice) {
      var box = choice.parentNode, outcome = box.getAttribute("data-outcome"), call = choice.getAttribute("data-call");
      var right = call === "invest" ? outcome !== "bust" : outcome === "bust";
      box.innerHTML = '<p class="yourcall ' + (right ? "ok" : "no") + '">You said <b>' + call + "</b> — " + (right ? "good call." : "wrong call.") + "</p>";
      var d = document.getElementById("reveal");
      if (d) { d.open = true; d.scrollIntoView({ behavior: "smooth", block: "nearest" }); }
      window.pjTrack("case_call", call + ":" + (right ? "right" : "wrong"));
      return;
    }
    var el = t.closest ? t.closest("[data-share],[data-copy]") : null;
    if (!el) return;
    var row = el.closest(".share-row");
    if (el.hasAttribute("data-copy")) { copy(el.getAttribute("data-copy"), el); window.pjTrack("share", "copy"); return; }
    var kind = el.getAttribute("data-share");
    if (kind === "native" && row) {
      var url = row.getAttribute("data-share-url"), text = row.getAttribute("data-share-text");
      if (navigator.share) navigator.share({ text: text, url: url }).catch(function () {});
      else copy(text, el);
    }
    window.pjTrack("share", kind);
  });
})();
