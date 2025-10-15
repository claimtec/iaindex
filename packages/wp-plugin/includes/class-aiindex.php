<?php
/**
 * The core plugin class.
 *
 * This is used to define internationalization, admin-specific hooks, and
 * public-facing site hooks.
 */
class AIIndex {

    /**
     * The loader that's responsible for maintaining and registering all hooks.
     */
    protected $loader;

    /**
     * The unique identifier of this plugin.
     */
    protected $plugin_name;

    /**
     * The current version of the plugin.
     */
    protected $version;

    /**
     * Define the core functionality of the plugin.
     */
    public function __construct() {
        $this->version = AIINDEX_VERSION;
        $this->plugin_name = 'aiindex';

        $this->load_dependencies();
        $this->set_locale();
        $this->define_admin_hooks();
        $this->define_public_hooks();
        $this->define_api_hooks();
    }

    /**
     * Load the required dependencies for this plugin.
     */
    private function load_dependencies() {
        require_once AIINDEX_PLUGIN_DIR . 'includes/class-loader.php';
        require_once AIINDEX_PLUGIN_DIR . 'includes/class-i18n.php';
        require_once AIINDEX_PLUGIN_DIR . 'includes/class-generator.php';
        require_once AIINDEX_PLUGIN_DIR . 'includes/class-signer.php';
        require_once AIINDEX_PLUGIN_DIR . 'includes/class-receipts.php';
        require_once AIINDEX_PLUGIN_DIR . 'includes/class-api.php';
        require_once AIINDEX_PLUGIN_DIR . 'admin/class-admin.php';
        require_once AIINDEX_PLUGIN_DIR . 'public/badge-shortcode.php';

        $this->loader = new AIIndex_Loader();
    }

    /**
     * Define the locale for this plugin for internationalization.
     */
    private function set_locale() {
        $plugin_i18n = new AIIndex_i18n();
        $this->loader->add_action('plugins_loaded', $plugin_i18n, 'load_plugin_textdomain');
    }

    /**
     * Register all of the hooks related to the admin area functionality.
     */
    private function define_admin_hooks() {
        $plugin_admin = new AIIndex_Admin($this->get_plugin_name(), $this->get_version());

        $this->loader->add_action('admin_enqueue_scripts', $plugin_admin, 'enqueue_styles');
        $this->loader->add_action('admin_enqueue_scripts', $plugin_admin, 'enqueue_scripts');
        $this->loader->add_action('admin_menu', $plugin_admin, 'add_plugin_admin_menu');
        $this->loader->add_action('admin_init', $plugin_admin, 'register_settings');
        $this->loader->add_action('add_meta_boxes', $plugin_admin, 'add_meta_box');
        $this->loader->add_action('save_post', $plugin_admin, 'save_meta_box');
        $this->loader->add_action('wp_dashboard_setup', $plugin_admin, 'add_dashboard_widget');

        // AJAX handlers
        $this->loader->add_action('wp_ajax_aiindex_generate_keys', $plugin_admin, 'ajax_generate_keys');
        $this->loader->add_action('wp_ajax_aiindex_verify_domain', $plugin_admin, 'ajax_verify_domain');
        $this->loader->add_action('wp_ajax_aiindex_export_receipts', $plugin_admin, 'ajax_export_receipts');
        $this->loader->add_action('wp_ajax_aiindex_sync_now', $plugin_admin, 'ajax_sync_now');
    }

    /**
     * Register all of the hooks related to the public-facing functionality.
     */
    private function define_public_hooks() {
        // Register shortcodes
        add_shortcode('aiindex_badge', 'aiindex_badge_shortcode');

        // Add template redirect for ai-index.json
        $this->loader->add_action('template_redirect', $this, 'serve_ai_index_json');

        // Schedule cron job
        if (!wp_next_scheduled('aiindex_sync_cron')) {
            wp_schedule_event(time(), 'hourly', 'aiindex_sync_cron');
        }
        $this->loader->add_action('aiindex_sync_cron', $this, 'run_scheduled_sync');
    }

    /**
     * Register all of the hooks related to the REST API.
     */
    private function define_api_hooks() {
        $plugin_api = new AIIndex_API();
        $this->loader->add_action('rest_api_init', $plugin_api, 'register_routes');
    }

    /**
     * Serve the ai-index.json file
     */
    public function serve_ai_index_json() {
        if ($_SERVER['REQUEST_URI'] === '/ai-index.json') {
            $generator = new AIIndex_Generator();
            $index_data = $generator->generate();

            header('Content-Type: application/json');
            header('Access-Control-Allow-Origin: *');
            echo json_encode($index_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
            exit;
        }
    }

    /**
     * Run the scheduled sync task
     */
    public function run_scheduled_sync() {
        $webhook_url = get_option('aiindex_webhook_url');

        if (empty($webhook_url)) {
            return;
        }

        $generator = new AIIndex_Generator();
        $index_data = $generator->generate();

        // Send to webhook
        wp_remote_post($webhook_url, array(
            'headers' => array('Content-Type' => 'application/json'),
            'body' => json_encode($index_data),
            'timeout' => 30
        ));
    }

    /**
     * Run the loader to execute all of the hooks with WordPress.
     */
    public function run() {
        $this->loader->run();
    }

    /**
     * The name of the plugin used to uniquely identify it.
     */
    public function get_plugin_name() {
        return $this->plugin_name;
    }

    /**
     * Retrieve the version number of the plugin.
     */
    public function get_version() {
        return $this->version;
    }
}
