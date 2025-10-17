<?php
/**
 * Dashboard Widget
 */

if (!defined('WPINC')) {
    die;
}

/**
 * Add dashboard widget
 */
function iaindex_add_dashboard_widget() {
    wp_add_dashboard_widget(
        'iaindex_dashboard_widget',
        __('IAIndex Status', 'iaindex'),
        'iaindex_render_dashboard_widget'
    );
}
add_action('wp_dashboard_setup', 'iaindex_add_dashboard_widget');

/**
 * Render dashboard widget
 */
function iaindex_render_dashboard_widget() {
    $settings = get_option('iaindex_settings');
    $verified = isset($settings['verified']) ? $settings['verified'] : false;

    $generator = new IAIndex_Generator();
    $stats = $generator->get_stats();

    $receipts_count = iaindex_get_receipts_count();

    ?>
    <div class="iaindex-dashboard-widget">
        <div class="iaindex-dashboard-stats">
            <div class="iaindex-stat-box">
                <div class="iaindex-stat-icon">
                    <?php if ($verified): ?>
                        <span class="dashicons dashicons-yes-alt" style="color: #46b450;"></span>
                    <?php else: ?>
                        <span class="dashicons dashicons-warning" style="color: #ffb900;"></span>
                    <?php endif; ?>
                </div>
                <div class="iaindex-stat-content">
                    <div class="iaindex-stat-label"><?php _e('Verification Status', 'iaindex'); ?></div>
                    <div class="iaindex-stat-value">
                        <?php echo $verified ? __('Verified', 'iaindex') : __('Not Verified', 'iaindex'); ?>
                    </div>
                </div>
            </div>

            <div class="iaindex-stat-box">
                <div class="iaindex-stat-icon">
                    <span class="dashicons dashicons-media-document" style="color: #0073aa;"></span>
                </div>
                <div class="iaindex-stat-content">
                    <div class="iaindex-stat-label"><?php _e('Index Entries', 'iaindex'); ?></div>
                    <div class="iaindex-stat-value"><?php echo esc_html($stats['entries_count']); ?></div>
                </div>
            </div>

            <div class="iaindex-stat-box">
                <div class="iaindex-stat-icon">
                    <span class="dashicons dashicons-tickets-alt" style="color: #826eb4;"></span>
                </div>
                <div class="iaindex-stat-content">
                    <div class="iaindex-stat-label"><?php _e('Receipts', 'iaindex'); ?></div>
                    <div class="iaindex-stat-value"><?php echo esc_html($receipts_count); ?></div>
                </div>
            </div>
        </div>

        <?php if ($stats['last_generated']): ?>
        <div class="iaindex-dashboard-info">
            <p>
                <strong><?php _e('Last Index Generation:', 'iaindex'); ?></strong>
                <?php echo esc_html(human_time_diff($stats['last_generated'], current_time('timestamp'))); ?> <?php _e('ago', 'iaindex'); ?>
            </p>
        </div>
        <?php endif; ?>

        <?php if (!$verified): ?>
        <div class="iaindex-dashboard-alert">
            <p>
                <span class="dashicons dashicons-info"></span>
                <?php _e('Your domain needs to be verified to use IAIndex features.', 'iaindex'); ?>
            </p>
        </div>
        <?php endif; ?>

        <div class="iaindex-dashboard-actions">
            <a href="<?php echo admin_url('options-general.php?page=iaindex'); ?>" class="button button-primary">
                <?php _e('Manage Settings', 'iaindex'); ?>
            </a>

            <?php if ($stats['exists']): ?>
            <a href="<?php echo esc_url($stats['index_url']); ?>" target="_blank" class="button">
                <?php _e('View Index', 'iaindex'); ?>
            </a>
            <?php endif; ?>

            <a href="<?php echo admin_url('edit.php?post_type=iaindex_receipt'); ?>" class="button">
                <?php _e('View Receipts', 'iaindex'); ?>
            </a>
        </div>
    </div>

    <style>
        .iaindex-dashboard-widget {
            margin: -12px -12px 0;
            padding: 12px;
        }

        .iaindex-dashboard-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }

        .iaindex-stat-box {
            display: flex;
            align-items: center;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 4px;
            gap: 12px;
        }

        .iaindex-stat-icon .dashicons {
            font-size: 32px;
            width: 32px;
            height: 32px;
        }

        .iaindex-stat-label {
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .iaindex-stat-value {
            font-size: 18px;
            font-weight: 600;
            color: #23282d;
        }

        .iaindex-dashboard-info {
            margin-bottom: 16px;
            padding: 12px;
            background: #e8f4f8;
            border-left: 3px solid #0073aa;
            border-radius: 3px;
        }

        .iaindex-dashboard-info p {
            margin: 0;
        }

        .iaindex-dashboard-alert {
            margin-bottom: 16px;
            padding: 12px;
            background: #fff8e5;
            border-left: 3px solid #ffb900;
            border-radius: 3px;
        }

        .iaindex-dashboard-alert p {
            margin: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .iaindex-dashboard-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
    </style>
    <?php
}

/**
 * Add receipts submenu to Tools menu
 */
function iaindex_add_receipts_menu() {
    add_submenu_page(
        'tools.php',
        __('IAIndex Receipts', 'iaindex'),
        __('IAIndex Receipts', 'iaindex'),
        'manage_options',
        'edit.php?post_type=iaindex_receipt'
    );
}
add_action('admin_menu', 'iaindex_add_receipts_menu');

/**
 * Customize receipts list columns
 */
function iaindex_receipts_columns($columns) {
    $new_columns = array(
        'cb' => $columns['cb'],
        'title' => __('Receipt ID', 'iaindex'),
        'content_url' => __('Content URL', 'iaindex'),
        'provider' => __('Provider', 'iaindex'),
        'timestamp' => __('Timestamp', 'iaindex'),
        'date' => __('Received', 'iaindex')
    );
    return $new_columns;
}
add_filter('manage_iaindex_receipt_posts_columns', 'iaindex_receipts_columns');

/**
 * Populate custom columns
 */
function iaindex_receipts_column_content($column, $post_id) {
    switch ($column) {
        case 'content_url':
            $url = get_post_meta($post_id, '_iaindex_content_url', true);
            if ($url) {
                echo '<a href="' . esc_url($url) . '" target="_blank">' . esc_html($url) . '</a>';
            }
            break;

        case 'provider':
            $provider = get_post_meta($post_id, '_iaindex_provider', true);
            echo $provider ? esc_html($provider) : '-';
            break;

        case 'timestamp':
            $timestamp = get_post_meta($post_id, '_iaindex_timestamp', true);
            if ($timestamp) {
                echo '<code>' . esc_html($timestamp) . '</code>';
            }
            break;
    }
}
add_action('manage_iaindex_receipt_posts_custom_column', 'iaindex_receipts_column_content', 10, 2);
