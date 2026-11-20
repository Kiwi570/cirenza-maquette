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
  /* Copie hébergée chez Wix : les images des œuvres et les photos sont dans la médiathèque Wix (assets/js/medias.js). */
  function M(p) { var m = window.LC_MEDIAS; return (m && m[p]) || A + p; }
  function urlOeuvre(id, taille) { return M('img/oeuvres/' + id + '-' + taille + '.webp'); }

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
    return; // v4 : pas de parallaxe (brief de Lisa : « no parallax gimmicks »)
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
    return; // v4 : bandes et panoramas défilent au doigt ou à la molette, sans effet lié au défilement de la page
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
  /* Horaires : une seule source (assets/data/horaires.json ; sur le site final, les collections Wix
     « Horaires » et « Exceptions »). L'éditeur de la maquette peut en proposer un aperçu, gardé dans ce navigateur. */
  var HOR = {
    cleApercu: 'lc-horaires-apercu',
    donnees: null,
    lire: function () {
      try {
        var a = localStorage.getItem(this.cleApercu);
        if (a) { var x = JSON.parse(a); if (x && x.horaires) { x._apercu = true; return x; } }
      } catch (e) { /* stockage indisponible */ }
      return this.donnees || (D.espace && D.espace.horaires) || null;
    },
    enMin: function (s) { var a = String(s).split(':'); return Number(a[0]) * 60 + Number(a[1]); },
    plus: function (iso, n) { return new Date(Date.parse(iso + 'T12:00:00Z') + n * 86400000).toISOString().slice(0, 10); },
    jourDe: function (iso) { return new Date(Date.parse(iso + 'T12:00:00Z')).getUTCDay(); },
    exception: function (H, iso) {
      var ex = H.exceptions || [];
      for (var i = 0; i < ex.length; i++) if (ex[i].du && ex[i].au && iso >= ex[i].du && iso <= ex[i].au) return ex[i];
      return null;
    },
    plagesDe: function (l) {
      var p = [];
      if (l && l.debut && l.fin) { p.push([l.debut, l.fin]); if (l.debut2 && l.fin2) p.push([l.debut2, l.fin2]); }
      return p;
    },
    ligneDuJour: function (H, j) {
      var L = H.horaires || [];
      for (var i = 0; i < L.length; i++) if (L[i].jour === j) return L[i];
      return { jour: j, ouvert: false };
    },
    plages: function (H, iso) {
      var x = this.exception(H, iso);
      if (x) return x.ferme ? [] : this.plagesDe(x);
      var l = this.ligneDuJour(H, this.jourDe(iso));
      return l.ouvert ? this.plagesDe(l) : [];
    },
    heure: function (hm) {
      var a = String(hm).split(':'), h = Number(a[0]), m = Number(a[1]);
      if (D.langue === 'fr') return h + ' h' + (m ? ' ' + String(m).padStart(2, '0') : '');
      var h12 = ((h + 11) % 12) + 1;
      return h12 + (m ? ':' + String(m).padStart(2, '0') : '') + (h >= 12 ? ' pm' : ' am');
    },
    textePlages: function (p) {
      var self = this;
      return p.map(function (x) { return self.heure(x[0]) + ' – ' + self.heure(x[1]); }).join(', ');
    },
    lignes: function (H) {
      var ordre = [1, 2, 3, 4, 5, 6, 0], groupes = [], self = this;
      ordre.forEach(function (j, k) {
        var l = self.ligneDuJour(H, j), p = l.ouvert ? self.plagesDe(l) : [];
        var cle = p.length ? 'o' + JSON.stringify(p) : (l.surRendezVous ? 'rdv' : 'f');
        var g = groupes[groupes.length - 1];
        if (g && g.cle === cle && g.k === k - 1) { g.jours.push(j); g.k = k; } else groupes.push({ cle: cle, jours: [j], k: k, p: p });
      });
      var noms = T.jours || [];
      var cap = function (x) { return x ? x.charAt(0).toUpperCase() + x.slice(1) : x; };
      return groupes.filter(function (g) { return g.cle !== 'f'; }).map(function (g) {
        var a = cap(noms[g.jours[0]]), b = noms[g.jours[g.jours.length - 1]];
        return [g.jours.length > 1 ? a + ' – ' + b : a, g.cle === 'rdv' ? (D.langue === 'fr' ? 'sur rendez-vous' : 'by appointment') : self.textePlages(g.p)];
      });
    },
    annonce: function (H, iso) {
      var ex = H.exceptions || [];
      for (var i = 0; i < ex.length; i++) {
        var x = ex[i], des = x.afficherDes || (x.du ? this.plus(x.du, -10) : '');
        var msg = D.langue === 'fr' ? x.messageFr : x.messageEn;
        if (msg && des && x.au && iso >= des && iso <= x.au) return msg;
      }
      return '';
    },
    statut: function (H) {
      var n = heureParis(), self = this;
      var auj = this.plages(H, n.date).map(function (p) { return [self.enMin(p[0]), self.enMin(p[1]), p]; });
      for (var i = 0; i < auj.length; i++) {
        if (n.min >= auj[i][0] && n.min < auj[i][1]) return { ouvert: true, texte: T.statut_ouvert + ' · ' + T.statut_ferme_a.replace('{h}', this.heure(auj[i][2][1])) };
      }
      for (var k = 0; k < 15; k++) {
        var iso = this.plus(n.date, k), pl = this.plages(H, iso);
        for (var q = 0; q < pl.length; q++) {
          if (k === 0 && this.enMin(pl[q][0]) <= n.min) continue;
          var h = this.heure(pl[q][0]);
          var jourTxt = k === 1 ? T.demain : T.jours[this.jourDe(iso)];
          if (k > 6) {
            var dt = new Date(Date.parse(iso + 'T12:00:00Z'));
            jourTxt = (D.langue === 'fr' ? 'le ' : 'on ') + dt.toLocaleDateString(D.langue === 'fr' ? 'fr-FR' : 'en-GB', { day: 'numeric', month: 'long', timeZone: 'UTC' });
          }
          var quand = k === 0 ? T.statut_ouvre_auj.replace('{h}', h) : T.statut_ouvre.replace('{jour}', jourTxt).replace('{h}', h);
          return { ouvert: false, texte: T.statut_ferme + ' · ' + quand };
        }
      }
      return { ouvert: false, texte: T.statut_ferme };
    }
  };

  function rafraichirHoraires() {
    var H = HOR.lire();
    if (!H) return;
    var n = heureParis();
    var s = null;
    try { s = HOR.statut(H); } catch (e) { s = null; }
    if (s) {
      $$('[data-statut]').forEach(function (el) {
        el.classList.toggle('est-ouvert', s.ouvert);
        var p = el.closest('.vapeur-statut');
        if (p) p.classList.toggle('est-ouvert', s.ouvert);
        var t = $('.statut__texte', el);
        if (t) t.textContent = s.texte;
      });
    }
    var msg = HOR.annonce(H, n.date);
    $$('[data-annonce]').forEach(function (a) { a.textContent = msg; a.hidden = !msg; });
    html.classList.toggle('a-annonce', !!msg);
    if (H._apercu || HOR.donnees) {
      var lignes = HOR.lignes(H);
      $$('[data-horaires-liste]').forEach(function (dl) {
        dl.textContent = '';
        lignes.forEach(function (l) {
          var div = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
          dt.textContent = l[0];
          dd.textContent = l[1];
          div.appendChild(dt);
          div.appendChild(dd);
          dl.appendChild(div);
        });
      });
    }
    if (H._apercu && !$('.apercu-horaires') && !$('[data-editeur-horaires]')) {
      var P = D.langue === 'fr' ? ['Aperçu des horaires modifiés', 'arrêter'] : ['Preview of the edited hours', 'stop'];
      var pastille = document.createElement('p');
      var lib = document.createElement('span');
      var arreter = document.createElement('button');
      pastille.className = 'apercu-horaires';
      lib.textContent = P[0];
      arreter.type = 'button';
      arreter.textContent = P[1];
      arreter.addEventListener('click', function () {
        try { localStorage.removeItem(HOR.cleApercu); } catch (e) { /* rien */ }
        location.reload();
      });
      pastille.appendChild(lib);
      pastille.appendChild(arreter);
      document.body.appendChild(pastille);
    }
  }
  function statutEspace() {
    rafraichirHoraires();
    setInterval(rafraichirHoraires, 30000);
    // les horaires publiés sont relus à chaque visite : modifier le fichier (sur le site final, la collection Wix) suffit
    if (window.fetch) {
      fetch((html.getAttribute('data-racine') || '/') + 'assets/data/horaires.json?t=' + Date.now(), { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          if (j && j.horaires) {
            HOR.donnees = j;
            rafraichirHoraires();
            document.dispatchEvent(new CustomEvent('lc:horaires'));
          }
        })
        .catch(function () { /* on garde les horaires de la page */ });
    }
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
      $('.fiche__faits', this.el).innerHTML = faits.map(function () { return '<div><dt></dt><dd></dd></div>'; }).join('');
      $$('.fiche__faits div', this.el).forEach(function (dv, i) { dv.children[0].textContent = faits[i][0]; dv.children[1].textContent = faits[i][1]; });
      $('.fiche__notes', this.el).textContent = (o.notes || []).join(' · ');
      var tx = $('.fiche__texte', this.el);
      tx.textContent = o.texte || '';
      tx.hidden = !o.texte;
      $('.fiche__prix', this.el).textContent = '';
      var dem = $('[data-action="demander"]', this.el);
      dem.textContent = T.demander;
      dem.href = 'mailto:' + D.espace.courriel + '?subject=' + encodeURIComponent((D.langue === 'fr' ? 'Demande : ' : 'Enquiry: ') + o.titreAff);
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
      var src = M(d.src);
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
    var se = params.get('seance');
    if (se && f.elements.seance) f.elements.seance.value = se;
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
      // v5 : les champs de l'objet choisi (retraite, cours privé, événement) partent en lignes « Libellé : valeur »,
      // faciles à lire pour Lisa comme pour un agent qui préparerait la réponse
      var details = [];
      blocs.forEach(function (b) {
        if (b.hidden) return;
        $$('select, input', b).forEach(function (c) {
          if (c.name === 'oeuvre' || c.name === 'retraite') return;
          var v = c.tagName === 'SELECT' ? (c.value ? c.options[c.selectedIndex].text : '') : (c.value || '').trim();
          if (!v) return;
          var l = c.id ? $('label[for="' + c.id + '"]', f) : null;
          details.push((l && l.firstChild ? l.firstChild.textContent.trim() : c.name) + (D.langue === 'fr' ? ' : ' : ': ') + v);
        });
      });
      var coord = [f.elements.prenom.value + ' ' + f.elements.nom.value, f.elements.email.value, f.elements.tel.value].filter(function (x) { return x.trim(); });
      var corps = [f.elements.message.value.trim(), ''].concat(details.length ? details.concat(['']) : []).concat(coord);
      var radio = $('input[name="objet"]:checked', f);
      var dest = (radio && radio.getAttribute('data-courriel')) || D.espace.courriel;
      var a = $('[data-mailto]', merci);
      if (a) a.href = 'mailto:' + dest + '?subject=' + encodeURIComponent(sujet) + '&body=' + encodeURIComponent(corps.join('\n'));
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

  /* ------------------------------------------------------------ v3 · paniers des deux comptoirs (simulés)
     Atelier = Lisa Cirenza Fine Art (artiste-auteur, compte Stripe 1) ; Espace = Créa-Tea-Vité (SAS, compte Stripe 2).
     Une seule source (localStorage), identique dans tous les onglets ; donnée abîmée nettoyée sans bloquer. */
  var PANIER_CLE = 'lc-paniers-v3';
  function lirePaniers() {
    try {
      var v = JSON.parse(localStorage.getItem(PANIER_CLE) || 'null');
      if (v && Array.isArray(v.atelier) && Array.isArray(v.espace)) return { atelier: v.atelier.filter(valide), espace: v.espace.filter(valide) };
    } catch (e) { }
    try { localStorage.removeItem(PANIER_CLE); } catch (e) { }
    return { atelier: [], espace: [] };
  }
  function valide(x) { return x && typeof x.id === 'string' && typeof x.titre === 'string'; }
  function ecrirePaniers(pn) { try { localStorage.setItem(PANIER_CLE, JSON.stringify(pn)); } catch (e) { } }
  function paniers() {
    var tiroir = $('#panier'), btn = $('[data-panier-ouvrir]'), txtEl = $('[data-textes-panier]');
    if (!tiroir || !txtEl) return;
    var TX = {};
    try { TX = JSON.parse(txtEl.getAttribute('data-textes-panier')); } catch (e) { }
    var noms = { atelier: $('.panier__comptoir--atelier h3 span', tiroir).textContent, espace: $('.panier__comptoir--espace h3 span', tiroir).textContent };
    var PN = lirePaniers();
    var dernierFocus = null;
    function prix(n) { return TX.fr ? n.toLocaleString('fr-FR') + ' €' : '€' + n.toLocaleString('en-GB'); }
    function lire(b) { try { return JSON.parse(b.getAttribute('data-ajouter')); } catch (e) { return null; } }
    function rendre() {
      ['atelier', 'espace'].forEach(function (c) {
        var ul = $('[data-liste="' + c + '"]', tiroir), sec = ul.closest('.panier__comptoir');
        ul.textContent = '';
        var total = 0, inconnus = 0, payables = 0;
        PN[c].forEach(function (it, i) {
          var li = document.createElement('li'); li.className = 'panier__ligne';
          var img = document.createElement('img'); img.src = M(it.image); img.alt = ''; img.width = 52; img.height = 52; img.loading = 'lazy';
          var d = document.createElement('div'); d.textContent = it.titre;
          var sm = document.createElement('small');
          if (it.prix) { total += it.prix; payables++; sm.textContent = prix(it.prix); }
          else if (it.genre === 'edition') { inconnus++; payables++; sm.textContent = TX.a_completer; }
          else sm.textContent = TX.sur_demande;
          d.appendChild(sm);
          var b = document.createElement('button'); b.type = 'button'; b.className = 'panier__retirer'; b.textContent = TX.retirer;
          b.setAttribute('aria-label', TX.retirer + ' : ' + it.titre);
          b.addEventListener('click', function () { PN[c].splice(i, 1); ecrirePaniers(PN); rendre(); });
          li.appendChild(img); li.appendChild(d); li.appendChild(b); ul.appendChild(li);
        });
        sec.classList.toggle('a-articles', PN[c].length > 0);
        $('[data-total="' + c + '"]', tiroir).textContent = !PN[c].length ? '—' : (payables ? (total ? prix(total) + (inconnus ? TX.plus_a_completer : '') : TX.a_completer) : TX.sur_demande);
        var pay = $('[data-payer="' + c + '"]', tiroir);
        pay.disabled = !PN[c].length;
        $('span', pay).textContent = payables ? TX.payer : TX.demande;
        pay.setAttribute('data-mode', payables ? 'payer' : 'demande');
        var n = $('[data-compte-panier="' + c + '"]');
        if (n) { n.textContent = PN[c].length; n.classList.toggle('est-vide', !PN[c].length); }
      });
      if (btn) btn.hidden = !(PN.atelier.length + PN.espace.length) && !P.boutique;
      $$('[data-ajouter]').forEach(function (b) {
        var d = lire(b);
        b.classList.toggle('est-ajoute', !!(d && PN[d.comptoir] && PN[d.comptoir].some(function (x) { return x.id === d.id; })));
      });
    }
    function ouvrir() {
      dernierFocus = document.activeElement;
      tiroir.hidden = false;
      html.classList.add('panier-ouvert');
      lissage.verrou++;
      document.body.style.overflow = 'hidden';
      var f = $('.panier__fermer', tiroir); if (f) f.focus();
    }
    function fermer() {
      if (tiroir.hidden) return;
      tiroir.hidden = true;
      html.classList.remove('panier-ouvert');
      lissage.verrou = Math.max(0, lissage.verrou - 1);
      document.body.style.overflow = '';
      $$('[data-recu]', tiroir).forEach(function (r) { r.hidden = true; });
      if (dernierFocus && dernierFocus.focus) dernierFocus.focus();
    }
    if (btn) btn.addEventListener('click', ouvrir);
    $$('[data-panier-fermer]', tiroir).forEach(function (b) { b.addEventListener('click', fermer); });
    document.addEventListener('keydown', function (e) {
      if (tiroir.hidden) return;
      if (e.key === 'Escape') { fermer(); return; }
      if (e.key === 'Tab') {
        var f = $$('button:not([disabled]), a[href], [tabindex="-1"]:not([hidden])', tiroir).filter(function (x) { return x.offsetParent !== null; });
        if (!f.length) return;
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      }
    });
    var annonce = document.createElement('p');
    annonce.className = 'annonce-panier'; annonce.setAttribute('role', 'status'); annonce.setAttribute('aria-live', 'polite');
    document.body.appendChild(annonce);
    var tAnnonce;
    function annoncer(txt) { annonce.textContent = txt; annonce.classList.add('est-visible'); clearTimeout(tAnnonce); tAnnonce = setTimeout(function () { annonce.classList.remove('est-visible'); }, 2600); }
    // l'œuvre s'envole jusqu'au panier de son comptoir
    function envol(depuis, cible, src, fin) {
      if (ETAT.reduit || !depuis || !cible) { fin(); return; }
      var a = depuis.getBoundingClientRect(), b = cible.getBoundingClientRect();
      if (!b.width || !a.width) { fin(); return; }
      var im = document.createElement('img'); im.className = 'envol'; im.src = src; im.alt = '';
      document.body.appendChild(im);
      var x0 = a.left + a.width / 2 - 36, y0 = a.top + a.height / 2 - 36, x1 = b.left + b.width / 2 - 36, y1 = b.top + b.height / 2 - 36;
      animer(820, function (e, p) {
        var x = lerp(x0, x1, e), y = lerp(y0, y1, e) - Math.sin(p * Math.PI) * 160, s = lerp(1, 0.28, e);
        im.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) scale(' + s.toFixed(3) + ') rotate(' + (p * 14).toFixed(1) + 'deg)';
        im.style.opacity = String(1 - Math.max(0, p - 0.85) / 0.15);
      }, EASE.io).promesse.then(function () { im.remove(); fin(); });
    }
    $$('[data-ajouter]').forEach(function (b) {
      b.addEventListener('click', function () {
        var d = lire(b);
        if (!d || !PN[d.comptoir]) return;
        if (!PN[d.comptoir].some(function (x) { return x.id === d.id; })) { PN[d.comptoir].push(d); ecrirePaniers(PN); }
        if (btn) btn.hidden = false;
        var h = $('[data-entete]'); if (h) h.classList.remove('est-cache');
        var cible = $('[data-compte-panier="' + d.comptoir + '"]');
        var carte = b.closest('.produit'), visuel = carte && $('img', carte);
        envol(visuel, cible, visuel ? (visuel.currentSrc || visuel.src) : M(d.image), function () {
          rendre();
          if (cible) { cible.classList.add('rebond'); setTimeout(function () { cible.classList.remove('rebond'); }, 380); }
          annoncer(TX.ajoute.replace('{n}', noms[d.comptoir]));
        });
      });
    });
    $$('[data-payer]', tiroir).forEach(function (b) {
      b.addEventListener('click', function () {
        var c = b.getAttribute('data-payer');
        if (!PN[c].length || b.disabled) return;
        b.disabled = true;
        var recu = $('[data-recu="' + c + '"]', tiroir);
        recu.textContent = (b.getAttribute('data-mode') === 'demande' ? TX.recu_demande : TX.recu_paye).replace('{n}', noms[c]);
        PN[c] = []; ecrirePaniers(PN);
        rendre();
        recu.hidden = false; recu.focus();
      });
    });
    addEventListener('storage', function (e) { if (e.key === PANIER_CLE) { PN = lirePaniers(); rendre(); } });
    // filtres du comptoir de l'atelier, gardés dans l'adresse
    var filtres = $('[data-filtres]'), produits = $$('[data-produits] .produit');
    if (filtres) {
      var filtrer = function (f, garder) {
        $$('.filtre', filtres).forEach(function (x) { x.setAttribute('aria-pressed', String(x.getAttribute('data-filtre') === f)); });
        produits.forEach(function (pr) { pr.hidden = !(f === 'tout' || pr.getAttribute('data-genre') === f); });
        if (garder) {
          var u = new URL(location.href);
          if (f === 'tout') u.searchParams.delete('filtre'); else u.searchParams.set('filtre', f);
          history.replaceState(history.state, '', u);
        }
        toutRemesurer();
      };
      $$('.filtre', filtres).forEach(function (x) { x.addEventListener('click', function () { filtrer(x.getAttribute('data-filtre'), true); }); });
      var f0 = params.get('filtre');
      if (f0 === 'edition' || f0 === 'original') filtrer(f0, false);
    }
    rendre();
  }

  /* ------------------------------------------------------------ v3 · vidéo de l'Espace, chargée seulement au clic */
  function videos() {
    $$('[data-video]').forEach(function (v) {
      var b = $('.video__bouton', v);
      if (!b) return;
      b.addEventListener('click', function () { demanderMedias(function () {
        var f = document.createElement('iframe');
        f.src = 'https://player.vimeo.com/video/' + v.getAttribute('data-video') + '?h=' + v.getAttribute('data-video-h') + '&autoplay=1&title=0&byline=0&portrait=0&dnt=1';
        f.allow = 'autoplay; fullscreen; picture-in-picture';
        f.setAttribute('allowfullscreen', '');
        f.title = b.getAttribute('aria-label') || 'Vimeo';
        b.replaceWith(f);
        f.focus();
      }); });
    });
  }

  /* ------------------------------------------------------------ v5 · éditeur des horaires (outil de la maquette)
     Même champs que les futures collections Wix « Horaires » et « Exceptions ». L'aperçu reste dans ce navigateur. */
  function editeurHoraires() {
    var racine = $('[data-editeur-horaires]');
    if (!racine) return;
    var X = (window.LC_PAGE && window.LC_PAGE.editeur) || {};
    var modele = null, publie = null;
    var ORDRE = [1, 2, 3, 4, 5, 6, 0];
    var cap = function (x) { return x ? x.charAt(0).toUpperCase() + x.slice(1) : x; };
    var copie = function (o) { return JSON.parse(JSON.stringify(o)); };
    function el(tag, attrs, texte) {
      var n = document.createElement(tag);
      Object.keys(attrs || {}).forEach(function (k) { if (attrs[k] !== null && attrs[k] !== undefined) n.setAttribute(k, attrs[k]); });
      if (texte !== undefined) n.textContent = texte;
      return n;
    }
    function champ(lib, input) { var l = el('label', { class: 'editeur__champ' }); l.appendChild(el('span', {}, lib)); l.appendChild(input); return l; }
    function heureInput(v, cb) { var i = el('input', { type: 'time', value: v || '', step: 300 }); i.addEventListener('input', function () { cb(i.value); maj(); }); return i; }
    function dateInput(v, cb) { var i = el('input', { type: 'date', value: v || '' }); i.addEventListener('input', function () { cb(i.value); maj(); }); return i; }
    function texteInput(v, cb) { var i = el('input', { type: 'text', value: v || '' }); i.addEventListener('input', function () { cb(i.value); maj(true); }); return i; }

    var semaine = $('[data-editeur-semaine]', racine), exceptions = $('[data-editeur-exceptions]', racine);
    var apercuListe = $('[data-editeur-liste]', racine), apercuStatut = $('[data-editeur-statut]', racine), apercuAnnonce = $('[data-editeur-annonce]', racine);
    var etat = $('[data-editeur-etat]', racine);

    function dessinerSemaine() {
      semaine.textContent = '';
      ORDRE.forEach(function (j) {
        var l = HOR.ligneDuJour(modele, j);
        if (modele.horaires.indexOf(l) < 0) { modele.horaires.push(l); }
        var ligne = el('div', { class: 'editeur__jour' });
        ligne.appendChild(el('p', { class: 'editeur__nom' }, cap(T.jours[j])));
        var sel = el('select', { 'aria-label': cap(T.jours[j]) });
        [['ferme', X.ferme], ['ouvert', X.ouvert], ['rdv', X.rdv]].forEach(function (o) { sel.appendChild(el('option', { value: o[0] }, o[1])); });
        sel.value = l.ouvert ? 'ouvert' : (l.surRendezVous ? 'rdv' : 'ferme');
        var heures = el('div', { class: 'editeur__heures' });
        function heuresVisibles() { heures.hidden = sel.value !== 'ouvert'; }
        sel.addEventListener('change', function () {
          l.ouvert = sel.value === 'ouvert';
          l.surRendezVous = sel.value === 'rdv';
          if (l.ouvert && !l.debut) { l.debut = '14:30'; l.fin = '18:30'; dessinerSemaine(); }
          heuresVisibles();
          maj();
        });
        heures.appendChild(champ(X.de, heureInput(l.debut, function (v) { l.debut = v; })));
        heures.appendChild(champ(X.a, heureInput(l.fin, function (v) { l.fin = v; })));
        heures.appendChild(champ(X.de2, heureInput(l.debut2, function (v) { l.debut2 = v; })));
        heures.appendChild(champ(X.a2, heureInput(l.fin2, function (v) { l.fin2 = v; })));
        heuresVisibles();
        ligne.appendChild(sel);
        ligne.appendChild(heures);
        semaine.appendChild(ligne);
      });
    }
    function dessinerExceptions() {
      exceptions.textContent = '';
      (modele.exceptions || []).forEach(function (x, i) {
        var f = el('fieldset', { class: 'editeur__exception' });
        var leg = el('legend', {}, X.exception + ' ' + (i + 1));
        if (x.exemple) leg.appendChild(el('span', { class: 'exemple' }, X.exemple));
        f.appendChild(leg);
        var dates = el('div', { class: 'editeur__ligne' });
        dates.appendChild(champ(X.du, dateInput(x.du, function (v) { x.du = v; })));
        dates.appendChild(champ(X.au, dateInput(x.au, function (v) { x.au = v; })));
        dates.appendChild(champ(X.afficher, dateInput(x.afficherDes, function (v) { x.afficherDes = v; })));
        f.appendChild(dates);
        var genre = el('select', {});
        [['ferme', X.ferme_ex], ['special', X.special]].forEach(function (o) { genre.appendChild(el('option', { value: o[0] }, o[1])); });
        genre.value = x.ferme ? 'ferme' : 'special';
        var hs = el('div', { class: 'editeur__ligne' });
        hs.appendChild(champ(X.de, heureInput(x.debut, function (v) { x.debut = v; })));
        hs.appendChild(champ(X.a, heureInput(x.fin, function (v) { x.fin = v; })));
        hs.hidden = !!x.ferme;
        genre.addEventListener('change', function () { x.ferme = genre.value === 'ferme'; hs.hidden = x.ferme; maj(); });
        f.appendChild(champ(X.genre, genre));
        f.appendChild(hs);
        var msgs = el('div', { class: 'editeur__ligne editeur__ligne--large' });
        msgs.appendChild(champ(X.msg_en, texteInput(x.messageEn, function (v) { x.messageEn = v; })));
        msgs.appendChild(champ(X.msg_fr, texteInput(x.messageFr, function (v) { x.messageFr = v; })));
        f.appendChild(msgs);
        var sup = el('button', { type: 'button', class: 'editeur__supprimer' }, X.supprimer);
        sup.addEventListener('click', function () { modele.exceptions.splice(i, 1); dessinerExceptions(); maj(); });
        f.appendChild(sup);
        exceptions.appendChild(f);
      });
    }
    function maj(texteSeul) {
      var lignes = HOR.lignes(modele);
      apercuListe.textContent = '';
      lignes.forEach(function (l) { var d = el('div'); d.appendChild(el('dt', {}, l[0])); d.appendChild(el('dd', {}, l[1])); apercuListe.appendChild(d); });
      var s = HOR.statut(modele);
      apercuStatut.textContent = s.texte;
      apercuStatut.parentNode.classList.toggle("est-ouvert", s.ouvert);
      var auj = heureParis().date;
      var a = HOR.annonce(modele, auj);
      var prochaines = (modele.exceptions || []).filter(function (x) { return x.au && x.au >= auj; }).map(function (x) {
        var des = x.afficherDes || (x.du ? HOR.plus(x.du, -10) : '');
        return (D.langue === 'fr' ? x.messageFr : x.messageEn) + ' (' + X.visible.replace('{du}', des).replace('{au}', x.au) + ')';
      });
      apercuAnnonce.textContent = a ? a : X.aucune;
      var liste = $('[data-editeur-prochaines]', racine);
      liste.textContent = '';
      prochaines.forEach(function (p) { liste.appendChild(el('li', {}, p)); });
      etat.textContent = JSON.stringify(nettoye()) === JSON.stringify(nettoye(publie)) ? X.etat_publie : X.etat_modifie;
    }
    function nettoye(m) {
      var x = copie(m || modele);
      delete x._apercu;
      x.horaires.sort(function (a, b) { return ORDRE.indexOf(a.jour) - ORDRE.indexOf(b.jour); });
      x.maj = heureParis().date;
      return x;
    }
    function charger(depart) {
      modele = copie(depart);
      delete modele._apercu;
      modele.horaires = modele.horaires || [];
      modele.exceptions = modele.exceptions || [];
      dessinerSemaine();
      dessinerExceptions();
      maj();
    }
    $('[data-editeur-ajouter]', racine).addEventListener('click', function () {
      var auj = heureParis().date;
      modele.exceptions.push({ du: auj, au: auj, ferme: true, messageEn: '', messageFr: '' });
      dessinerExceptions();
      maj();
    });
    $('[data-editeur-apercu]', racine).addEventListener('click', function () {
      try { localStorage.setItem(HOR.cleApercu, JSON.stringify(nettoye())); etat.textContent = X.apercu_actif; } catch (e) { etat.textContent = X.stockage; }
    });
    $('[data-editeur-arreter]', racine).addEventListener('click', function () {
      try { localStorage.removeItem(HOR.cleApercu); } catch (e) { /* rien */ }
      charger(publie);
      etat.textContent = X.etat_publie;
    });
    $('[data-editeur-telecharger]', racine).addEventListener('click', function () {
      var blob = new Blob([JSON.stringify(nettoye(), null, 2) + '\n'], { type: 'application/json' });
      var a = el('a', { href: URL.createObjectURL(blob), download: 'horaires.json' });
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.parentNode.removeChild(a); }, 500);
    });
    publie = copie(HOR.donnees || (D.espace && D.espace.horaires));
    charger(HOR.lire());
    document.addEventListener('lc:horaires', function () {
      publie = copie(HOR.donnees);
      var a = null;
      try { a = localStorage.getItem(HOR.cleApercu); } catch (e) { a = null; }
      if (!a) charger(publie);
    });
  }

  /* ------------------------------------------------------------ v6 · cookies : rien de facultatif avant l'accord, « Refuser » aussi visible qu'« Accepter »
     Le site lui-même ne pose aucun cookie et ne mesure rien. Seuls les lecteurs vidéo (Vimeo, Wix Video) et, plus tard,
     les lecteurs de podcast peuvent poser les leurs : ils ne se chargent qu'avec l'accord du visiteur. */
  var CONSENT = {
    cle: 'lc-cookies-v1',
    lire: function () { try { return localStorage.getItem(this.cle); } catch (e) { return null; } },
    ecrire: function (v) { try { localStorage.setItem(this.cle, v); } catch (e) { /* rien */ } },
    medias: function () { return this.lire() === 'accepte'; },
    attente: []
  };
  function cookies() {
    var fr = D.langue === 'fr';
    var X = fr
      ? { titre: 'Cookies', texte: 'Ce site ne pose aucun cookie et ne mesure pas votre visite. Les vidéos (Vimeo, Wix Video) et lecteurs audio peuvent poser leurs propres cookies quand vous les lancez : nous ne les chargeons qu’avec votre accord.', ok: 'Accepter', non: 'Refuser', lien: 'Politique cookies (texte de Lisa à venir)' }
      : { titre: 'Cookies', texte: 'This site sets no cookies and does not track your visit. Videos (Vimeo, Wix Video) and audio players may set their own cookies when you play them: we only load them with your consent.', ok: 'Accept', non: 'Refuse', lien: 'Cookie policy (Lisa’s text to come)' };
    var b = document.createElement('div');
    b.className = 'cookies';
    b.setAttribute('role', 'dialog');
    b.setAttribute('aria-labelledby', 'cookies-titre');
    b.hidden = true;
    b.innerHTML = '<h2 id="cookies-titre"></h2><p class="cookies__texte"></p><p class="cookies__lien"></p><div class="cookies__boutons"><button type="button" class="cookies__bouton" data-choix="refuse"></button><button type="button" class="cookies__bouton" data-choix="accepte"></button></div>';
    $('#cookies-titre', b).textContent = X.titre;
    $('.cookies__texte', b).textContent = X.texte;
    $('.cookies__lien', b).textContent = X.lien;
    $('[data-choix="refuse"]', b).textContent = X.non;
    $('[data-choix="accepte"]', b).textContent = X.ok;
    document.body.appendChild(b);
    function ouvrir() { b.hidden = false; html.classList.add('a-cookies'); }
    function fermer() { b.hidden = true; html.classList.remove('a-cookies'); }
    $$('[data-choix]', b).forEach(function (bt) {
      bt.addEventListener('click', function () {
        CONSENT.ecrire(bt.getAttribute('data-choix'));
        fermer();
        var a = CONSENT.attente.splice(0);
        if (CONSENT.medias()) a.forEach(function (f) { f(); });
      });
    });
    $$('[data-cookies-ouvrir]').forEach(function (bt) { bt.addEventListener('click', ouvrir); });
    if (!CONSENT.lire() && params.get('ouverture') !== 'non') ouvrir();
    CONSENT.demander = function (f) {
      if (CONSENT.medias()) { f(); return; }
      CONSENT.attente.push(f);
      ouvrir();
      var ok = $('[data-choix="accepte"]', b);
      if (ok) ok.focus();
    };
  }
  function demanderMedias(f) { if (CONSENT.demander) CONSENT.demander(f); else f(); }

  /* ------------------------------------------------------------ v6 · vidéos du procédé (Wix Video), chargées au clic, après accord */
  function videosProcede() {
    $$('[data-video-mp4]').forEach(function (li) {
      var b = $('.video-procede__bouton', li);
      if (!b) return;
      b.addEventListener('click', function () {
        demanderMedias(function () {
          var v = document.createElement('video');
          v.src = li.getAttribute('data-video-mp4');
          v.controls = true;
          v.autoplay = true;
          v.playsInline = true;
          v.preload = 'auto';
          v.setAttribute('aria-label', b.getAttribute('aria-label') || '');
          b.replaceWith(v);
          v.focus();
        });
      });
    });
  }

  /* ------------------------------------------------------------ v6 · formulaires d'inscription aux retraites (maquette : rien n'est envoyé)
     Sur le site final, les réponses partent au même formulaire Wix (data-wix-form-id), puis l'acompte de 200 € est encaissé. */
  function inscriptions() {
    $$('[data-inscription]').forEach(function (f) {
      var merci = f.parentNode.querySelector('.inscription__merci');
      var resume = $('.formulaire__erreurs', f);
      var fr = D.langue === 'fr';
      var OBL = T.form_obligatoire || (fr ? 'Ce champ est obligatoire.' : 'This field is required.');
      function erreur(champ, msg) {
        var wrap = champ.closest('.champ');
        var p = wrap && $('.champ__erreur', wrap);
        if (wrap) wrap.classList.toggle('a-erreur', !!msg);
        if (p) p.textContent = msg || '';
        if (msg) champ.setAttribute('aria-invalid', 'true'); else champ.removeAttribute('aria-invalid');
      }
      f.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var premier = null;
        $$('input[required]', f).forEach(function (c) {
          var vide = c.type === 'radio' ? !$('input[name="' + c.name + '"]:checked', f) : (c.type === 'checkbox' ? !c.checked : !(c.value || '').trim());
          var msg = vide ? OBL : '';
          if (!msg && c.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(c.value.trim())) msg = T.form_email_invalide || OBL;
          erreur(c, msg);
          if (msg && !premier) premier = c;
        });
        var sante = $('[data-sante]', f), allergies = f.elements.allergies;
        if (sante && allergies && (allergies.value || '').trim() && !sante.checked) {
          erreur(sante, OBL);
          if (!premier) premier = sante;
        } else if (sante) erreur(sante, '');
        if (premier) { resume.hidden = false; premier.focus(); return; }
        resume.hidden = true;
        f.hidden = true;
        if (merci) { merci.hidden = false; merci.focus(); }
      });
    });
  }

  /* ------------------------------------------------------------ v6 · recherche sur tout le site (index statique, sans service externe) */
  function recherche() {
    var f = $('[data-recherche]');
    if (!f || !P.recherche) return;
    var liste = $('[data-recherche-resultats]'), etat = $('.recherche__etat');
    var fr = D.langue === 'fr';
    var index = null;
    var norme = function (x) { return (x || '').toString().normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); };
    var GROUPES = fr ? { page: 'Page', serie: 'Série', oeuvre: 'Œuvre', presse: 'Presse' } : { page: 'Page', serie: 'Series', oeuvre: 'Work', presse: 'Press' };
    function chercher(q) {
      var mots = norme(q).split(/\s+/).filter(Boolean);
      liste.textContent = '';
      if (!mots.length) { etat.textContent = ''; return; }
      var res = index.map(function (it) {
        var t = norme(it.t), d = norme(it.d), score = 0;
        for (var i = 0; i < mots.length; i++) {
          if (t.indexOf(mots[i]) > -1) score += 3; else if (d.indexOf(mots[i]) > -1) score += 1; else return null;
        }
        return { it: it, score: score };
      }).filter(Boolean).sort(function (a, b) { return b.score - a.score; }).slice(0, 40);
      etat.textContent = res.length ? (fr ? res.length + ' résultat' + (res.length > 1 ? 's' : '') : res.length + ' result' + (res.length > 1 ? 's' : '')) : (fr ? 'Aucun résultat.' : 'No results.');
      res.forEach(function (r) {
        var li = document.createElement('li'), a = document.createElement('a'), g = document.createElement('span'), t = document.createElement('strong'), d = document.createElement('span');
        a.href = r.it.u;
        g.className = 'recherche__groupe'; g.textContent = GROUPES[r.it.g] || '';
        t.textContent = r.it.t;
        d.className = 'recherche__desc'; d.textContent = r.it.d;
        a.appendChild(g); a.appendChild(t); a.appendChild(d); li.appendChild(a); liste.appendChild(li);
      });
    }
    fetch((html.getAttribute('data-racine') || '/') + P.recherche).then(function (r) { return r.json(); }).then(function (j) {
      index = j;
      var q = params.get('q') || '';
      f.elements.q.value = q;
      if (q) chercher(q);
    });
    f.addEventListener('submit', function (ev) { ev.preventDefault(); if (!index) return; var q = f.elements.q.value; history.replaceState(null, '', '?q=' + encodeURIComponent(q)); chercher(q); });
    f.elements.q.addEventListener('input', function () { if (index) chercher(f.elements.q.value); });
  }

  /* ------------------------------------------------------------ v5 · tirages creativehub : format et papier
     Chaque choix a sa référence (SKU), la même dans Wix et dans creativehub : c'est elle qui relie la vente au bon tirage. */
  function variantes() {
    $$('[data-variante]').forEach(function (sel) {
      var carte = sel.closest('.produit');
      var bouton = carte && $('[data-ajouter]', carte);
      var prixEl = carte && $('.produit__prix', carte);
      if (!bouton) return;
      function prixTxt(n) { return D.langue === 'fr' ? n.toLocaleString('fr-FR') + ' €' : '€' + n.toLocaleString('en-GB'); }
      sel.addEventListener('change', function () {
        var o = sel.options[sel.selectedIndex];
        var d;
        try { d = JSON.parse(bouton.getAttribute('data-ajouter')); } catch (e) { return; }
        var px = Number(o.getAttribute('data-prix'));
        d.id = o.value;
        d.sku = o.value;
        d.prix = px;
        d.titre = sel.getAttribute('data-titre') + ' · ' + o.getAttribute('data-lib');
        bouton.setAttribute('data-ajouter', JSON.stringify(d));
        bouton.classList.remove('est-ajoute');
        if (prixEl) prixEl.textContent = prixTxt(px);
      });
    });
  }

  /* ------------------------------------------------------------ v5 · suggestion de langue (jamais de redirection forcée)
     Un visiteur dont le navigateur est en français voit, une fois, une invitation discrète vers la version française,
     et inversement. Bon pour le référencement : chaque version garde sa propre adresse. */
  function suggestionLangue() {
    var cle = 'lc-langue-vue';
    try { if (localStorage.getItem(cle)) return; } catch (e) { return; }
    if (params.get('ouverture') === 'non') return;
    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || '';
    var veutFr = /^fr\b/i.test(nav);
    var lien = $('.entete__langue');
    if (!lien || (D.langue === 'fr') === veutFr) return;
    var txt = veutFr ? ['Ce site existe aussi en français.', 'Voir en français', 'Rester en anglais'] : ['This site is also in English.', 'View in English', 'Stay in French'];
    var b = document.createElement('div');
    b.className = 'suggestion-langue';
    b.setAttribute('role', 'region');
    b.setAttribute('aria-label', txt[0]);
    b.setAttribute('lang', veutFr ? 'fr' : 'en');
    var p = document.createElement('p'); p.textContent = txt[0];
    var aller = document.createElement('a'); aller.href = lien.getAttribute('href'); aller.textContent = txt[1]; aller.className = 'suggestion-langue__aller';
    var non = document.createElement('button'); non.type = 'button'; non.textContent = txt[2];
    function vu() { try { localStorage.setItem(cle, '1'); } catch (e) { /* rien */ } }
    aller.addEventListener('click', vu);
    non.addEventListener('click', function () { vu(); b.parentNode.removeChild(b); });
    b.appendChild(p); b.appendChild(aller); b.appendChild(non);
    document.body.appendChild(b);
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
    editeurHoraires();
    suggestionLangue();
    variantes();
    comptes();
    formulaire();
    lettres();
    cookies();
    paniers();
    videos();
    videosProcede();
    inscriptions();
    recherche();
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
