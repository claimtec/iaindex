<?php
/**
 * IAIndex API Client
 */

if (!defined('WPINC')) {
    die;
}

class IAIndex_API_Client {

    private $api_base_url;
    private $api_key;

    public function __construct() {
        $this->api_base_url = IAINDEX_API_BASE_URL;
        $settings = get_option('iaindex_settings');
        $this->api_key = isset($settings['api_key']) ? $settings['api_key'] : '';
    }

    /**
     * Set API key
     */
    public function set_api_key($api_key) {
        $this->api_key = $api_key;
    }

    /**
     * Make API request
     */
    private function request($endpoint, $method = 'GET', $body = null) {
        $url = trailingslashit($this->api_base_url) . ltrim($endpoint, '/');

        $args = array(
            'method' => $method,
            'headers' => array(
                'Content-Type' => 'application/json',
            ),
            'timeout' => 30,
        );

        if ($this->api_key) {
            $args['headers']['Authorization'] = 'Bearer ' . $this->api_key;
        }

        if ($body !== null) {
            $args['body'] = is_array($body) ? json_encode($body) : $body;
        }

        $response = wp_remote_request($url, $args);

        if (is_wp_error($response)) {
            return array(
                'success' => false,
                'error' => $response->get_error_message()
            );
        }

        $response_code = wp_remote_retrieve_response_code($response);
        $response_body = wp_remote_retrieve_body($response);

        $data = json_decode($response_body, true);

        return array(
            'success' => ($response_code >= 200 && $response_code < 300),
            'code' => $response_code,
            'data' => $data,
            'raw' => $response_body
        );
    }

    /**
     * Verify domain with IAIndex
     */
    public function verify_domain($domain) {
        return $this->request('v1/publishers/verify', 'POST', array(
            'domain' => $domain
        ));
    }

    /**
     * Submit receipt to IAIndex
     */
    public function submit_receipt($receipt_data) {
        return $this->request('v1/receipts/submit', 'POST', $receipt_data);
    }

    /**
     * Get publisher status
     */
    public function get_publisher_status($domain) {
        return $this->request('v1/publishers/' . urlencode($domain), 'GET');
    }

    /**
     * Get receipts for domain
     */
    public function get_receipts($domain, $limit = 10) {
        return $this->request('v1/receipts?domain=' . urlencode($domain) . '&limit=' . $limit, 'GET');
    }

    /**
     * Register publisher
     */
    public function register_publisher($data) {
        return $this->request('v1/publishers/register', 'POST', $data);
    }

    /**
     * Check index validity
     */
    public function check_index($index_url) {
        return $this->request('v1/publishers/check-index', 'POST', array(
            'indexUrl' => $index_url
        ));
    }
}
