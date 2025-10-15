<?php
/**
 * Generate AI index JSON from WordPress content
 */
class AIIndex_Generator {

    /**
     * Generate the complete index data
     */
    public function generate() {
        $site_url = get_site_url();
        $site_name = get_bloginfo('name');

        $index = array(
            'version' => '1.1',
            'domain' => parse_url($site_url, PHP_URL_HOST),
            'siteName' => $site_name,
            'lastUpdated' => current_time('c'),
            'content' => $this->get_content(),
            'publicKey' => get_option('aiindex_public_key', ''),
            'signature' => '',
            'policy' => $this->get_policy_settings(),
            'receipts' => $this->get_receipt_settings(),
            'render_fallback' => $this->get_render_fallback_settings()
        );

        // Sign the content if keys are available
        $signer = new AIIndex_Signer();
        $signature = $signer->sign_content($index['content']);
        if ($signature) {
            $index['signature'] = $signature;
        }

        return $index;
    }

    /**
     * Get policy settings for v1.1
     */
    private function get_policy_settings() {
        $policy = array();

        if (get_option('aiindex_block_training', '0') === '1') {
            $policy['training'] = 'block';
        }

        if (get_option('aiindex_allow_retrieval_only', '0') === '1') {
            $policy['training'] = 'block';
            $policy['retrieval'] = 'allow';
        }

        return !empty($policy) ? $policy : array('training' => 'allow', 'retrieval' => 'allow');
    }

    /**
     * Get receipt settings for v1.1
     */
    private function get_receipt_settings() {
        return array(
            'require_signed' => get_option('aiindex_require_signed_receipts', '0') === '1'
        );
    }

    /**
     * Get render fallback settings for v1.1
     */
    private function get_render_fallback_settings() {
        if (get_option('aiindex_enable_render_fallback', '0') === '1') {
            return array(
                'mode' => 'edge',
                'enabled' => true
            );
        }

        return array(
            'enabled' => false
        );
    }

    /**
     * Generate policy JSON file for .well-known directory
     */
    public function generate_policy_json() {
        $policy_data = array(
            'version' => '1.1',
            'domain' => parse_url(get_site_url(), PHP_URL_HOST),
            'lastUpdated' => current_time('c'),
            'policy' => $this->get_policy_settings(),
            'receipts' => $this->get_receipt_settings(),
            'render_fallback' => $this->get_render_fallback_settings()
        );

        // Save to uploads directory (will be served via rewrite rule)
        $upload_dir = wp_upload_dir();
        $policy_file = $upload_dir['basedir'] . '/aiindex-policy.json';

        file_put_contents($policy_file, json_encode($policy_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

        return $policy_data;
    }

    /**
     * Get all indexable content
     */
    private function get_content() {
        $content = array();

        // Get posts
        if (get_option('aiindex_include_posts', '1') === '1') {
            $content = array_merge($content, $this->get_posts());
        }

        // Get pages
        if (get_option('aiindex_include_pages', '1') === '1') {
            $content = array_merge($content, $this->get_pages());
        }

        return $content;
    }

    /**
     * Get all posts
     */
    private function get_posts() {
        $args = array(
            'post_type' => 'post',
            'post_status' => 'publish',
            'posts_per_page' => -1,
            'orderby' => 'modified',
            'order' => 'DESC'
        );

        $posts = get_posts($args);
        $content = array();

        foreach ($posts as $post) {
            // Check if post is excluded
            if (get_post_meta($post->ID, '_aiindex_exclude', true) === '1') {
                continue;
            }

            $content[] = $this->format_post($post);
        }

        return $content;
    }

    /**
     * Get all pages
     */
    private function get_pages() {
        $args = array(
            'post_type' => 'page',
            'post_status' => 'publish',
            'posts_per_page' => -1,
            'orderby' => 'modified',
            'order' => 'DESC'
        );

        $pages = get_posts($args);
        $content = array();

        foreach ($pages as $page) {
            // Check if page is excluded
            if (get_post_meta($page->ID, '_aiindex_exclude', true) === '1') {
                continue;
            }

            $content[] = $this->format_post($page);
        }

        return $content;
    }

    /**
     * Format a post for the index
     */
    private function format_post($post) {
        $content_text = wp_strip_all_tags($post->post_content);
        $content_text = preg_replace('/\s+/', ' ', $content_text);
        $content_text = trim($content_text);

        return array(
            'url' => get_permalink($post->ID),
            'title' => $post->post_title,
            'content' => $content_text,
            'lastModified' => mysql2date('c', $post->post_modified),
            'contentType' => $post->post_type,
            'author' => get_the_author_meta('display_name', $post->post_author),
            'categories' => $this->get_categories($post->ID),
            'tags' => $this->get_tags($post->ID)
        );
    }

    /**
     * Get categories for a post
     */
    private function get_categories($post_id) {
        $categories = get_the_category($post_id);
        if (empty($categories)) {
            return array();
        }

        return array_map(function($cat) {
            return $cat->name;
        }, $categories);
    }

    /**
     * Get tags for a post
     */
    private function get_tags($post_id) {
        $tags = get_the_tags($post_id);
        if (empty($tags) || is_wp_error($tags)) {
            return array();
        }

        return array_map(function($tag) {
            return $tag->name;
        }, $tags);
    }
}
