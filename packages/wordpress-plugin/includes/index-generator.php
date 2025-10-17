<?php
/**
 * IAIndex Generator
 */

if (!defined('WPINC')) {
    die;
}

class IAIndex_Generator {

    /**
     * Generate IAIndex JSON from WordPress posts
     */
    public function generate_index() {
        $settings = get_option('iaindex_settings');
        $domain = isset($settings['domain']) ? $settings['domain'] : get_site_url();

        // Get all published posts
        $args = array(
            'post_type' => 'post',
            'post_status' => 'publish',
            'posts_per_page' => -1,
            'orderby' => 'date',
            'order' => 'DESC'
        );

        $posts = get_posts($args);
        $entries = array();

        foreach ($posts as $post) {
            $author = get_the_author_meta('display_name', $post->post_author);
            $published_date = get_the_date('c', $post->ID); // ISO 8601 format

            $entry = array(
                'url' => get_permalink($post->ID),
                'title' => get_the_title($post->ID),
                'author' => $author,
                'publishedDate' => $published_date,
                'license' => array(
                    'type' => 'CC-BY-4.0' // Default license, can be customized
                )
            );

            // Add optional fields if available
            $excerpt = get_the_excerpt($post->ID);
            if (!empty($excerpt)) {
                $entry['description'] = $excerpt;
            }

            // Add categories as tags
            $categories = get_the_category($post->ID);
            if (!empty($categories)) {
                $entry['tags'] = array_map(function($cat) {
                    return $cat->name;
                }, $categories);
            }

            $entries[] = $entry;
        }

        // Create IAIndex structure
        $iaindex = array(
            'domain' => parse_url($domain, PHP_URL_HOST) ?: $domain,
            'version' => '1.1',
            'entries' => $entries,
            'generatedAt' => gmdate('c')
        );

        // Save to file
        $upload_dir = wp_upload_dir();
        $iaindex_dir = $upload_dir['basedir'] . '/iaindex';

        if (!file_exists($iaindex_dir)) {
            wp_mkdir_p($iaindex_dir);
        }

        $json_file = $iaindex_dir . '/iaindex.json';
        $json_content = json_encode($iaindex, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);

        $result = file_put_contents($json_file, $json_content);

        if ($result === false) {
            return array(
                'success' => false,
                'error' => 'Failed to write index file'
            );
        }

        // Update last generated timestamp
        $settings['last_generated'] = current_time('timestamp');
        $settings['entries_count'] = count($entries);
        update_option('iaindex_settings', $settings);

        return array(
            'success' => true,
            'file' => $json_file,
            'url' => $upload_dir['baseurl'] . '/iaindex/iaindex.json',
            'wellknown_url' => trailingslashit($domain) . '.well-known/iaindex.json',
            'entries_count' => count($entries)
        );
    }

    /**
     * Get index file path
     */
    public function get_index_path() {
        $upload_dir = wp_upload_dir();
        return $upload_dir['basedir'] . '/iaindex/iaindex.json';
    }

    /**
     * Get index URL
     */
    public function get_index_url() {
        $settings = get_option('iaindex_settings');
        $domain = isset($settings['domain']) ? $settings['domain'] : get_site_url();
        return trailingslashit($domain) . '.well-known/iaindex.json';
    }

    /**
     * Check if index exists
     */
    public function index_exists() {
        return file_exists($this->get_index_path());
    }

    /**
     * Get index stats
     */
    public function get_stats() {
        $settings = get_option('iaindex_settings');

        return array(
            'exists' => $this->index_exists(),
            'entries_count' => isset($settings['entries_count']) ? $settings['entries_count'] : 0,
            'last_generated' => isset($settings['last_generated']) ? $settings['last_generated'] : null,
            'index_url' => $this->get_index_url()
        );
    }
}
