# Le Radar sans Claude : format des données

Le Radar est, dans l'implémentation de référence, une base de documents lue et écrite avec un outil de Claude. Pour tout autre assistant, les mêmes documents vivent dans des fichiers JSON. Les champs de chaque document sont ceux de la section 1 de `AGENTS.md` (collections `offers`, `contacts`, `runs`, `reports`, `config`) ; ce fichier ne décrit que ce qui est propre au stockage en fichiers.

## Disposition (assistant avec accès aux fichiers)
```
radar/
  offers/<key>.json         une offre par fichier ; <key> = slug(entreprise)-slug(intitulé)-slug(ville)
  contacts/<slug>.json      un contact par fichier ; <slug> = slug du nom
  runs/<AAAA-MM-JJ>.json    journal des passages de veille : { "day": "...", "scans": [ ... ] }
  reports/<AAAA-Www>.json   bilan hebdomadaire
  config/match_grid.json    la grille de notation de l'utilisateur, versionnée
```

## Règles d'écriture
- Un fichier = un objet JSON. L'identifiant du document est le nom du fichier, sans `.json`.
- Dates en ISO 8601 UTC (`2026-10-30T15:00:00Z`). Sans horloge, demander la date et l'heure à l'utilisateur, ou prendre la date du jour avec `T00:00:00Z` : ne jamais inventer une heure précise.
- JSON valide obligatoire. Dans les textes (`text`, `score_detail`, `fit_note`, `notes`), écrire les citations avec des guillemets français « » ; un guillemet droit `"` doit être échappé (`\"`). Après chaque écriture, relire le fichier et vérifier qu'il se lit comme du JSON ; sinon le corriger avant de continuer.
- Toujours lire le fichier avant de le modifier, puis le réécrire entièrement avec tous ses champs existants. Ne jamais supprimer un fichier sans demande explicite de l'utilisateur.
- Avant de créer une offre, lister `radar/offers/` pour vérifier le doublon et le quasi-doublon (même entreprise, intitulé très proche, même ville).
- Plusieurs écritures (une veille, une re-notation) : les faire d'un seul tenant, puis relire pour contrôler. En cas d'erreur à mi-parcours, le dire et ne pas continuer.
- Garder une copie du dossier avant une re-notation de masse (`radar-backup-<date>/`).

## Exemple d'offre
```json
{
  "key": "acme-it-operations-manager-lyon",
  "company": "Acme",
  "title": "IT Operations Manager",
  "location": "Lyon",
  "mode": "hybrid",
  "source": "LinkedIn",
  "url": "https://example.com/jobs/123",
  "status": "nouveau",
  "tier": "B",
  "match_pct": 78,
  "score_detail": "rôle 24/30 (poste secondaire) · séniorité 12/15 (un cran en dessous) · langue 16/20 (basique) · zone 17/20 (hybride) · entreprise 5/7 (nommée) · techno 4/8 = 78",
  "grid_version": "v1-2026-10-30",
  "hebrew": "basique",
  "fit_note": "Une phrase qui justifie la note.",
  "first_seen": "2026-10-30T15:00:00Z",
  "last_seen": "2026-10-30T15:00:00Z",
  "repost_count": 0,
  "origin": "veille"
}
```
(Les valeurs ci-dessus sont fictives. Le champ `hebrew` désigne le niveau de langue locale demandé, quel que soit le pays.)

## Exemple de grille
```json
{
  "version": "v1-2026-10-30",
  "updated_at": "2026-10-30T15:00:00Z",
  "source": "Profil de l'utilisateur au 30 octobre 2026",
  "weights": { "role": 30, "seniority": 15, "language": 20, "zone": 20, "company": 7, "tech": 8 },
  "text": "Les barèmes de la section 2 de AGENTS.md, remplis avec les valeurs du profil (postes visés, échelle des villes et trajets, types d'entreprises préférés, compétences clés)."
}
```

## Sans fichiers (chat seul)
Tenir le Radar en un seul objet :
```json
{ "offers": { "<key>": { } }, "contacts": { "<slug>": { } }, "runs": { }, "reports": { }, "config": { "match_grid": { } } }
```
L'utilisateur le colle en début de session. À la fin, rendre uniquement les documents créés ou modifiés (même forme), que l'utilisateur fusionne dans son fichier. Si la conversation est longue, proposer de rendre l'objet complet à intervalles réguliers.
