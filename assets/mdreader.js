/* sg-compute.sgit.ai — in-page markdown reader.
   Renders the raw markdown file named by #mdread[data-src] into the page using
   marked (loaded from CDN before this script). The raw file stays the source of
   truth; this is presentation only. Any failure falls back to a link to the raw
   file, so the document is always reachable. */
(function () {
  var el = document.getElementById('mdread');
  if (!el) return;
  var src = el.getAttribute('data-src');
  function fail() {
    el.innerHTML = '<p class="dim">Could not render the document in-page — ' +
      '<a href="' + src + '">open the raw markdown</a> instead.</p>';
  }
  el.innerHTML = '<p class="dim">Loading the document…</p>';
  fetch(src).then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.text();
  }).then(function (t) {
    if (!window.marked) return fail();
    el.innerHTML = marked.parse(t);
    /* Render ```mermaid fences as diagrams. Best-effort: if the mermaid module
       cannot load, the fence stays visible as a code block — never a blank hole. */
    var fences = el.querySelectorAll('code.language-mermaid');
    if (fences.length) {
      fences.forEach(function (c) {
        var holder = document.createElement('pre');
        holder.className = 'mermaid';
        holder.textContent = c.textContent;
        (c.parentElement.tagName === 'PRE' ? c.parentElement : c).replaceWith(holder);
      });
      import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs')
        .then(function (m) {
          m.default.initialize({ startOnLoad: false, theme: 'neutral',
            themeVariables: { fontFamily: 'ui-sans-serif, system-ui, sans-serif' } });
          m.default.run({ nodes: el.querySelectorAll('pre.mermaid') });
        })
        .catch(function () { /* fences remain readable as code */ });
    }
  }).catch(fail);
})();
