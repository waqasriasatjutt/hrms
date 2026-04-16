/** @odoo-module **/

// Inject HTML, CSS and audio for confetti animation
function injectConfettiEnvironment() {
    if (document.getElementById('confetti-style')) return;
  
    // Style
    const style = document.createElement('style');
    style.id = 'confetti-style';
    style.textContent = `
      @keyframes confetti-fire {
        0% {
          transform: translate(0, 0) rotate(0deg);
          opacity: 0;
        }
        10% {
          opacity: 1;
        }
        50% {
          transform: translate(var(--xPeak), -100vh) rotate(180deg);
        }
        100% {
          transform: translate(var(--xFall), 110vh) rotate(360deg);
          opacity: 0;
        }
      }
  
      .confetti {
        position: absolute;
        width: 10px;
        height: 20px;
        background-color: green;
        animation: confetti-fire ease-out forwards;
        z-index: 99999;
        pointer-events: none;
      }
    `;
    document.head.appendChild(style);
  
    // Audio
    if (!document.getElementById('redeemSound')) {
      const audio = document.createElement('audio');
      audio.id = 'redeemSound';
      audio.src = '/rewards_codes/static/lib/sounds/autoredeem_sound.mp3';
      audio.preload = 'auto';
      document.body.appendChild(audio);
    }
  }
  
  export function triggerConfetti() {
    injectConfettiEnvironment();
  
    for (let i = 0; i < 60; i++) {
      const confetti = document.createElement('div');
      confetti.className = 'confetti';
      confetti.style.left = '50vw';
      confetti.style.bottom = '-20px';
  
      const colors = ['green', 'yellow', 'red'];
      confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
  
      const xPeak = Math.random() * 1000 - 500;
      const xFall = xPeak + (Math.random() * 400 - 200);
  
      confetti.style.setProperty('--xPeak', `${xPeak}px`);
      confetti.style.setProperty('--xFall', `${xFall}px`);
  
      const duration = Math.random() * 1.5 + 2.5;
      confetti.style.animationDuration = `${duration}s`;
  
      if (Math.random() < 0.5) {
        const delay = Math.random() * 0.7 + 0.3;
        confetti.style.animationDelay = `${delay}s`;
      }
  
      document.body.appendChild(confetti);
  
      setTimeout(() => confetti.remove(), duration * 1000 + 1000);
    }
  
    const sound = document.getElementById('redeemSound');
    if (sound) sound.play();
  }
  