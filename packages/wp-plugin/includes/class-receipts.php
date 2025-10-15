<?php
/**
 * Manage indexing receipts
 */
class AIIndex_Receipts {

    /**
     * Save a receipt to the database
     */
    public function save_receipt($receipt_data) {
        global $wpdb;

        $table_name = $wpdb->prefix . 'aiindex_receipts';

        $data = array(
            'receipt_id' => sanitize_text_field($receipt_data['receiptId']),
            'content_url' => esc_url_raw($receipt_data['contentUrl']),
            'content_hash' => sanitize_text_field($receipt_data['contentHash']),
            'indexed_at' => sanitize_text_field($receipt_data['indexedAt']),
            'indexer_name' => isset($receipt_data['indexer']['name']) ? sanitize_text_field($receipt_data['indexer']['name']) : null,
            'indexer_url' => isset($receipt_data['indexer']['url']) ? esc_url_raw($receipt_data['indexer']['url']) : null,
            'verification_status' => 'verified',
            'metadata' => json_encode($receipt_data)
        );

        $format = array('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');

        // Check if receipt already exists
        $existing = $wpdb->get_var($wpdb->prepare(
            "SELECT id FROM $table_name WHERE receipt_id = %s",
            $data['receipt_id']
        ));

        if ($existing) {
            $wpdb->update(
                $table_name,
                $data,
                array('receipt_id' => $data['receipt_id']),
                $format,
                array('%s')
            );
            return $existing;
        } else {
            $wpdb->insert($table_name, $data, $format);
            return $wpdb->insert_id;
        }
    }

    /**
     * Get all receipts
     */
    public function get_receipts($limit = 100, $offset = 0) {
        global $wpdb;

        $table_name = $wpdb->prefix . 'aiindex_receipts';

        $results = $wpdb->get_results($wpdb->prepare(
            "SELECT * FROM $table_name ORDER BY indexed_at DESC LIMIT %d OFFSET %d",
            $limit,
            $offset
        ), ARRAY_A);

        return $results;
    }

    /**
     * Get receipt count
     */
    public function get_receipt_count() {
        global $wpdb;

        $table_name = $wpdb->prefix . 'aiindex_receipts';

        return $wpdb->get_var("SELECT COUNT(*) FROM $table_name");
    }

    /**
     * Get receipts by date range
     */
    public function get_receipts_by_date($start_date, $end_date) {
        global $wpdb;

        $table_name = $wpdb->prefix . 'aiindex_receipts';

        return $wpdb->get_results($wpdb->prepare(
            "SELECT * FROM $table_name WHERE indexed_at BETWEEN %s AND %s ORDER BY indexed_at DESC",
            $start_date,
            $end_date
        ), ARRAY_A);
    }

    /**
     * Get analytics data
     */
    public function get_analytics() {
        global $wpdb;

        $table_name = $wpdb->prefix . 'aiindex_receipts';

        $total = $wpdb->get_var("SELECT COUNT(*) FROM $table_name");

        $last_7_days = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM $table_name WHERE indexed_at >= %s",
            date('Y-m-d H:i:s', strtotime('-7 days'))
        ));

        $last_30_days = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM $table_name WHERE indexed_at >= %s",
            date('Y-m-d H:i:s', strtotime('-30 days'))
        ));

        $by_indexer = $wpdb->get_results(
            "SELECT indexer_name, COUNT(*) as count FROM $table_name
             WHERE indexer_name IS NOT NULL
             GROUP BY indexer_name
             ORDER BY count DESC
             LIMIT 10",
            ARRAY_A
        );

        return array(
            'total' => intval($total),
            'last_7_days' => intval($last_7_days),
            'last_30_days' => intval($last_30_days),
            'by_indexer' => $by_indexer
        );
    }

    /**
     * Export receipts to CSV
     */
    public function export_to_csv() {
        $receipts = $this->get_receipts(10000);

        $csv = "Receipt ID,Content URL,Content Hash,Indexed At,Indexer Name,Indexer URL,Status\n";

        foreach ($receipts as $receipt) {
            $csv .= sprintf(
                '"%s","%s","%s","%s","%s","%s","%s"' . "\n",
                $receipt['receipt_id'],
                $receipt['content_url'],
                $receipt['content_hash'],
                $receipt['indexed_at'],
                $receipt['indexer_name'],
                $receipt['indexer_url'],
                $receipt['verification_status']
            );
        }

        return $csv;
    }

    /**
     * Delete old receipts
     */
    public function cleanup_old_receipts($days = 90) {
        global $wpdb;

        $table_name = $wpdb->prefix . 'aiindex_receipts';

        $wpdb->query($wpdb->prepare(
            "DELETE FROM $table_name WHERE indexed_at < %s",
            date('Y-m-d H:i:s', strtotime("-$days days"))
        ));
    }
}
