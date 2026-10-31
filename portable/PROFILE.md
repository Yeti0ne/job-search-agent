# Modèle de profil

L'agent ne suppose rien : tout ce qui dépend de toi, de ton métier ou de ton pays vient de ce profil. Remplis ce qui est utile, laisse vide ce que tu ne sais pas encore (l'agent le demandera une seule fois), puis donne le fichier à l'assistant au début de la première session, ou colle-le dans les instructions de ton projet.

Ce fichier contient des données personnelles : ne le publie pas et ne le committe pas dans un dépôt public. N'y mets ni numéro d'identité, ni mot de passe, ni information de santé, de famille ou de finances sans rapport avec la recherche.

Au premier lancement, l'agent peut aussi te poser ces questions en trois blocs courts et remplir ce fichier avec toi. Il te lit ensuite un résumé d'une dizaine de lignes à valider.

## Bloc 1 : qui tu es et ce que tu vises
- Prénom et nom, e-mail et téléphone à mettre sur les CV et les messages :
- Métier, niveau de séniorité (junior, confirmé, senior, manager, direction), titre de marché que les recruteurs reconnaissent :
- Parcours, du plus récent au plus ancien : poste, entreprise, dates, et pour chacun deux ou trois réalisations chiffrées (ce que tu as fait, de combien, en combien de temps) :
- Compétences, outils et certifications dont tu es sûr :
- Formation :
- Langues et niveaux (honnêtes : l'agent n'écrira jamais un niveau que tu n'as pas) :
- Points faibles ou écarts connus que l'agent ne doit pas masquer, mais préparer :
- Postes visés : principaux / secondaires / adjacents (proches de ton métier, que tu accepterais) :
- Types d'entreprises que tu préfères (start-up, grand groupe, public, association, conseil…), et entreprises cibles par priorité (A, B) :
- Objectif de la campagne : prises de contact, entretiens, offre, échéance :

## Bloc 2 : où et comment tu cherches
- Pays et zone de recherche :
- Modes acceptés : sur site / hybride / remote (remote dans le pays seulement, ou aussi à l'étranger) :
- Domicile (ville, quartier) pour calculer les trajets, heure de départ, moyen de transport. Seule la ville ira dans la configuration du Radar :
- Trajet maximum accepté, et villes classées de la plus à la moins souhaitée (ou « à établir avec toi ») :
- Langue locale du pays et ton niveau (lu / parlé / professionnel), outil ou cahier d'apprentissage éventuel :
- Semaine ouvrée du pays (ex. lundi à vendredi, ou dimanche à jeudi), jours fériés (liste ou calendrier à utiliser) :
- Fuseau horaire :
- Devise et façon de parler du salaire (brut mensuel, brut annuel…) ; fourchette visée, si tu en as une (estimation, à vérifier) :
- Préavis ou disponibilité :
- Freins éventuels : autorisation de travail, nationalité exigée, habilitation de sécurité, obligations locales :
- Sites d'emploi à surveiller dans le pays (laisse vide pour que l'agent propose une liste) :
- Cabinets, associations et ressources d'aide utiles dans le pays :

## Bloc 3 : tes règles
- Règles de CV : langue(s), longueur maximale, localisation à écrire (pays seulement, ville…), mentions à éviter :
- Relances sur les candidatures déjà envoyées : jamais / après N jours / seulement après un contact :
- Rythme : nombre de candidatures par semaine (10 par défaut), jours où tu ne veux rien (autres que fériés) :
- Notifications : seulement pour une offre A ou B et pour une réponse à confirmer (par défaut), ou autre :
- Langue de travail avec l'agent, et langue des messages aux recruteurs (la langue de l'offre par défaut) :
- Tout ce que l'agent doit toujours ou ne doit jamais faire pour toi :

## Ce qui part dans le Radar (document `config/profile`)
Seulement ce dont la page et les tâches planifiées ont besoin, sans coordonnées ni parcours : `country`, `timezone`, `work_week`, `holidays`, `currency`, `local_language` (nom et niveau), `modes`, `target_roles` (main, secondary, adjacent), `home_area` (la ville seulement), `zone_scale` (ville → points de 4 à 20), `job_sites`, `preferred_company_types`, `target_companies`, `weekly_target`, `followup_pref`, `notify`, `ui_language`. Exemple fictif :

```json
{
  "country": "France",
  "timezone": "Europe/Paris",
  "work_week": ["lun", "mar", "mer", "jeu", "ven"],
  "holidays": "jours fériés légaux de France",
  "currency": "EUR",
  "local_language": { "name": "français", "level": "natif" },
  "modes": ["hybrid", "remote"],
  "target_roles": { "main": ["Responsable exploitation IT"], "secondary": ["Chef de projet infrastructure"], "adjacent": ["Support niveau 3"] },
  "home_area": "Lyon",
  "zone_scale": { "Lyon": 20, "Villeurbanne": 20, "Grenoble": 12, "Paris": 6 },
  "job_sites": ["LinkedIn", "Indeed", "Welcome to the Jungle", "APEC"],
  "preferred_company_types": ["scale-up", "ETI"],
  "target_companies": { "A": ["Exemple SA"], "B": [] },
  "weekly_target": 10,
  "followup_pref": "pas de relance sur une candidature envoyée avant 14 jours",
  "notify": "ab_et_reponses",
  "ui_language": "fr"
}
```
(Valeurs fictives : l'agent remplit le vrai document à partir de ton profil, après ta validation.)
