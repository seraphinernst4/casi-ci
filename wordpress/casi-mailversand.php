<?php
/**
 * CASI -- Mails aus dem Mail-Baukasten ueber den IONOS-Server verschicken.
 *
 * Ablauf: Im Mail-Baukasten (ci.casinitiative.org/mail/) auf „Über CASI versenden“
 * klicken. Die fertige Mail (HTML und Textfassung) kommt per Formular hierher und
 * liegt als Entwurf beim angemeldeten Benutzer. Auf der Seite „Mailversand“ im
 * Backend: Absender waehlen, Empfaenger eintragen (sie bekommen die Mail per BCC,
 * niemand sieht die anderen), zuerst eine Testmail an sich selbst, dann senden.
 *
 * Absender:
 *  - info@casinitiative.org ueber das Postfach von WP Mail SMTP (wie die
 *    Bestaetigungsmail des Newsletters),
 *  - weitere Postfaecher (z. B. christoph.ernst@) mit eigenem IONOS-Zugang. Das
 *    Passwort traegt eine Administratorin oder ein Administrator auf der Seite
 *    selbst ein; es liegt verschluesselt in der Datenbank (Schluessel aus den
 *    WordPress-Salts).
 *
 * Nur fuer angemeldete Benutzer mit dem Recht „edit_posts“; Postfaecher
 * einrichten nur mit „manage_options“. Gesendet wird erst, wenn fuer genau diese
 * Mail und diesen Absender eine Testmail rausging.
 *
 * Quelle: Repo casi-ci, wordpress/casi-mailversand.php
 */
if (!defined('ABSPATH')) { exit; }

const CASI_MV_SEITE = 'casi-mailversand';
const CASI_MV_OPT = 'casi_mailversand';
const CASI_MV_LOG = 'casi_mailversand_log';
const CASI_MV_ENTWURF = '_casi_mail_entwurf';
const CASI_MV_BAUKASTEN = 'https://ci.casinitiative.org/mail/';
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

function casi_mv_pruefsumme($e, $von) { return md5(($e['html'] ?? '') . '|' . ($e['betreff'] ?? '') . '|' . $von); }

/* ---------- Entwurf aus dem Baukasten annehmen ---------- */

add_action('admin_post_casi_mail_entwurf', function () {
    if (!current_user_can('edit_posts')) { wp_die('Für den Mailversand fehlen dir die Rechte. Bitte bei der Administration melden.'); }
    $html = isset($_POST['html']) ? wp_unslash($_POST['html']) : '';
    if ($html === '' || strlen($html) > 2000000) { wp_die('Es kam keine Mail an. Bitte im Mail-Baukasten nochmals „Über CASI versenden“ klicken.'); }
    update_user_meta(get_current_user_id(), CASI_MV_ENTWURF, array(
        'html' => casi_mv_html($html),
        'text' => isset($_POST['text']) ? sanitize_textarea_field(wp_unslash($_POST['text'])) : '',
        'betreff' => isset($_POST['betreff']) ? sanitize_text_field(wp_unslash($_POST['betreff'])) : '',
        'zeit' => time(),
        'getestet' => '',
    ));
    wp_safe_redirect(admin_url('admin.php?page=' . CASI_MV_SEITE));
    exit;
});

add_action('admin_post_nopriv_casi_mail_entwurf', function () {
    wp_safe_redirect(wp_login_url(admin_url('admin.php?page=' . CASI_MV_SEITE . '&anmelden=1')));
    exit;
});

/* ---------- Testmail und Versand ---------- */

add_action('admin_post_casi_mail_senden', function () {
    if (!current_user_can('edit_posts')) { wp_die('Für den Mailversand fehlen dir die Rechte.'); }
    check_admin_referer('casi_mail_senden');
    $uid = get_current_user_id();
    $e = get_user_meta($uid, CASI_MV_ENTWURF, true);
    $zurueck = admin_url('admin.php?page=' . CASI_MV_SEITE);
    if (!is_array($e) || empty($e['html'])) { wp_safe_redirect($zurueck); exit; }

    $von = sanitize_email(wp_unslash($_POST['von'] ?? ''));
    $name = sanitize_text_field(wp_unslash($_POST['name'] ?? ''));
    $e['betreff'] = sanitize_text_field(wp_unslash($_POST['betreff'] ?? $e['betreff']));
    $e['von'] = $von;
    $e['name'] = $name;
    $e['empfaenger'] = sanitize_textarea_field(wp_unslash($_POST['empfaenger'] ?? ''));
    $art = ($_POST['art'] ?? '') === 'senden' ? 'senden' : 'test';
    $html = $e['html'];
    if (strpos($html, '<title>') !== false) { $html = preg_replace('#<title>.*?</title>#s', '<title>' . esc_html($e['betreff']) . '</title>', $html, 1); }

    if ($art === 'test') {
        $an = wp_get_current_user()->user_email;
        $ok = casi_mv_senden($von, $name, $an, array(), '[Test] ' . $e['betreff'], $html, $e['text'], $fehler);
        if ($ok) { $e['getestet'] = casi_mv_pruefsumme($e, $von); }
        update_user_meta($uid, CASI_MV_ENTWURF, $e);
        $msg = $ok ? array('ok', 'Testmail an ' . $an . ' ist raus. Bitte am Rechner und am Handy ansehen, dann senden.') : array('fehler', 'Testmail ging nicht raus: ' . $fehler);
    } else {
        list($gut, $schlecht) = casi_mv_empfaenger($e['empfaenger']);
        if ($e['getestet'] !== casi_mv_pruefsumme($e, $von)) {
            $msg = array('fehler', 'Bitte zuerst eine Testmail an dich schicken – für genau diese Mail und diesen Absender.');
        } elseif (!$gut) {
            $msg = array('fehler', 'Keine gültige Empfängeradresse eingetragen.');
        } elseif (count($gut) > CASI_MV_MAX) {
            $msg = array('fehler', 'Höchstens ' . CASI_MV_MAX . ' Empfänger je Versand – bitte aufteilen.');
        } else {
            @set_time_limit(300);
            $raus = 0; $fehlerliste = array();
            foreach (array_chunk($gut, CASI_MV_PAKET) as $i => $paket) {
                if ($i) { sleep(2); }
                if (casi_mv_senden($von, $name, $von, $paket, $e['betreff'], $html, $e['text'], $f)) { $raus += count($paket); }
                else { $fehlerliste[] = $f; }
            }
            $log = get_option(CASI_MV_LOG, array());
            array_unshift($log, array('zeit' => time(), 'wer' => wp_get_current_user()->display_name, 'von' => $von, 'betreff' => $e['betreff'], 'anzahl' => $raus, 'fehler' => count($gut) - $raus));
            update_option(CASI_MV_LOG, array_slice($log, 0, 50), false);
            if ($raus === count($gut)) {
                $e['gesendet'] = time();
                $msg = array('ok', 'Verschickt an ' . $raus . ' Empfänger (BCC).' . ($schlecht ? ' Übersprungen, weil keine gültige Adresse: ' . implode(', ', $schlecht) : ''));
            } else {
                $msg = array('fehler', 'Nur ' . $raus . ' von ' . count($gut) . ' verschickt. Fehler: ' . implode(' · ', array_unique($fehlerliste)));
            }
            update_user_meta($uid, CASI_MV_ENTWURF, $e);
        }
    }
    set_transient('casi_mv_meldung_' . $uid, $msg, 120);
    wp_safe_redirect($zurueck);
    exit;
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
    wp_safe_redirect(admin_url('admin.php?page=' . CASI_MV_SEITE . '#postfaecher'));
    exit;
});

/* ---------- Seite im Backend ---------- */

add_action('admin_menu', function () {
    add_menu_page('Mailversand', 'Mailversand', 'edit_posts', CASI_MV_SEITE, 'casi_mv_seite', 'dashicons-email-alt', 26);
});

function casi_mv_seite() {
    if (!current_user_can('edit_posts')) { return; }
    $uid = get_current_user_id();
    $e = get_user_meta($uid, CASI_MV_ENTWURF, true);
    $msg = get_transient('casi_mv_meldung_' . $uid);
    delete_transient('casi_mv_meldung_' . $uid);
    $abs = casi_mv_absender();
    $von = (is_array($e) && !empty($e['von']) && isset($abs[$e['von']])) ? $e['von'] : 'info@casinitiative.org';
    ?>
    <div class="wrap casi-mv">
    <style>
      .casi-mv { max-width: 1180px; }
      .casi-mv .raster { display: grid; grid-template-columns: minmax(0, 440px) minmax(0, 1fr); gap: 32px; align-items: start; margin-top: 16px; }
      @media (max-width: 1100px) { .casi-mv .raster { grid-template-columns: 1fr; } }
      .casi-mv label { display: block; font-size: 13px; margin: 14px 0 4px; }
      .casi-mv input[type=text], .casi-mv input[type=email], .casi-mv input[type=password], .casi-mv select, .casi-mv textarea { width: 100%; max-width: none; }
      .casi-mv textarea { min-height: 140px; font-family: inherit; }
      .casi-mv .box { background: #EEF2F1; border-radius: 10px; padding: 20px 24px; margin: 16px 0; }
      .casi-mv .vorschau { background: #EEF2F1; border-radius: 10px; padding: 16px; }
      .casi-mv .vorschau-kopf { display: flex; gap: 8px; margin: 0 0 10px; }
      .casi-mv iframe { display: block; width: 100%; height: 900px; border: 0; border-radius: 8px; background: #fff; margin: 0 auto; transition: width .2s; }
      .casi-mv .knoepfe { display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0 0; align-items: center; }
      .casi-mv .klein { font-size: 12px; color: #5F7471; }
      .casi-mv table.log td, .casi-mv table.log th { padding: 6px 12px 6px 0; text-align: left; font-size: 13px; }
    </style>
    <h1>Mailversand</h1>
    <p>Mails aus dem <a href="<?php echo esc_url(CASI_MV_BAUKASTEN); ?>" target="_blank" rel="noopener">Mail-Baukasten</a> direkt über den CASI-Server verschicken – so, wie sie gestaltet sind, auch auf dem Handy.</p>
    <?php if ($msg) : ?>
      <div class="notice notice-<?php echo $msg[0] === 'ok' ? 'success' : 'error'; ?>"><p><?php echo esc_html($msg[1]); ?></p></div>
    <?php endif; ?>

    <?php if (!is_array($e) || empty($e['html'])) : ?>
      <div class="box">
        <p><strong>Noch keine Mail da.</strong> Im <a href="<?php echo esc_url(CASI_MV_BAUKASTEN); ?>" target="_blank" rel="noopener">Mail-Baukasten</a> die Mail bauen und auf „Über CASI versenden“ klicken – sie erscheint dann hier.</p>
        <?php if (!empty($_GET['anmelden'])) : ?><p class="klein">Du warst vorher nicht angemeldet. Bitte im Baukasten nochmals auf „Über CASI versenden“ klicken.</p><?php endif; ?>
      </div>
    <?php else : ?>
      <div class="raster">
        <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
          <input type="hidden" name="action" value="casi_mail_senden">
          <?php wp_nonce_field('casi_mail_senden'); ?>
          <p class="klein">Übernommen aus dem Baukasten: <?php echo esc_html(wp_date('j. F Y, H:i', (int) $e['zeit'])); ?><?php if (!empty($e['gesendet'])) { echo ' · verschickt: ' . esc_html(wp_date('j. F Y, H:i', (int) $e['gesendet'])); } ?></p>

          <label for="mv-betreff">Betreff</label>
          <input type="text" id="mv-betreff" name="betreff" value="<?php echo esc_attr($e['betreff']); ?>" required>

          <label for="mv-von">Absender</label>
          <select id="mv-von" name="von">
            <?php foreach ($abs as $adr => $a) : ?>
              <option value="<?php echo esc_attr($adr); ?>" data-name="<?php echo esc_attr($a['name']); ?>" <?php selected($adr, $von); disabled(!$a['bereit']); ?>>
                <?php echo esc_html($adr . ($a['bereit'] ? '' : ' – noch einrichten')); ?>
              </option>
            <?php endforeach; ?>
          </select>

          <label for="mv-name">Absendername</label>
          <input type="text" id="mv-name" name="name" value="<?php echo esc_attr($e['name'] ?? $abs[$von]['name']); ?>">

          <label for="mv-an">Empfänger – eine Adresse pro Zeile oder durch Komma getrennt</label>
          <textarea id="mv-an" name="empfaenger" placeholder="name@beispiel.org"><?php echo esc_textarea($e['empfaenger'] ?? ''); ?></textarea>
          <p class="klein"><span id="mv-zahl">0</span> Adressen · Alle bekommen die Mail per BCC, niemand sieht die anderen. Höchstens <?php echo (int) CASI_MV_MAX; ?> je Versand.</p>

          <div class="knoepfe">
            <button type="submit" name="art" value="test" class="button">Testmail an mich</button>
            <button type="submit" name="art" value="senden" class="button button-primary" id="mv-senden">Senden</button>
          </div>
          <p class="klein">Senden geht erst, wenn für genau diese Mail und diesen Absender eine Testmail an dich rausging (<?php echo esc_html(wp_get_current_user()->user_email); ?>).</p>
          <p class="klein"><a href="<?php echo esc_url(CASI_MV_BAUKASTEN); ?>" target="_blank" rel="noopener">Mail im Baukasten ändern</a> – danach dort nochmals „Über CASI versenden“.</p>
        </form>

        <div class="vorschau">
          <div class="vorschau-kopf">
            <button type="button" class="button" data-breite="100%">Rechner</button>
            <button type="button" class="button" data-breite="390px">Handy</button>
          </div>
          <iframe id="mv-vorschau" sandbox="" title="Vorschau der Mail" srcdoc="<?php echo esc_attr($e['html']); ?>"></iframe>
        </div>
      </div>
      <script>
      (function () {
        var an = document.getElementById('mv-an'), zahl = document.getElementById('mv-zahl');
        var zaehle = function () { var t = an.value.split(/[\s,;]+/).filter(function (x) { return /@/.test(x); }); zahl.textContent = t.length; };
        an.addEventListener('input', zaehle); zaehle();
        var von = document.getElementById('mv-von'), name = document.getElementById('mv-name');
        von.addEventListener('change', function () { name.value = von.options[von.selectedIndex].getAttribute('data-name') || ''; });
        document.getElementById('mv-senden').addEventListener('click', function (ev) {
          if (!window.confirm('Jetzt an ' + zahl.textContent + ' Empfänger senden? Das lässt sich nicht zurückholen.')) { ev.preventDefault(); }
        });
        [].forEach.call(document.querySelectorAll('[data-breite]'), function (b) {
          b.addEventListener('click', function () { document.getElementById('mv-vorschau').style.width = b.getAttribute('data-breite'); });
        });
      })();
      </script>
    <?php endif; ?>

    <?php if (current_user_can('manage_options')) : ?>
      <h2 id="postfaecher" style="margin-top:40px;">Absender-Postfächer</h2>
      <p>info@casinitiative.org läuft über das Postfach der Website (WP Mail SMTP). Für jedes weitere Postfach hier einmal das IONOS-Passwort eintragen – es wird verschlüsselt gespeichert und beim Speichern direkt bei IONOS geprüft.</p>
      <?php foreach ($abs as $adr => $a) : if (!$a['eigen']) { continue; } ?>
        <form class="box" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
          <input type="hidden" name="action" value="casi_mail_postfach">
          <input type="hidden" name="adresse" value="<?php echo esc_attr($adr); ?>">
          <?php wp_nonce_field('casi_mail_postfach'); ?>
          <strong><?php echo esc_html($adr); ?></strong> – <?php echo $a['bereit'] ? 'eingerichtet' : 'noch kein Passwort'; ?>
          <label>Name</label><input type="text" name="name" value="<?php echo esc_attr($a['name']); ?>">
          <label>IONOS-Passwort <?php echo $a['bereit'] ? '(leer lassen = unverändert)' : ''; ?></label><input type="password" name="passwort" autocomplete="new-password">
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
    <?php endif; ?>
    </div>
    <?php
}
