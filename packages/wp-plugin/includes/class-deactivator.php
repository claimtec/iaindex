<?php
/**
 * Fired during plugin deactivation
 */
class AIIndex_Deactivator {

    /**
     * Clean up scheduled tasks
     */
    public static function deactivate() {
        // Clear scheduled cron job
        $timestamp = wp_next_scheduled('aiindex_sync_cron');
        if ($timestamp) {
            wp_unschedule_event($timestamp, 'aiindex_sync_cron');
        }
    }
}
