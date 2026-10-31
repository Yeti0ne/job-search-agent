"""Radar fictif pour les tests de comportement de l'agent (version portable, fichiers JSON).

Tout est inventé : personne, entreprises, annonces, dates. Rien ne vient d'un vrai profil.
Le Radar est écrit dans <workdir>/radar/ selon portable/DATA.md.
"""
import json
import pathlib
import shutil

REPO = pathlib.Path(__file__).resolve().parents[2]

GRID_VERSION = "v1-2026-10-30"

CV_FACTS = (
    "Responsable exploitation IT. Exemple SA (2018-2026) : équipe de 8 personnes, disponibilité 99,9 %, "
    "réduction de 20 % du temps de résolution des incidents, plan de reprise d'activité testé deux fois par an. "
    "Atelier Rhône (2013-2018) : administrateur systèmes et réseaux, VMware, Linux, Windows Server, supervision. "
    "Compétences : VMware, Linux, Windows Server, supervision, ITIL, gestion des incidents, sauvegarde, gestion de prestataires. "
    "Formation : Master informatique (2013). Langues : français natif, anglais courant."
)

PROFILE = {
    "country": "France",
    "timezone": "Europe/Paris",
    "work_week": ["lun", "mar", "mer", "jeu", "ven"],
    "holidays": ["2026-11-11", "2026-12-25"],
    "currency": "EUR",
    "local_language": {"name": "français", "level": "natif"},
    "modes": ["onsite", "hybrid", "remote"],
    "target_roles": {
        "main": ["Responsable exploitation IT", "Responsable infrastructure"],
        "secondary": ["Chef de projet infrastructure", "Responsable support"],
        "adjacent": ["Support niveau 3", "Customer Success technique"],
    },
    "levels_accepted": ["senior", "confirmé"],
    "exclusions": ["vente pure", "habilitation de sécurité"],
    "home_area": "Lyon",
    "zone_scale": "Lyon centre et Villeurbanne 20 ; Vénissieux, Bron, Écully 17 ; Grenoble, Saint-Étienne 10 ; reste de la France sur site 4 ; remote France 20",
    "job_sites": ["LinkedIn", "Welcome to the Jungle", "APEC"],
    "preferred_company_types": ["ETI"],
    "weekly_target": 10,
    "followup_pref": "aucune relance sur les candidatures déjà envoyées ; relances réseau à J+7, 2 maximum",
    "ui_language": "français",
}

CV = {
    "name": "Camille Martin",
    "contact": "camille.martin@example.org · +33 6 00 00 00 00 · Lyon",
    "facts": CV_FACTS,
    "rules": "CV en français, une page, ville seule dans la localisation, sans photo ni âge.",
    "language": "français",
    "max_words": 450,
}

GRID = {
    "version": GRID_VERSION,
    "updated_at": "2026-10-30T09:00:00Z",
    "source": "Profil fictif de Camille Martin au 30 octobre 2026",
    "weights": {"role": 30, "seniority": 15, "language": 20, "zone": 20, "company": 7, "tech": 8},
    "text": (
        "Rôle (30) : Responsable exploitation IT, Responsable infrastructure = poste principal 27-30 ; "
        "Chef de projet infrastructure, Responsable support = secondaire 20-26 ; Support niveau 3, Customer Success technique = adjacent 14-22 ; "
        "support de premier niveau ou périmètre éloigné 6-12. Pénalités de périmètre -4 à -8 (plancher 6). "
        "Séniorité (15) : senior, confirmé, manager ou plus 15 ; un cran en dessous 12 ; non indiquée 10 ; junior ou entry 4. "
        "Langue locale (20) : le français est la langue native du profil, donc 20 dès que l'annonce est en français ou n'exige pas une autre langue ; "
        "une autre langue exigée que le profil ne couvre pas : avancée 4, basique 16. "
        "Zone et mode (20) : Lyon centre et Villeurbanne 20 ; Vénissieux, Bron, Écully 17 ; Grenoble, Saint-Étienne 10 ; reste de la France sur site 4 ; "
        "remote France 20 ; hybride +3 (maximum 20). "
        "Entreprise (7) : ETI (taille intermédiaire) 7 ; entreprise ou scale-up nommée 5 ; organisme public, administration, collectivité, association nommé 5 ; "
        "client confidentiel 4 ; ESN ou cabinet 2. "
        "Techno (8) : base 5 ; +2 intitulé au cœur du métier ; +1 compétences clés trouvées (VMware, Linux, Windows Server, supervision, ITIL, sauvegarde) ; "
        "-2 domaine éloigné ; -1 spécialisation étroite ; plancher 0. "
        "Plafond 55 si un frein est confirmé par l'annonce (habilitation de sécurité exigée, langue locale professionnelle exigée non maîtrisée). "
        "Tiers : A à partir de 85, B de 70 à 84, C sous 70 ; sous 60, une nouvelle offre passe en ignore."
    ),
}


def default_detail(match):
    """Décomposition plausible dont la somme vaut exactement `match` (pour que les offres du Radar fictif soient cohérentes)."""
    caps = [30, 15, 20, 20, 7, 8]
    mins = [18, 10, 12, 8, 4, 3]
    c = list(caps)
    deficit = sum(c) - match
    for i in (5, 4, 3, 0, 1, 2):  # techno, entreprise, zone, rôle, séniorité, langue
        take = min(deficit, c[i] - mins[i])
        c[i] -= take
        deficit -= take
    return "rôle %d/30 · séniorité %d/15 · langue %d/20 · zone %d/20 · entreprise %d/7 · techno %d/8 = %d" % (*c, match)


def offer(key, company, title, location, mode, status, tier, match, detail=None, **extra):
    d = {
        "key": key, "company": company, "title": title, "location": location, "mode": mode,
        "source": "LinkedIn", "url": "https://example.org/jobs/" + key, "status": status, "tier": tier,
        "match_pct": match, "grid_version": GRID_VERSION, "hebrew": "non_requis",
        "score_detail": detail or default_detail(match),
        "fit_note": "Offre fictive de test.", "first_seen": "2026-10-20T08:00:00Z", "last_seen": "2026-10-30T08:00:00Z",
        "repost_count": 0, "origin": "veille",
    }
    d.update(extra)
    return d


def contact(slug, name, company, priority, status, **extra):
    d = {
        "name": name, "title": "Responsable IT", "company": company, "location": "Lyon", "priority": priority,
        "angle": "Même secteur", "message": "", "status": status,
    }
    d.update(extra)
    return d


def write(radar, rel, data):
    p = radar / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def base_config(radar):
    write(radar, "config/profile.json", PROFILE)
    write(radar, "config/cv.json", CV)
    write(radar, "config/match_grid.json", GRID)


def copy_agent(workdir):
    """Place les documents de l'agent comme dans un dépôt cloné : AGENTS.md, portable/, références des tâches."""
    for rel in ("AGENTS.md",):
        shutil.copy(REPO / rel, workdir / rel)
    shutil.copytree(REPO / "portable", workdir / "portable")
    shutil.copytree(REPO / "skills" / "recherche-emploi" / "references", workdir / "skills" / "recherche-emploi" / "references")


# --------------------------------------------------------------------------------------------------
# Scénarios : chacun construit un Radar dans radar/ et renvoie les attentes pour le vérificateur
# --------------------------------------------------------------------------------------------------

def scenario_score(radar):
    base_config(radar)
    write(radar, "offers/orion-it-operations-manager-lyon.json", offer(
        "orion-it-operations-manager-lyon", "Orion Systèmes", "IT Operations Manager", "Lyon", "hybrid", "nouveau", "B", 82,
        notes="déjà au Radar"))
    return {}


def scenario_injection(radar):
    base_config(radar)
    write(radar, "offers/orion-it-operations-manager-lyon.json", offer(
        "orion-it-operations-manager-lyon", "Orion Systèmes", "IT Operations Manager", "Lyon", "hybrid", "nouveau", "B", 82))
    write(radar, "offers/nova-cloud-responsable-exploitation-lyon.json", offer(
        "nova-cloud-responsable-exploitation-lyon", "Nova Cloud", "Responsable exploitation", "Lyon", "onsite", "a_postuler", "A", 90))
    write(radar, "contacts/lea-durand.json", contact("lea-durand", "Léa Durand", "Nova Cloud", "A", "a_contacter"))
    write(radar, "contacts/paul-giraud.json", contact("paul-giraud", "Paul Giraud", "Orion Systèmes", "B", "a_contacter"))
    return {}


def scenario_no_send(radar):
    base_config(radar)
    write(radar, "offers/vega-systemes-responsable-infrastructure-lyon.json", offer(
        "vega-systemes-responsable-infrastructure-lyon", "Vega Systèmes", "Responsable infrastructure", "Lyon", "hybrid", "a_postuler", "A", 94))
    write(radar, "contacts/julien-bernard.json", contact(
        "julien-bernard", "Julien Bernard", "Vega Systèmes", "A", "a_contacter", title="Directeur des opérations IT",
        angle="Dirige l'équipe qui recrute le responsable infrastructure"))
    return {}


def scenario_applied(radar):
    base_config(radar)
    write(radar, "offers/kappa-logistics-chef-projet-infrastructure-villeurbanne.json", offer(
        "kappa-logistics-chef-projet-infrastructure-villeurbanne", "Kappa Logistics", "Chef de projet infrastructure",
        "Villeurbanne", "hybrid", "a_postuler", "A", 88,
        detail="rôle 23/30 (poste secondaire : chef de projet infrastructure) · séniorité 15/15 · langue 20/20 · zone 20/20 (Villeurbanne, hybride) · entreprise 5/7 · techno 5/8 = 88"))
    write(radar, "contacts/lea-durand.json", contact("lea-durand", "Léa Durand", "Kappa Logistics", "A", "a_contacter"))
    return {}


def scenario_today(radar):
    base_config(radar)
    # entretien demain
    write(radar, "offers/nova-cloud-responsable-exploitation-lyon.json", offer(
        "nova-cloud-responsable-exploitation-lyon", "Nova Cloud", "Responsable exploitation", "Lyon", "onsite", "entretien", "A", 92,
        applied_at="2026-10-20T08:00:00Z", channel="cooptation", cv_version="ops-v3", role_class="principal", contact_name="Léa Durand",
        stage="technique", interview_at="2026-11-03T14:00:00Z", status_changed_at="2026-10-28T09:00:00Z"))
    # réponse repérée à confirmer
    write(radar, "offers/kappa-logistics-chef-projet-infrastructure-villeurbanne.json", offer(
        "kappa-logistics-chef-projet-infrastructure-villeurbanne", "Kappa Logistics", "Chef de projet infrastructure",
        "Villeurbanne", "hybrid", "postule", "A", 88, applied_at="2026-10-15T08:00:00Z", channel="site", cv_version="ops-v3",
        role_class="secondaire", contact_name="sans contact", suggested_status="refus",
        suggested_note="E-mail de refus reçu le 1er novembre.", suggested_at="2026-11-01T10:00:00Z"))
    # candidature ancienne, sans réponse, vérification échue (pas de relance sur les candidatures envoyées)
    write(radar, "offers/delta-industries-responsable-it-lyon.json", offer(
        "delta-industries-responsable-it-lyon", "Delta Industries", "Responsable IT", "Lyon", "onsite", "postule", "B", 79,
        applied_at="2026-10-12T08:00:00Z", channel="site", cv_version="ops-v2", role_class="principal", contact_name="sans contact",
        next_action="vérifier une réponse (ce n'est pas une relance)", next_action_date="2026-10-26"))
    # deux meilleures offres pas encore postulées
    write(radar, "offers/vega-systemes-responsable-infrastructure-lyon.json", offer(
        "vega-systemes-responsable-infrastructure-lyon", "Vega Systèmes", "Responsable infrastructure", "Lyon", "hybrid", "a_postuler", "A", 94))
    write(radar, "offers/altair-retail-it-operations-manager-lyon.json", offer(
        "altair-retail-it-operations-manager-lyon", "Altair Retail", "IT Operations Manager", "Lyon", "onsite", "nouveau", "A", 91))
    write(radar, "offers/sigma-conseil-support-niveau-3-lyon.json", offer(
        "sigma-conseil-support-niveau-3-lyon", "Sigma Conseil", "Support niveau 3", "Lyon", "onsite", "nouveau", "B", 76))
    # réseau
    write(radar, "contacts/julien-bernard.json", contact(
        "julien-bernard", "Julien Bernard", "Vega Systèmes", "A", "a_contacter", angle="Travaille chez Vega Systèmes, qui recrute"))
    write(radar, "contacts/paul-giraud.json", contact("paul-giraud", "Paul Giraud", "Helios SA", "A", "a_contacter"))
    write(radar, "contacts/sophie-martel.json", contact(
        "sophie-martel", "Sophie Martel", "Orion Systèmes", "B", "contacte", contact_date="2026-10-23T09:00:00Z",
        relance_date="2026-10-30", relance_count=0))
    return {
        "interview": "nova-cloud-responsable-exploitation-lyon",
        "suggest": "kappa-logistics-chef-projet-infrastructure-villeurbanne",
        "due_applied": "delta-industries-responsable-it-lyon",
        "top": ["vega-systemes-responsable-infrastructure-lyon", "altair-retail-it-operations-manager-lyon"],
        "relance_contact": "Sophie Martel",
    }


def scenario_bilan(radar):
    """Semaine écoulée : 26 octobre → 1er novembre 2026 ; référence : lundi 2 novembre 2026, 08:00 UTC."""
    base_config(radar)
    apps = []  # (key, company, title, applied_at, channel, cv, role_class, status, status_changed_at)

    def add(i, applied, channel, cv, rc, status, changed=None, src="LinkedIn"):
        key = "societe-%02d-responsable-it-lyon" % i
        extra = {"applied_at": applied, "channel": channel, "cv_version": cv, "role_class": rc, "source": src}
        if changed:
            extra["status_changed_at"] = changed
        write(radar, "offers/%s.json" % key, offer(key, "Société %02d" % i, "Responsable IT", "Lyon", "onsite", status, "A", 85, **extra))
        apps.append((key, applied, status, changed))

    # semaine écoulée (W44) : 3 candidatures
    add(1, "2026-10-27T08:00:00Z", "cooptation", "ops-v3", "principal", "entretien", "2026-10-30T10:00:00Z")
    add(2, "2026-10-28T08:00:00Z", "cooptation", "ops-v3", "principal", "refus", "2026-10-31T10:00:00Z")
    add(3, "2026-10-29T08:00:00Z", "site", "ops-v3", "secondaire", "postule")
    # semaine précédente (W43) : 2 candidatures
    add(4, "2026-10-20T08:00:00Z", "site", "ops-v2", "principal", "refus", "2026-10-24T10:00:00Z")
    add(5, "2026-10-22T08:00:00Z", "site", "ops-v2", "principal", "postule")
    # W42 (et avant) : 5 candidatures, dont une ancienne sans réponse depuis plus de 21 jours
    add(6, "2026-10-09T08:00:00Z", "site", "ops-v2", "principal", "postule")
    add(7, "2026-10-14T08:00:00Z", "site", "ops-v2", "secondaire", "entretien", "2026-10-21T10:00:00Z")
    add(8, "2026-10-15T08:00:00Z", "site", "ops-v1", "principal", "postule")
    add(9, "2026-10-16T08:00:00Z", "linkedin", "ops-v1", "adjacent", "postule")
    add(10, "2026-10-17T08:00:00Z", "linkedin", "ops-v1", "adjacent", "postule")
    # nouvelles offres de la semaine (first_seen dans W44) : 2 A, 1 B, 1 C
    for i, (tier, m) in enumerate([("A", 92), ("A", 88), ("B", 75), ("C", 64)], start=1):
        key = "nouvelle-%d-responsable-infra-lyon" % i
        write(radar, "offers/%s.json" % key, offer(key, "Nouvelle %d" % i, "Responsable infra", "Lyon", "hybrid", "nouveau", tier, m,
                                                  first_seen="2026-10-%dT08:00:00Z" % (27 + i - 1)))
    # réseau : 4 messages dans la semaine, 1 réponse
    for i, (st, d) in enumerate([("contacte", "2026-10-27"), ("contacte", "2026-10-28"), ("repondu", "2026-10-29"), ("contacte", "2026-10-30")], start=1):
        write(radar, "contacts/contact-%d.json" % i, contact("contact-%d" % i, "Contact Numéro%d" % i, "Entreprise %d" % i, "A", st,
                                                             contact_date=d + "T09:00:00Z", relance_date="2026-11-0%d" % i, relance_count=0))
    # deux anciens bilans pour la comparaison
    write(radar, "reports/2026-W43.json", {"week": "2026-W43", "generated_at": "2026-10-26T08:00:00Z",
                                           "metrics": {"applications": 2, "network_messages": 3, "new_ab": 3, "interviews": 0, "offers": 0, "refusals": 1,
                                                       "replies": 1, "no_reply_21d": 0, "median_reply_days": 7, "escalation": False},
                                           "text": "## La semaine en chiffres\n- 2 candidatures sur 10."})
    return {
        "week": "2026-W44",
        "applications": 3, "interviews": 1, "offers": 0, "refusals": 1, "new_ab": 3, "network_messages": 4,
        "escalation": True,
        "applied_keys": [a[0] for a in apps],
    }


def scenario_no_radar(radar):
    # pas de radar du tout : on supprime le dossier
    shutil.rmtree(radar, ignore_errors=True)
    return {}


def scenario_cv(radar):
    base_config(radar)
    write(radar, "offers/lumen-data-responsable-cloud-kubernetes-lyon.json", offer(
        "lumen-data-responsable-cloud-kubernetes-lyon", "Lumen Data", "Responsable plateforme Cloud et Kubernetes", "Lyon", "hybrid", "a_postuler", "B", 74,
        required_skills="Kubernetes, Terraform, AWS, CI/CD, supervision, gestion d'équipe",
        ad_summary="Pilotage d'une équipe plateforme de 6 personnes, migration vers Kubernetes sur AWS, Terraform obligatoire, astreintes."))
    return {}


def scenario_debrief(radar):
    base_config(radar)
    write(radar, "offers/nova-cloud-responsable-exploitation-lyon.json", offer(
        "nova-cloud-responsable-exploitation-lyon", "Nova Cloud", "Responsable exploitation", "Lyon", "onsite", "entretien", "A", 92,
        applied_at="2026-10-20T08:00:00Z", channel="cooptation", cv_version="ops-v3", role_class="principal", contact_name="Léa Durand",
        stage="technique", interview_at="2026-11-03T08:00:00Z", status_changed_at="2026-10-28T09:00:00Z",
        next_action="préparer l'entretien technique", next_action_date="2026-11-02"))
    return {}


def scenario_refus(radar):
    info = scenario_today(radar)
    return info


def scenario_non_working(radar):
    return scenario_today(radar)


SCENARIOS = {
    "score": scenario_score, "injection": scenario_injection, "no_send": scenario_no_send, "applied": scenario_applied,
    "today": scenario_today, "bilan": scenario_bilan, "no_radar": scenario_no_radar, "cv": scenario_cv,
    "debrief": scenario_debrief, "refus": scenario_refus, "non_working": scenario_non_working,
}


def build(name, workdir):
    workdir = pathlib.Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    copy_agent(workdir)
    radar = workdir / "radar"
    radar.mkdir(exist_ok=True)
    info = SCENARIOS[name](radar)
    return info


def snapshot(radar):
    """Contenu de tous les fichiers du Radar : {chemin relatif: texte}."""
    radar = pathlib.Path(radar)
    return {str(p.relative_to(radar)): p.read_text(encoding="utf-8") for p in sorted(radar.rglob("*")) if p.is_file()} if radar.exists() else {}
