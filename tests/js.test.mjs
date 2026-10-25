// Node tests for the shared game logic in site/assets/core.js.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const ctx = { window: {} };
vm.createContext(ctx);
vm.runInContext(readFileSync(path.join(root, "site/assets/core.js"), "utf8"), ctx);
const C = ctx.window.pjCore;
const deck = JSON.parse(readFileSync(path.join(root, "data/pitches.json"), "utf8"));
const slugs = deck.map((p) => p.slug);
const outcomeOf = Object.fromEntries(deck.map((p) => [p.slug, p.outcome]));

test("day numbers count from the epoch in UTC", () => {
  assert.equal(C.dayNumber("2026-10-25", new Date(Date.UTC(2026, 9, 25, 0, 0))), 1);
  assert.equal(C.dayNumber("2026-10-25", new Date(Date.UTC(2026, 9, 25, 23, 59))), 1);
  assert.equal(C.dayNumber("2026-10-25", new Date(Date.UTC(2026, 9, 26, 0, 1))), 2);
});

test("the daily set is the same for everyone and changes each day", () => {
  const a = C.dailySet(slugs, 7, 5), b = C.dailySet(slugs.slice().reverse(), 7, 5);
  assert.deepEqual([...a], [...b]);
  assert.equal(a.length, 5);
  assert.notDeepEqual([...C.dailySet(slugs, 8, 5)], [...a]);
});

test("a full cycle deals every pitch at most once", () => {
  const per = Math.floor(slugs.length / 5);
  const seen = new Set();
  for (let d = 1; d <= per; d++) for (const s of C.dailySet(slugs, d, 5)) { assert.ok(!seen.has(s), "repeat " + s); seen.add(s); }
  assert.equal(seen.size, per * 5);
});

test("scoring and share text", () => {
  assert.equal(C.isRight("invest", "breakout"), true);
  assert.equal(C.isRight("invest", "success"), true);
  assert.equal(C.isRight("invest", "bust"), false);
  assert.equal(C.isRight("pass", "bust"), true);
  assert.equal(C.isRight("pass", "success"), false);
  const text = C.shareText("daily", 12, [{ call: "invest", outcome: "breakout" }, { call: "pass", outcome: "bust" }, { call: "invest", outcome: "bust" }], "https://x/");
  assert.equal(text, "Would You Fund It? #12 2/3\n🦄✅❌\nhttps://x/");
});

test("practice deals distinct pitches", () => {
  const set = C.practiceSet(slugs, 10, C.mulberry32(42));
  assert.equal(new Set(set).size, 10);
});

test("stratified dailies mix busts and winners and still never repeat within a cycle", () => {
  const per = Math.floor(slugs.length / 5);
  const seen = new Set();
  for (let d = 1; d <= per; d++) {
    const set = [...C.dailySet(slugs, d, 5, outcomeOf)];
    const busts = set.filter((s) => outcomeOf[s] === "bust").length;
    assert.ok(busts >= 2 && busts <= 3, "day " + d + " has " + busts + " busts");
    for (const s of set) { assert.ok(!seen.has(s)); seen.add(s); }
  }
  assert.deepEqual([...C.dailySet(slugs, 3, 5, outcomeOf)], [...C.dailySet(slugs.slice().reverse(), 3, 5, outcomeOf)]);
});
