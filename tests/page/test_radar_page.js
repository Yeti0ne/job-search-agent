/* Test de la page Radar générique sur un profil FICTIF (Lyon, euro, français natif) avec un runtime Claude simulé.
   Usage : NODE_PATH=$(npm root -g) node test_generic.js <page.html> [fichier_termes_interdits] */
const { chromium } = require('playwright');
const fs = require('fs');
const html = require('path').resolve(process.argv[2]);
const termsFile = process.argv[3];
const mock = fs.readFileSync(__dirname + '/mock_runtime.js', 'utf8');
let failed = 0;
function ok(c, m) { console.log((c ? 'OK   ' : 'FAIL ') + m); if (!c) failed++; }
const iso = (d) => d.toISOString();
const now = new Date('2026-10-31T09:00:00Z');
const day = (n) => new Date(now.getTime() + n * 86400000);
const GRID = 'GRILLE match_pct v1-test. Total 100 = rôle 30 + séniorité 15 + langue 20 + zone et mode 20 + entreprise 7 + techno 8.\n' + 'Rôle : poste principal 27-30, secondaire 20-26, adjacent 14-19. Séniorité : niveau visé 13-15. Langue : français natif, rien à pénaliser. Zone : Lyon 20, Grenoble 12. Entreprise : nommée 5. Techno : 0-8 selon le recoupement.';
function offer(key, extra) { return Object.assign({ key, company: 'Société ' + key, title: 'Responsable exploitation IT', location: 'Lyon', mode: 'hybrid', source: 'LinkedIn', url: 'https://example.org/jobs/' + key, status: 'nouveau', tier: 'B', match_pct: 78, hebrew: 'non_requis', fit_note: 'Test.', first_seen: iso(day(-2)), last_seen: iso(day(-1)), repost_count: 0, origin: 'veille' }, extra || {}); }
const AD = 'Nous recherchons un responsable exploitation pour piloter supervision, gestion des incidents, supervision des astreintes et amélioration continue. Expérience en gestion des incidents, supervision et automatisation exigée. Gestion des incidents au quotidien, astreintes et amélioration continue des processus de supervision.';
const fx = {
  config: {
    profile: { country: 'France', timezone: 'Europe/Paris', work_week: ['lun', 'mar', 'mer', 'jeu', 'ven'], currency: 'EUR', local_language: { name: 'français', level: 'natif' }, target_roles: { main: ['Responsable exploitation IT'], secondary: ['Chef de projet infrastructure'], adjacent: ['Support niveau 3'] }, levels_accepted: ['senior'], exclusions: ['vente pure'], home_area: 'Lyon', job_sites: ['LinkedIn', 'Welcome to the Jungle', 'APEC', { name: 'Site maison', url: 'https://example.org/jobs' }], preferred_company_types: ['ETI'], weekly_target: 10, followup_pref: 'pas de relance avant 14 jours' },
    cv: { name: 'Camille Martin', contact: 'camille.martin@example.org · +33 6 12 34 56 78 · Lyon', facts: 'Camille Martin, responsable exploitation IT.\nExpérience : Responsable exploitation chez Exemple SA (2018-2026) : équipe de 8 personnes, disponibilité 99,9 %.\nCompétences : supervision, gestion des incidents, automatisation.\nFormation : Master informatique.\nLangues : français natif, anglais courant.', rules: 'CV en français, une page, ville seule dans la localisation.', language: 'français', max_words: 450 },
    match_grid: { version: 'v1-test', updated_at: iso(now), text: GRID, weights: { role: 30, seniority: 15, language: 20, zone: 20, company: 7, tech: 8 } }
  },
  offers: {
    a1: offer('a1', { description: AD }),
    a2: offer('a2', { tier: 'A', match_pct: 91 }),
    a3: offer('a3', { status: 'a_postuler' }),
    a4: offer('a4', { status: 'postule', applied_at: '2026-10-20', next_action: 'Vérifier une réponse (ce n\'est pas une relance)', next_action_date: '2026-10-30', suggested_status: 'entretien', suggested_note: 'Le recruteur propose un appel jeudi.', suggested_at: iso(day(0)) }),
    a5: offer('a5', { status: 'entretien', stage: 'technique', interview_at: '2026-11-01T14:00', applied_at: '2026-10-15' }),
    a6: offer('a6', { status: 'hebreu_avance' }),
    a7: offer('a7', { status: 'surqualifie' }),
    a8: offer('a8', { status: 'ignore', reject_reason: 'salaire' }),
    a9: offer('a9', { first_seen: '2026-10-30T23:30:00Z', title: 'Responsable nuit' }),
    a10: offer('a10', { status: 'postule', applied_at: '2026-10-10', channel: 'linkedin', cv_version: 'v1' })
  },
  contacts: { c1: { name: 'Jean Dupont', company: 'Société a2', title: 'DSI', priority: 'A', status: 'a_contacter' } },
  runs: {}, reports: {}
};
async function openCard(page, key) {
  const row = page.locator('article.row[data-id="' + key + '"]');
  if (!(await row.locator('h4').first().isVisible().catch(() => false))) { await row.locator('[data-toggle="' + key + '"]').first().click(); await page.waitForTimeout(250); }
  return row;
}
async function newPage(ctx, fixture, opts) {
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|net::ERR/.test(m.text())) errors.push('console: ' + m.text()); });
  await page.route(/^https?:\/\//, r => r.abort());
  await page.addInitScript('window.__FIXTURE__ = ' + JSON.stringify(fixture) + ';');
  if (opts && opts.init) await page.addInitScript(opts.init);
  await page.addInitScript('try { localStorage.clear(); } catch (e) {}');
  await page.addInitScript(mock);
  await page.goto('file://' + html);
  await page.waitForTimeout(700);
  page.__errors = errors;
  return page;
}
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 900 }, timezoneId: 'America/Los_Angeles', locale: 'fr-FR' });
  const page = await newPage(ctx, fx, { init: `
    window.__JSON_REPLY__ = function (p) {
      if (/Estime la fourchette/.test(p)) return { low: 42000, high: 52000, period: 'an', basis: 'Marché lyonnais, profil senior.' };
      if (/Il ajoute une annonce/.test(p)) return { company: 'Acme Lyon', title: 'Responsable exploitation', location: 'Lyon', mode: 'hybrid', hebrew: 'non_requis', scores: { role: 27, seniority: 13, hebrew: 20, zone: 19, company: 5, tech: 6 }, score_detail: 'rôle 27/30 (principal) · séniorité 13/15 · langue 20/20 · zone 19/20 · entreprise 5/7 · techno 6/8', fit_note: 'Poste principal à Lyon.' };
      return {};
    };
    window.__SAMPLE_TEXT__ = function (p) {
      if (/Tu rédiges le CV/.test(p)) return '# Camille Martin\\nResponsable exploitation IT | camille.martin@example.org | +33 6 12 34 56 78 | Lyon\\n## Profil\\nResponsable exploitation, gestion des incidents et supervision.\\n## Compétences\\n- Supervision, gestion des incidents, automatisation, astreintes\\n## Expérience\\n**Responsable exploitation** | Exemple SA, Lyon | 2018 - 2026\\n- Équipe de 8 personnes, disponibilité de 99,9 %, amélioration continue des processus\\n## Formation\\n- Master informatique\\n## Langues\\n- Français natif, anglais courant';
      return '## Section test\\n- Réponse simulée';
    };` });
  ok(page.__errors.length === 0, 'aucune erreur JS au chargement ' + JSON.stringify(page.__errors.slice(0, 3)));
  // --- réglages lus dans config/profile
  ok(await page.title() === 'Radar Emploi France', 'titre de la page : ' + await page.title());
  const sub = await page.locator('#subLine').innerText();
  ok(/Responsable exploitation IT/.test(sub) && /France/.test(sub), 'sous-titre issu du profil : ' + sub);
  const sites = await page.locator('#sites a').evaluateAll(a => a.map(x => x.getAttribute('href')));
  ok(sites.length === 4 && sites.some(h => /linkedin\.com\/jobs/.test(h)) && sites.some(h => /welcometothejungle/.test(h)) && sites.some(h => /apec\.fr/.test(h)) && sites.includes('https://example.org/jobs'), 'sites suivis construits depuis job_sites (' + sites.length + ')');
  ok(await page.locator('#fHebRow').isHidden(), 'filtre de langue locale masqué (français natif)');
  ok(await page.locator('#fTrip, #fHelp, #salcGo, #salcBox').count() === 0, 'ni filtre trajet, ni coup de main, ni calculateur de salaire');
  const bodyTxt = await page.locator('body').innerText();
  ok(!/Calculateur de salaire|Coup de main|Trop qualifié \d|Accréd/.test(bodyTxt), 'aucune tuile ou section réservée à un autre profil');
  // --- liste et statuts
  const rows = await page.locator('article.row').count();
  ok(rows >= 6, 'liste rendue (' + rows + ' lignes actives)');
  const st = await page.locator('article.row select[data-status]').first().evaluate(s => Array.from(s.options).map(o => o.value));
  ok(st.length === 9 && !st.includes('hebreu_avance') && !st.includes('surqualifie') && !st.includes('accred_defense'), 'les 9 statuts publics seulement : ' + st.join(','));
  await page.locator('#tabs [data-tab="archive"]').click(); await page.waitForTimeout(200);
  const archKeys = await page.locator('article.row').evaluateAll(r => r.map(x => x.getAttribute('data-id')));
  ok(['a6', 'a7', 'a8'].every(k => archKeys.includes(k)), 'anciens statuts ramenés dans l\'archive (« ignoré »)');
  await page.locator('#tabs [data-tab="all"]').click(); await page.waitForTimeout(200);
  // --- fuseau : a9 vu le 30/10 à 23:30 UTC = 31/10 00:30 à Paris, alors que le navigateur est à Los Angeles
  const daily = await page.locator('#daily').innerText();
  const i31 = daily.search(/31 octobre/i), i30 = daily.search(/30 octobre/i);
  const seg31 = i31 >= 0 ? daily.slice(i31, i30 > i31 ? i30 : undefined) : '';
  ok(i31 >= 0 && /Responsable nuit/.test(seg31), 'fuseau du profil appliqué (jour de première vue = 31 octobre à Paris) ' + JSON.stringify(daily.slice(0, 260)));
  // --- motif d'écartement
  await openCard(page, 'a2');
  await page.locator('article.row[data-id="a2"] select[data-status]').selectOption('ignore'); await page.waitForTimeout(300);
  let w = await page.evaluate(() => window.__store.offers.a2);
  ok(w.status === 'ignore' && w.status_changed_at, 'statut « ignoré » enregistré');
  await page.locator('#tabs [data-tab="archive"]').click(); await page.waitForTimeout(200);
  await openCard(page, 'a2');
  const rs = page.locator('article.row[data-id="a2"] select[data-field="reject_reason"]');
  ok(await rs.count() === 1, 'sélecteur « motif d\'écartement » présent sur une offre ignorée');
  await rs.selectOption('distance'); await page.waitForTimeout(300);
  w = await page.evaluate(() => window.__store.offers.a2);
  ok(w.reject_reason === 'distance', 'reject_reason enregistré');
  await page.locator('#tabs [data-tab="all"]').click(); await page.waitForTimeout(200);
  // --- ajout d'une annonce : prompt et document écrit
  await page.locator('#addBtn').click();
  await page.locator('#addUrl').fill('https://example.org/jobs/nouveau-poste');
  await page.locator('#addText').fill('Responsable exploitation à Lyon. Supervision, incidents. Hybride.');
  await page.locator('#addGo').click(); await page.waitForTimeout(700);
  const added = await page.evaluate(() => Object.values(window.__store.offers).filter(o => o.company === 'Acme Lyon')[0]);
  ok(added && added.match_pct === 90 && added.tier === 'A' && added.grid_version === 'v1-test' && added.location === 'Lyon' && added.hebrew === 'non_requis', 'annonce ajoutée avec la grille du Radar : ' + (added && added.match_pct + ' ' + added.tier + ' ' + added.grid_version));
  const addP = await page.evaluate(() => window.__samples.filter(s => /Il ajoute une annonce/.test(s.prompt)).pop().prompt);
  ok(/Camille Martin/.test(addP) && /GRILLE match_pct v1-test/.test(addP) && /Responsable exploitation IT/.test(addP) && /France/.test(addP), 'prompt d\'ajout : profil, cible et grille du Radar');
  // --- plan, estimation de salaire, CV
  const card = await openCard(page, 'a1');
  await card.locator('[data-act="ai-run"][data-kind="plan"]').click(); await page.waitForTimeout(500);
  const planP = await page.evaluate(() => window.__samples.filter(s => /plan de candidature/.test(s.prompt)).pop().prompt);
  ok(/Camille Martin/.test(planP) && /Exemple SA/.test(planP) && /ville seule/.test(planP), 'prompt du plan : faits du CV et règles du candidat');
  await card.locator('[data-act="salary"]').click(); await page.waitForTimeout(500);
  w = await page.evaluate(() => window.__store.offers.a1);
  ok(w.salary_est === true && w.salary_text === '≈ 42–52 kEUR brut/an', 'estimation de salaire dans la devise et l\'unité du profil : ' + w.salary_text);
  await card.locator('[data-act="cv"]').click(); await page.waitForTimeout(800);
  const cvP = await page.evaluate(() => window.__samples.filter(s => /Tu rédiges le CV/.test(s.prompt)).pop().prompt);
  ok(/Langue du CV : français/.test(cvP) && /camille\.martin@example\.org/.test(cvP) && /450 mots/.test(cvP) && /ANNONCE/.test(cvP), 'prompt du CV : langue, coordonnées, longueur et annonce');
  const ats = await page.locator('article.row[data-id="a1"] .ats').innerText().catch(() => '');
  ok(/Contrôle ATS/i.test(ats) && /Coordonnées/i.test(ats) && !/manquant/.test(ats), 'contrôle ATS générique : coordonnées trouvées ' + JSON.stringify(ats.slice(0, 400)));
  ok(/Mots-clés de l'annonce présents/.test(ats) && /(incidents|supervision)/.test(ats), 'mots-clés tirés de l\'annonce elle-même');
  // --- boucle après candidature
  await page.locator('#tabs [data-tab="suivi"]').click(); await page.waitForTimeout(200);
  const routine = await page.locator('#routine').innerText();
  ok(/Réponse repérée/.test(routine), 'routine : réponse repérée à confirmer');
  await page.locator('#routine [data-act="sug-ok"][data-oid="a4"]').click(); await page.waitForTimeout(300);
  w = await page.evaluate(() => window.__store.offers.a4);
  ok(w.status === 'entretien' && !w.suggested_status, 'confirmation : statut « entretien », suggestion effacée');
  const pick = page.locator('#routine [data-act="applied"]').first();
  const pk = await pick.getAttribute('data-oid');
  await pick.click(); await page.waitForTimeout(300);
  const sp = await page.evaluate(k => window.__store.offers[k], pk);
  const nd = new Date(sp.next_action_date + 'T12:00:00'), td = new Date(); td.setHours(12, 0, 0, 0);
  let n = 0, c = new Date(td); while (c < nd) { c.setDate(c.getDate() + 1); if ([1, 2, 3, 4, 5].includes(c.getDay())) n++; }
  ok(sp.status === 'postule' && n === 10, '« J\'ai postulé » : prochaine action à 10 jours ouvrés lundi-vendredi (' + n + ')');
  // --- réseau
  await page.locator('#viewsw [data-view="net"]').click(); await page.waitForTimeout(300);
  ok(/Jean Dupont/.test(await page.locator('#netList').innerText()), 'vue réseau : contact affiché');
  // --- aucun terme réservé à un autre profil dans la page, le texte affiché et les prompts
  if (termsFile) {
    const terms = fs.readFileSync(termsFile, 'utf8').split('\n').filter(l => l.trim() && !l.startsWith('#'));
    const visible = await page.evaluate(() => document.documentElement.innerText);
    const prompts = (await page.evaluate(() => window.__samples.map(s => s.prompt))).join('\n');
    const src = fs.readFileSync(html, 'utf8');
    const hit = [];
    for (const t of terms) { const re = new RegExp(t, 'i'); for (const [name, txt] of [['source', src], ['texte affiché', visible], ['prompts', prompts]]) { const m = re.exec(txt); if (m) hit.push(name + ' : ' + m[0]); } }
    ok(hit.length === 0, 'aucun terme réservé à un autre profil (source, texte affiché, prompts) ' + JSON.stringify(hit.slice(0, 5)));
  }
  ok(page.__errors.length === 0, 'aucune erreur JS pendant le parcours ' + JSON.stringify(page.__errors.slice(0, 3)));
  await page.locator('#viewsw [data-view="offers"]').click(); await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(200);
  await page.screenshot({ path: process.env.SHOT || '/tmp/shot_generic.png' });

  // --- profil sans CV enregistré : message clair, pas de prompt envoyé
  const fx2 = JSON.parse(JSON.stringify(fx)); delete fx2.config.cv; fx2.config.profile.local_language = { name: 'japonais', level: 'débutant' }; fx2.config.profile.timezone = 'Asia/Tokyo';
  const p2 = await newPage(ctx, fx2);
  ok(await p2.locator('#fHebRow').isVisible(), 'langue locale non native : filtre visible');
  ok(/Japonais non requis/.test(await p2.locator('#fHebLbl').innerText()), 'libellé du filtre : ' + await p2.locator('#fHebLbl').innerText());
  const c2 = await openCard(p2, 'a1');
  ok(await c2.locator('[data-act="ai-run"][data-kind="heb"]').count() === 1, 'section « langue locale d\'entretien » proposée');
  await c2.locator('[data-act="cv"]').click(); await p2.waitForTimeout(300);
  ok(/Profil de CV introuvable/.test(await p2.locator('#toast').innerText()) && await p2.evaluate(() => window.__samples.filter(s => /Tu rédiges le CV/.test(s.prompt)).length) === 0, 'sans config/cv : message clair, aucun appel à Claude');
  ok(p2.__errors.length === 0, 'profil sans CV : aucune erreur JS ' + JSON.stringify(p2.__errors.slice(0, 3)));

  // --- aucune configuration du tout (Radar neuf) et mode sans base
  const p3 = await newPage(ctx, { offers: { z1: offer('z1') } });
  ok(p3.__errors.length === 0 && await p3.locator('article.row').count() === 1, 'Radar neuf sans config : la page s\'affiche sans erreur');
  const p4 = await newPage(ctx, {}, { init: 'window.__NO_DB__ = true;' });
  ok(p4.__errors.length === 0, 'sans base : aucune erreur JS ' + JSON.stringify(p4.__errors.slice(0, 3)));
  await browser.close();
  console.log(failed ? ('ECHECS : ' + failed) : 'TOUS LES TESTS PASSENT');
  process.exit(failed ? 1 : 0);
})();
