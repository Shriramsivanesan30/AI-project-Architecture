// MCET Activity System — Main JavaScript
// Branding: Orange (#E8420A), High Engagement

// ─────────────────────────────────────────────────────────────────────────────
// COIN TOSS ANIMATION (The "Tossing" Effect)
// ─────────────────────────────────────────────────────────────────────────────

window.tossCoins = function (x, y, amount = 5, points = 100) {
  const coinEmoji = '🪙';

  for (let i = 0; i < amount; i++) {
    const coin = document.createElement('div');
    coin.innerHTML = coinEmoji;
    coin.style.position = 'fixed';
    coin.style.left = x + 'px';
    coin.style.top = y + 'px';
    coin.style.fontSize = '1.5rem';
    coin.style.zIndex = '99999'; // Boost z-index
    coin.style.pointerEvents = 'none';
    coin.style.userSelect = 'none';
    document.body.appendChild(coin);

    const angle = (Math.random() * Math.PI) - Math.PI;
    const velocity = 8 + Math.random() * 12;
    let vx = Math.cos(angle) * (velocity * 0.6);
    let vy = Math.sin(angle) * velocity;
    let rotation = 0;
    let opacity = 1;
    let curX = x;
    let curY = y;

    const gravity = 0.6;

    function animate() {
      curX += vx;
      curY += vy;
      vy += gravity;
      rotation += 15;
      opacity -= 0.015;

      coin.style.transform = `translate(${curX - x}px, ${curY - y}px) rotate(${rotation}deg)`;
      coin.style.opacity = opacity;

      if (opacity > 0) {
        requestAnimationFrame(animate);
      } else {
        coin.remove();
      }
    }
    requestAnimationFrame(animate);
  }

  const msg = document.createElement('div');
  msg.innerHTML = `<strong>+${points} PTS</strong>`;
  msg.style.position = 'fixed';
  msg.style.left = x + 'px';
  msg.style.top = (y - 40) + 'px';
  msg.style.color = '#E8420A';
  msg.style.fontSize = '2.2rem'; // Making text larger
  msg.style.fontWeight = '900';
  msg.style.zIndex = '100000';
  msg.style.pointerEvents = 'none';
  msg.style.textShadow = '0 0 20px rgba(232, 66, 10, 0.6)';
  document.body.appendChild(msg);

  msg.animate([
    { transform: 'translateY(0) scale(1)', opacity: 1 },
    { transform: 'translateY(-200px) scale(1.5)', opacity: 0 }
  ], {
    duration: 1800,
    easing: 'ease-out'
  }).onfinish = () => msg.remove();
};

// ─────────────────────────────────────────────────────────────────────────────
// EVENT INTERCEPTORS
// ─────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // 1. Intercept Approvals (SPOC/HOD/IQAC) - Stays with the button for Admins

  // 3. Alert Auto-Dismiss
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      alert.style.transition = 'all 0.5s ease';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// SIDEBAR & UI UTILS
// ─────────────────────────────────────────────────────────────────────────────

function toggleSidebar() {
  document.querySelector('.sidebar')?.classList.toggle('open');
}

window.toggleMetrics = function() {
  const el = document.getElementById('consolidation');
  if (el) {
    const isHidden = window.getComputedStyle(el).display === 'none';
    el.style.display = isHidden ? 'block' : 'none';
    if (isHidden) {
      // Small delay to let the display:block settle before scrolling
      setTimeout(() => {
        const topbarHeight = document.querySelector('.topbar')?.offsetHeight || 70;
        const elementPosition = el.getBoundingClientRect().top + window.pageYOffset;
        window.scrollTo({
          top: elementPosition - topbarHeight - 20, // 20px extra padding
          behavior: 'smooth'
        });
      }, 50);
    }
  } else {
    window.location.href = "/dashboard/?openMetrics=1";
  }
};

function showRejectForm(id) {
  const el = document.getElementById('reject-form-' + id) || document.getElementById('reject-box');
  if (el) {
    el.style.display = (el.style.display === 'none' || el.style.display === '') ? 'block' : 'none';
    if (el.style.display === 'block') el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}
