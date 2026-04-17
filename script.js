/* ═══════════════════════════════════════════════════════════════════════════
   OKUBI Website — Scripts
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ─── Sticky Nav ────────────────────────────────────────────────────────
  const nav = document.getElementById('nav');
  const floatingCta = document.getElementById('floatingCta');
  const ctaPlaceholder = document.getElementById('heroCtaPlaceholder');
  const backToTop = document.getElementById('backToTop');

  const onScroll = () => {
    nav.classList.toggle('nav--scrolled', window.scrollY > 60);

    // Sticky CTA buttons — show fixed when scrolled past hero
    if (floatingCta && ctaPlaceholder) {
      const placeholderBottom = ctaPlaceholder.getBoundingClientRect().bottom;
      floatingCta.classList.toggle('floating-cta--visible', placeholderBottom < 0);
    }

    // Back to top button — show after scrolling 600px
    if (backToTop) {
      backToTop.classList.toggle('back-to-top--visible', window.scrollY > 600);
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ─── Back to Top Click ────────────────────────────────────────────────
  if (backToTop) {
    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ─── Founder Section — Gold Glow on Scroll ───────────────────────────
  const founderSection = document.getElementById('founderSection');
  const founderGlow = document.getElementById('founderGlow');

  if (founderSection && founderGlow) {
    const founderObs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        founderGlow.classList.toggle('founder-glow--active', e.isIntersecting);
        founderSection.classList.toggle('founder--visible', e.isIntersecting);
      });
    }, { threshold: 0.3 });
    founderObs.observe(founderSection);
  }

  // ─── Mobile Menu Toggle ───────────────────────────────────────────────
  const burger = document.getElementById('burger');
  const navLinks = document.querySelector('.nav__links-vertical');
  if (burger && navLinks) {
    burger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const spans = burger.querySelectorAll('span');
      const isOpen = navLinks.classList.contains('open');
      spans[0].style.transform = isOpen ? 'rotate(45deg) translate(5px, 5px)' : '';
      spans[1].style.opacity   = isOpen ? '0' : '1';
      spans[2].style.transform = isOpen ? 'rotate(-45deg) translate(5px, -5px)' : '';
    });

    // Close on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        const spans = burger.querySelectorAll('span');
        spans[0].style.transform = '';
        spans[1].style.opacity = '1';
        spans[2].style.transform = '';
      });
    });
  }

  // ─── Scroll Reveal ────────────────────────────────────────────────────
  const reveals = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
    );
    reveals.forEach((el) => observer.observe(el));
  } else {
    // Fallback: show everything
    reveals.forEach((el) => el.classList.add('revealed'));
  }

  // ─── Social Dropdown Toggle ──────────────────────────────────────────
  const socialBtn = document.getElementById('socialToggle');
  const socialDrop = document.getElementById('socialDropdown');
  if (socialBtn && socialDrop) {
    socialBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      socialDrop.classList.toggle('open');
    });
    document.addEventListener('click', () => {
      socialDrop.classList.remove('open');
    });
  }

  // ─── Smooth scroll for anchor links (fallback for older browsers) ─────
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ─── Parallax on Hero (subtle) ────────────────────────────────────────
  const heroBg = document.querySelector('.hero__bg');
  if (heroBg) {
    window.addEventListener('scroll', () => {
      const scrolled = window.scrollY;
      if (scrolled < window.innerHeight) {
        heroBg.style.transform = `translateY(${scrolled * 0.35}px)`;
      }
    }, { passive: true });
  }

  // ─── Feature Showcase (Dune-style) ──────────────────────────────────────
  const showcaseBg     = document.getElementById('showcaseBg');
  const showcaseTitle  = document.getElementById('showcaseTitle');
  const showcaseDesc   = document.getElementById('showcaseDesc');
  const showcaseGif    = document.getElementById('showcaseGif');
  const showcasePrev   = document.getElementById('showcasePrev');
  const showcaseNext   = document.getElementById('showcaseNext');

  if (showcaseBg) {
    const scBase = 'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2118100/';
    const scSlides = [
      {
        title: 'Crafting',
        desc: 'Forge powerful weapons, armor, and consumables from materials gathered across the world. Master recipes, refine your craft, and create gear worthy of legend.',
        bg: scBase + '9da5113383fd59e693e75b5d17daf2d0c4a0ee31/ss_9da5113383fd59e693e75b5d17daf2d0c4a0ee31.1920x1080.jpg?t=1771880532',
      },
      {
        title: 'Dynamic World\nEvents',
        desc: 'Unpredictable events erupt across the battlefield \u2014 meteor storms, power surges, and boss incursions. Adapt on the fly or be consumed by chaos.',
        bg: scBase + '0af0df51dd6d49ad833d1c31da54951a4fd54024/ss_0af0df51dd6d49ad833d1c31da54951a4fd54024.1920x1080.jpg?t=1771880532',
      },
      {
        title: 'Player-Driven\nEconomy',
        desc: 'Trade crafted masterpieces, rare materials, and coveted gear in a fully player-driven marketplace. Supply and demand shape the world\u2019s economy.',
        bg: scBase + 'ss_d5e9eacb3154eb00e00c06333f0508f95b6409a0.1920x1080.jpg?t=1771880532',
      },
      {
        title: 'Arenas',
        desc: 'Conquer diverse and treacherous PvP arenas where every battle is a step toward immortality. Crush your rivals and forge your name in ranked combat.',
        bg: scBase + 'ss_73670356941113b15de99a947a8f5a78d330fc03.1920x1080.jpg?t=1771880532',
      },
      {
        title: 'Planet\nIncursion',
        desc: 'Hostile forces invade from distant planets, unleashing waves of enemies across the map. Rally your allies, repel the incursion, and claim powerful rewards.',
        bg: scBase + '2b84f5d18ba9e7d3220f66bb2452f81d0a7468e0/ss_2b84f5d18ba9e7d3220f66bb2452f81d0a7468e0.1920x1080.jpg?t=1771880532',
      },
      {
        title: 'Gathering',
        desc: 'Explore the world to harvest rare resources, mine precious ores, and collect exotic materials. Every expedition fuels your crafting and trading ambitions.',
        bg: scBase + '7565960bb62dd2b6dcf468a49f6bc2aa57abe4e4/ss_7565960bb62dd2b6dcf468a49f6bc2aa57abe4e4.1920x1080.jpg?t=1771880532',
      },
    ];

    // Extra images for the GIF preview box (cycles randomly)
    const scPreviews = [
      scBase + '6aa4612bf582cd106b821c67c43e813867842ff4/ss_6aa4612bf582cd106b821c67c43e813867842ff4.1920x1080.jpg?t=1771880532',
      scBase + '1e9896257594062dc094547c53bafe2594175ed6/ss_1e9896257594062dc094547c53bafe2594175ed6.1920x1080.jpg?t=1771880532',
      scBase + 'ss_59483cb06c25df402b3ae31ce8a5a6549c85a165.1920x1080.jpg?t=1771880532',
      scBase + 'ss_6777c5d4c980e785c6b9590cd3b2d8baf9fa2e3a.1920x1080.jpg?t=1771880532',
      scBase + 'ss_58eac9c9aacc221dfe8cdfb19878cf7426bfea89.1920x1080.jpg?t=1771880532',
      scBase + 'ss_e14ab091205790f9fb0b5ba56ea975b129d87251.1920x1080.jpg?t=1771880532',
      scBase + 'ss_c4fb7988fb462a3d3169df0c43fee9ac96877032.1920x1080.jpg?t=1771880532',
      scBase + 'ss_2d50b11c0265189ccafb7515d559c89c31df2931.1920x1080.jpg?t=1771880532',
    ];

    let scIndex = 0;
    let scAutoTimer = null;

    function scGoTo(idx) {
      idx = ((idx % scSlides.length) + scSlides.length) % scSlides.length;
      if (idx === scIndex && showcaseBg.style.backgroundImage) return;

      // Fade out text
      showcaseTitle.style.opacity = '0';
      showcaseDesc.style.opacity = '0';

      // Fade background
      showcaseBg.classList.add('showcase__bg--fading');

      setTimeout(function() {
        scIndex = idx;
        var slide = scSlides[scIndex];
        showcaseBg.style.backgroundImage = "url('" + slide.bg + "')";
        showcaseBg.classList.remove('showcase__bg--fading');
        showcaseBg.classList.remove('showcase__bg--active');

        // Update text (replace \n with <br>)
        showcaseTitle.innerHTML = slide.title.replace(/\n/g, '<br>');
        showcaseDesc.textContent = slide.desc;

        showcaseTitle.style.opacity = '1';
        showcaseDesc.style.opacity = '1';

        // Ken Burns restart
        void showcaseBg.offsetWidth;
        showcaseBg.classList.add('showcase__bg--active');

        // Cycle preview image randomly
        var rnd = Math.floor(Math.random() * scPreviews.length);
        showcaseGif.src = scPreviews[rnd];
      }, 400);
    }

    function scNext() { scGoTo(scIndex + 1); }
    function scPrevFn() { scGoTo(scIndex - 1); }

    function scResetAuto() {
      clearInterval(scAutoTimer);
      scAutoTimer = setInterval(scNext, 7000);
    }

    if (showcaseNext) showcaseNext.addEventListener('click', function() { scNext(); scResetAuto(); });
    if (showcasePrev) showcasePrev.addEventListener('click', function() { scPrevFn(); scResetAuto(); });

    // Init first slide
    scGoTo(0);
    scResetAuto();
  }

  // ─── Auth: check login state ──────────────────────────────────────────
  const loginBtn = document.getElementById('loginBtn');
  const profileMenu = document.getElementById('profileMenu');
  const profileBtn = document.getElementById('profileBtn');
  const profileBtnName = document.getElementById('profileBtnName');
  const profileAvatar = document.getElementById('profileAvatar');
  const profileName = document.getElementById('profileName');
  const profileDropdown = document.getElementById('profileDropdown');

  if (loginBtn && profileMenu) {
    fetch('/auth/me')
      .then(r => r.json())
      .then(data => {
        if (data.logged_in) {
          loginBtn.style.display = 'none';
          profileMenu.style.display = '';
          const giftHint = document.getElementById('giftHint');
          if (giftHint) giftHint.style.display = 'none';
          profileBtnName.textContent = data.username || data.steam_id;
          profileName.textContent = data.username || data.steam_id;
          if (data.avatar) {
            profileAvatar.src = data.avatar;
            profileAvatar.alt = data.username;
          } else {
            profileAvatar.style.display = 'none';
          }
          const curr03El = document.getElementById('profileCurr03');
          if (data.curr03 && curr03El) {
            curr03El.textContent = '✦ ' + Number(data.curr03).toLocaleString();
          }
        }
      })
      .catch(() => {});

    if (profileBtn) {
      profileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        profileDropdown.classList.toggle('open');
      });
      document.addEventListener('click', () => {
        profileDropdown.classList.remove('open');
      });
    }
  }

  /* ── Corruption Showcase Tab Switching ── */
  const corruptionData = {
    tainted: {
      eyebrow: 'Tainted Zones',
      title: 'Lands Beyond Saving',
      body1: "Regions consumed by OKUBI's influence twist into nightmarish landscapes. The ground pulses with dark energy, creatures mutate into abominations, and the very air corrodes your armor.",
      body2: 'Venture deep enough and the corruption begins to affect your character — warping abilities, distorting vision, and whispering promises of power.',
      stats: [{ num: '12', label: 'Tainted Regions' }, { num: '5', label: 'Corruption Tiers' }, { num: '∞', label: 'Shifting Threats' }],
      bg: 'linear-gradient(225deg, rgba(80, 10, 10, 0.8) 0%, rgba(10, 10, 15, 0.95) 50%, rgba(30, 5, 20, 0.6) 100%)'
    },
    purification: {
      eyebrow: 'Purification Raids',
      title: 'Cleanse the Darkness',
      body1: 'Assemble elite squads to breach corrupted strongholds. Each raid demands coordination, sacrifice, and an iron will — one misstep and the corruption claims another soul.',
      body2: 'Purified zones unlock rare resources, ancient relics, and forgotten lore. The world remembers those who fought to heal it.',
      stats: [{ num: '8', label: 'Raid Dungeons' }, { num: '40', label: 'Player Capacity' }, { num: '3', label: 'Difficulty Modes' }],
      bg: 'linear-gradient(225deg, rgba(20, 60, 80, 0.8) 0%, rgba(10, 10, 15, 0.95) 50%, rgba(10, 40, 60, 0.6) 100%)'
    },
    worldboss: {
      eyebrow: 'World Boss Events',
      title: 'Titans of Corruption',
      body1: 'Colossal corrupted entities emerge without warning, reshaping entire regions. Hundreds of warriors must unite to bring down these world-ending threats before the corruption spreads further.',
      body2: 'Each titan has unique phases, mechanics, and devastating attacks. Defeat them to earn legendary rewards and push back the darkness — for now.',
      stats: [{ num: '6', label: 'Corrupted Titans' }, { num: '100+', label: 'Players per Fight' }, { num: '24h', label: 'Spawn Cycles' }],
      bg: 'linear-gradient(225deg, rgba(100, 40, 0, 0.8) 0%, rgba(10, 10, 15, 0.95) 50%, rgba(60, 20, 5, 0.6) 100%)'
    },
    spread: {
      eyebrow: 'Dynamic Corruption Spread',
      title: 'A Living Plague',
      body1: "The corruption isn't static — it grows, recedes, and adapts based on player activity across the entire server. Neglect a region and watch it fall. Defend it and earn its loyalty.",
      body2: 'Server-wide events trigger corruption surges that can consume safe zones overnight. The balance of the world rests in the hands of every player.',
      stats: [{ num: '∞', label: 'Dynamic Events' }, { num: '100%', label: 'Server-Driven' }, { num: '4', label: 'World States' }],
      bg: 'linear-gradient(225deg, rgba(50, 10, 60, 0.8) 0%, rgba(10, 10, 15, 0.95) 50%, rgba(40, 5, 50, 0.6) 100%)'
    }
  };

  const corruptionTags = document.querySelectorAll('.corruption__tag');
  const corruptionShowcase = document.getElementById('corruptionShowcase');
  const corruptionBg = document.getElementById('corruptionBg');

  if (corruptionTags.length && corruptionShowcase) {
    corruptionTags.forEach(tag => {
      tag.addEventListener('click', () => {
        const key = tag.dataset.corruption;
        const data = corruptionData[key];
        if (!data) return;

        corruptionTags.forEach(t => t.classList.remove('corruption__tag--active'));
        tag.classList.add('corruption__tag--active');

        corruptionShowcase.style.opacity = '0';
        corruptionShowcase.style.transform = 'translateY(12px)';

        setTimeout(() => {
          corruptionShowcase.innerHTML = `
            <p class="corruption-showcase__eyebrow">${data.eyebrow}</p>
            <h2 class="corruption-showcase__title">${data.title}</h2>
            <p class="corruption-showcase__body">${data.body1}</p>
            <p class="corruption-showcase__body">${data.body2}</p>
            <div class="corruption-showcase__stats">
              ${data.stats.map(s => `
                <div class="corruption-showcase__stat">
                  <span class="corruption-showcase__stat-num">${s.num}</span>
                  <span class="corruption-showcase__stat-label">${s.label}</span>
                </div>
              `).join('')}
            </div>
          `;
          if (corruptionBg) corruptionBg.style.background = data.bg;
          corruptionShowcase.style.opacity = '1';
          corruptionShowcase.style.transform = 'translateY(0)';
        }, 250);
      });
    });

    corruptionShowcase.style.transition = 'opacity 0.3s, transform 0.3s';
  }

  // ─── Classes Row — Click & Drag Scroll ─────────────────────────────────
  const classesRow = document.querySelector('.classes-row');
  if (classesRow) {
    let isDown = false, startX, scrollLeft, hasDragged = false;

    classesRow.addEventListener('mousedown', e => {
      isDown = true;
      hasDragged = false;
      startX = e.pageX - classesRow.offsetLeft;
      scrollLeft = classesRow.scrollLeft;
    });

    classesRow.addEventListener('mouseleave', () => {
      isDown = false;
      classesRow.classList.remove('is-dragging');
    });

    classesRow.addEventListener('mouseup', () => {
      isDown = false;
      setTimeout(() => classesRow.classList.remove('is-dragging'), 0);
    });

    classesRow.addEventListener('mousemove', e => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - classesRow.offsetLeft;
      const walk = x - startX;
      if (Math.abs(walk) > 5) {
        hasDragged = true;
        classesRow.classList.add('is-dragging');
      }
      classesRow.scrollLeft = scrollLeft - walk;
    });

    // Prevent click navigation when dragging
    classesRow.addEventListener('click', e => {
      if (hasDragged) {
        e.preventDefault();
        e.stopPropagation();
        hasDragged = false;
      }
    }, true);
  }

  // ─── Radar Chart Generator ──────────────────────────────────────────
  const radarEl = document.querySelector('.radar-chart');
  if (radarEl) {
    const stats = radarEl.dataset.stats.split(',').map(Number);
    const labels = ['Utility', 'Damage', 'Tankyness', 'Mobility', 'Burst'];
    const cx = 160, cy = 160, maxR = 120, levels = 5, n = 5;

    function polarToXY(angle, r) {
      const rad = (angle - 90) * Math.PI / 180;
      return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
    }

    const angles = labels.map((_, i) => i * 360 / n);
    let svg = `<svg viewBox="0 0 320 320" xmlns="http://www.w3.org/2000/svg">`;

    // Grid levels
    for (let lv = 1; lv <= levels; lv++) {
      const r = maxR * lv / levels;
      const pts = angles.map(a => polarToXY(a, r).join(',')).join(' ');
      svg += `<polygon points="${pts}" class="radar-chart__grid"/>`;
    }

    // Axis lines
    angles.forEach(a => {
      const [x, y] = polarToXY(a, maxR);
      svg += `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" class="radar-chart__axis"/>`;
    });

    // Data polygon
    const dataPts = stats.map((v, i) => polarToXY(angles[i], maxR * v / 10));
    svg += `<polygon points="${dataPts.map(p => p.join(',')).join(' ')}" class="radar-chart__data"/>`;

    // Data dots
    dataPts.forEach(([x, y]) => {
      svg += `<circle cx="${x}" cy="${y}" r="4" class="radar-chart__dot"/>`;
    });

    // Labels
    angles.forEach((a, i) => {
      const [x, y] = polarToXY(a, maxR + 22);
      svg += `<text x="${x}" y="${y}" class="radar-chart__label">${labels[i]}</text>`;
    });

    svg += `</svg>`;
    radarEl.innerHTML = svg;
  }

  // ─── Class Page Tab Switching ───────────────────────────────────────
  const tabBtns = document.querySelectorAll('.class-tabs__btn');
  const tabPanels = document.querySelectorAll('.class-tab-panel');

  if (tabBtns.length && tabPanels.length) {
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.tab;
        tabBtns.forEach(b => b.classList.remove('class-tabs__btn--active'));
        tabPanels.forEach(p => p.classList.remove('class-tab-panel--active'));
        btn.classList.add('class-tabs__btn--active');
        const panel = document.querySelector(`[data-panel="${target}"]`);
        if (panel) panel.classList.add('class-tab-panel--active');
      });
    });
  }

  // ─── Faction Card + Tab Switching ──────────────────────────────────
  const factionCards = document.querySelectorAll('.faction-card[data-faction]');
  const factionTabs = document.querySelectorAll('.faction-detail__tab');
  const factionPanels = document.querySelectorAll('.faction-panel');

  if (factionCards.length) {
    let activeFaction = null;

    factionCards.forEach(card => {
      card.addEventListener('click', () => {
        activeFaction = card.dataset.faction;
        factionCards.forEach(c => c.classList.remove('faction-card--active'));
        document.querySelectorAll(`.faction-card[data-faction="${card.dataset.faction}"]`)
          .forEach(c => c.classList.add('faction-card--active'));
      });
    });

    // ─── Dim overlays as main buttons ───
    const factionGlow = document.getElementById('factions-glow');
    const dimLeft = document.getElementById('factions-dim-left');
    const dimRight = document.getElementById('factions-dim-right');

    function selectFaction(faction) {
      activeFaction = faction;
      factionCards.forEach(c => c.classList.remove('faction-card--active'));
      document.querySelectorAll(`.faction-card[data-faction="${faction}"]`)
        .forEach(c => c.classList.add('faction-card--active'));
      // Toggle centered detail panel
      document.querySelectorAll('.faction-center-detail__content')
        .forEach(el => el.classList.remove('faction-center-detail__content--active'));
      const panel = document.querySelector(`[data-fcontent="${faction}"]`);
      if (panel) panel.classList.add('faction-center-detail__content--active');
      if (dimLeft && dimRight) {
        dimLeft.classList.remove('factions__dim--revealed');
        dimRight.classList.remove('factions__dim--revealed');
        if (faction === 'umbra') dimLeft.classList.add('factions__dim--revealed');
        else if (faction === 'sol') dimRight.classList.add('factions__dim--revealed');
      }
      if (factionGlow) {
        factionGlow.className = 'factions__glow factions__glow--' + faction;
      }
    }

    if (dimLeft) {
      // dims are visual only, no click/hover
    }
    if (dimRight) {
      // dims are visual only, no click/hover
    }
    // Faction card name + icon clicks trigger selection
    factionCards.forEach(card => {
      const clickables = card.querySelectorAll('.faction-card__name, .faction-card__icon');
      clickables.forEach(el => {
        el.addEventListener('click', () => selectFaction(card.dataset.faction));
        el.addEventListener('mouseenter', () => {
          document.querySelectorAll(`.faction-card[data-faction="${card.dataset.faction}"]`)
            .forEach(c => c.classList.add('faction-card--hovered'));
        });
        el.addEventListener('mouseleave', () => {
          document.querySelectorAll(`.faction-card[data-faction="${card.dataset.faction}"]`)
            .forEach(c => c.classList.remove('faction-card--hovered'));
        });
      });
    });

    // Default: select left side (umbra)
    selectFaction('umbra');
  }

  // ─── Screenshots Carousel ────────────────────────────────────────────
  const ssImage = document.getElementById('ssImage');
  const ssDots = document.getElementById('ssDots');
  const ssArrowPrev = document.getElementById('ssArrowPrev');
  const ssArrowNext = document.getElementById('ssArrowNext');

  if (ssImage && ssDots) {
    const ssBase = 'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2118100/';
    const ssScreenshots = [
      '9da5113383fd59e693e75b5d17daf2d0c4a0ee31/ss_9da5113383fd59e693e75b5d17daf2d0c4a0ee31.1920x1080.jpg?t=1771880532',
      '0af0df51dd6d49ad833d1c31da54951a4fd54024/ss_0af0df51dd6d49ad833d1c31da54951a4fd54024.1920x1080.jpg?t=1771880532',
      'ss_d5e9eacb3154eb00e00c06333f0508f95b6409a0.1920x1080.jpg?t=1771880532',
      'ss_73670356941113b15de99a947a8f5a78d330fc03.1920x1080.jpg?t=1771880532',
      '2b84f5d18ba9e7d3220f66bb2452f81d0a7468e0/ss_2b84f5d18ba9e7d3220f66bb2452f81d0a7468e0.1920x1080.jpg?t=1771880532',
      '7565960bb62dd2b6dcf468a49f6bc2aa57abe4e4/ss_7565960bb62dd2b6dcf468a49f6bc2aa57abe4e4.1920x1080.jpg?t=1771880532',
      '6aa4612bf582cd106b821c67c43e813867842ff4/ss_6aa4612bf582cd106b821c67c43e813867842ff4.1920x1080.jpg?t=1771880532',
      '1e9896257594062dc094547c53bafe2594175ed6/ss_1e9896257594062dc094547c53bafe2594175ed6.1920x1080.jpg?t=1771880532',
      'ss_59483cb06c25df402b3ae31ce8a5a6549c85a165.1920x1080.jpg?t=1771880532',
      'ss_6777c5d4c980e785c6b9590cd3b2d8baf9fa2e3a.1920x1080.jpg?t=1771880532',
      'ss_58eac9c9aacc221dfe8cdfb19878cf7426bfea89.1920x1080.jpg?t=1771880532',
      'ss_e14ab091205790f9fb0b5ba56ea975b129d87251.1920x1080.jpg?t=1771880532',
      'ss_c4fb7988fb462a3d3169df0c43fee9ac96877032.1920x1080.jpg?t=1771880532',
      'ss_2d50b11c0265189ccafb7515d559c89c31df2931.1920x1080.jpg?t=1771880532',
    ];

    let ssIndex = 0;
    let ssTimer = null;

    ssScreenshots.forEach((_, i) => {
      const dot = document.createElement('button');
      dot.className = 'screenshots-carousel__dot' + (i === 0 ? ' screenshots-carousel__dot--active' : '');
      dot.addEventListener('click', () => ssGoTo(i));
      ssDots.appendChild(dot);
    });

    function ssGoTo(idx) {
      if (idx === ssIndex) return;
      ssImage.classList.add('screenshots-carousel__img--fading');
      setTimeout(() => {
        ssIndex = idx;
        ssImage.src = ssBase + ssScreenshots[ssIndex];
        ssImage.alt = 'OKUBI Screenshot ' + (ssIndex + 1);
        ssImage.classList.remove('screenshots-carousel__img--fading');
        ssDots.querySelectorAll('.screenshots-carousel__dot').forEach((d, i) => {
          d.classList.toggle('screenshots-carousel__dot--active', i === ssIndex);
        });
      }, 300);
      ssResetTimer();
    }

    function ssNext() { ssGoTo((ssIndex + 1) % ssScreenshots.length); }
    function ssPrev() { ssGoTo((ssIndex - 1 + ssScreenshots.length) % ssScreenshots.length); }

    function ssResetTimer() {
      clearInterval(ssTimer);
      ssTimer = setInterval(ssNext, 7000);
    }

    if (ssArrowPrev) ssArrowPrev.addEventListener('click', ssPrev);
    if (ssArrowNext) ssArrowNext.addEventListener('click', ssNext);

    ssResetTimer();
  }

})();
