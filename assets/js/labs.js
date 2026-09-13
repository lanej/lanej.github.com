// Load the WebGL application only when the reader asks to run it.
for (const demo of document.querySelectorAll('.live-demo')) {
  demo.addEventListener('toggle', () => {
    const frame = demo.querySelector('iframe');
    if (demo.open && !frame.getAttribute('src')) frame.src = frame.dataset.src;
    // Closing releases the embedded application's graphics and playback resources.
    if (!demo.open) frame.removeAttribute('src');
  });
}
