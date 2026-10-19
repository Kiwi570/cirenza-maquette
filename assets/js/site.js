/* =====================================================================
   Lisa Cirenza · moteur d'animation « Strates » (sans bibliothèque)
   Défilement fluide, ouverture en carotte de cire (WebGL), révélations « cire qui fond »,
   salles épinglées, colonne stratigraphique, grattage, carte en courbes de niveau,
   fiche d'œuvre avec loupe et Voir au mur, statut de l'Espace en direct.
   Au repos, chaque œuvre est une simple image : couleurs et cadrage intacts.
   ===================================================================== */
(function () {
  'use strict';

  var D = window.LC_DONNEES || { textes: {}, oeuvres: {}, series: {} };
  var T = D.textes || {};
  var P = window.LC_PAGE || {};
  var html = document.documentElement;
  var RACINE = html.getAttribute('data-racine') || '';
  var A = RACINE + 'assets/';
  var params = new URLSearchParams(location.search);
  var ETAT = {
    reduit: html.classList.contains('mouvement-reduit'),
    fin: !!(window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches),
    gl: null
  };
  var CALCAIRE = '#f2efe8';

  /* ------------------------------------------------------------ outils */
  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  var EASE = {
    sortie: function (t) { return 1 - Math.pow(1 - t, 3); },
    io: function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  };
  function attendre(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function animer(duree, maj, ease) {
    ease = ease || EASE.sortie;
    var annule = false;
    var promesse = new Promise(function (res) {
      var t0 = performance.now();
      function f(now) {
        if (annule) { res(false); return; }
        var p = clamp((now - t0) / duree, 0, 1);
        maj(ease(p), p);
        if (p < 1) requestAnimationFrame(f); else res(true);
      }
      requestAnimationFrame(f);
    });
    return { promesse: promesse, annuler: function () { annule = true; } };
  }
  function decoder(img) {
    if (!img) return Promise.resolve();
    if (img.decode) return img.decode().catch(function () {});
    return new Promise(function (r) { if (img.complete) r(); else { img.onload = r; img.onerror = r; } });
  }
  function chargerImage(src) {
    return new Promise(function (res, rej) {
      var i = new Image();
      i.decoding = 'async';
      i.onload = function () { res(i); };
      i.onerror = rej;
      i.src = src;
    });
  }
  function urlOeuvre(id, taille) { return A + 'img/oeuvres/' + id + '-' + taille + '.webp'; }

  /* ------------------------------------------------------------ boucle unique */
  var taches = [];
  var dernier = performance.now();
  function boucle(now) {
    var dt = Math.min(0.064, (now - dernier) / 1000);
    dernier = now;
    for (var i = 0; i < taches.length; i++) taches[i](dt, now);
    requestAnimationFrame(boucle);
  }
  requestAnimationFrame(boucle);
  var redims = [];
  function surRedim(f) { redims.push(f); }
  function toutRemesurer() { redims.forEach(function (f) { try { f(); } catch (e) { console.warn(e); } }); }
  (function () {
    var t, lw = innerWidth, lh = innerHeight;
    addEventListener('resize', function () {
      clearTimeout(t);
      t = setTimeout(function () {
        var dw = innerWidth !== lw, dh = Math.abs(innerHeight - lh) > 120;
        if (!dw && !dh) return;
        lw = innerWidth; lh = innerHeight;
        toutRemesurer();
      }, 160);
    });
  })();

  /* ------------------------------------------------------------ défilement fluide */
  var lissage = {
    actif: false, cible: 0, courant: 0, enCours: false, verrou: 0,
    max: function () { return Math.max(0, document.documentElement.scrollHeight - innerHeight); },
    init: function () {
      var self = this;
      if (ETAT.reduit || !ETAT.fin) return;
      this.actif = true;
      this.cible = this.courant = scrollY;
      addEventListener('wheel', function (e) {
        if (self.verrou || e.ctrlKey || e.defaultPrevented) return;
        var t = e.target;
        if (t && t.closest && t.closest('[data-defilement-natif], .fiche, .mur, .menu, select, textarea')) return;
        if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
        e.preventDefault();
        var dy = e.deltaY;
        if (e.deltaMode === 1) dy *= 40; else if (e.deltaMode === 2) dy *= innerHeight;
        if (!self.enCours) self.cible = self.courant = scrollY;
        self.cible = clamp(self.cible + dy, 0, self.max());
        self.enCours = true;
      }, { passive: false });
      addEventListener('scroll', function () { if (!self.enCours) self.cible = self.courant = scrollY; }, { passive: true });
      addEventListener('keydown', function (e) {
        if (['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' ', 'Spacebar'].indexOf(e.key) > -1) self.stop();
      });
      addEventListener('pointerdown', function () { self.stop(); }, { passive: true });
      taches.push(function (dt) { self.tic(dt); });
    },
    stop: function () { this.enCours = false; this.cible = this.courant = scrollY; },
    tic: function (dt) {
      if (!this.enCours) return;
      var k = 1 - Math.pow(1 - 0.11, dt * 60);
      this.courant = lerp(this.courant, this.cible, k);
      if (Math.abs(this.cible - this.courant) < 0.5) { this.courant = this.cible; this.enCours = false; }
      window.scrollTo(0, this.courant);
    },
    aller: function (y, instant) {
      y = clamp(y, 0, this.max());
      if (!this.actif || instant) { window.scrollTo(0, y); this.cible = this.courant = y; this.enCours = false; return; }
      this.courant = scrollY; this.cible = y; this.enCours = true;
    }
  };

  /* ------------------------------------------------------------ couleur de fond */
  var demandesFond = [];
  var fondCourant = null;
  taches.push(function () {
    var c = CALCAIRE;
    for (var i = 0; i < demandesFond.length; i++) { var d = demandesFond[i](); if (d) c = d; }
    if (c === fondCourant) return;
    fondCourant = c;
    html.style.setProperty('--fond', c);
    var meta = $('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', c);
  });

  /* ------------------------------------------------------------ lettres une à une */
  function decouper(el) {
    if (el.getAttribute('data-decoupe')) return;
    el.setAttribute('data-decoupe', '1');
    var texte = el.textContent.replace(/\s+/g, ' ').trim();
    var vis = document.createElement('span');
    vis.setAttribute('aria-hidden', 'true');
    while (el.firstChild) vis.appendChild(el.firstChild);
    var i = 0;
    (function traiter(noeud) {
      Array.prototype.slice.call(noeud.childNodes).forEach(function (enfant) {
        if (enfant.nodeType === 3) {
          var frag = document.createDocumentFragment();
          enfant.textContent.normalize('NFC').split(/(\s+)/).forEach(function (m) {
            if (!m) return;
            if (/^\s+$/.test(m)) { frag.appendChild(document.createTextNode(' ')); return; }
            m.replace(/-/g, '-\u0000').split('\u0000').forEach(function (morceau) {
              if (!morceau) return;
              var mot = document.createElement('span');
              mot.className = 'mot';
              Array.from(morceau).forEach(function (c) {
                var l = document.createElement('span');
                l.className = 'l';
                l.style.setProperty('--i', i++);
                l.textContent = c;
                mot.appendChild(l);
              });
              frag.appendChild(mot);
            });
          });
          enfant.parentNode.replaceChild(frag, enfant);
        } else if (enfant.nodeType === 1) traiter(enfant);
      });
    })(vis);
    var vh = document.createElement('span');
    vh.className = 'vh';
    vh.textContent = texte;
    el.appendChild(vh);
    el.appendChild(vis);
  }

  /* ------------------------------------------------------------ révélations */
  function montrer(el) {
    el.classList.add('est-visible');
    var masque = el.matches('[data-revele], .cire-fond') || el.querySelector(':scope > .oeuvre__bouton .cire-fond');
    if (masque) {
      var fini = function () { el.classList.add('revele-fini'); };
      setTimeout(fini, 1700);
    }
    if (el.classList.contains('jauge')) compteur(el);
  }
  var obs = ('IntersectionObserver' in window) ? new IntersectionObserver(function (entrees) {
    entrees.forEach(function (en) {
      if (en.isIntersecting) { montrer(en.target); obs.unobserve(en.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }) : null;
  function observer(el) {
    if (ETAT.reduit || !obs) { el.classList.add('est-visible', 'revele-fini'); if (el.classList.contains('jauge')) compteur(el); return; }
    obs.observe(el);
  }
  function revelations() {
    $$('[data-lettres]').forEach(decouper);
    $$('[data-lettres]').forEach(function (el) {
      if (el.hasAttribute('data-lettres-auto')) return;
      if (el.closest('.menu')) return;
      observer(el);
    });
    $$('[data-apparait]').forEach(function (el) { if (!el.closest('[data-ouverture]')) observer(el); });
    $$('[data-revele], .cire-fond, [data-colonne], [data-frise] .couche, .jauge').forEach(function (el) {
      if (el.closest('.salle--epinglee') && el.classList.contains('cire-fond')) { observerSalle(el); return; }
      observer(el);
    });
  }
  // dans une salle épinglée, l'observation se fait sur l'axe horizontal du collant
  var obsSalle = null;
  function observerSalle(el) {
    if (ETAT.reduit || !('IntersectionObserver' in window)) { el.classList.add('est-visible', 'revele-fini'); return; }
    if (!obsSalle) obsSalle = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (en) { if (en.isIntersecting) { montrer(en.target); obsSalle.unobserve(en.target); } });
    }, { rootMargin: '0px -6% 0px -6%', threshold: 0.05 });
    obsSalle.observe(el);
  }

  /* ------------------------------------------------------------ mots lus au défilement */
  function mots() {
    $$('[data-mots]').forEach(function (el) {
      var texte = el.textContent.trim();
      el.textContent = '';
      var liste = texte.split(/\s+/).map(function (m, i, arr) {
        var s = document.createElement('span');
        s.className = 'mot-m';
        s.textContent = m;
        el.appendChild(s);
        if (i < arr.length - 1) el.appendChild(document.createTextNode(' '));
        return s;
      });
      if (ETAT.reduit) return;
      var haut = 0, hauteur = 0, n = -1;
      function mesurer() { var r = el.getBoundingClientRect(); haut = r.top + scrollY; hauteur = r.height; n = -1; }
      mesurer(); surRedim(mesurer); addEventListener('load', mesurer);
      taches.push(function () {
        var p = clamp((scrollY + innerHeight * 0.86 - haut) / (hauteur + innerHeight * 0.32), 0, 1);
        var k = Math.round(p * liste.length);
        if (k === n) return;
        n = k;
        for (var i = 0; i < liste.length; i++) liste[i].classList.toggle('est-lu', i < k);
      });
    });
  }

  /* ------------------------------------------------------------ parallaxe douce */
  function parallaxes() {
    if (ETAT.reduit) return;
    var items = $$('[data-parallaxe]').map(function (el) { return { el: el, f: Number(el.getAttribute('data-parallaxe')) || 0, c: 0 }; });
    if (!items.length) return;
    var dernierY = -1;
    function mesurer() {
      items.forEach(function (it) {
        it.el.style.transform = '';
        var r = it.el.getBoundingClientRect();
        it.c = r.top + scrollY + r.height / 2;
      });
      dernierY = -1;
    }
    mesurer(); surRedim(mesurer); addEventListener('load', mesurer);
    taches.push(function () {
      var y = scrollY;
      if (y === dernierY) return;
      dernierY = y;
      var milieu = y + innerHeight / 2;
      items.forEach(function (it) {
        var d = it.c - milieu;
        if (Math.abs(d) > innerHeight * 1.6) return;
        it.el.style.transform = 'translate3d(0,' + (d * it.f).toFixed(1) + 'px,0)';
      });
    });
  }

  /* panorama du lac (glisse à l'horizontale) */
  function panoramas() {
    if (ETAT.reduit) return;
    $$('[data-panorama]').forEach(function (bloc) {
      var img = $('img', bloc);
      if (!img) return;
      var haut = 0, h = 0;
      function mesurer() { var r = bloc.getBoundingClientRect(); haut = r.top + scrollY; h = r.height; }
      mesurer(); surRedim(mesurer); addEventListener('load', mesurer);
      taches.push(function () {
        var p = clamp((scrollY + innerHeight - haut) / (innerHeight + h), 0, 1);
        img.style.transform = 'translate3d(' + (-p * 16).toFixed(2) + '%,0,0)';
      });
    });
    // carnets de photos : la bande glisse à l'horizontale pendant que la section traverse l'écran
    $$('[data-defile]').forEach(function (piste) {
      var fen = piste.parentNode, sec = piste.closest('section') || fen;
      var dist = 0, haut = 0, h = 0, dernier = -1;
      function mesurer() {
        piste.style.transform = 'none';
        dist = Math.max(0, piste.scrollWidth - fen.clientWidth);
        var r = sec.getBoundingClientRect(); haut = r.top + scrollY; h = r.height; dernier = -1;
      }
      mesurer(); surRedim(mesurer); addEventListener('load', mesurer);
      taches.push(function () {
        if (!dist) return;
        var p = clamp((scrollY + innerHeight - haut) / (innerHeight + h), 0, 1);
        if (Math.abs(p - dernier) < 0.0005) return;
        dernier = p;
        piste.style.transform = 'translate3d(' + (-p * dist).toFixed(1) + 'px,0,0)';
      });
    });
    // panorama épinglé de l'Espace
    $$('[data-panorama-pin]').forEach(function (sec) {
      var col = $('.panorama__collant', sec), img = $('img', sec);
      if (!col || !img) return;
      sec.classList.add('panorama--epingle');
      var dist = 0, haut = 0;
      function mesurer() {
        img.style.transform = 'none';
        dist = Math.max(0, img.getBoundingClientRect().width - innerWidth);
        sec.style.height = Math.round(innerHeight + dist * 0.9) + 'px';
        haut = sec.getBoundingClientRect().top + scrollY;
      }
      if (img.complete) mesurer(); else img.addEventListener('load', mesurer);
      surRedim(mesurer); addEventListener('load', mesurer);
      taches.push(function () {
        var p = dist ? clamp((scrollY - haut) / (dist * 0.9), 0, 1) : 0;
        img.style.transform = 'translate3d(' + (-p * dist).toFixed(1) + 'px,0,0)';
      });
    });
  }

  /* ------------------------------------------------------------ en-tête, menu */
  function entete() {
    var h = $('[data-entete]');
    if (!h) return;
    var ancien = scrollY;
    taches.push(function () {
      var y = scrollY;
      if (Math.abs(y - ancien) < 3) return;
      var descend = y > ancien;
      h.classList.toggle('est-cache', descend && y > 180 && !html.classList.contains('menu-ouvert'));
      h.classList.toggle('a-defile', y > 16);
      ancien = y;
    });
  }
  function menu() {
    var b = $('.entete__menu'), m = $('#menu');
    if (!b || !m) return;
    var txt = $('.entete__menu-texte', b);
    function basculer(ouvrir) {
      b.setAttribute('aria-expanded', String(ouvrir));
      m.hidden = !ouvrir;
      html.classList.toggle('menu-ouvert', ouvrir);
      if (txt) txt.textContent = ouvrir ? T.fermer : T.menu;
      if (ouvrir) {
        lissage.verrou++;
        document.body.style.overflow = 'hidden';
        $$('[data-lettres]', m).forEach(function (el) { el.classList.remove('est-visible'); void el.offsetWidth; el.classList.add('est-visible'); });
        var a = $('a', m);
        if (a) a.focus();
      } else {
        lissage.verrou = Math.max(0, lissage.verrou - 1);
        document.body.style.overflow = '';
      }
    }
    b.addEventListener('click', function () { basculer(m.hidden); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !m.hidden) { basculer(false); b.focus(); } });
    m.addEventListener('click', function (e) { if (e.target.closest('a')) basculer(false); });
  }

  /* ------------------------------------------------------------ altimètre */
  function altimetre() {
    var alt = $('.altimetre');
    if (!alt) return;
    var cur = $('.altimetre__curseur', alt), lab = $('.altimetre__strate', alt);
    var secs = [];
    function mesurer() {
      secs = $$('[data-strate]').map(function (s) { return { t: s.getBoundingClientRect().top + scrollY, n: s.getAttribute('data-strate') }; });
    }
    mesurer(); surRedim(mesurer); addEventListener('load', mesurer);
    setTimeout(mesurer, 1500);
    var dernierP = -1, dernierN = null;
    taches.push(function () {
      var max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
      var p = clamp(scrollY / max, 0, 1);
      if (Math.abs(p - dernierP) > 0.001) { dernierP = p; cur.style.setProperty('--p', p.toFixed(4)); }
      var y = scrollY + innerHeight * 0.4, n = secs.length ? secs[0].n : '';
      for (var i = 0; i < secs.length; i++) if (secs[i].t <= y) n = secs[i].n;
      if (n !== dernierN) { dernierN = n; lab.textContent = n; }
    });
  }

  /* ------------------------------------------------------------ curseur chalumeau, aimants, inclinaison */
  var curseur = null;
  function initCurseur() {
    if (!ETAT.fin || ETAT.reduit) return;
    html.classList.add('curseur-perso');
    var c = document.createElement('div');
    c.className = 'curseur';
    c.setAttribute('aria-hidden', 'true');
    c.innerHTML = '<span class="curseur__flamme"></span><span class="curseur__point"></span><span class="curseur__texte"></span>';
    document.body.appendChild(c);
    var txt = $('.curseur__texte', c);
    var x = -100, y = -100, cx = -100, cy = -100;
    addEventListener('pointermove', function (e) {
      if (e.pointerType && e.pointerType !== 'mouse') return;
      x = e.clientX; y = e.clientY;
      if (!c.classList.contains('est-actif')) { cx = x; cy = y; c.classList.add('est-actif'); }
    }, { passive: true });
    document.documentElement.addEventListener('pointerleave', function () { c.classList.remove('est-actif'); });
    document.addEventListener('pointerover', function (e) {
      var t = e.target.closest ? e.target.closest('[data-curseur]') : null;
      var etiquette = t && t.getAttribute('data-curseur');
      if (etiquette) { txt.textContent = etiquette; c.classList.add('a-etiquette'); c.classList.remove('sur-lien'); }
      else {
        c.classList.remove('a-etiquette');
        c.classList.toggle('sur-lien', !!(e.target.closest && e.target.closest('a, button, input, select, textarea, label, summary')));
      }
    });
    taches.push(function (dt) {
      var k = 1 - Math.pow(1 - 0.3, dt * 60);
      cx += (x - cx) * k; cy += (y - cy) * k;
      c.style.transform = 'translate3d(' + cx.toFixed(1) + 'px,' + cy.toFixed(1) + 'px,0)';
    });
    curseur = c;
  }
  function aimants() {
    if (!ETAT.fin || ETAT.reduit) return;
    $$('.aimant').forEach(function (el) {
      var r = null, s = el.querySelector('span');
      el.addEventListener('pointerenter', function () {
        r = el.getBoundingClientRect();
        el.style.transition = 'transform .25s cubic-bezier(.22,1,.36,1)';
        if (s) s.style.transition = el.style.transition;
      });
      el.addEventListener('pointermove', function (e) {
        if (!r) r = el.getBoundingClientRect();
        var dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
        el.style.transform = 'translate(' + (dx * 0.22).toFixed(1) + 'px,' + (dy * 0.3).toFixed(1) + 'px)';
        if (s) s.style.transform = 'translate(' + (dx * 0.08).toFixed(1) + 'px,' + (dy * 0.1).toFixed(1) + 'px)';
      });
      el.addEventListener('pointerleave', function () {
        r = null;
        el.style.transition = 'transform .9s cubic-bezier(.34,1.56,.64,1)';
        el.style.transform = '';
        if (s) { s.style.transition = el.style.transition; s.style.transform = ''; }
      });
    });
  }
  function inclinaisons() {
    if (!ETAT.fin || ETAT.reduit) return;
    $$('[data-incline]').forEach(function (el) {
      var cible = el.querySelector(':scope > a') || el;
      var r = null;
      el.addEventListener('pointerenter', function () { r = el.getBoundingClientRect(); cible.style.transition = 'transform .2s'; });
      el.addEventListener('pointermove', function (e) {
        if (!r) r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
        cible.style.transform = 'rotateY(' + (px * 9).toFixed(2) + 'deg) rotateX(' + (-py * 9).toFixed(2) + 'deg) translateZ(6px)';
      });
      el.addEventListener('pointerleave', function () { r = null; cible.style.transition = 'transform .8s cubic-bezier(.22,1,.36,1)'; cible.style.transform = ''; });
    });
  }

  /* ------------------------------------------------------------ salles épinglées */
  function Piste(sec) {
    var self = this;
    this.sec = sec;
    this.collant = $('.salle__collant', sec);
    this.piste = $('.salle__piste', sec);
    this.items = Array.prototype.slice.call(this.piste.children);
    this.barre = $('.salle__progres', sec);
    this.p = -1; this.actif = -1; this.couleur = null;
    sec.classList.add('salle--epinglee');
    this.mesurer();
    surRedim(function () { self.mesurer(); });
    addEventListener('load', function () { self.mesurer(); });
    taches.push(function () { self.maj(); });
    demandesFond.push(function () { return self.enZone ? self.couleur : null; });
    sec.addEventListener('focusin', function (e) { self.focus(e); });
  }
  Piste.prototype.mesurer = function () {
    this.piste.style.transform = 'none';
    var vw = this.collant.clientWidth || innerWidth;
    var vh = this.collant.clientHeight || innerHeight;
    this.distance = Math.max(0, this.piste.scrollWidth - vw);
    this.sec.style.height = Math.round(this.distance + vh) + 'px';
    this.haut = this.sec.getBoundingClientRect().top + scrollY;
    this.vw = vw; this.vh = vh;
    this.centres = this.items.map(function (it) { return it.offsetLeft + it.offsetWidth / 2; });
    this.p = -1;
  };
  Piste.prototype.maj = function () {
    var y = scrollY;
    this.enZone = y > this.haut - this.vh * 0.5 && y < this.haut + this.distance + this.vh * 0.4;
    if (y + innerHeight < this.haut - 300 || y > this.haut + this.distance + innerHeight + 300) return;
    var p = this.distance ? clamp((y - this.haut) / this.distance, 0, 1) : 0;
    if (p === this.p) return;
    this.p = p;
    var x = -p * this.distance;
    this.piste.style.transform = 'translate3d(' + x.toFixed(1) + 'px,0,0)';
    if (this.barre) this.barre.style.setProperty('--p', p.toFixed(4));
    var c = -x + this.vw / 2, best = 0, d = Infinity;
    for (var i = 0; i < this.centres.length; i++) { var dd = Math.abs(this.centres[i] - c); if (dd < d) { d = dd; best = i; } }
    if (best !== this.actif) {
      this.actif = best;
      var f = this.items[best].getAttribute('data-fond');
      if (f) this.couleur = f;
    }
  };
  Piste.prototype.focus = function (e) {
    var it = this.items.filter(function (i) { return i.contains(e.target); })[0];
    if (!it || !this.distance) return;
    var idx = this.items.indexOf(it);
    var cible = clamp((this.centres[idx] - this.vw / 2) / this.distance, 0, 1);
    lissage.aller(this.haut + cible * this.distance, true);
  };

  /* ------------------------------------------------------------ carottage (biographie) */
  function carottage() {
    var liste = $('[data-carottage]');
    if (!liste || ETAT.reduit) return;
    var haut = 0, h = 0;
    function mesurer() { var r = liste.getBoundingClientRect(); haut = r.top + scrollY; h = r.height; }
    mesurer(); surRedim(mesurer); addEventListener('load', mesurer);
    taches.push(function () {
      var p = clamp((scrollY + innerHeight * 0.75 - haut) / h, 0.02, 1);
      liste.style.setProperty('--carotte', p.toFixed(4));
    });
  }

  /* ------------------------------------------------------------ jauges */
  function jauges() {
    $$('[data-jauge]').forEach(function (j) {
      var n = Number(j.getAttribute('data-jauge')) || 0;
      var box = $('.jauge__points', j);
      for (var k = 0; k < n; k++) { var i = document.createElement('i'); i.style.setProperty('--k', k); box.appendChild(i); }
    });
  }
  function compteur(j) {
    var el = $('[data-compteur]', j);
    if (!el || ETAT.reduit) return;
    var n = Number(el.getAttribute('data-compteur'));
    animer(1400, function (e) { el.textContent = String(Math.round(e * n)); });
  }

  /* ------------------------------------------------------------ WebGL */
  var VS = 'attribute vec2 p;varying vec2 v;void main(){v=vec2(p.x*.5+.5,.5-p.y*.5);gl_Position=vec4(p,0.,1.);}';
  var FS_STRATES = [
    'precision mediump float;',
    'varying vec2 v;',
    'uniform sampler2D uStr;uniform sampler2D uRel;',
    'uniform float uT;uniform float uAspect;uniform float uTexAspect;uniform vec2 uSouris;uniform float uChaleur;',
    'void main(){',
    '  float n=9.;',
    '  vec2 uv=v;',
    '  float ca=uAspect/uTexAspect;',
    '  vec2 tuv=uv;',
    '  if(ca>1.){tuv.y=(uv.y-.5)/ca+.5;}else{tuv.x=(uv.x-.5)*ca+.5;}',
    '  float b=floor(uv.y*n);',
    '  float yy=fract(uv.y*n);',
    '  float r=texture2D(uRel,vec2(uv.x*1.3,b*.13+.05)).r;',
    '  float r2=texture2D(uRel,vec2(uv.x*3.1+.2,b*.21)).r;',
    '  float ts=b/n*.5;',
    '  float d=distance(vec2(uv.x*uAspect,uv.y),vec2(uSouris.x*uAspect,uSouris.y));',
    '  float chaud=uChaleur*(1.-smoothstep(0.,.32,d));',
    '  float m=clamp((uT-ts)/.42+chaud*.35,0.,1.);',
    '  m=m*m*(3.-2.*m);',
    '  float bord=m*(1.32+(r-.5)*.9)+(r2-.5)*.12*m;',
    '  float al=mix(1.,smoothstep(bord-.03,bord+.03,yy),step(.002,m));',
    '  float creux=1.-smoothstep(0.,.5,abs(yy-bord-.25));',
    '  vec2 s=vec2(tuv.x+(r-.5)*.02*m,(b+clamp(yy-m*.28,0.,1.))/n);',
    '  if(ca>1.){s.y=(s.y-.5)/ca+.5;}',
    '  vec3 col=texture2D(uStr,s).rgb;',
    '  float brillance=(1.-smoothstep(0.,.09,yy-bord))*step(bord,yy)*.45*sign(m);',
    '  col=col+brillance*vec3(1.,.93,.8)+creux*.04*m;',
    '  al*=1.-smoothstep(.9,1.,uT);',
    '  gl_FragColor=vec4(col*al,al);',
    '}'
  ].join('\n');
  var FS_TRANSITION = [
    'precision mediump float;',
    'varying vec2 v;',
    'uniform sampler2D uA;uniform sampler2D uB;uniform sampler2D uRelief;',
    'uniform vec4 uRA;uniform vec4 uRB;uniform float uP;uniform float uDir;',
    'vec4 lire(sampler2D t,vec4 r,vec2 uv){vec2 l=(uv-r.xy)/r.zw;if(l.x<0.||l.x>1.||l.y<0.||l.y>1.)return vec4(0.);return vec4(texture2D(t,l).rgb,1.);}',
    'void main(){',
    '  float r=texture2D(uRelief,v*vec2(1.2,.8)).r;',
    '  float front=mix(-.4,1.4,uP);',
    '  float w=1.-smoothstep(front-.1,front+.1,v.y+(r-.5)*.5);',
    '  float onde=sin(uP*3.14159);',
    '  vec2 d=vec2((r-.5)*.04,(r-.3)*.12*uDir)*onde;',
    '  vec4 a=lire(uA,uRA,v-d*(1.-w));',
    '  vec4 b=lire(uB,uRB,v+d*w*.6);',
    '  vec4 col=mix(a,b,w);',
    '  gl_FragColor=vec4(col.rgb*col.a,col.a);',
    '}'
  ].join('\n');

  function glDispo() {
    if (ETAT.gl !== null) return ETAT.gl;
    var choix = params.get('gl');
    if (choix === 'non' || ETAT.reduit) return (ETAT.gl = false);
    try {
      var c = document.createElement('canvas');
      var g = c.getContext('webgl', { failIfMajorPerformanceCaveat: choix !== 'force' });
      if (!g) return (ETAT.gl = false);
      if (choix !== 'force') {
        var ext = g.getExtension('WEBGL_debug_renderer_info');
        var r = ext ? String(g.getParameter(ext.UNMASKED_RENDERER_WEBGL)) : '';
        if (/swiftshader|llvmpipe|software|basic render/i.test(r)) return (ETAT.gl = false);
        if ((navigator.deviceMemory && navigator.deviceMemory < 2) || (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 3)) return (ETAT.gl = false);
      }
      var perte = g.getExtension('WEBGL_lose_context');
      if (perte) perte.loseContext();
      return (ETAT.gl = true);
    } catch (e) { return (ETAT.gl = false); }
  }
  function moteurGL(canvas, frag) {
    var gl = null;
    try { gl = canvas.getContext('webgl', { premultipliedAlpha: true, alpha: true, antialias: false }); } catch (e) { return null; }
    if (!gl) return null;
    function sh(type, src) {
      var s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { console.warn(gl.getShaderInfoLog(s)); return null; }
      return s;
    }
    var vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, frag);
    if (!vs || !fs) return null;
    var prog = gl.createProgram();
    gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return null;
    gl.useProgram(prog);
    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, 'p');
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var textures = {}, perdu = false;
    canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); perdu = true; });
    return {
      gl: gl,
      perdu: function () { return perdu || gl.isContextLost(); },
      u: function (n) { return gl.getUniformLocation(prog, n); },
      texture: function (unite, nom, source, repeter) {
        var t = textures[nom] || gl.createTexture();
        gl.activeTexture(gl.TEXTURE0 + unite);
        gl.bindTexture(gl.TEXTURE_2D, t);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
        gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, source);
        gl.uniform1i(gl.getUniformLocation(prog, nom), unite);
        textures[nom] = t;
      },
      taille: function () {
        var dpr = Math.min(1.5, window.devicePixelRatio || 1);
        var w = Math.max(1, Math.round(canvas.clientWidth * dpr)), h = Math.max(1, Math.round(canvas.clientHeight * dpr));
        if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
        gl.viewport(0, 0, w, h);
        return [w, h];
      },
      dessiner: function () { gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); gl.drawArrays(gl.TRIANGLES, 0, 3); },
      liberer: function () {
        Object.keys(textures).forEach(function (k) { gl.deleteTexture(textures[k]); });
        gl.deleteBuffer(buf); gl.deleteProgram(prog);
        var ext = gl.getExtension('WEBGL_lose_context');
        if (ext) ext.loseContext();
      }
    };
  }

  /* ------------------------------------------------------------ ouverture : la carotte de cire fond */
  function ouverture() {
    var sec = $('[data-ouverture]');
    if (!sec) return;
    var titre = $('#titre-accueil');
    var auto = $$('[data-lettres-auto]', sec);
    var apparait = $$('[data-apparait]', sec);
    var passer = $('.ouverture__passer', sec);
    var canvas = $('.ouverture__gl', sec);
    var img = $('.ouverture__toile img', sec);
    var moteur = null, anim = null, termine = false;
    function toutMontrer() {
      auto.forEach(function (a) { a.classList.add('est-visible'); });
      apparait.forEach(function (a) { a.classList.add('est-visible'); });
    }
    if (ETAT.reduit || params.get('ouverture') === 'non') { toutMontrer(); return; }
    html.classList.add('ouverture-en-cours');
    if (passer) passer.hidden = false;
    function surTouche(e) { if (['Escape', 'Enter', ' ', 'Tab', 'ArrowDown', 'PageDown'].indexOf(e.key) > -1) terminer(); }
    function terminer() {
      if (termine) return;
      termine = true;
      if (anim) anim.annuler();
      html.classList.remove('ouverture-en-cours', 'ouverture-gl', 'ouverture-css');
      if (passer) passer.hidden = true;
      toutMontrer();
      if (moteur) { moteur.liberer(); moteur = null; }
      removeEventListener('keydown', surTouche);
      removeEventListener('wheel', terminer);
      removeEventListener('touchstart', terminer);
    }
    if (passer) passer.addEventListener('click', terminer);
    addEventListener('keydown', surTouche);
    addEventListener('wheel', terminer, { passive: true });
    addEventListener('touchstart', terminer, { passive: true });
    setTimeout(terminer, 5600);
    var vertical = window.matchMedia && matchMedia('(max-width: 900px) and (orientation: portrait)').matches;
    var srcStr = A + 'img/textures/' + (vertical ? 'strates-cire-9x16' : 'strates-cire-16x9') + '.webp';
    var jouerGL = glDispo() ? Promise.all([chargerImage(srcStr), chargerImage(A + 'img/textures/cire-relief.webp')]) : Promise.reject(new Error('sans gl'));
    Promise.race([jouerGL, attendre(1200).then(function () { throw new Error('lent'); })]).then(function (tx) {
      if (termine) return;
      moteur = moteurGL(canvas, FS_STRATES);
      if (!moteur) throw new Error('gl');
      moteur.texture(0, 'uStr', tx[0]);
      moteur.texture(1, 'uRel', tx[1]);
      var gl = moteur.gl;
      var taille = moteur.taille();
      gl.uniform1f(moteur.u('uAspect'), taille[0] / taille[1]);
      gl.uniform1f(moteur.u('uTexAspect'), tx[0].naturalWidth / tx[0].naturalHeight);
      var uT = moteur.u('uT'), uS = moteur.u('uSouris'), uC = moteur.u('uChaleur');
      var sx = 0.5, sy = 0.4, chaleur = 0;
      function bouge(e) { var r = canvas.getBoundingClientRect(); sx = (e.clientX - r.left) / r.width; sy = (e.clientY - r.top) / r.height; chaleur = 1; }
      addEventListener('pointermove', bouge, { passive: true });
      html.classList.add('ouverture-gl');
      gl.uniform2f(uS, sx, sy);
      gl.uniform1f(uC, 0);
      var figer = params.get('ouvT');
      if (figer !== null) { gl.uniform1f(uT, Number(figer)); moteur.dessiner(); termine = true; toutMontrer(); return; }
      gl.uniform1f(uT, 0); moteur.dessiner();
      anim = animer(2500, function (e, p) {
        if (!moteur || moteur.perdu()) return;
        chaleur *= 0.96;
        gl.uniform2f(uS, sx, sy);
        gl.uniform1f(uC, chaleur);
        gl.uniform1f(uT, p);
        moteur.dessiner();
      }, function (t) { return t; });
      anim.promesse.then(function (ok) { removeEventListener('pointermove', bouge); if (ok) terminer(); });
    }).catch(function () {
      if (termine) return;
      if (moteur) { try { moteur.liberer(); } catch (e) { } moteur = null; }
      html.classList.add('ouverture-css');
      setTimeout(terminer, 2300);
    });
    setTimeout(function () { if (!termine) auto.forEach(function (a) { a.classList.add('est-visible'); }); }, 900);
    apparait.forEach(function (a, i) { setTimeout(function () { if (!termine) a.classList.add('est-visible'); }, 1500 + i * 140); });
    decoder(img);
  }

  /* ------------------------------------------------------------ grattage de la cire */
  function grattages() {
    $$('[data-grattage]').forEach(function (bloc) {
      var canvas = $('.grattage__cire', bloc);
      var btn = $('[data-tout-reveler]', bloc);
      if (!canvas || ETAT.reduit) { if (canvas) canvas.classList.add('est-fini'); return; }
      var ctx = canvas.getContext('2d');
      var pret = false, fini = false, dernierTest = 0;
      var tex = new Image();
      tex.src = A + 'img/decors/cire-fondue-1x1-640.webp';
      function peindre() {
        var r = canvas.getBoundingClientRect();
        if (!r.width) return;
        var dpr = Math.min(2, window.devicePixelRatio || 1);
        canvas.width = Math.round(r.width * dpr); canvas.height = Math.round(r.height * dpr);
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.globalCompositeOperation = 'source-over';
        var g = ctx.createLinearGradient(0, 0, 0, canvas.height);
        g.addColorStop(0, '#efe2c8'); g.addColorStop(0.5, '#e3c58f'); g.addColorStop(1, '#d9b06e');
        ctx.fillStyle = g; ctx.fillRect(0, 0, canvas.width, canvas.height);
        if (tex.complete && tex.naturalWidth) {
          ctx.globalAlpha = 0.55; ctx.globalCompositeOperation = 'multiply';
          var s = Math.max(canvas.width / tex.naturalWidth, canvas.height / tex.naturalHeight);
          ctx.drawImage(tex, 0, 0, tex.naturalWidth * s, tex.naturalHeight * s);
          ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
        }
        for (var k = 1; k < 7; k++) {
          ctx.fillStyle = 'rgba(255,255,255,' + (0.05 + (k % 2) * 0.05) + ')';
          ctx.fillRect(0, canvas.height * k / 7 - 2, canvas.width, 3);
        }
        pret = true;
      }
      if (tex.complete) peindre(); else { tex.onload = peindre; tex.onerror = peindre; }
      peindre();
      surRedim(function () { if (!fini) peindre(); });
      function gratter(x, y, rayon) {
        if (!pret || fini) return;
        var r = canvas.getBoundingClientRect();
        var k = canvas.width / r.width;
        var px = (x - r.left) * k, py = (y - r.top) * k, rr = rayon * k;
        ctx.globalCompositeOperation = 'destination-out';
        var g = ctx.createRadialGradient(px, py, rr * 0.2, px, py, rr);
        g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(px, py, rr, 0, Math.PI * 2); ctx.fill();
        var now = performance.now();
        if (now - dernierTest > 350) { dernierTest = now; tester(); }
      }
      function tester() {
        try {
          var w = 40, h = Math.max(1, Math.round(40 * canvas.height / canvas.width));
          var c2 = document.createElement('canvas'); c2.width = w; c2.height = h;
          var x2 = c2.getContext('2d'); x2.drawImage(canvas, 0, 0, w, h);
          var d = x2.getImageData(0, 0, w, h).data, vide = 0;
          for (var i = 3; i < d.length; i += 4) if (d[i] < 40) vide++;
          if (vide / (w * h) > 0.5) finir();
        } catch (e) { }
      }
      function finir() { if (fini) return; fini = true; canvas.classList.add('est-fini'); if (btn) btn.closest('.grattage__aide').style.visibility = 'hidden'; }
      var appui = false;
      canvas.addEventListener('pointerdown', function (e) { appui = true; gratter(e.clientX, e.clientY, 46); });
      addEventListener('pointerup', function () { appui = false; });
      canvas.addEventListener('pointermove', function (e) {
        if (e.pointerType === 'mouse' || appui) gratter(e.clientX, e.clientY, e.pointerType === 'mouse' ? 38 : 46);
      });
      if (btn) btn.addEventListener('click', finir);
    });
  }

  /* ------------------------------------------------------------ bandeau : le portrait émerge de la glace */
  function glaces() {
    $$('[data-glace]').forEach(function (el) {
      if (ETAT.reduit) { el.classList.add('est-fondu'); return; }
      var img = $('img', el);
      decoder(img).then(function () { setTimeout(function () { el.classList.add('est-fondu'); }, 500); });
    });
  }

  /* ------------------------------------------------------------ carte du parcours des retraites */
  function Carte(sec) {
    var self = this;
    this.sec = sec;
    this.collant = $('.carte__collant', sec);
    this.etapes = $$('.etape', sec);
    this.n = this.etapes.length;
    this.route = $('[data-route]', sec);
    this.cumul = this.route.getAttribute('data-longueurs').split(',').map(Number);
    this.total = this.cumul[this.cumul.length - 1];
    this.lieux = $$('.topo__lieu', sec);
    this.barre = $('.carte__progres', sec);
    this.route.style.strokeDasharray = this.total + ' ' + this.total;
    this.actif = -1; this.p = -1;
    var vertical = window.matchMedia && matchMedia('(max-width: 900px)').matches;
    if (ETAT.reduit) {
      this.route.style.strokeDashoffset = '0';
      this.lieux.forEach(function (l) { l.classList.add('est-atteint'); });
      return;
    }
    sec.classList.add('carte--epinglee');
    this.route.style.strokeDashoffset = String(this.total);
    this.mesurer();
    surRedim(function () { self.mesurer(); });
    addEventListener('load', function () { self.mesurer(); });
    taches.push(function () { self.maj(); });
    this.activer(0);
  }
  Carte.prototype.mesurer = function () {
    var vh = innerHeight;
    this.longueur = vh * 0.7 * this.n;
    this.sec.style.height = Math.round(this.longueur + vh) + 'px';
    this.haut = this.sec.getBoundingClientRect().top + scrollY;
    this.p = -1;
  };
  Carte.prototype.activer = function (i) {
    if (i === this.actif) return;
    this.actif = i;
    this.etapes.forEach(function (et, k) { et.classList.toggle('est-active', k === i); });
    this.lieux.forEach(function (l) {
      var k = Number(l.getAttribute('data-etape'));
      l.classList.toggle('est-atteint', k <= i + 1);
      l.classList.toggle('est-actif', k === i + 1);
    });
  };
  Carte.prototype.maj = function () {
    var y = scrollY;
    if (y + innerHeight < this.haut - 200 || y > this.haut + this.longueur + innerHeight) return;
    var p = clamp((y - this.haut) / this.longueur, 0, 1);
    if (p === this.p) return;
    this.p = p;
    var f = clamp(p * this.n * 1.04, 0, this.n);
    var i = Math.min(this.n - 1, Math.floor(f));
    var frac = clamp((f - i) * 1.3, 0, 1);
    var L = this.cumul[i] + (this.cumul[i + 1] - this.cumul[i]) * EASE.io(frac);
    this.route.style.strokeDashoffset = (this.total - L).toFixed(1);
    this.activer(i);
    if (this.barre) this.barre.style.setProperty('--p', p.toFixed(4));
  };

  /* ------------------------------------------------------------ statut de l'Espace, comptes à rebours, exposition */
  function heureParis() {
    var parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Paris', weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).formatToParts(new Date());
    var get = function (t) { for (var i = 0; i < parts.length; i++) if (parts[i].type === t) return parts[i].value; return '0'; };
    return { jour: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(get('weekday')), min: Number(get('hour')) * 60 + Number(get('minute')), date: get('year') + '-' + get('month') + '-' + get('day') };
  }
  function statutEspace() {
    var els = $$('[data-statut]');
    if (!els.length || !D.espace) return;
    var H = D.espace.horaires;
    function enMin(s) { var a = s.split(':'); return Number(a[0]) * 60 + Number(a[1]); }
    var plages = H.plages.map(function (p) { return [enMin(p[0]), enMin(p[1])]; });
    function heure(min) {
      var h = Math.floor(min / 60), m = min % 60;
      if (D.langue === 'fr') return h + ' h' + (m ? ' ' + String(m).padStart(2, '0') : '');
      var h12 = ((h + 11) % 12) + 1;
      return h12 + (m ? ':' + String(m).padStart(2, '0') : '') + (h >= 12 ? ' pm' : ' am');
    }
    function calculer() {
      var n = heureParis();
      if (H.jours.indexOf(n.jour) > -1) {
        for (var i = 0; i < plages.length; i++) if (n.min >= plages[i][0] && n.min < plages[i][1]) return { ouvert: true, texte: T.statut_ouvert + ' · ' + T.statut_ferme_a.replace('{h}', heure(plages[i][1])) };
      }
      for (var k = 0; k < 8; k++) {
        var j = (n.jour + k) % 7;
        if (H.jours.indexOf(j) < 0) continue;
        for (var q = 0; q < plages.length; q++) {
          if (k === 0 && plages[q][0] <= n.min) continue;
          var h = heure(plages[q][0]);
          var quand = k === 0 ? T.statut_ouvre_auj.replace('{h}', h) : T.statut_ouvre.replace('{jour}', k === 1 ? T.demain : T.jours[j]).replace('{h}', h);
          return { ouvert: false, texte: T.statut_ferme + ' · ' + quand };
        }
      }
      return { ouvert: false, texte: T.statut_ferme };
    }
    function maj() {
      var s;
      try { s = calculer(); } catch (e) { return; }
      els.forEach(function (el) {
        el.classList.toggle('est-ouvert', s.ouvert);
        var p = el.closest('.vapeur-statut');
        if (p) p.classList.toggle('est-ouvert', s.ouvert);
        var t = $('.statut__texte', el);
        if (t) t.textContent = s.texte;
      });
    }
    maj();
    setInterval(maj, 30000);
  }
  function comptes() {
    var auj = heureParis().date;
    var j0 = Date.parse(auj + 'T00:00:00Z');
    $$('[data-compte]').forEach(function (el) {
      var n = Math.round((Date.parse(el.getAttribute('data-compte') + 'T00:00:00Z') - j0) / 86400000);
      el.textContent = n === 0 ? T.aujourdhui : (n < 0 ? T.passe : (n === 1 ? T.jour_restant : T.jours_restants.replace('{n}', n)));
    });
    $$('[data-expo]').forEach(function (sec) {
      var fin = sec.getAttribute('data-expo');
      var et = $('[data-expo-etat]', sec);
      var termine = auj > fin;
      sec.classList.toggle('est-terminee', termine);
      if (et) et.textContent = et.getAttribute(termine ? 'data-terminee' : 'data-en-cours');
    });
  }

  /* ------------------------------------------------------------ fiche d'une œuvre */
  var fiche = {
    el: null, ouverte: false, id: null, liste: [], index: 0, source: null, aPousse: false, occupe: false,
    loupeActive: false, hd: null, gl: null, glRelief: null,
    construire: function () {
      if (this.el) return;
      var f = document.createElement('div');
      f.className = 'fiche';
      f.hidden = true;
      f.setAttribute('role', 'dialog');
      f.setAttribute('aria-modal', 'true');
      f.setAttribute('aria-labelledby', 'fiche-titre');
      f.innerHTML =
        '<div class="fiche__scene">' +
        '  <p class="fiche__compteur" aria-live="polite"></p>' +
        '  <div class="fiche__cadre" data-curseur="' + (T.agrandir || '') + '"><img class="fiche__img" alt="" decoding="async"><div class="loupe" hidden></div></div>' +
        '  <canvas class="fiche__gl" aria-hidden="true"></canvas>' +
        '  <button class="fiche__nav fiche__nav--prec" type="button" aria-label="' + T.precedente + '">←</button>' +
        '  <button class="fiche__nav fiche__nav--suiv" type="button" aria-label="' + T.suivante + '">→</button>' +
        '</div>' +
        '<div class="fiche__panneau" data-defilement-natif>' +
        '  <p class="js-apparait fiche__serie"></p>' +
        '  <h2 class="fiche__titre js-apparait" id="fiche-titre"></h2>' +
        '  <dl class="fiche__faits js-apparait"></dl>' +
        '  <p class="fiche__notes js-apparait"></p>' +
        '  <p class="fiche__texte js-apparait"></p>' +
        '  <p class="fiche__prix js-apparait"></p>' +
        '  <div class="fiche__actions js-apparait">' +
        '    <button class="fiche__action" type="button" data-action="loupe" aria-pressed="false">' + T.loupe + '</button>' +
        '    <button class="fiche__action" type="button" data-action="mur">' + T.voir_au_mur + '</button>' +
        '    <a class="fiche__action fiche__action--principale" data-action="demander" href="#"></a>' +
        '  </div>' +
        '  <p class="fiche__aide js-apparait" aria-live="polite"></p>' +
        '</div>' +
        '<button class="fiche__fermer" type="button" aria-label="' + T.fermer_fiche + '">✕</button>';
      document.body.appendChild(f);
      this.el = f;
      this.scene = $('.fiche__scene', f);
      this.cadre = $('.fiche__cadre', f);
      this.img = $('.fiche__img', f);
      this.lentille = $('.loupe', f);
      this.canvas = $('.fiche__gl', f);
      this.compteur = $('.fiche__compteur', f);
      var self = this;
      $('.fiche__fermer', f).addEventListener('click', function () { self.fermer(); });
      $('.fiche__nav--prec', f).addEventListener('click', function () { self.aller(-1); });
      $('.fiche__nav--suiv', f).addEventListener('click', function () { self.aller(1); });
      $('[data-action="loupe"]', f).addEventListener('click', function () { self.basculerLoupe(); });
      $('[data-action="mur"]', f).addEventListener('click', function () { mur.ouvrir(self.id); });
      f.addEventListener('keydown', function (e) {
        if (mur.ouvert) return;
        if (e.key === 'Escape') { e.preventDefault(); self.fermer(); }
        else if (e.key === 'ArrowLeft') { e.preventDefault(); self.aller(-1); }
        else if (e.key === 'ArrowRight') { e.preventDefault(); self.aller(1); }
        else if (e.key === 'Tab') self.pieger(e);
      });
      this.cadre.addEventListener('click', function () { if (!self.loupeActive) self.basculerLoupe(); });
      this.cadre.addEventListener('pointermove', function (e) { self.bougerLoupe(e); });
      this.cadre.addEventListener('pointerdown', function (e) { if (self.loupeActive && e.pointerType !== 'mouse') { self.cadre.setPointerCapture(e.pointerId); self.bougerLoupe(e); } });
      this.cadre.addEventListener('pointerup', function (e) { if (e.pointerType !== 'mouse') self.lentille.hidden = true; });
      this.cadre.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') self.lentille.hidden = true; });
      var x0 = null, y0 = null;
      this.scene.addEventListener('touchstart', function (e) { if (self.loupeActive) return; x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
      this.scene.addEventListener('touchend', function (e) {
        if (x0 === null || self.loupeActive) return;
        var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
        x0 = null;
        if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.4) self.aller(dx < 0 ? 1 : -1);
      }, { passive: true });
      surRedim(function () { if (self.ouverte) self.cadrer(D.oeuvres[self.id]); });
    },
    pieger: function (e) {
      var foc = $$('button:not([disabled]), a[href]', this.el).filter(function (x) { return x.offsetParent !== null; });
      if (!foc.length) return;
      var premier = foc[0], dernierF = foc[foc.length - 1];
      if (e.shiftKey && document.activeElement === premier) { e.preventDefault(); dernierF.focus(); }
      else if (!e.shiftKey && document.activeElement === dernierF) { e.preventDefault(); premier.focus(); }
    },
    zone: function () {
      var cs = getComputedStyle(this.scene);
      var w = this.scene.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      var h = this.scene.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
      return { w: Math.max(80, w), h: Math.max(80, h) };
    },
    taillePour: function (o) {
      var z = this.zone(), r = o.ratio || 0.75;
      var w = z.w, h = w / r;
      if (h > z.h) { h = z.h; w = h * r; }
      return { w: Math.round(w), h: Math.round(h) };
    },
    cadrer: function (o) {
      var t = this.taillePour(o);
      this.cadre.style.width = t.w + 'px';
      this.cadre.style.height = t.h + 'px';
      return t;
    },
    remplir: function (o, id) {
      var s = D.series[this.serie] || D.series[o.series[0]];
      $('.fiche__serie', this.el).textContent = s ? s.titre : '';
      var ti = $('#fiche-titre', this.el);
      ti.textContent = o.titreAff;
      ti.classList.toggle('est-vide', !o.titre);
      var etat = o.statut === 'vendu' ? T.vendu : (o.statut === 'en-cours' ? T.en_cours : T.prix_demande);
      var faits = [[T.fiche_dims, o.dims ? o.dims + ' (' + T.dims_note + ')' : T.a_completer]];
      if (o.technique) faits.push([T.fiche_technique, o.technique]);
      if (o.edition) faits.push([T.fiche_edition, o.edition]);
      if (!o.technique && !o.edition) faits.push([T.fiche_technique, T.a_completer]);
      faits.push([T.fiche_annee, o.annee || T.a_completer]);
      faits.push([T.fiche_etat, etat]);
      $('.fiche__faits', this.el).innerHTML = faits.map(function () { return '<div><dt></dt><dd></dd></div>'; }).join('');
      $$('.fiche__faits div', this.el).forEach(function (dv, i) { dv.children[0].textContent = faits[i][0]; dv.children[1].textContent = faits[i][1]; });
      $('.fiche__notes', this.el).textContent = (o.notes || []).join(' · ');
      var tx = $('.fiche__texte', this.el);
      tx.textContent = o.texte || '';
      tx.hidden = !o.texte;
      $('.fiche__prix', this.el).textContent = etat;
      var dem = $('[data-action="demander"]', this.el);
      dem.textContent = o.statut === 'vendu' ? T.demander_vendu : T.demander;
      dem.href = RACINE + D.pageContact + '?oeuvre=' + encodeURIComponent(id);
      $('[data-action="loupe"]', this.el).disabled = !o.loupe;
      $('[data-action="mur"]', this.el).disabled = !(o.h && o.l);
      this.compteur.textContent = (this.index + 1) + ' ' + T.sur + ' ' + this.liste.length;
      this.el.style.setProperty('--fond-fiche', o.fond);
      this.aide(!o.loupe ? T.loupe_indispo : '');
      var nav = this.liste.length > 1;
      $$('.fiche__nav', this.el).forEach(function (b) { b.hidden = !nav; });
    },
    poserImage: function (o, id) {
      this.img.srcset = urlOeuvre(id, '640') + ' ' + o.t['640'][0] + 'w, ' + urlOeuvre(id, '1600') + ' ' + o.t['1600'][0] + 'w';
      this.img.sizes = Math.round(parseFloat(this.cadre.style.width) || 800) + 'px';
      this.img.src = urlOeuvre(id, '1600');
      this.img.alt = o.alt;
    },
    aide: function (t) { var a = $('.fiche__aide', this.el); if (a) a.textContent = t || ''; },
    ouvrir: function (id, opts) {
      opts = opts || {};
      var o = D.oeuvres[id];
      if (!o || this.occupe) return;
      this.construire();
      var self = this;
      this.occupe = true;
      this.serie = opts.liste && D.series[opts.liste] ? opts.liste : o.series[0];
      this.liste = (D.series[this.serie] && D.series[this.serie].oeuvres) || [id];
      if (this.liste.indexOf(id) < 0) this.liste = [id];
      this.index = Math.max(0, this.liste.indexOf(id));
      this.id = id;
      this.source = opts.source || null;
      this.ouverte = true;
      this.el.hidden = false;
      this.el.classList.remove('est-prete');
      html.classList.add('fiche-ouverte');
      lissage.verrou++;
      document.body.style.overflow = 'hidden';
      $$('body > header, body > main, body > footer, body > .menu, body > .altimetre').forEach(function (x) { x.setAttribute('inert', ''); x.setAttribute('aria-hidden', 'true'); });
      this.remplir(o, id);
      this.cadrer(o);
      this.poserImage(o, id);
      var imgSource = this.source ? this.source.querySelector('img') : null;
      var fin = function () {
        self.el.classList.add('est-prete');
        self.occupe = false;
        var ferme = $('.fiche__fermer', self.el);
        if (ferme) ferme.focus({ preventScroll: true });
      };
      if (!opts.sansHistorique) { history.pushState({ oeuvre: id }, '', this.url(id)); this.aPousse = true; }
      if (imgSource && !ETAT.reduit && imgSource.getBoundingClientRect().width > 0) {
        var rs = imgSource.getBoundingClientRect();
        var rc = this.cadre.getBoundingClientRect();
        var clone = new Image();
        clone.src = imgSource.currentSrc || imgSource.src;
        clone.className = 'fiche__clone';
        clone.alt = '';
        clone.style.width = rc.width + 'px';
        clone.style.height = rc.height + 'px';
        document.body.appendChild(clone);
        imgSource.style.visibility = 'hidden';
        this.imgCachee = imgSource;
        this.img.style.opacity = '0';
        this.el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 420, easing: 'ease-out' });
        var de = 'translate(' + rs.left + 'px,' + rs.top + 'px) scale(' + (rs.width / rc.width) + ',' + (rs.height / rc.height) + ')';
        var a = 'translate(' + rc.left + 'px,' + rc.top + 'px) scale(1,1)';
        var anim = clone.animate([{ transform: de }, { transform: a }], { duration: 860, easing: 'cubic-bezier(.22,1,.36,1)', fill: 'forwards' });
        anim.finished.then(function () { return decoder(self.img); }).then(function () {
          self.img.style.opacity = '';
          clone.remove();
          if (self.imgCachee) self.imgCachee.style.visibility = '';
          fin();
        });
      } else {
        this.el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: ETAT.reduit ? 1 : 380, easing: 'ease-out' }).finished.then(fin);
      }
    },
    url: function (id) {
      var u = new URL(location.href);
      if (id) u.searchParams.set('oeuvre', id); else u.searchParams.delete('oeuvre');
      return u.pathname + u.search + u.hash;
    },
    vignette: function (id) {
      var b = $('[data-ouvrir="' + id + '"] img');
      if (!b) return null;
      var r = b.getBoundingClientRect();
      if (r.width < 4 || r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) return null;
      return b;
    },
    fermer: function (opts) {
      opts = opts || {};
      if (!this.ouverte || this.occupe) return;
      var self = this;
      this.occupe = true;
      if (this.loupeActive) this.basculerLoupe();
      if (mur.ouvert) mur.fermer();
      var id = this.id;
      var restaurer = function () {
        self.el.hidden = true;
        self.ouverte = false;
        self.occupe = false;
        html.classList.remove('fiche-ouverte');
        lissage.verrou = Math.max(0, lissage.verrou - 1);
        document.body.style.overflow = '';
        $$('[inert]').forEach(function (x) { x.removeAttribute('inert'); x.removeAttribute('aria-hidden'); });
        var b = $('[data-ouvrir="' + id + '"]') || self.source;
        if (b) b.focus({ preventScroll: true });
      };
      if (!opts.historique) {
        if (this.aPousse) { this.aPousse = false; this.ignorerPop = true; history.back(); }
        else history.replaceState(null, '', this.url(null));
      }
      var cible = ETAT.reduit ? null : this.vignette(id);
      if (cible) {
        var rc = this.cadre.getBoundingClientRect();
        var rs = cible.getBoundingClientRect();
        var clone = new Image();
        clone.src = this.img.currentSrc || this.img.src;
        clone.className = 'fiche__clone';
        clone.alt = '';
        clone.style.width = rc.width + 'px';
        clone.style.height = rc.height + 'px';
        document.body.appendChild(clone);
        cible.style.visibility = 'hidden';
        this.img.style.opacity = '0';
        this.el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 520, easing: 'ease-in', fill: 'forwards' });
        var anim = clone.animate([
          { transform: 'translate(' + rc.left + 'px,' + rc.top + 'px) scale(1,1)' },
          { transform: 'translate(' + rs.left + 'px,' + rs.top + 'px) scale(' + (rs.width / rc.width) + ',' + (rs.height / rc.height) + ')' }
        ], { duration: 720, easing: 'cubic-bezier(.65,0,.35,1)', fill: 'forwards' });
        anim.finished.then(function () {
          cible.style.visibility = '';
          clone.remove();
          self.img.style.opacity = '';
          self.el.getAnimations().forEach(function (a) { a.cancel(); });
          restaurer();
        });
      } else {
        this.el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: ETAT.reduit ? 1 : 300, easing: 'ease-in', fill: 'forwards' }).finished.then(function () {
          self.el.getAnimations().forEach(function (a) { a.cancel(); });
          restaurer();
        });
      }
    },
    aller: function (delta) {
      if (this.occupe || !this.ouverte || this.liste.length < 2) return;
      var self = this;
      this.occupe = true;
      if (this.loupeActive) this.basculerLoupe();
      this.index = (this.index + delta + this.liste.length) % this.liste.length;
      var id = this.liste[this.index], o = D.oeuvres[id];
      this.id = id;
      history.replaceState({ oeuvre: id }, '', this.url(id));
      var scene = this.scene.getBoundingClientRect();
      var rA = this.cadre.getBoundingClientRect();
      var tB = this.taillePour(o);
      var cs = getComputedStyle(this.scene);
      var pt = parseFloat(cs.paddingTop), pb = parseFloat(cs.paddingBottom), pl = parseFloat(cs.paddingLeft), pr = parseFloat(cs.paddingRight);
      var rB = { left: scene.left + pl + (scene.width - pl - pr - tB.w) / 2, top: scene.top + pt + (scene.height - pt - pb - tB.h) / 2, width: tB.w, height: tB.h };
      var panneau = $$('.js-apparait', this.el);
      panneau.forEach(function (x) { x.style.transition = 'opacity .25s'; x.style.opacity = '0'; });
      var majTexte = function () {
        self.remplir(o, id);
        panneau.forEach(function (x) { x.style.opacity = ''; setTimeout(function () { x.style.transition = ''; }, 400); });
      };
      var terminer = function () { self.occupe = false; };
      chargerImage(urlOeuvre(id, '1600')).then(function (imgB) {
        var glOk = !ETAT.reduit && glDispo() && self.preparerGL();
        if (glOk) {
          try {
            var m = self.gl, gl = m.gl;
            self.canvas.style.width = scene.width + 'px';
            self.canvas.style.height = scene.height + 'px';
            self.canvas.classList.add('est-active');
            m.taille();
            m.texture(0, 'uA', self.img);
            m.texture(1, 'uB', imgB);
            var rel = function (r) { return [(r.left - scene.left) / scene.width, (r.top - scene.top) / scene.height, r.width / scene.width, r.height / scene.height]; };
            var a = rel(rA), b = rel(rB);
            gl.uniform4f(m.u('uRA'), a[0], a[1], a[2], a[3]);
            gl.uniform4f(m.u('uRB'), b[0], b[1], b[2], b[3]);
            gl.uniform1f(m.u('uDir'), delta);
            var uP = m.u('uP');
            gl.uniform1f(uP, 0); m.dessiner();
            self.cadre.style.visibility = 'hidden';
            self.cadrer(o);
            majTexte();
            animer(1000, function (e) { gl.uniform1f(uP, e); m.dessiner(); }, EASE.io).promesse.then(function () {
              self.poserImage(o, id);
              return decoder(self.img);
            }).then(function () {
              self.cadre.style.visibility = '';
              self.canvas.classList.remove('est-active');
              terminer();
            });
            return;
          } catch (err) { self.canvas.classList.remove('est-active'); self.cadre.style.visibility = ''; }
        }
        self.img.style.transition = 'opacity .22s';
        self.img.style.opacity = '0';
        setTimeout(function () {
          self.cadrer(o); majTexte(); self.poserImage(o, id);
          self.img.style.transition = 'none'; self.img.style.opacity = '1';
          if (!ETAT.reduit) {
            self.cadre.classList.add('fiche__balayage');
            void self.cadre.offsetWidth;
            decoder(self.img).then(function () {
              self.cadre.classList.add('est-visible');
              setTimeout(function () { self.cadre.classList.remove('fiche__balayage', 'est-visible'); self.img.style.transition = ''; terminer(); }, 1000);
            });
          } else { self.img.style.transition = ''; terminer(); }
        }, ETAT.reduit ? 0 : 230);
      }).catch(function () { self.cadrer(o); majTexte(); self.poserImage(o, id); terminer(); });
    },
    preparerGL: function () {
      if (this.gl && !this.gl.perdu()) return true;
      if (this.glEchec || !this.glRelief) return false;
      this.gl = moteurGL(this.canvas, FS_TRANSITION);
      if (!this.gl) { this.glEchec = true; return false; }
      this.gl.texture(2, 'uRelief', this.glRelief);
      return true;
    },
    basculerLoupe: function () {
      var o = D.oeuvres[this.id];
      var btn = $('[data-action="loupe"]', this.el);
      if (!o.loupe) { this.aide(T.loupe_indispo); return; }
      this.loupeActive = !this.loupeActive;
      btn.setAttribute('aria-pressed', String(this.loupeActive));
      this.cadre.classList.toggle('loupe-active', this.loupeActive);
      html.classList.toggle('loupe-en-cours', this.loupeActive);
      this.cadre.setAttribute('data-curseur', this.loupeActive ? '' : (T.agrandir || ''));
      var self = this;
      if (this.loupeActive) {
        this.aide(T.loupe_chargement);
        var id = this.id;
        this.hd = null;
        chargerImage(urlOeuvre(id, 'hd')).then(function (im) {
          if (!self.loupeActive || self.id !== id) return;
          self.hd = { w: im.naturalWidth, h: im.naturalHeight };
          self.lentille.style.backgroundImage = 'url("' + im.src + '")';
          self.aide(ETAT.fin ? T.loupe_aide : T.loupe_aide_tactile);
        }).catch(function () { self.aide(T.loupe_indispo); });
      } else { this.lentille.hidden = true; this.aide(''); }
    },
    bougerLoupe: function (e) {
      if (!this.loupeActive || !this.hd) return;
      var r = this.cadre.getBoundingClientRect();
      var x = e.clientX - r.left, y = e.clientY - r.top;
      if (x < 0 || y < 0 || x > r.width || y > r.height) { this.lentille.hidden = true; return; }
      var L = this.lentille;
      L.hidden = false;
      var R = L.offsetWidth / 2;
      var z = clamp(this.hd.w / r.width, 1.8, 4.5);
      L.style.left = x + 'px';
      L.style.top = y + 'px';
      L.style.backgroundSize = (r.width * z) + 'px ' + (r.height * z) + 'px';
      L.style.backgroundPosition = (R - x * z) + 'px ' + (R - y * z) + 'px';
    }
  };
  addEventListener('popstate', function () {
    if (fiche.ignorerPop) { fiche.ignorerPop = false; return; }
    var id = new URLSearchParams(location.search).get('oeuvre');
    if (fiche.ouverte && !id) fiche.fermer({ historique: true });
    else if (!fiche.ouverte && id && D.oeuvres[id] && !$('[data-formulaire]')) fiche.ouvrir(id, { liste: P.salle, sansHistorique: true });
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-ouvrir]') : null;
    if (!b) return;
    e.preventDefault();
    if (html.classList.contains('ouverture-en-cours')) return;
    fiche.ouvrir(b.getAttribute('data-ouvrir'), { source: b, liste: b.getAttribute('data-liste') });
  });

  /* ------------------------------------------------------------ Voir au mur */
  var SILHOUETTE = 'M30 1a10 10 0 1 1 0 20a10 10 0 1 1 0-20zM19 24q11-3 22 0l6 5q3 2 3 7l2 52q0 4-4 4h-2l-1-40h-2l1 46-2 68q0 4-4 4h-4l-2-64h-4l-2 64h-4q-4 0-4-4l-2-68 1-46h-2l-1 40h-2q-4 0-4-4l2-52q0-5 3-7z';
  var mur = {
    el: null, ouvert: false, decor: 'chalet', silhouette: false, id: null,
    construire: function () {
      if (this.el) return;
      var m = document.createElement('div');
      m.className = 'mur';
      m.hidden = true;
      m.setAttribute('role', 'dialog');
      m.setAttribute('aria-modal', 'true');
      m.setAttribute('aria-label', T.mur_titre);
      m.innerHTML =
        '<div class="mur__scene"><img class="mur__decor" alt="" decoding="async"><div class="mur__toile"><img alt="" decoding="async"></div>' +
        '<svg class="mur__silhouette" viewBox="0 0 60 170" aria-hidden="true" preserveAspectRatio="none"><path d="' + SILHOUETTE + '"/></svg>' +
        '<div class="mur__regle" aria-hidden="true">' + T.mur_un_metre + '</div></div>' +
        '<div class="mur__barre"><p class="mur__legende"></p>' +
        '<div class="mur__choix" role="group"><button type="button" data-decor="chalet" aria-pressed="true">' + T.mur_chalet + '</button>' +
        '<button type="button" data-decor="galerie" aria-pressed="false">' + T.mur_galerie + '</button>' +
        '<button type="button" data-silhouette aria-pressed="false">' + T.mur_silhouette + '</button></div>' +
        '<button class="mur__fermer" type="button">' + T.mur_fermer + '</button></div>';
      document.body.appendChild(m);
      this.el = m;
      this.scene = $('.mur__scene', m);
      this.imgDecor = $('.mur__decor', m);
      this.toile = $('.mur__toile', m);
      this.imgToile = $('.mur__toile img', m);
      this.sil = $('.mur__silhouette', m);
      this.regle = $('.mur__regle', m);
      var self = this;
      $$('[data-decor]', m).forEach(function (b) { b.addEventListener('click', function () { self.decor = b.getAttribute('data-decor'); self.majBoutons(); self.placer(); }); });
      $('[data-silhouette]', m).addEventListener('click', function () { self.silhouette = !self.silhouette; self.majBoutons(); self.placer(); });
      $('.mur__fermer', m).addEventListener('click', function () { self.fermer(); });
      m.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { e.preventDefault(); self.fermer(); }
        if (e.key === 'Tab') {
          var foc = $$('button', m);
          if (e.shiftKey && document.activeElement === foc[0]) { e.preventDefault(); foc[foc.length - 1].focus(); }
          else if (!e.shiftKey && document.activeElement === foc[foc.length - 1]) { e.preventDefault(); foc[0].focus(); }
        }
      });
      surRedim(function () { if (self.ouvert) self.placer(); });
      addEventListener('resize', function () { if (self.ouvert) self.placer(); });
    },
    majBoutons: function () {
      var self = this;
      $$('[data-decor]', this.el).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-decor') === self.decor)); });
      $('[data-silhouette]', this.el).setAttribute('aria-pressed', String(this.silhouette));
    },
    ouvrir: function (id) {
      var o = D.oeuvres[id];
      if (!o || !o.h || !o.l) return;
      this.construire();
      this.id = id;
      this.ouvert = true;
      this.el.hidden = false;
      this.imgToile.src = urlOeuvre(id, '1600');
      var leg = $('.mur__legende', this.el);
      leg.innerHTML = '<strong></strong> · <span class="d"></span><br><small></small>';
      $('strong', leg).textContent = o.titreAff;
      $('.d', leg).textContent = o.dims || '';
      $('small', leg).textContent = T.mur_echelle;
      this.majBoutons();
      this.placer();
      $('.mur__fermer', this.el).focus();
    },
    fermer: function () {
      if (!this.ouvert) return;
      this.ouvert = false;
      this.el.hidden = true;
      var b = fiche.el && $('[data-action="mur"]', fiche.el);
      if (b) b.focus();
    },
    placer: function () {
      var o = D.oeuvres[this.id];
      var W = this.scene.clientWidth, H = this.scene.clientHeight;
      var cle = this.decor === 'chalet' && W / H < 0.95 ? 'chaletV' : this.decor;
      var d = D.decors[cle];
      var src = A + d.src;
      if (this.imgDecor.getAttribute('src') !== src) this.imgDecor.src = src;
      var s = Math.max(W / d.w, H / d.h);
      var ox = clamp(W / 2 - d.cx * s, W - d.w * s, 0);
      var oy = (H - d.h * s) / 2;
      this.imgDecor.style.width = d.w + 'px';
      this.imgDecor.style.height = d.h + 'px';
      this.imgDecor.style.transform = 'translate(' + ox.toFixed(1) + 'px,' + oy.toFixed(1) + 'px) scale(' + s.toFixed(4) + ')';
      var k = d.pxcm * s;
      var r = o.ratio;
      var pw = o.l * k, ph = pw / r;
      if (ph > o.h * k * 1.001) { ph = o.h * k; pw = ph * r; }
      var centreCm = Math.max(150, d.basMin + (ph / k) / 2);
      var cx = ox + d.cx * s;
      var cy = oy + (d.sol - centreCm * d.pxcm) * s;
      // toile, règle (à gauche) et silhouette (à droite) forment un groupe qui doit tenir dans l'écran, à l'échelle réelle
      var m = 12, ecart = 40 * k, R = 100 * k;
      var sh = 170 * k, sw = 60 * k;
      var droite = this.silhouette ? ecart + sw : 0;
      var regleCote = true;
      var minX = m + R + ecart + pw / 2, maxX = W - m - droite - pw / 2;
      if (minX > maxX) { regleCote = false; minX = m + pw / 2; }
      var tx = minX <= maxX ? clamp(cx, minX, maxX) : (minX + maxX) / 2;
      this.toile.style.width = pw.toFixed(1) + 'px';
      this.toile.style.height = ph.toFixed(1) + 'px';
      this.toile.style.left = (tx - pw / 2).toFixed(1) + 'px';
      this.toile.style.top = (cy - ph / 2).toFixed(1) + 'px';
      this.sil.style.width = sw.toFixed(1) + 'px';
      this.sil.style.height = sh.toFixed(1) + 'px';
      this.sil.style.left = (tx + pw / 2 + ecart).toFixed(1) + 'px';
      this.sil.style.top = (oy + d.sol * s - sh).toFixed(1) + 'px';
      this.sil.style.opacity = this.silhouette ? '1' : '0';
      this.regle.style.width = R.toFixed(1) + 'px';
      if (regleCote) {
        this.regle.style.left = (tx - pw / 2 - ecart - R).toFixed(1) + 'px';
        this.regle.style.top = (cy - ph / 2).toFixed(1) + 'px';
      } else {
        this.regle.style.left = (tx - pw / 2).toFixed(1) + 'px';
        this.regle.style.top = Math.max(8, cy - ph / 2 - 36).toFixed(1) + 'px';
      }
    }
  };

  /* ------------------------------------------------------------ formulaires (simulés) */
  function formulaire() {
    var f = $('[data-formulaire]');
    if (!f) return;
    var merci = $('.formulaire__merci');
    var blocs = $$('[data-pour]', f);
    var resume = $('.formulaire__erreurs', f);
    function objet() { var r = $('input[name="objet"]:checked', f); return r ? r.value : 'oeuvre'; }
    function majObjet() { var v = objet(); blocs.forEach(function (b) { b.hidden = b.getAttribute('data-pour') !== v; }); }
    var o = params.get('oeuvre'), ob = params.get('objet'), re = params.get('retraite');
    if (o && f.elements.oeuvre) { f.elements.oeuvre.value = o; }
    if (ob) { var r = $('input[name="objet"][value="' + ob + '"]', f); if (r) r.checked = true; }
    if (re && f.elements.retraite) f.elements.retraite.value = re;
    majObjet();
    $$('input[name="objet"]', f).forEach(function (x) { x.addEventListener('change', majObjet); });
    function erreur(champ, msg) {
      var wrap = champ.closest('.champ');
      var p = wrap && $('.champ__erreur', wrap);
      if (wrap) wrap.classList.toggle('a-erreur', !!msg);
      if (p) p.textContent = msg || '';
      if (msg) champ.setAttribute('aria-invalid', 'true'); else champ.removeAttribute('aria-invalid');
    }
    $$('input, textarea', f).forEach(function (c) { c.addEventListener('input', function () { erreur(c, ''); }); c.addEventListener('change', function () { erreur(c, ''); }); });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var premier = null;
      ['prenom', 'nom', 'email', 'message'].forEach(function (n) {
        var c = f.elements[n];
        var v = (c.value || '').trim();
        var msg = '';
        if (!v) msg = T.form_obligatoire;
        else if (n === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) msg = T.form_email_invalide;
        erreur(c, msg);
        if (msg && !premier) premier = c;
      });
      var acc = f.elements.accord;
      erreur(acc, acc.checked ? '' : T.form_obligatoire);
      if (!acc.checked && !premier) premier = acc;
      if (premier) { resume.hidden = false; premier.focus(); return; }
      resume.hidden = true;
      var lab = $('input[name="objet"]:checked + span', f);
      var sujet = lab ? lab.textContent : '';
      if (objet() === 'oeuvre' && f.elements.oeuvre.value && D.oeuvres[f.elements.oeuvre.value]) sujet += ' – ' + D.oeuvres[f.elements.oeuvre.value].titreAff;
      if (objet() === 'retraite' && f.elements.retraite) sujet += ' – ' + f.elements.retraite.options[f.elements.retraite.selectedIndex].text;
      var corps = [f.elements.message.value.trim(), '', f.elements.prenom.value + ' ' + f.elements.nom.value, f.elements.email.value, f.elements.tel.value].filter(function (x, i) { return i < 2 || x.trim(); });
      var a = $('[data-mailto]', merci);
      if (a) a.href = 'mailto:' + D.espace.courriel + '?subject=' + encodeURIComponent(sujet) + '&body=' + encodeURIComponent(corps.join('\n'));
      f.hidden = true;
      merci.hidden = false;
      merci.focus();
      lissage.aller(merci.getBoundingClientRect().top + scrollY - 120, true);
    });
  }
  function lettres() {
    $$('[data-lettre]').forEach(function (f) {
      f.addEventListener('submit', function (e) {
        e.preventDefault();
        var i = f.elements.email;
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test((i.value || '').trim())) { i.setAttribute('aria-invalid', 'true'); i.focus(); return; }
        i.removeAttribute('aria-invalid');
        var m = $('.lettre__merci', f);
        m.hidden = false; m.focus();
      });
    });
  }

  /* ------------------------------------------------------------ liens d'ancre */
  function ancres() {
    document.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
      if (!a) return;
      var id = a.getAttribute('href').slice(1);
      var cible = id && document.getElementById(id);
      if (!cible) return;
      e.preventDefault();
      lissage.aller(cible.getBoundingClientRect().top + scrollY - 80);
      cible.focus({ preventScroll: true });
    });
    if (location.hash) {
      var c = document.getElementById(location.hash.slice(1));
      if (c) setTimeout(function () { window.scrollTo(0, c.getBoundingClientRect().top + scrollY - 80); }, 120);
    }
  }

  /* ------------------------------------------------------------ démarrage */
  function demarrer() {
    lissage.init();
    jauges();
    revelations();
    mots();
    parallaxes();
    panoramas();
    entete();
    menu();
    altimetre();
    initCurseur();
    aimants();
    inclinaisons();
    ancres();
    statutEspace();
    comptes();
    formulaire();
    lettres();
    glaces();
    grattages();
    carottage();
    if (!ETAT.reduit) $$('[data-piste]').forEach(function (s) { new Piste(s); $$('.cire-fond', s).forEach(observerSalle); });
    $$('[data-carte]').forEach(function (s) { new Carte(s); });
    ouverture();
    if (glDispo()) chargerImage(A + 'img/textures/cire-relief.webp').then(function (i) { fiche.glRelief = i; }).catch(function () {});
    var id = params.get('oeuvre');
    if (id && D.oeuvres[id] && !$('[data-formulaire]')) setTimeout(function () { fiche.ouvrir(id, { liste: P.salle, sansHistorique: true }); }, 80);
    addEventListener('load', toutRemesurer);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(toutRemesurer);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', demarrer);
  else demarrer();
})();
