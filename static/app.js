// tiny helpers (no build step)
(function () {
  // Auto-close Django flash messages after 4s (optional)
  const msgs = document.querySelectorAll('[data-auto-hide]');
  if (!msgs.length) return;
  setTimeout(() => msgs.forEach(m => m.remove()), 4000);
})();
