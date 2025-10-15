<?php
/**
 * REST API endpoints for AIIndex
 */
class AIIndex_API {

    /**
     * Register REST API routes
     */
    public function register_routes() {
        register_rest_route('aiindex/v1', '/receipt', array(
            'methods' => 'POST',
            'callback' => array($this, 'receive_receipt'),
            'permission_callback' => '__return_true',
            'args' => array(
                'receiptId' => array(
                    'required' => true,
                    'type' => 'string'
                ),
                'contentUrl' => array(
                    'required' => true,
                    'type' => 'string'
                ),
                'contentHash' => array(
                    'required' => true,
                    'type' => 'string'
                ),
                'indexedAt' => array(
                    'required' => true,
                    'type' => 'string'
                )
            )
        ));

        register_rest_route('aiindex/v1', '/receipts', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_receipts'),
            'permission_callback' => array($this, 'check_admin_permission')
        ));

        register_rest_route('aiindex/v1', '/index', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_index'),
            'permission_callback' => '__return_true'
        ));
    }

    /**
     * Receive and store a receipt
     */
    public function receive_receipt($request) {
        $receipt_data = $request->get_params();

        // Validate receipt data
        if (!$this->validate_receipt($receipt_data)) {
            return new WP_Error(
                'invalid_receipt',
                __('Invalid receipt data', 'aiindex'),
                array('status' => 400)
            );
        }

        // Save receipt
        $receipts = new AIIndex_Receipts();
        $receipt_id = $receipts->save_receipt($receipt_data);

        if ($receipt_id) {
            return new WP_REST_Response(array(
                'success' => true,
                'message' => __('Receipt saved successfully', 'aiindex'),
                'id' => $receipt_id
            ), 200);
        } else {
            return new WP_Error(
                'save_failed',
                __('Failed to save receipt', 'aiindex'),
                array('status' => 500)
            );
        }
    }

    /**
     * Get receipts via API
     */
    public function get_receipts($request) {
        $receipts = new AIIndex_Receipts();

        $limit = $request->get_param('limit') ?: 100;
        $offset = $request->get_param('offset') ?: 0;

        $data = $receipts->get_receipts($limit, $offset);
        $total = $receipts->get_receipt_count();

        return new WP_REST_Response(array(
            'receipts' => $data,
            'total' => $total,
            'limit' => $limit,
            'offset' => $offset
        ), 200);
    }

    /**
     * Get the current index
     */
    public function get_index($request) {
        $generator = new AIIndex_Generator();
        $index = $generator->generate();

        return new WP_REST_Response($index, 200);
    }

    /**
     * Validate receipt data
     */
    private function validate_receipt($receipt_data) {
        $required_fields = array('receiptId', 'contentUrl', 'contentHash', 'indexedAt');

        foreach ($required_fields as $field) {
            if (empty($receipt_data[$field])) {
                return false;
            }
        }

        // Validate URL
        if (!filter_var($receipt_data['contentUrl'], FILTER_VALIDATE_URL)) {
            return false;
        }

        // Validate date format
        if (!strtotime($receipt_data['indexedAt'])) {
            return false;
        }

        return true;
    }

    /**
     * Check if user has admin permission
     */
    public function check_admin_permission() {
        return current_user_can('manage_options');
    }
}
