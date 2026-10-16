<?php
/**
 * CASI -- Mail-Baukasten im Backend: Mails bauen und ueber den IONOS-Server verschicken.
 *
 * Menue „Mail-Baukasten“: die Seite zeigt den Baukasten (casi-mailbaukasten.html im
 * selben Ordner) als eigenes Dokument in voller Hoehe. Dort Mail bauen, Absender
 * waehlen, Empfaenger eintragen (sie bekommen die Mail per BCC, niemand sieht die
 * anderen), zuerst eine Testmail an sich selbst, dann senden -- alles per AJAX.
 * Vorausgefuellte Links von Claude: ...admin.php?page=casi-mailversand&m=<Daten>
 * (Mail) bzw. &s=<Daten> (Signatur); ohne Anmeldung fuehrt WordPress erst zum Login.
 *
 * Absender:
 *  - info@casinitiative.org ueber das Postfach von WP Mail SMTP (wie die
 *    Bestaetigungsmail des Newsletters),
 *  - weitere Postfaecher (z. B. christoph.ernst@) mit eigenem IONOS-Zugang; das
 *    Passwort traegt die Administration unter „Postfaecher“ selbst ein, es liegt
 *    verschluesselt in der Datenbank (Schluessel aus den WordPress-Salts).
 *
 * Rechte: Baukasten und Versand „edit_posts“, Postfaecher „manage_options“.
 * Eine Testmail an sich selbst ist moeglich, aber keine Pflicht.
 *
 * Quelle: Repo casi-ci, wordpress/casi-mailversand.php und wordpress/casi-mailbaukasten.html
 */
if (!defined('ABSPATH')) { exit; }

const CASI_MV_SEITE = 'casi-mailversand';
const CASI_MV_OPT = 'casi_mailversand';
const CASI_MV_LOG = 'casi_mailversand_log';
const CASI_MV_GETESTET = '_casi_mail_getestet';
const CASI_MV_POSTFAECHER = 'casi-mail-postfaecher';
const CASI_MV_MAX = 300;   // Empfaenger je Versand
const CASI_MV_PAKET = 40;  // BCC-Empfaenger je Mail

/* ---------- Absender ---------- */

function casi_mv_absender() {
    $o = get_option(CASI_MV_OPT, array());
    $liste = array(
        'info@casinitiative.org' => array('name' => 'Carbon Accounting Standards Initiative', 'eigen' => false, 'bereit' => true),
    );
    $pf = isset($o['postfaecher']) && is_array($o['postfaecher']) ? $o['postfaecher'] : array();
    if (!isset($pf['christoph.ernst@casinitiative.org'])) {
        $pf['christoph.ernst@casinitiative.org'] = array('name' => 'Christoph Ernst', 'pass' => '');
    }
    foreach ($pf as $adr => $p) {
        $liste[$adr] = array('name' => (string) ($p['name'] ?? ''), 'eigen' => true, 'bereit' => !empty($p['pass']));
    }
    return $liste;
}

function casi_mv_schluessel() { return hash('sha256', wp_salt('auth') . '|casi-mailversand', true); }
function casi_mv_verschluesseln($t) {
    $iv = random_bytes(16);
    return base64_encode($iv . openssl_encrypt($t, 'aes-256-cbc', casi_mv_schluessel(), OPENSSL_RAW_DATA, $iv));
}
function casi_mv_entschluesseln($t) {
    $r = base64_decode((string) $t, true);
    if ($r === false || strlen($r) < 17) { return ''; }
    $k = openssl_decrypt(substr($r, 16), 'aes-256-cbc', casi_mv_schluessel(), OPENSSL_RAW_DATA, substr($r, 0, 16));
    return $k === false ? '' : $k;
}

/* ---------- Versand ---------- */

function casi_mv_senden($von, $name, $an, $bcc, $betreff, $html, $text, &$fehler) {
    $fehler = '';
    $abs = casi_mv_absender();
    if (empty($abs[$von]) || !$abs[$von]['bereit']) { $fehler = 'Dieser Absender ist noch nicht eingerichtet.'; return false; }
    $name = $name !== '' ? $name : $abs[$von]['name'];

    if (!$abs[$von]['eigen']) {
        // info@: ueber WP Mail SMTP, wie die Bestaetigungsmail
        $alt = function ($m) use ($text) { $m->AltBody = $text; };
        $err = function ($e) use (&$fehler) { $fehler = $e->get_error_message(); };
        add_action('phpmailer_init', $alt, 99);
        add_action('wp_mail_failed', $err);
        $h = array('Content-Type: text/html; charset=UTF-8', 'From: ' . $name . ' <' . $von . '>', 'Reply-To: ' . $name . ' <' . $von . '>');
        foreach ($bcc as $b) { $h[] = 'Bcc: ' . $b; }
        $ok = wp_mail($an, $betreff, $html, $h);
        remove_action('phpmailer_init', $alt, 99);
        remove_action('wp_mail_failed', $err);
        if (!$ok && $fehler === '') { $fehler = 'Der Mailserver hat die Mail nicht angenommen.'; }
        return $ok;
    }

    // eigenes Postfach: direkt ueber IONOS
    $o = get_option(CASI_MV_OPT, array());
    $pass = casi_mv_entschluesseln($o['postfaecher'][$von]['pass'] ?? '');
    if ($pass === '') { $fehler = 'Das Passwort dieses Postfachs fehlt oder ist nicht lesbar.'; return false; }
    require_once ABSPATH . WPINC . '/PHPMailer/PHPMailer.php';
    require_once ABSPATH . WPINC . '/PHPMailer/SMTP.php';
    require_once ABSPATH . WPINC . '/PHPMailer/Exception.php';
    $m = new PHPMailer\PHPMailer\PHPMailer(true);
    try {
        $m->isSMTP();
        $m->Host = 'smtp.ionos.de';
        $m->Port = 587;
        $m->SMTPSecure = 'tls';
        $m->SMTPAuth = true;
        $m->Username = $von;
        $m->Password = $pass;
        $m->CharSet = 'UTF-8';
        $m->Timeout = 20;
        $m->setFrom($von, $name);
        $m->addReplyTo($von, $name);
        $m->addAddress($an);
        foreach ($bcc as $b) { $m->addBCC($b); }
        $m->Subject = $betreff;
        $m->isHTML(true);
        $m->Body = $html;
        $m->AltBody = $text;
        $m->send();
        return true;
    } catch (\Exception $e) {
        $fehler = $m->ErrorInfo ?: $e->getMessage();
        return false;
    }
}

function casi_mv_empfaenger($roh) {
    $teile = preg_split('/[\s,;]+/', (string) $roh, -1, PREG_SPLIT_NO_EMPTY);
    $gut = array(); $schlecht = array();
    foreach ($teile as $t) {
        $t = trim($t, " \t<>\"'");
        if ($t === '') { continue; }
        if (is_email($t)) { $gut[strtolower($t)] = $t; } else { $schlecht[] = $t; }
    }
    return array(array_values($gut), $schlecht);
}

function casi_mv_html($html) {
    return preg_replace('#<script\b[^>]*>.*?</script>#is', '', (string) $html);
}

function casi_mv_pruefsumme($e) { return md5($e['html'] . '|' . $e['betreff'] . '|' . $e['von']); }

/* ---------- Baukasten ausliefern ---------- */

add_action('admin_post_casi_mail_app', function () {
    if (!current_user_can('edit_posts')) { wp_die('Für den Mail-Baukasten fehlen dir die Rechte. Bitte bei der Administration melden.'); }
    $h = (string) @file_get_contents(WP_CONTENT_DIR . '/novamira-sandbox/casi-mailbaukasten.html');
    if ($h === '') { wp_die('Der Mail-Baukasten fehlt (casi-mailbaukasten.html).'); }
    $abs = array();
    foreach (casi_mv_absender() as $adr => $a) { $abs[] = array('adresse' => $adr, 'name' => $a['name'], 'bereit' => $a['bereit']); }
    $cfg = array(
        'ajax' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('casi_mail_app'),
        'mail' => wp_get_current_user()->user_email,
        'absender' => $abs,
        'max' => CASI_MV_MAX,
        'postfaecher' => current_user_can('manage_options') ? admin_url('admin.php?page=' . CASI_MV_POSTFAECHER) : '',
    );
    $h = str_replace('<!--CASI_MV_KONFIG-->', '<script>window.CASI_MV = ' . wp_json_encode($cfg) . ';</script>', $h);
    nocache_headers();
    header('Content-Type: text/html; charset=utf-8');
    echo $h;
    exit;
});

/* ---------- Testmail und Versand (AJAX) ---------- */

function casi_mv_eingabe() {
    check_ajax_referer('casi_mail_app');
    if (!current_user_can('edit_posts')) { wp_send_json_error('Für den Mailversand fehlen dir die Rechte.', 403); }
    $html = casi_mv_html(wp_unslash($_POST['html'] ?? ''));
    if ($html === '' || strlen($html) > 2000000) { wp_send_json_error('Die Mail kam nicht vollständig an.'); }
    $e = array(
        'html' => $html,
        'text' => sanitize_textarea_field(wp_unslash($_POST['text'] ?? '')),
        'betreff' => sanitize_text_field(wp_unslash($_POST['betreff'] ?? '')),
        'von' => sanitize_email(wp_unslash($_POST['von'] ?? '')),
        'name' => sanitize_text_field(wp_unslash($_POST['name'] ?? '')),
    );
    if ($e['betreff'] === '') { wp_send_json_error('Bitte einen Betreff eintragen.'); }
    return $e;
}

add_action('wp_ajax_casi_mail_test', function () {
    $e = casi_mv_eingabe();
    $an = wp_get_current_user()->user_email;
    if (casi_mv_senden($e['von'], $e['name'], $an, array(), '[Test] ' . $e['betreff'], $e['html'], $e['text'], $fehler)) {
        update_user_meta(get_current_user_id(), CASI_MV_GETESTET, casi_mv_pruefsumme($e));
        wp_send_json_success(array('an' => $an));
    }
    wp_send_json_error($fehler);
});

add_action('wp_ajax_casi_mail_senden', function () {
    $e = casi_mv_eingabe();
    $uid = get_current_user_id();
    list($gut, $schlecht) = casi_mv_empfaenger(wp_unslash($_POST['empfaenger'] ?? ''));
    if (!$gut) { wp_send_json_error('Keine gültige Empfängeradresse eingetragen.'); }
    if (count($gut) > CASI_MV_MAX) { wp_send_json_error('Höchstens ' . CASI_MV_MAX . ' Empfänger je Versand – bitte aufteilen.'); }
    @set_time_limit(300);
    $raus = 0; $fehlerliste = array();
    foreach (array_chunk($gut, CASI_MV_PAKET) as $i => $paket) {
        if ($i) { sleep(2); }
        if (casi_mv_senden($e['von'], $e['name'], $e['von'], $paket, $e['betreff'], $e['html'], $e['text'], $f)) { $raus += count($paket); }
        else { $fehlerliste[] = $f; }
    }
    $log = get_option(CASI_MV_LOG, array());
    array_unshift($log, array('zeit' => time(), 'wer' => wp_get_current_user()->display_name, 'von' => $e['von'], 'betreff' => $e['betreff'], 'anzahl' => $raus, 'fehler' => count($gut) - $raus));
    update_option(CASI_MV_LOG, array_slice($log, 0, 50), false);
    delete_user_meta($uid, CASI_MV_GETESTET);
    if ($raus === count($gut)) {
        wp_send_json_success(array('meldung' => 'Verschickt an ' . $raus . ' Empfänger (BCC).' . ($schlecht ? ' Übersprungen, weil keine gültige Adresse: ' . implode(', ', $schlecht) : '')));
    }
    wp_send_json_error('Nur ' . $raus . ' von ' . count($gut) . ' verschickt. Fehler: ' . implode(' · ', array_unique($fehlerliste)));
});

/* ---------- Postfaecher einrichten (nur Administration) ---------- */

add_action('admin_post_casi_mail_postfach', function () {
    if (!current_user_can('manage_options')) { wp_die('Nur die Administration kann Postfächer einrichten.'); }
    check_admin_referer('casi_mail_postfach');
    $o = get_option(CASI_MV_OPT, array());
    $pf = isset($o['postfaecher']) && is_array($o['postfaecher']) ? $o['postfaecher'] : array();
    $adr = sanitize_email(wp_unslash($_POST['adresse'] ?? ''));
    $uid = get_current_user_id();
    if (!is_email($adr) || substr(strtolower($adr), -strlen('@casinitiative.org')) !== '@casinitiative.org') {
        set_transient('casi_mv_meldung_' . $uid, array('fehler', 'Nur Adressen @casinitiative.org.'), 120);
    } elseif (!empty($_POST['entfernen'])) {
        unset($pf[$adr]);
        set_transient('casi_mv_meldung_' . $uid, array('ok', 'Postfach ' . $adr . ' entfernt.'), 120);
    } else {
        $alt = $pf[$adr] ?? array('name' => '', 'pass' => '');
        $pass = (string) wp_unslash($_POST['passwort'] ?? '');
        $pf[$adr] = array(
            'name' => sanitize_text_field(wp_unslash($_POST['name'] ?? $alt['name'])),
            'pass' => $pass !== '' ? casi_mv_verschluesseln($pass) : $alt['pass'],
        );
        $msg = array('ok', 'Postfach ' . $adr . ' gespeichert.');
        if ($pass !== '') {
            require_once ABSPATH . WPINC . '/PHPMailer/PHPMailer.php';
            require_once ABSPATH . WPINC . '/PHPMailer/SMTP.php';
            require_once ABSPATH . WPINC . '/PHPMailer/Exception.php';
            $m = new PHPMailer\PHPMailer\PHPMailer(true);
            try {
                $m->isSMTP(); $m->Host = 'smtp.ionos.de'; $m->Port = 587; $m->SMTPSecure = 'tls'; $m->SMTPAuth = true;
                $m->Username = $adr; $m->Password = $pass; $m->Timeout = 15;
                $m->smtpConnect(); $m->smtpClose();
                $msg = array('ok', 'Postfach ' . $adr . ' gespeichert – die Anmeldung bei IONOS hat geklappt.');
            } catch (\Exception $ex) {
                $msg = array('fehler', 'Gespeichert, aber IONOS lehnt die Anmeldung ab: ' . ($m->ErrorInfo ?: $ex->getMessage()));
            }
        }
        set_transient('casi_mv_meldung_' . $uid, $msg, 120);
    }
    $o['postfaecher'] = $pf;
    update_option(CASI_MV_OPT, $o, false);
    wp_safe_redirect(admin_url('admin.php?page=' . CASI_MV_POSTFAECHER));
    exit;
});

/* ---------- Seiten im Backend ---------- */

add_action('admin_menu', function () {
    add_menu_page('Mail-Baukasten', 'Mail-Baukasten', 'edit_posts', CASI_MV_SEITE, 'casi_mv_seite', 'dashicons-email-alt', 26);
    add_submenu_page(CASI_MV_SEITE, 'Mail-Baukasten', 'Mail-Baukasten', 'edit_posts', CASI_MV_SEITE, 'casi_mv_seite');
    add_submenu_page(CASI_MV_SEITE, 'Absender-Postfächer', 'Postfächer', 'manage_options', CASI_MV_POSTFAECHER, 'casi_mv_postfaecher_seite');
});

add_action('admin_head', function () {
    if (($_GET['page'] ?? '') !== CASI_MV_SEITE) { return; }
    echo '<style>#wpbody-content{padding-bottom:0}#wpfooter{display:none}.casi-mb{margin:0 0 0 -20px}.casi-mb iframe{display:block;width:100%;height:calc(100vh - 32px);border:0;background:#fff}@media (max-width:782px){.casi-mb{margin-left:-10px}.casi-mb iframe{height:calc(100vh - 46px)}}</style>';
});

function casi_mv_seite() {
    if (!current_user_can('edit_posts')) { return; }
    // Vorausgefuellte Links: &m=<Daten> (Mail) oder &s=<Daten> (Signatur) wandern als #… in den Baukasten
    $hash = '';
    foreach (array('m', 's') as $k) {
        if (!empty($_GET[$k]) && preg_match('/^[A-Za-z0-9._-]+$/', (string) $_GET[$k])) { $hash = '#' . $k . '=' . $_GET[$k]; break; }
    }
    echo '<div class="casi-mb"><iframe src="' . esc_url(admin_url('admin-post.php?action=casi_mail_app')) . esc_attr($hash) . '" title="Mail-Baukasten"></iframe></div>';
}

function casi_mv_postfaecher_seite() {
    if (!current_user_can('manage_options')) { return; }
    $uid = get_current_user_id();
    $msg = get_transient('casi_mv_meldung_' . $uid);
    delete_transient('casi_mv_meldung_' . $uid);
    $abs = casi_mv_absender();
    ?>
    <div class="wrap casi-mv">
    <style>
      .casi-mv { max-width: 760px; }
      .casi-mv label { display: block; font-size: 13px; margin: 12px 0 4px; }
      .casi-mv input[type=text], .casi-mv input[type=email], .casi-mv input[type=password] { width: 100%; }
      .casi-mv .box { background: #EEF2F1; border-radius: 10px; padding: 20px 24px; margin: 16px 0; }
      .casi-mv .knoepfe { display: flex; gap: 12px; margin-top: 16px; align-items: center; }
      .casi-mv table.log td, .casi-mv table.log th { padding: 6px 12px 6px 0; text-align: left; font-size: 13px; vertical-align: top; }
    </style>
    <h1>Absender-Postfächer</h1>
    <?php if ($msg) : ?><div class="notice notice-<?php echo $msg[0] === 'ok' ? 'success' : 'error'; ?>"><p><?php echo esc_html($msg[1]); ?></p></div><?php endif; ?>
    <p>info@casinitiative.org läuft über das Postfach der Website (WP Mail SMTP). Für jedes weitere Postfach hier einmal das IONOS-Passwort eintragen – es wird verschlüsselt gespeichert und beim Speichern direkt bei IONOS geprüft. Danach steht das Postfach im <a href="<?php echo esc_url(admin_url('admin.php?page=' . CASI_MV_SEITE)); ?>">Mail-Baukasten</a> als Absender bereit.</p>
    <?php foreach ($abs as $adr => $a) : if (!$a['eigen']) { continue; } ?>
      <form class="box" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
        <input type="hidden" name="action" value="casi_mail_postfach">
        <input type="hidden" name="adresse" value="<?php echo esc_attr($adr); ?>">
        <?php wp_nonce_field('casi_mail_postfach'); ?>
        <strong><?php echo esc_html($adr); ?></strong> – <?php echo $a['bereit'] ? 'eingerichtet' : 'noch kein Passwort'; ?>
        <label>Name</label><input type="text" name="name" value="<?php echo esc_attr($a['name']); ?>">
        <label>IONOS-Passwort<?php echo $a['bereit'] ? ' (leer lassen = unverändert)' : ''; ?></label><input type="password" name="passwort" autocomplete="new-password">
        <div class="knoepfe"><button type="submit" class="button">Speichern und prüfen</button>
        <?php if ($adr !== 'christoph.ernst@casinitiative.org') : ?><button type="submit" name="entfernen" value="1" class="button-link">Entfernen</button><?php endif; ?></div>
      </form>
    <?php endforeach; ?>
    <form class="box" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
      <input type="hidden" name="action" value="casi_mail_postfach">
      <?php wp_nonce_field('casi_mail_postfach'); ?>
      <strong>Weiteres Postfach</strong>
      <label>Adresse (@casinitiative.org)</label><input type="email" name="adresse">
      <label>Name</label><input type="text" name="name">
      <label>IONOS-Passwort</label><input type="password" name="passwort" autocomplete="new-password">
      <div class="knoepfe"><button type="submit" class="button">Hinzufügen und prüfen</button></div>
    </form>
    <?php $log = get_option(CASI_MV_LOG, array()); if ($log) : ?>
      <h2>Zuletzt verschickt</h2>
      <table class="log"><tr><th>Wann</th><th>Wer</th><th>Absender</th><th>Betreff</th><th>Empfänger</th></tr>
      <?php foreach ($log as $l) : ?>
        <tr><td><?php echo esc_html(wp_date('j. n. Y, H:i', (int) $l['zeit'])); ?></td><td><?php echo esc_html($l['wer']); ?></td><td><?php echo esc_html($l['von']); ?></td><td><?php echo esc_html($l['betreff']); ?></td><td><?php echo (int) $l['anzahl'] . ($l['fehler'] ? ' (' . (int) $l['fehler'] . ' Fehler)' : ''); ?></td></tr>
      <?php endforeach; ?>
      </table>
    <?php endif; ?>
    </div>
    <?php
}
