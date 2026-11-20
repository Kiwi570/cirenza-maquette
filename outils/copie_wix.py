"""Prépare la copie de la maquette pour le site Wix headless « Lisa Cirenza – Atelier » (385612fb-…).

Usage :
  python3 -I outils/generer.py <copie> --liens html     (après avoir copié le dépôt dans <copie>)
  python3 -I outils/copie_wix.py <copie>

Wix limite les fichiers d'un site hébergé à 20 Mio : les images des œuvres et les photos (56 Mo) sont dans la
médiathèque Wix du site. Ce script remplace leurs adresses par celles de la médiathèque (connecteurs/medias-wix.tsv),
ajoute assets/js/medias.js (lu par site.js pour les images chargées en JavaScript), retire les dossiers d'images,
robots.txt, sitemap.xml et vercel.json. Une nouvelle image doit d'abord être importée dans la médiathèque et ajoutée
au fichier medias-wix.tsv.
"""
import re, json, pathlib, shutil, sys
COPIE = pathlib.Path(sys.argv[1]).resolve()
HOTE = "https://headless-znxwbqojlvv-kiwixteam-1409.wix-site-host.com"
carte = {}
for l in open(pathlib.Path(__file__).resolve().parent.parent / "connecteurs" / "medias-wix.tsv", encoding="utf-8"):
    p, i = l.rstrip("\n").split("\t")
    carte["img/" + p] = "https://static.wixstatic.com/media/" + i
motif = re.compile(r'(?:https://cirenza-maquette\.vercel\.app/|/|(?:\.\./)*)assets/(img/(?:oeuvres|photos)/[A-Za-z0-9._-]+\.webp)')
inconnus, n_rempl, n_fichiers = set(), 0, 0
for f in sorted(COPIE.rglob("*")):
    if f.suffix not in (".html", ".js", ".json", ".txt", ".css") or not f.is_file(): continue
    s = f.read_text(encoding="utf-8"); s0 = s
    def rempl(m):
        global n_rempl
        u = carte.get(m.group(1))
        if not u: inconnus.add(m.group(1)); return m.group(0)
        n_rempl += 1; return u
    s = motif.sub(rempl, s)
    s = s.replace("https://cirenza-maquette.vercel.app", HOTE)
    if f.suffix == ".html":
        # medias.js avant site.js (scripts « defer » : exécutés dans l'ordre)
        m = re.search(r'<script defer src="((?:\.\./)*|/)assets/js/site\.js\?v=(\d+)"></script>', s)
        if m and "medias.js" not in s:
            s = s.replace(m.group(0), f'<script defer src="{m.group(1)}assets/js/medias.js?v={m.group(2)}"></script>' + m.group(0), 1)
        elif not m:
            print("sans site.js :", f.relative_to(COPIE))
    if s != s0:
        f.write_text(s, encoding="utf-8"); n_fichiers += 1
(COPIE / "assets/js/medias.js").write_text(
    "/* Copie hébergée chez Wix : chemin d'origine -> image dans la médiathèque Wix du site « Lisa Cirenza – Atelier ». */\n"
    "window.LC_MEDIAS = " + json.dumps(carte, separators=(",", ":"), sort_keys=True) + ";\n", encoding="utf-8")
for d in ("assets/img/oeuvres", "assets/img/photos"):
    shutil.rmtree(COPIE / d, ignore_errors=True)
for x in ("robots.txt", "sitemap.xml", "vercel.json"):
    (COPIE / x).unlink(missing_ok=True)
print("remplacements", n_rempl, "dans", n_fichiers, "fichiers ; inconnus", sorted(inconnus)[:10])
