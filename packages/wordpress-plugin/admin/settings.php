<?php
/**
 * Settings Page
 */

if (!defined('WPINC')) {
    die;
}

/**
 * Add settings page to WordPress admin
 */
function iaindex_add_settings_page() {
    add_options_page(
        __('IAIndex Settings', 'iaindex'),
        __('IAIndex', 'iaindex'),
        'manage_options',
        'iaindex',
        'iaindex_render_settings_page'
    );
}
add_action('admin_menu', 'iaindex_add_settings_page');

/**
 * Render settings page
 */
function iaindex_render_settings_page() {
    if (!current_user_can('manage_options')) {
        return;
    }

    // Handle form submission
    if (isset($_POST['iaindex_settings_submit'])) {
        check_admin_referer('iaindex_settings_nonce');

        $settings = get_option('iaindex_settings');
        $settings['domain'] = sanitize_text_field($_POST['iaindex_domain']);
        $settings['api_key'] = sanitize_text_field($_POST['iaindex_api_key']);
        $settings['auto_generate'] = isset($_POST['iaindex_auto_generate']) ? true : false;

        update_option('iaindex_settings', $settings);

        echo '<div class="notice notice-success"><p>' . __('Settings saved successfully!', 'iaindex') . '</p></div>';
    }

    $settings = get_option('iaindex_settings');
    $domain = isset($settings['domain']) ? $settings['domain'] : get_site_url();
    $api_key = isset($settings['api_key']) ? $settings['api_key'] : '';
    $auto_generate = isset($settings['auto_generate']) ? $settings['auto_generate'] : true;
    $verified = isset($settings['verified']) ? $settings['verified'] : false;

    $generator = new IAIndex_Generator();
    $stats = $generator->get_stats();

    ?>
    <div class="wrap iaindex-settings">
        <h1><?php echo esc_html(get_admin_page_title()); ?></h1>

        <div class="iaindex-container">
            <div class="iaindex-main-content">
                <div class="card">
                    <h2><?php _e('Configuration', 'iaindex'); ?></h2>

                    <form method="post" action="">
                        <?php wp_nonce_field('iaindex_settings_nonce'); ?>

                        <table class="form-table">
                            <tr>
                                <th scope="row">
                                    <label for="iaindex_domain"><?php _e('Domain', 'iaindex'); ?></label>
                                </th>
                                <td>
                                    <input type="text"
                                           id="iaindex_domain"
                                           name="iaindex_domain"
                                           value="<?php echo esc_attr($domain); ?>"
                                           class="regular-text" />
                                    <p class="description">
                                        <?php _e('Your website domain (e.g., https://example.com)', 'iaindex'); ?>
                                    </p>
                                </td>
                            </tr>

                            <tr>
                                <th scope="row">
                                    <label for="iaindex_api_key"><?php _e('API Key', 'iaindex'); ?></label>
                                </th>
                                <td>
                                    <input type="password"
                                           id="iaindex_api_key"
                                           name="iaindex_api_key"
                                           value="<?php echo esc_attr($api_key); ?>"
                                           class="regular-text" />
                                    <p class="description">
                                        <?php _e('Your IAIndex API key for authentication', 'iaindex'); ?>
                                    </p>
                                </td>
                            </tr>

                            <tr>
                                <th scope="row">
                                    <?php _e('Auto-Generate Index', 'iaindex'); ?>
                                </th>
                                <td>
                                    <label>
                                        <input type="checkbox"
                                               id="iaindex_auto_generate"
                                               name="iaindex_auto_generate"
                                               value="1"
                                               <?php checked($auto_generate, true); ?> />
                                        <?php _e('Automatically regenerate index when posts are published', 'iaindex'); ?>
                                    </label>
                                </td>
                            </tr>
                        </table>

                        <?php submit_button(__('Save Settings', 'iaindex'), 'primary', 'iaindex_settings_submit'); ?>
                    </form>
                </div>

                <div class="card">
                    <h2><?php _e('Domain Verification', 'iaindex'); ?></h2>

                    <div class="iaindex-verification-status">
                        <?php if ($verified): ?>
                            <div class="notice notice-success inline">
                                <p>
                                    <span class="dashicons dashicons-yes-alt"></span>
                                    <?php _e('Domain verified successfully!', 'iaindex'); ?>
                                </p>
                            </div>
                        <?php else: ?>
                            <div class="notice notice-warning inline">
                                <p>
                                    <span class="dashicons dashicons-warning"></span>
                                    <?php _e('Domain not verified yet', 'iaindex'); ?>
                                </p>
                            </div>
                        <?php endif; ?>

                        <p>
                            <button type="button"
                                    class="button button-secondary"
                                    id="iaindex-verify-domain">
                                <?php _e('Verify Domain Now', 'iaindex'); ?>
                            </button>
                            <span class="spinner" style="float: none; margin: 0 10px;"></span>
                        </p>

                        <div id="iaindex-verification-result"></div>
                    </div>
                </div>

                <div class="card">
                    <h2><?php _e('Index Management', 'iaindex'); ?></h2>

                    <table class="form-table">
                        <tr>
                            <th scope="row"><?php _e('Index Status', 'iaindex'); ?></th>
                            <td>
                                <?php if ($stats['exists']): ?>
                                    <span class="iaindex-status-indicator iaindex-status-success">
                                        <span class="dashicons dashicons-yes-alt"></span>
                                        <?php _e('Index file exists', 'iaindex'); ?>
                                    </span>
                                <?php else: ?>
                                    <span class="iaindex-status-indicator iaindex-status-error">
                                        <span class="dashicons dashicons-dismiss"></span>
                                        <?php _e('No index file generated yet', 'iaindex'); ?>
                                    </span>
                                <?php endif; ?>
                            </td>
                        </tr>

                        <?php if ($stats['last_generated']): ?>
                        <tr>
                            <th scope="row"><?php _e('Last Generated', 'iaindex'); ?></th>
                            <td>
                                <?php echo esc_html(date_i18n(get_option('date_format') . ' ' . get_option('time_format'), $stats['last_generated'])); ?>
                            </td>
                        </tr>
                        <?php endif; ?>

                        <tr>
                            <th scope="row"><?php _e('Entries Count', 'iaindex'); ?></th>
                            <td><?php echo esc_html($stats['entries_count']); ?></td>
                        </tr>

                        <tr>
                            <th scope="row"><?php _e('Index URL', 'iaindex'); ?></th>
                            <td>
                                <code><?php echo esc_html($stats['index_url']); ?></code>
                                <?php if ($stats['exists']): ?>
                                    <a href="<?php echo esc_url($stats['index_url']); ?>"
                                       target="_blank"
                                       class="button button-small">
                                        <?php _e('View', 'iaindex'); ?>
                                    </a>
                                <?php endif; ?>
                            </td>
                        </tr>
                    </table>

                    <p>
                        <button type="button"
                                class="button button-primary"
                                id="iaindex-generate-index">
                            <?php _e('Generate Index Now', 'iaindex'); ?>
                        </button>
                        <span class="spinner" style="float: none; margin: 0 10px;"></span>
                    </p>

                    <div id="iaindex-generation-result"></div>
                </div>
            </div>

            <div class="iaindex-sidebar">
                <div class="card">
                    <h3><?php _e('About IAIndex', 'iaindex'); ?></h3>
                    <p><?php _e('IAIndex helps track and verify AI-generated content with blockchain-backed receipts.', 'iaindex'); ?></p>

                    <h4><?php _e('Features', 'iaindex'); ?></h4>
                    <ul>
                        <li><?php _e('Automatic index generation', 'iaindex'); ?></li>
                        <li><?php _e('Domain verification', 'iaindex'); ?></li>
                        <li><?php _e('Receipt tracking', 'iaindex'); ?></li>
                        <li><?php _e('API integration', 'iaindex'); ?></li>
                    </ul>

                    <p>
                        <a href="https://aiindex.io" target="_blank" class="button">
                            <?php _e('Learn More', 'iaindex'); ?>
                        </a>
                    </p>
                </div>

                <div class="card">
                    <h3><?php _e('Need Help?', 'iaindex'); ?></h3>
                    <p><?php _e('Check out our documentation or contact support.', 'iaindex'); ?></p>
                    <p>
                        <a href="https://docs.aiindex.io" target="_blank">
                            <?php _e('Documentation', 'iaindex'); ?>
                        </a>
                    </p>
                </div>
            </div>
        </div>
    </div>
    <?php
}

/**
 * AJAX handler for domain verification
 */
function iaindex_ajax_verify_domain() {
    check_ajax_referer('iaindex_nonce', 'nonce');

    if (!current_user_can('manage_options')) {
        wp_send_json_error(array('message' => 'Unauthorized'));
        return;
    }

    $settings = get_option('iaindex_settings');
    $domain = isset($settings['domain']) ? $settings['domain'] : get_site_url();

    $api_client = new IAIndex_API_Client();
    $result = $api_client->verify_domain($domain);

    if ($result['success']) {
        $settings['verified'] = true;
        $settings['verified_at'] = current_time('timestamp');
        update_option('iaindex_settings', $settings);

        wp_send_json_success(array(
            'message' => 'Domain verified successfully!',
            'data' => $result['data']
        ));
    } else {
        wp_send_json_error(array(
            'message' => isset($result['error']) ? $result['error'] : 'Verification failed',
            'data' => $result
        ));
    }
}
add_action('wp_ajax_iaindex_verify_domain', 'iaindex_ajax_verify_domain');

/**
 * AJAX handler for index generation
 */
function iaindex_ajax_generate_index() {
    check_ajax_referer('iaindex_nonce', 'nonce');

    if (!current_user_can('manage_options')) {
        wp_send_json_error(array('message' => 'Unauthorized'));
        return;
    }

    $generator = new IAIndex_Generator();
    $result = $generator->generate_index();

    if ($result['success']) {
        wp_send_json_success(array(
            'message' => 'Index generated successfully!',
            'data' => $result
        ));
    } else {
        wp_send_json_error(array(
            'message' => isset($result['error']) ? $result['error'] : 'Generation failed'
        ));
    }
}
add_action('wp_ajax_iaindex_generate_index', 'iaindex_ajax_generate_index');
