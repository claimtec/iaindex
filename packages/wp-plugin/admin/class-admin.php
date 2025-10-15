<?php
/**
 * The admin-specific functionality of the plugin
 */
class AIIndex_Admin {

    private $plugin_name;
    private $version;

    public function __construct($plugin_name, $version) {
        $this->plugin_name = $plugin_name;
        $this->version = $version;
    }

    /**
     * Register the stylesheets for the admin area
     */
    public function enqueue_styles() {
        wp_enqueue_style(
            $this->plugin_name,
            AIINDEX_PLUGIN_URL . 'admin/assets/admin.css',
            array(),
            $this->version,
            'all'
        );
    }

    /**
     * Register the JavaScript for the admin area
     */
    public function enqueue_scripts() {
        wp_enqueue_script(
            $this->plugin_name,
            AIINDEX_PLUGIN_URL . 'admin/assets/admin.js',
            array('jquery'),
            $this->version,
            true
        );

        wp_localize_script($this->plugin_name, 'aiindex_admin', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('aiindex_admin_nonce'),
            'strings' => array(
                'generating' => __('Generating...', 'aiindex'),
                'verifying' => __('Verifying...', 'aiindex'),
                'success' => __('Success!', 'aiindex'),
                'error' => __('Error occurred', 'aiindex')
            )
        ));
    }

    /**
     * Add plugin admin menu
     */
    public function add_plugin_admin_menu() {
        add_menu_page(
            __('AIIndex', 'aiindex'),
            __('AIIndex', 'aiindex'),
            'manage_options',
            'aiindex',
            array($this, 'display_plugin_admin_page'),
            'dashicons-networking',
            80
        );

        add_submenu_page(
            'aiindex',
            __('Settings', 'aiindex'),
            __('Settings', 'aiindex'),
            'manage_options',
            'aiindex',
            array($this, 'display_plugin_admin_page')
        );

        add_submenu_page(
            'aiindex',
            __('Receipts', 'aiindex'),
            __('Receipts', 'aiindex'),
            'manage_options',
            'aiindex-receipts',
            array($this, 'display_receipts_page')
        );
    }

    /**
     * Display the main admin page
     */
    public function display_plugin_admin_page() {
        require_once AIINDEX_PLUGIN_DIR . 'admin/admin-settings.php';
    }

    /**
     * Display the receipts page
     */
    public function display_receipts_page() {
        require_once AIINDEX_PLUGIN_DIR . 'admin/admin-receipts.php';
    }

    /**
     * Register plugin settings
     */
    public function register_settings() {
        // General settings
        register_setting('aiindex_general', 'aiindex_enabled');
        register_setting('aiindex_general', 'aiindex_include_posts');
        register_setting('aiindex_general', 'aiindex_include_pages');
        register_setting('aiindex_general', 'aiindex_webhook_url');
        register_setting('aiindex_general', 'aiindex_sync_frequency');

        // Keys
        register_setting('aiindex_general', 'aiindex_public_key');
        register_setting('aiindex_general', 'aiindex_private_key');

        // Verification
        register_setting('aiindex_verification', 'aiindex_verification_status');
        register_setting('aiindex_verification', 'aiindex_verification_code');
        register_setting('aiindex_verification', 'aiindex_verified_at');
    }

    /**
     * Add meta box to posts/pages
     */
    public function add_meta_box() {
        $post_types = array('post', 'page');

        foreach ($post_types as $post_type) {
            add_meta_box(
                'aiindex_meta_box',
                __('AIIndex Settings', 'aiindex'),
                array($this, 'render_meta_box'),
                $post_type,
                'side',
                'default'
            );
        }
    }

    /**
     * Render the meta box
     */
    public function render_meta_box($post) {
        wp_nonce_field('aiindex_meta_box', 'aiindex_meta_box_nonce');

        $exclude = get_post_meta($post->ID, '_aiindex_exclude', true);
        ?>
        <p>
            <label>
                <input type="checkbox" name="aiindex_exclude" value="1" <?php checked($exclude, '1'); ?>>
                <?php _e('Exclude from AI Index', 'aiindex'); ?>
            </label>
        </p>
        <p class="description">
            <?php _e('Check this to exclude this content from the AI index file.', 'aiindex'); ?>
        </p>
        <?php
    }

    /**
     * Save meta box data
     */
    public function save_meta_box($post_id) {
        if (!isset($_POST['aiindex_meta_box_nonce'])) {
            return;
        }

        if (!wp_verify_nonce($_POST['aiindex_meta_box_nonce'], 'aiindex_meta_box')) {
            return;
        }

        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
            return;
        }

        if (!current_user_can('edit_post', $post_id)) {
            return;
        }

        $exclude = isset($_POST['aiindex_exclude']) ? '1' : '0';
        update_post_meta($post_id, '_aiindex_exclude', $exclude);
    }

    /**
     * Add dashboard widget
     */
    public function add_dashboard_widget() {
        wp_add_dashboard_widget(
            'aiindex_dashboard_widget',
            __('AIIndex Analytics', 'aiindex'),
            array($this, 'render_dashboard_widget')
        );
    }

    /**
     * Render dashboard widget
     */
    public function render_dashboard_widget() {
        $receipts = new AIIndex_Receipts();
        $analytics = $receipts->get_analytics();
        ?>
        <div class="aiindex-dashboard-widget">
            <div class="aiindex-stats">
                <div class="aiindex-stat">
                    <span class="aiindex-stat-value"><?php echo esc_html($analytics['total']); ?></span>
                    <span class="aiindex-stat-label"><?php _e('Total Receipts', 'aiindex'); ?></span>
                </div>
                <div class="aiindex-stat">
                    <span class="aiindex-stat-value"><?php echo esc_html($analytics['last_7_days']); ?></span>
                    <span class="aiindex-stat-label"><?php _e('Last 7 Days', 'aiindex'); ?></span>
                </div>
                <div class="aiindex-stat">
                    <span class="aiindex-stat-value"><?php echo esc_html($analytics['last_30_days']); ?></span>
                    <span class="aiindex-stat-label"><?php _e('Last 30 Days', 'aiindex'); ?></span>
                </div>
            </div>

            <?php if (!empty($analytics['by_indexer'])): ?>
            <div class="aiindex-indexers">
                <h4><?php _e('Top Indexers', 'aiindex'); ?></h4>
                <ul>
                    <?php foreach ($analytics['by_indexer'] as $indexer): ?>
                    <li>
                        <strong><?php echo esc_html($indexer['indexer_name']); ?></strong>
                        <span><?php echo esc_html($indexer['count']); ?> receipts</span>
                    </li>
                    <?php endforeach; ?>
                </ul>
            </div>
            <?php endif; ?>

            <p>
                <a href="<?php echo admin_url('admin.php?page=aiindex-receipts'); ?>" class="button">
                    <?php _e('View All Receipts', 'aiindex'); ?>
                </a>
            </p>
        </div>
        <?php
    }

    /**
     * AJAX: Generate keys
     */
    public function ajax_generate_keys() {
        check_ajax_referer('aiindex_admin_nonce', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('Permission denied', 'aiindex')));
        }

        $signer = new AIIndex_Signer();
        $keys = $signer->generate_keys();

        if (isset($keys['error'])) {
            wp_send_json_error(array('message' => $keys['error']));
        }

        update_option('aiindex_public_key', $keys['public_key']);
        update_option('aiindex_private_key', $keys['private_key']);

        wp_send_json_success(array(
            'public_key' => $keys['public_key'],
            'message' => __('Keys generated successfully', 'aiindex')
        ));
    }

    /**
     * AJAX: Verify domain
     */
    public function ajax_verify_domain() {
        check_ajax_referer('aiindex_admin_nonce', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('Permission denied', 'aiindex')));
        }

        // Check if ai-index.json is accessible
        $site_url = get_site_url();
        $index_url = $site_url . '/ai-index.json';

        $response = wp_remote_get($index_url);

        if (is_wp_error($response)) {
            wp_send_json_error(array('message' => __('Could not access ai-index.json', 'aiindex')));
        }

        $code = wp_remote_retrieve_response_code($response);

        if ($code === 200) {
            update_option('aiindex_verification_status', 'verified');
            update_option('aiindex_verified_at', current_time('mysql'));

            wp_send_json_success(array(
                'message' => __('Domain verified successfully', 'aiindex'),
                'verified_at' => current_time('c')
            ));
        } else {
            wp_send_json_error(array('message' => __('Verification failed', 'aiindex')));
        }
    }

    /**
     * AJAX: Export receipts
     */
    public function ajax_export_receipts() {
        check_ajax_referer('aiindex_admin_nonce', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_die(__('Permission denied', 'aiindex'));
        }

        $receipts = new AIIndex_Receipts();
        $csv = $receipts->export_to_csv();

        header('Content-Type: text/csv');
        header('Content-Disposition: attachment; filename="aiindex-receipts-' . date('Y-m-d') . '.csv"');
        echo $csv;
        exit;
    }

    /**
     * AJAX: Sync now
     */
    public function ajax_sync_now() {
        check_ajax_referer('aiindex_admin_nonce', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('Permission denied', 'aiindex')));
        }

        $webhook_url = get_option('aiindex_webhook_url');

        if (empty($webhook_url)) {
            wp_send_json_error(array('message' => __('Webhook URL not configured', 'aiindex')));
        }

        $generator = new AIIndex_Generator();
        $index_data = $generator->generate();

        $response = wp_remote_post($webhook_url, array(
            'headers' => array('Content-Type' => 'application/json'),
            'body' => json_encode($index_data),
            'timeout' => 30
        ));

        if (is_wp_error($response)) {
            wp_send_json_error(array('message' => $response->get_error_message()));
        }

        wp_send_json_success(array(
            'message' => __('Index synced successfully', 'aiindex')
        ));
    }
}
