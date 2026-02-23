// Smooth diagonal lines animation using requestAnimationFrame
(function() {
    const overlay = document.querySelector('.diagonal-lines');
    if (!overlay) return;

    let position = 0;
    const speed = 0.02; // pixels per frame – slow and smooth

    function animate() {
        position += speed;
        // Keep within pattern size (24px pattern)
        if (position >= 24) position = 0;
        overlay.style.backgroundPosition = `${position}px ${position}px`;
        requestAnimationFrame(animate);
    }

    animate();
})();