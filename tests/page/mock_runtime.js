/* Runtime Claude simulé pour tester la page du Radar : base de documents en mémoire, sample factice. */
(function () {
  var fixture = window.__FIXTURE__ || {};
  var store = {};
  Object.keys(fixture).forEach(function (c) { store[c] = {}; Object.keys(fixture[c]).forEach(function (id) { store[c][id] = JSON.parse(JSON.stringify(fixture[c][id])); }); });
  var listeners = {};
  var writes = [];
  function snapOf(c, q) {
    var ids = Object.keys(store[c] || {});
    var docs = ids.map(function (id) { return { id: id, data: function () { return JSON.parse(JSON.stringify(store[c][id])); } }; });
    if (q && q.order) { docs.sort(function (a, b) { var x = a.data()[q.order], y = b.data()[q.order]; return (q.dir === "desc" ? -1 : 1) * (x > y ? 1 : x < y ? -1 : 0); }); }
    if (q && q.limit) docs = docs.slice(0, q.limit);
    return { docs: docs, size: docs.length, empty: !docs.length };
  }
  function notify(c) { (listeners[c] || []).forEach(function (l) { setTimeout(function () { l.cb(snapOf(c, l.q)); }, 0); }); }
  function coll(c, q) {
    q = q || {};
    return {
      onSnapshot: function (cb) { (listeners[c] = listeners[c] || []).push({ cb: cb, q: q }); setTimeout(function () { cb(snapOf(c, q)); }, 0); return function () {}; },
      orderBy: function (f, d) { return coll(c, { order: f, dir: d || "asc", limit: q.limit }); },
      limit: function (n) { return coll(c, { order: q.order, dir: q.dir, limit: n }); },
      doc: function (id) {
        return {
          update: function (d) { writes.push({ op: "update", c: c, id: id, d: d }); store[c] = store[c] || {}; if (!store[c][id]) return Promise.reject({ code: "not_found" }); Object.assign(store[c][id], JSON.parse(JSON.stringify(d))); notify(c); return Promise.resolve(); },
          set: function (d) { writes.push({ op: "set", c: c, id: id, d: d }); store[c] = store[c] || {}; store[c][id] = JSON.parse(JSON.stringify(d)); notify(c); return Promise.resolve(); },
          get: function () { return Promise.resolve({ exists: !!(store[c] && store[c][id]), data: function () { return store[c] && store[c][id]; } }); }
        };
      }
    };
  }
  var samples = [];
  function sample(prompt, opts) {
    samples.push({ prompt: prompt, opts: opts && { modelTier: opts.modelTier } });
    var text = typeof window.__SAMPLE_TEXT__ === "function" ? window.__SAMPLE_TEXT__(prompt) : "## Section test\n- Réponse simulée";
    if (opts && opts.onText) opts.onText({ text: text });
    return Promise.resolve({ text: text });
  }
  sample.json = function (prompt) { samples.push({ prompt: prompt, json: true }); var r = window.__JSON_REPLY__; return Promise.resolve(typeof r === "function" ? r(prompt) : (r || {})); };
  window.__store = store; window.__writes = writes; window.__samples = samples;
  window.claude = {
    use: function (name) {
      if (window.__NO_DB__ && name === "db") return Promise.resolve(null);
      if (name === "db") return Promise.resolve({ collection: function (c) { return coll(c); } });
      if (name === "sample") return Promise.resolve(sample);
      if (name === "downloads") return Promise.resolve(null);
      return Promise.resolve(null);
    }
  };
})();
