<?php
/**
 * Plugin Name: AIIndex for WordPress
 * Plugin URI: https://aiindex.dev
 * Description: Generate and manage AI index files for your WordPress site with verification and receipt tracking
 * Version: 1.0.0
 * Author: AIIndex
 * Author URI: https://aiindex.dev
 * License: MIT
 * Text Domain: aiindex
 * Domain Path: /languages
 */

// If this file is called directly, abort.
if (!defined('WPINC')) {
    die;
}

// Plugin version
define('AIINDEX_VERSION', '1.0.0');
define('AIINDEX_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('AIINDEX_PLUGIN_URL', plugin_dir_url(__FILE__));
define('AIINDEX_PLUGIN_BASENAME', plugin_basename(__FILE__));

/**
 * The code that runs during plugin activation.
 */
function activate_aiindex() {
    require_once AIINDEX_PLUGIN_DIR . 'includes/class-activator.php';
    AIIndex_Activator::activate();
}

/**
 * The code that runs during plugin deactivation.
 */
function deactivate_aiindex() {
    require_once AIINDEX_PLUGIN_DIR . 'includes/class-deactivator.php';
    AIIndex_Deactivator::deactivate();
}

register_activation_hook(__FILE__, 'activate_aiindex');
register_deactivation_hook(__FILE__, 'deactivate_aiindex');

/**
 * The core plugin class
 */
require AIINDEX_PLUGIN_DIR . 'includes/class-aiindex.php';

/**
 * Begins execution of the plugin.
 */
function run_aiindex() {
    $plugin = new AIIndex();
    $plugin->run();
}

run_aiindex();
