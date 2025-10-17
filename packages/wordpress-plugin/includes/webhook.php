<?php
/**
 * IAIndex Webhook Handler
 */

if (!defined('WPINC')) {
    die;
}

/**
 * Register REST API endpoints
 */
function iaindex_register_rest_routes() {
    register_rest_route('iaindex/v1', '/receipt', array(
        'methods' => 'POST',
        'callback' => 'iaindex_handle_receipt_webhook',
        'permission_callback' => 'iaindex_verify_webhook_request'
    ));

    register_rest_route('iaindex/v1', '/receipts', array(
        'methods' => 'GET',
        'callback' => 'iaindex_get_receipts',
        'permission_callback' => function() {
            return current_user_can('manage_options');
        }
    ));
}
add_action('rest_api_init', 'iaindex_register_rest_routes');

/**
 * Verify webhook request
 */
function iaindex_verify_webhook_request($request) {
    // Get API key from settings
    $settings = get_option('iaindex_settings');
    $api_key = isset($settings['api_key']) ? $settings['api_key'] : '';

    // Check Authorization header
    $auth_header = $request->get_header('Authorization');

    if (empty($auth_header)) {
        return new WP_Error(
            'unauthorized',
            'Missing authorization header',
            array('status' => 401)
        );
    }

    // Extract Bearer token
    $token = str_replace('Bearer ', '', $auth_header);

    // Verify token matches API key
    if ($token !== $api_key) {
        return new WP_Error(
            'unauthorized',
            'Invalid API key',
            array('status' => 401)
        );
    }

    return true;
}

/**
 * Handle incoming receipt webhook
 */
function iaindex_handle_receipt_webhook($request) {
    $params = $request->get_json_params();

    if (empty($params)) {
        return new WP_Error(
            'invalid_request',
            'Invalid JSON payload',
            array('status' => 400)
        );
    }

    // Store receipt as custom post type
    $receipt_id = iaindex_store_receipt($params);

    if (is_wp_error($receipt_id)) {
        return new WP_Error(
            'storage_error',
            $receipt_id->get_error_message(),
            array('status' => 500)
        );
    }

    return new WP_REST_Response(array(
        'success' => true,
        'receipt_id' => $receipt_id,
        'message' => 'Receipt stored successfully'
    ), 200);
}

/**
 * Store receipt in database
 */
function iaindex_store_receipt($receipt_data) {
    $post_data = array(
        'post_type' => 'iaindex_receipt',
        'post_title' => 'Receipt: ' . (isset($receipt_data['receiptId']) ? $receipt_data['receiptId'] : uniqid()),
        'post_content' => json_encode($receipt_data, JSON_PRETTY_PRINT),
        'post_status' => 'publish'
    );

    $post_id = wp_insert_post($post_data);

    if (is_wp_error($post_id)) {
        return $post_id;
    }

    // Store receipt metadata
    if (isset($receipt_data['receiptId'])) {
        update_post_meta($post_id, '_iaindex_receipt_id', sanitize_text_field($receipt_data['receiptId']));
    }

    if (isset($receipt_data['contentUrl'])) {
        update_post_meta($post_id, '_iaindex_content_url', esc_url_raw($receipt_data['contentUrl']));
    }

    if (isset($receipt_data['timestamp'])) {
        update_post_meta($post_id, '_iaindex_timestamp', sanitize_text_field($receipt_data['timestamp']));
    }

    if (isset($receipt_data['provider'])) {
        update_post_meta($post_id, '_iaindex_provider', sanitize_text_field($receipt_data['provider']));
    }

    return $post_id;
}

/**
 * Get receipts via REST API
 */
function iaindex_get_receipts($request) {
    $limit = $request->get_param('limit') ?: 10;

    $args = array(
        'post_type' => 'iaindex_receipt',
        'posts_per_page' => intval($limit),
        'orderby' => 'date',
        'order' => 'DESC'
    );

    $receipts = get_posts($args);
    $result = array();

    foreach ($receipts as $receipt) {
        $receipt_data = json_decode($receipt->post_content, true);
        $result[] = array(
            'id' => $receipt->ID,
            'date' => $receipt->post_date,
            'receipt_id' => get_post_meta($receipt->ID, '_iaindex_receipt_id', true),
            'content_url' => get_post_meta($receipt->ID, '_iaindex_content_url', true),
            'timestamp' => get_post_meta($receipt->ID, '_iaindex_timestamp', true),
            'provider' => get_post_meta($receipt->ID, '_iaindex_provider', true),
            'data' => $receipt_data
        );
    }

    return new WP_REST_Response(array(
        'success' => true,
        'receipts' => $result,
        'count' => count($result)
    ), 200);
}

/**
 * Get receipts count
 */
function iaindex_get_receipts_count() {
    $count = wp_count_posts('iaindex_receipt');
    return isset($count->publish) ? $count->publish : 0;
}
