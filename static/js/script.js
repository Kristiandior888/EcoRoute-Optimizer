// Создание частиц для фона
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('particles');
    const particleCount = 41;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');

        const size = Math.random() * 20 + 5;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${Math.random() * 100}vw`;
        particle.style.animationDuration = `${Math.random() * 10 + 10}s`;
        particle.style.opacity = Math.random() * 0.5 + 0.1;
        particle.style.animationDelay = `${Math.random() * 5}s`;

        container.appendChild(particle);
    }
});