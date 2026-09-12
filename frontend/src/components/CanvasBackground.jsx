import React, { useEffect, useRef } from 'react';

/**
 * CanvasBackground
 * High-performance, cursor-reactive constellation particle simulation.
 * - 60 particles drifting at gentle velocities
 * - Smooth lerped repelling vector when within 150px of cursor
 * - Faint constellation connecting threads (< 100px) in #2FD97F / #8FEFC3
 * - Radial cursor aura for subtle ambient illumination
 * - 60fps requestAnimationFrame with throttled ref position tracking
 * - Respects prefers-reduced-motion
 */
export default function CanvasBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let animId;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Mouse coordinates stored in ref/variables (no React state updates per frame)
    const mouse = {
      x: -1000,
      y: -1000,
      targetX: -1000,
      targetY: -1000,
      radius: 160,
      active: false,
    };

    const handleMouseMove = (e) => {
      mouse.targetX = e.clientX;
      mouse.targetY = e.clientY;
      mouse.active = true;
    };

    const handleMouseLeave = () => {
      mouse.active = false;
      mouse.targetX = -1000;
      mouse.targetY = -1000;
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    // Create 55-65 particles
    const particleCount = Math.floor(Math.min(width, 1600) / 26);
    const particles = [];

    const colors = [
      'rgba(244, 63, 133, 0.85)', // Radiant Dark Pink #F43F85
      'rgba(253, 164, 175, 0.78)', // Luminous Pearl Rose #FDA4AF
      'rgba(253, 251, 253, 0.65)', // Pearl White #FDFBFD
    ];

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        originX: Math.random() * width,
        originY: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        radius: Math.random() * 1.5 + 1.2,
        color: colors[i % colors.length],
        pulseSpeed: Math.random() * 0.02 + 0.008,
        pulseVal: Math.random() * Math.PI,
      });
    }

    if (prefersReducedMotion) {
      // Draw static peaceful constellation grid without animation
      ctx.clearRect(0, 0, width, height);
      particles.forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.fill();
      });
      return () => {
        window.removeEventListener('resize', handleResize);
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseleave', handleMouseLeave);
      };
    }

    // 60fps Render Loop
    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Smooth mouse lerp
      mouse.x += (mouse.targetX - mouse.x) * 0.12;
      mouse.y += (mouse.targetY - mouse.y) * 0.12;

      // Draw subtle ambient cursor glow if active (Dark Pink / Pearl Rose)
      if (mouse.active && mouse.x > 0 && mouse.y > 0) {
        const glowGradient = ctx.createRadialGradient(
          mouse.x,
          mouse.y,
          0,
          mouse.x,
          mouse.y,
          mouse.radius * 1.25
        );
        glowGradient.addColorStop(0, 'rgba(244, 63, 133, 0.12)');
        glowGradient.addColorStop(0.5, 'rgba(253, 164, 175, 0.04)');
        glowGradient.addColorStop(1, 'rgba(11, 8, 10, 0)');
        ctx.fillStyle = glowGradient;
        ctx.beginPath();
        ctx.arc(mouse.x, mouse.y, mouse.radius * 1.25, 0, Math.PI * 2);
        ctx.fill();
      }

      // Update and draw particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Natural drifting
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around boundaries
        if (p.x < -10) p.x = width + 10;
        else if (p.x > width + 10) p.x = -10;
        if (p.y < -10) p.y = height + 10;
        else if (p.y > height + 10) p.y = -10;

        // Cursor interaction: smooth repelling vector
        const dx = p.x - mouse.x;
        const dy = p.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < mouse.radius && mouse.active) {
          const force = (1 - dist / mouse.radius) * 3.5;
          const angle = Math.atan2(dy, dx);
          p.x += Math.cos(angle) * force;
          p.y += Math.sin(angle) * force;
        }

        // Draw connections to nearby neighbors
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const cdx = p.x - p2.x;
          const cdy = p.y - p2.y;
          const cdist = Math.sqrt(cdx * cdx + cdy * cdy);

          if (cdist < 105) {
            // Check if connection is near mouse for subtle proximity brighten
            const midX = (p.x + p2.x) / 2;
            const midY = (p.y + p2.y) / 2;
            const mouseDist = Math.sqrt(
              (midX - mouse.x) ** 2 + (midY - mouse.y) ** 2
            );
            const proximityBoost = mouseDist < mouse.radius && mouse.active ? 0.08 : 0;

            const alpha = Math.min(
              0.18,
              (1 - cdist / 105) * 0.13 + proximityBoost
            );
            ctx.strokeStyle = `rgba(253, 164, 175, ${alpha})`;
            ctx.lineWidth = 0.85;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }

        // Draw particle with gentle breathing pulse
        p.pulseVal += p.pulseSpeed;
        const currentSize = p.radius + Math.sin(p.pulseVal) * 0.35;

        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, currentSize, 0, Math.PI * 2);
        ctx.fill();
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
      cancelAnimationFrame(animId);
    };
  }, []);

  return <canvas ref={canvasRef} className="canvas-background" />;
}
