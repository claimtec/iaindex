<?php
/**
 * Handle cryptographic signing of content
 */
class AIIndex_Signer {

    /**
     * Generate a new key pair
     */
    public function generate_keys() {
        // Generate Ed25519 key pair (requires PHP 7.2+ with sodium extension)
        if (!function_exists('sodium_crypto_sign_keypair')) {
            return array(
                'error' => __('Sodium extension not available. PHP 7.2+ with sodium is required.', 'aiindex')
            );
        }

        $keypair = sodium_crypto_sign_keypair();
        $public_key = sodium_crypto_sign_publickey($keypair);
        $secret_key = sodium_crypto_sign_secretkey($keypair);

        return array(
            'public_key' => base64_encode($public_key),
            'private_key' => base64_encode($secret_key)
        );
    }

    /**
     * Sign content with private key
     */
    public function sign_content($content) {
        $private_key = get_option('aiindex_private_key');

        if (empty($private_key)) {
            return '';
        }

        if (!function_exists('sodium_crypto_sign_detached')) {
            return '';
        }

        try {
            $content_string = json_encode($content);
            $secret_key = base64_decode($private_key);
            $signature = sodium_crypto_sign_detached($content_string, $secret_key);

            return base64_encode($signature);
        } catch (Exception $e) {
            error_log('AIIndex signing error: ' . $e->getMessage());
            return '';
        }
    }

    /**
     * Verify a signature
     */
    public function verify_signature($content, $signature, $public_key) {
        if (!function_exists('sodium_crypto_sign_verify_detached')) {
            return false;
        }

        try {
            $content_string = json_encode($content);
            $signature_decoded = base64_decode($signature);
            $public_key_decoded = base64_decode($public_key);

            return sodium_crypto_sign_verify_detached(
                $signature_decoded,
                $content_string,
                $public_key_decoded
            );
        } catch (Exception $e) {
            error_log('AIIndex verification error: ' . $e->getMessage());
            return false;
        }
    }
}
