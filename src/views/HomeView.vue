<template>
  <div class="home">
    <div class="hero">
      <div class="hero-content">
        <p class="hero-eyebrow">Find your person</p>
        <h1 class="hero-title">Where connections<br><em>drift</em> into love</h1>
        <p class="hero-sub">DriftDater matches you with people who share your passions,
          your pace, and your place.</p>
        <div class="hero-cta">
          <router-link to="/register" class="btn btn-primary btn-lg">Get Started Free</router-link>
          <router-link to="/login"    class="btn btn-outline-light btn-lg">Sign In</router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="card-stack">
          <div class="fc fc1"><div class="fc-dot"></div>Alice, 25 · Kingston</div>
          <div class="fc fc2"><div class="fc-dot"></div>Bob, 27 · Half Way Tree</div>
          <div class="fc fc3"><div class="fc-dot rose"></div>Match! 💞</div>
        </div>
      </div>
    </div>

    <div class="features">
      <div class="feature">
        <div class="feat-icon">🎯</div>
        <h3>Smart Matching</h3>
        <p>Our algorithm scores compatibility on interests, location, and preferences — not just looks.</p>
      </div>
      <div class="feature">
        <div class="feat-icon">🔒</div>
        <h3>Safe & Private</h3>
        <p>Control who sees your profile. Message only people you've mutually matched with.</p>
      </div>
      <div class="feature">
        <div class="feat-icon">💬</div>
        <h3>Real Conversations</h3>
        <p>No bots, no spam. Just genuine people ready to connect.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home { background: var(--navy); min-height: 100vh; color: #fff; }
.hero {
  max-width: 1100px; margin: 0 auto; padding: 80px 24px 60px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center;
}
.hero-eyebrow {
  text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.8rem;
  color: var(--rose2); font-weight: 600; margin-bottom: 16px;
}
.hero-title {
  font-size: clamp(2.4rem, 5vw, 3.6rem); line-height: 1.15;
  color: #fff; margin-bottom: 20px;
}
.hero-title em { color: var(--rose2); font-style: italic; }
.hero-sub { color: rgba(255,255,255,0.6); font-size: 1.05rem; line-height: 1.7; margin-bottom: 36px; }
.hero-cta { display: flex; gap: 14px; flex-wrap: wrap; }
.btn-lg { padding: 13px 30px; font-size: 1rem; }
.btn-outline-light {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 13px 30px; font-size: 1rem; border-radius: 50px;
  border: 1.5px solid rgba(255,255,255,0.35); color: #fff;
  background: transparent; font-weight: 600; transition: all 0.2s;
}
.btn-outline-light:hover { background: rgba(255,255,255,0.08); }

/* Card stack visual */
.hero-visual { display: flex; justify-content: center; align-items: center; }
.card-stack { position: relative; width: 260px; height: 220px; }
.fc {
  position: absolute; padding: 18px 22px;
  background: rgba(255,255,255,0.07); backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.12); border-radius: 16px;
  font-size: 0.95rem; color: rgba(255,255,255,0.85); font-weight: 500;
  display: flex; align-items: center; gap: 10px;
}
.fc-dot { width: 10px; height: 10px; border-radius: 50%; background: #34d399; flex-shrink: 0; }
.fc-dot.rose { background: var(--rose); }
.fc1 { top: 0; left: 0; transform: rotate(-4deg); }
.fc2 { top: 60px; left: 30px; transform: rotate(2deg); }
.fc3 { top: 130px; left: 10px; background: rgba(244,63,94,0.15); border-color: rgba(244,63,94,0.4); }

.features {
  background: var(--navy2); padding: 70px 24px;
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 32px; max-width: 1100px; margin: 0 auto;
}
.feature { text-align: center; padding: 20px; }
.feat-icon { font-size: 2.2rem; margin-bottom: 14px; }
.feature h3 { font-size: 1.15rem; margin-bottom: 10px; color: #fff; }
.feature p  { color: rgba(255,255,255,0.55); line-height: 1.65; font-size: 0.92rem; }

@media (max-width: 768px) {
  .hero { grid-template-columns: 1fr; text-align: center; padding: 60px 20px 40px; }
  .hero-cta { justify-content: center; }
  .hero-visual { margin-top: 10px; }
  .features { grid-template-columns: 1fr; }
}
</style>
