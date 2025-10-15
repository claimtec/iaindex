<?php
/**
 * Fired during plugin activation
 */
class AIIndex_Activator {

    /**
     * Create database tables and set default options
     */
    public static function activate() {
        global $wpdb;

        $charset_collate = $wpdb->get_charset_collate();
        $table_name = $wpdb->prefix . 'aiindex_receipts';

        $sql = "CREATE TABLE $table_name (
            id bigint(20) NOT NULL AUTO_INCREMENT,
            receipt_id varchar(255) NOT NULL,
            content_url text NOT NULL,
            content_hash varchar(64) NOT NULL,
            indexed_at datetime NOT NULL,
            indexer_name varchar(255) DEFAULT NULL,
            indexer_url text DEFAULT NULL,
            verification_status varchar(50) DEFAULT 'pending',
            metadata longtext DEFAULT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY  (id),
            UNIQUE KEY receipt_id (receipt_id),
            KEY content_hash (content_hash),
            KEY indexed_at (indexed_at)
        ) $charset_collate;";

        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);

        // Set default options
        add_option('aiindex_version', AIINDEX_VERSION);
        add_option('aiindex_enabled', '1');
        add_option('aiindex_include_posts', '1');
        add_option('aiindex_include_pages', '1');
        add_option('aiindex_sync_frequency', 'hourly');
        add_option('aiindex_verification_status', 'pending');

        // Schedule cron job
        if (!wp_next_scheduled('aiindex_sync_cron')) {
            wp_schedule_event(time(), 'hourly', 'aiindex_sync_cron');
        }
    }
}
