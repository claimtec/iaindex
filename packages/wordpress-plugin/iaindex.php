<?php
/**
 * Plugin Name: IAIndex Integration
 * Plugin URI: https://aiindex.io
 * Description: Integration with IAIndex for AI content tracking and receipts
 * Version: 1.0.0
 * Author: ClaimTec
 * Author URI: https://claimtec.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: iaindex
 * Requires at least: 6.0
 * Requires PHP: 7.4
 */

// If this file is called directly, abort.
if (!defined('WPINC')) {
    die;
}

// Define plugin constants
define('IAINDEX_VERSION', '1.0.0');
define('IAINDEX_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('IAINDEX_PLUGIN_URL', plugin_dir_url(__FILE__));
define('IAINDEX_API_BASE_URL', 'https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io');

// Include required files
require_once IAINDEX_PLUGIN_DIR . 'includes/api-client.php';
require_once IAINDEX_PLUGIN_DIR . 'includes/index-generator.php';
require_once IAINDEX_PLUGIN_DIR . 'includes/webhook.php';

// Admin files
if (is_admin()) {
    require_once IAINDEX_PLUGIN_DIR . 'admin/settings.php';
    require_once IAINDEX_PLUGIN_DIR . 'admin/dashboard.php';
}

/**
 * Activation hook
 */
function iaindex_activate() {
    // Create custom post type for receipts
    iaindex_register_receipt_post_type();

    // Flush rewrite rules
    flush_rewrite_rules();

    // Create uploads directory if needed
    $upload_dir = wp_upload_dir();
    $iaindex_dir = $upload_dir['basedir'] . '/iaindex';
    if (!file_exists($iaindex_dir)) {
        wp_mkdir_p($iaindex_dir);
    }

    // Set default options
    if (!get_option('iaindex_settings')) {
        add_option('iaindex_settings', array(
            'domain' => get_site_url(),
            'api_key' => '',
            'auto_generate' => true,
            'verified' => false
        ));
    }
}
register_activation_hook(__FILE__, 'iaindex_activate');

/**
 * Deactivation hook
 */
function iaindex_deactivate() {
    flush_rewrite_rules();
}
register_deactivation_hook(__FILE__, 'iaindex_deactivate');

/**
 * Register custom post type for receipts
 */
function iaindex_register_receipt_post_type() {
    $args = array(
        'public' => false,
        'show_ui' => true,
        'show_in_menu' => false,
        'capability_type' => 'post',
        'supports' => array('title', 'editor'),
        'labels' => array(
            'name' => __('IAIndex Receipts', 'iaindex'),
            'singular_name' => __('Receipt', 'iaindex'),
        ),
    );
    register_post_type('iaindex_receipt', $args);
}
add_action('init', 'iaindex_register_receipt_post_type');

/**
 * Enqueue admin scripts and styles
 */
function iaindex_enqueue_admin_assets($hook) {
    // Only load on our settings page
    if ($hook !== 'settings_page_iaindex') {
        return;
    }

    wp_enqueue_style(
        'iaindex-admin-css',
        IAINDEX_PLUGIN_URL . 'assets/css/admin.css',
        array(),
        IAINDEX_VERSION
    );

    wp_enqueue_script(
        'iaindex-admin-js',
        IAINDEX_PLUGIN_URL . 'assets/js/admin.js',
        array('jquery'),
        IAINDEX_VERSION,
        true
    );

    wp_localize_script('iaindex-admin-js', 'iaindexAjax', array(
        'ajaxurl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('iaindex_nonce')
    ));
}
add_action('admin_enqueue_scripts', 'iaindex_enqueue_admin_assets');

/**
 * Add settings link on plugins page
 */
function iaindex_add_settings_link($links) {
    $settings_link = '<a href="' . admin_url('options-general.php?page=iaindex') . '">' . __('Settings', 'iaindex') . '</a>';
    array_unshift($links, $settings_link);
    return $links;
}
add_filter('plugin_action_links_' . plugin_basename(__FILE__), 'iaindex_add_settings_link');

/**
 * Auto-generate index when post is published
 */
function iaindex_auto_generate_on_publish($ID, $post) {
    $settings = get_option('iaindex_settings');

    if (isset($settings['auto_generate']) && $settings['auto_generate']) {
        $generator = new IAIndex_Generator();
        $generator->generate_index();
    }
}
add_action('publish_post', 'iaindex_auto_generate_on_publish', 10, 2);

/**
 * Create .well-known redirect
 */
function iaindex_wellknown_redirect() {
    $request_uri = $_SERVER['REQUEST_URI'];

    if (strpos($request_uri, '/.well-known/iaindex.json') !== false) {
        $upload_dir = wp_upload_dir();
        $json_file = $upload_dir['basedir'] . '/iaindex/iaindex.json';

        if (file_exists($json_file)) {
            header('Content-Type: application/json');
            header('Access-Control-Allow-Origin: *');
            readfile($json_file);
            exit;
        } else {
            wp_die('IAIndex file not found. Please generate the index first.', 'Not Found', array('response' => 404));
        }
    }
}
add_action('init', 'iaindex_wellknown_redirect', 1);

/**
 * Add rewrite rule for .well-known
 */
function iaindex_rewrite_rules() {
    add_rewrite_rule(
        '^\.well-known/iaindex\.json$',
        'index.php?iaindex_wellknown=1',
        'top'
    );
}
add_action('init', 'iaindex_rewrite_rules');

/**
 * Add query var for .well-known
 */
function iaindex_query_vars($vars) {
    $vars[] = 'iaindex_wellknown';
    return $vars;
}
add_filter('query_vars', 'iaindex_query_vars');

/**
 * Handle .well-known template redirect
 */
function iaindex_template_redirect() {
    if (get_query_var('iaindex_wellknown')) {
        $upload_dir = wp_upload_dir();
        $json_file = $upload_dir['basedir'] . '/iaindex/iaindex.json';

        if (file_exists($json_file)) {
            header('Content-Type: application/json');
            header('Access-Control-Allow-Origin: *');
            readfile($json_file);
            exit;
        } else {
            wp_die('IAIndex file not found. Please generate the index first.', 'Not Found', array('response' => 404));
        }
    }
}
add_action('template_redirect', 'iaindex_template_redirect');
