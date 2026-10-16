<?php
/**
 * CASI -- Werkzeuge im Backend: Kachel-Baukasten und die Uebersicht auf dem Dashboard.
 *
 * Kachel-Baukasten: Menue „Kachel-Baukasten“, die Seite zeigt den Baukasten
 * (casi-kachelbaukasten.html im Sandbox-Ordner) als eigenes Dokument in voller
 * Hoehe. Vorausgefuellte Links von Claude: ...admin.php?page=casi-kacheln&k=<Daten>.
 *
 * Dashboard-Kasten „CASI-Werkzeuge“ (ganz oben): Connector fuer Claude einrichten,
 * die beiden Baukaesten, alle Vorlagen zum Herunterladen. Die Liste der Vorlagen
 * kommt live vom Connector (ci.casinitiative.org/vorlagen/<Wort>), eine Stunde
 * zwischengespeichert -- neue Vorlagen erscheinen also ohne Aenderung hier.
 *
 * ci.casinitiative.org bleibt nur die Technik-Adresse fuer Claude (Connector,
 * Downloads). Alles, was Menschen benutzen, liegt hier im Backend.
 *
 * Quelle: Repo casi-ci, wordpress/casi-werkzeuge.php und wordpress/casi-kachelbaukasten.html
 */
if (!defined('ABSPATH')) { exit; }

const CASI_WZ_KACHELN = 'casi-kacheln';
const CASI_WZ_CONNECTOR = 'https://ci.casinitiative.org/mcp/CasimirMonnem';
const CASI_WZ_VORLAGEN = 'https://ci.casinitiative.org/vorlagen/CasimirMonnem';

/* ---------- Kachel-Baukasten ---------- */

add_action('admin_post_casi_kachel_app', function () {
    if (!current_user_can('edit_posts')) { wp_die('Für den Kachel-Baukasten fehlen dir die Rechte. Bitte bei der Administration melden.'); }
    $h = (string) @file_get_contents(WP_CONTENT_DIR . '/novamira-sandbox/casi-kachelbaukasten.html');
    if ($h === '') { wp_die('Der Kachel-Baukasten fehlt (casi-kachelbaukasten.html).'); }
    nocache_headers();
    header('Content-Type: text/html; charset=utf-8');
    echo $h;
    exit;
});

add_action('admin_menu', function () {
    add_menu_page('Kachel-Baukasten', 'Kachel-Baukasten', 'edit_posts', CASI_WZ_KACHELN, 'casi_wz_kacheln', 'dashicons-format-image', 27);
});

add_action('admin_head', function () {
    if (($_GET['page'] ?? '') !== CASI_WZ_KACHELN) { return; }
    echo '<style>#wpbody-content{padding-bottom:0}#wpfooter{display:none}.casi-kb{margin:0 0 0 -20px}.casi-kb iframe{display:block;width:100%;height:calc(100vh - 32px);border:0;background:#fff}@media (max-width:782px){.casi-kb{margin-left:-10px}.casi-kb iframe{height:calc(100vh - 46px)}}</style>';
});

function casi_wz_kacheln() {
    if (!current_user_can('edit_posts')) { return; }
    $hash = (!empty($_GET['k']) && preg_match('/^[A-Za-z0-9._-]+$/', (string) $_GET['k'])) ? '#k=' . $_GET['k'] : '';
    echo '<div class="casi-kb"><iframe src="' . esc_url(admin_url('admin-post.php?action=casi_kachel_app')) . esc_attr($hash) . '" title="Kachel-Baukasten"></iframe></div>';
}

/* ---------- Dashboard: CASI-Werkzeuge ---------- */

add_action('wp_dashboard_setup', function () {
    if (!current_user_can('edit_posts')) { return; }
    wp_add_dashboard_widget('casi_werkzeuge', 'CASI-Werkzeuge', 'casi_wz_dashboard');
    // ganz nach oben
    global $wp_meta_boxes;
    $n = $wp_meta_boxes['dashboard']['normal']['core'] ?? array();
    if (isset($n['casi_werkzeuge'])) {
        $w = array('casi_werkzeuge' => $n['casi_werkzeuge']);
        unset($n['casi_werkzeuge']);
        $wp_meta_boxes['dashboard']['normal']['core'] = $w + $n;
    }
}, 1000);

function casi_wz_vorlagen() {
    $l = get_transient('casi_wz_vorlagen');
    if (is_array($l)) { return $l; }
    $r = wp_remote_get(CASI_WZ_VORLAGEN, array('timeout' => 8));
    $d = is_wp_error($r) ? null : json_decode(wp_remote_retrieve_body($r), true);
    $l = is_array($d['vorlagen'] ?? null) ? $d['vorlagen'] : array();
    set_transient('casi_wz_vorlagen', $l, $l ? HOUR_IN_SECONDS : 5 * MINUTE_IN_SECONDS);
    return $l;
}

function casi_wz_dashboard() {
    $gruppen = array(
        'slides' => 'Folien', 'document' => 'Dokumente, Briefe, Factsheets', 'poster' => 'Plakate',
        'email' => 'Mails (HTML)', 'farben' => 'Office-Design und Farben', 'fonts' => 'Schriften', 'graphics' => 'Symbole',
    );
    $nach = array();
    foreach (casi_wz_vorlagen() as $v) {
        if (empty($v['datei']) || empty($v['url'])) { continue; } // Baukaesten stehen oben
        $nach[$v['medium'] ?? ''][] = $v;
    }
    ?>
    <style>
      .casi-wz h3 { font-size: 14px; margin: 18px 0 6px; }
      .casi-wz h3:first-child { margin-top: 0; }
      .casi-wz p, .casi-wz li { font-size: 13px; line-height: 1.55; }
      .casi-wz ol { margin: 0 0 0 18px; }
      .casi-wz .werkzeuge { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 6px; }
      .casi-wz code { font-size: 12px; user-select: all; }
      .casi-wz .vorlagen { columns: 2 260px; column-gap: 24px; }
      .casi-wz .vorlagen div { break-inside: avoid; margin: 0 0 10px; }
      .casi-wz .vorlagen strong { display: block; font-size: 12px; margin: 0 0 2px; }
      .casi-wz .vorlagen a { display: block; font-size: 13px; }
    </style>
    <div class="casi-wz">
      <h3>Baukästen</h3>
      <div class="werkzeuge">
        <a class="button button-primary" href="<?php echo esc_url(admin_url('admin.php?page=casi-mailversand')); ?>">Mail-Baukasten</a>
        <a class="button" href="<?php echo esc_url(admin_url('admin.php?page=' . CASI_WZ_KACHELN)); ?>">Kachel-Baukasten</a>
      </div>
      <p>Mails und Signatur bauen und direkt über den CASI-Server verschicken · Bilder für LinkedIn.</p>

      <h3>Claude mit der CASI-Gestaltung</h3>
      <ol>
        <li>Auf claude.ai „Customize“ → „Connectors“ → „+ Add“ → „Add custom connector“.</li>
        <li>Name: CASI CI · Adresse: <code><?php echo esc_html(CASI_WZ_CONNECTOR); ?></code></li>
        <li>„No sign in“ wählen und „Add“ klicken; im Chat über „+“ → „Connectors“ einschalten.</li>
      </ol>
      <p>Dann gestaltet Claude Folien, Dokumente, Plakate, Grafiken und Mails nach der aktuellen CI und öffnet Mails und Kacheln fertig in den Baukästen. Die Adresse bitte nur intern weitergeben.</p>

      <h3>Vorlagen</h3>
      <?php if (!$nach) : ?>
        <p>Die Liste ist gerade nicht erreichbar – bitte später nochmals laden.</p>
      <?php else : ?>
        <div class="vorlagen">
        <?php foreach ($gruppen as $k => $titel) : if (empty($nach[$k])) { continue; } ?>
          <div><strong><?php echo esc_html($titel); ?></strong>
          <?php foreach ($nach[$k] as $v) : ?>
            <a href="<?php echo esc_url($v['url']); ?>"><?php echo esc_html($v['titel']); ?></a>
          <?php endforeach; ?>
          </div>
        <?php endforeach; ?>
        </div>
      <?php endif; ?>
    </div>
    <?php
}
