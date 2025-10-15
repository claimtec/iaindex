<?php
/**
 * Admin settings page template
 */

// Security check
if (!defined('WPINC')) {
    die;
}

// Get current tab
$active_tab = isset($_GET['tab']) ? sanitize_text_field($_GET['tab']) : 'general';

// Save settings
if (isset($_POST['aiindex_save_settings'])) {
    check_admin_referer('aiindex_settings_nonce');

    if ($active_tab === 'general') {
        update_option('aiindex_enabled', isset($_POST['aiindex_enabled']) ? '1' : '0');
        update_option('aiindex_include_posts', isset($_POST['aiindex_include_posts']) ? '1' : '0');
        update_option('aiindex_include_pages', isset($_POST['aiindex_include_pages']) ? '1' : '0');
        update_option('aiindex_webhook_url', sanitize_text_field($_POST['aiindex_webhook_url']));
        update_option('aiindex_sync_frequency', sanitize_text_field($_POST['aiindex_sync_frequency']));
    } elseif ($active_tab === 'policies') {
        // v1.1 Policy Controls
        update_option('aiindex_block_training', isset($_POST['aiindex_block_training']) ? '1' : '0');
        update_option('aiindex_allow_retrieval_only', isset($_POST['aiindex_allow_retrieval_only']) ? '1' : '0');
        update_option('aiindex_require_signed_receipts', isset($_POST['aiindex_require_signed_receipts']) ? '1' : '0');
        update_option('aiindex_enable_render_fallback', isset($_POST['aiindex_enable_render_fallback']) ? '1' : '0');

        // Regenerate policy JSON
        $generator = new AIIndex_Generator();
        $generator->generate_policy_json();
    }

    echo '<div class="notice notice-success"><p>' . __('Settings saved successfully.', 'aiindex') . '</p></div>';
}

?>

<div class="wrap">
    <h1><?php echo esc_html(get_admin_page_title()); ?></h1>

    <h2 class="nav-tab-wrapper">
        <a href="?page=aiindex&tab=general" class="nav-tab <?php echo $active_tab === 'general' ? 'nav-tab-active' : ''; ?>">
            <?php _e('General', 'aiindex'); ?>
        </a>
        <a href="?page=aiindex&tab=policies" class="nav-tab <?php echo $active_tab === 'policies' ? 'nav-tab-active' : ''; ?>">
            <?php _e('Policy Controls', 'aiindex'); ?>
        </a>
        <a href="?page=aiindex&tab=keys" class="nav-tab <?php echo $active_tab === 'keys' ? 'nav-tab-active' : ''; ?>">
            <?php _e('Keys', 'aiindex'); ?>
        </a>
        <a href="?page=aiindex&tab=verification" class="nav-tab <?php echo $active_tab === 'verification' ? 'nav-tab-active' : ''; ?>">
            <?php _e('Verification', 'aiindex'); ?>
        </a>
        <a href="?page=aiindex&tab=analytics" class="nav-tab <?php echo $active_tab === 'analytics' ? 'nav-tab-active' : ''; ?>">
            <?php _e('Analytics', 'aiindex'); ?>
        </a>
    </h2>

    <?php if ($active_tab === 'general'): ?>
        <form method="post" action="">
            <?php wp_nonce_field('aiindex_settings_nonce'); ?>

            <table class="form-table">
                <tr>
                    <th scope="row">
                        <label for="aiindex_enabled"><?php _e('Enable AIIndex', 'aiindex'); ?></label>
                    </th>
                    <td>
                        <input type="checkbox" name="aiindex_enabled" id="aiindex_enabled" value="1"
                            <?php checked(get_option('aiindex_enabled', '1'), '1'); ?>>
                        <p class="description">
                            <?php _e('Enable or disable the AI index generation.', 'aiindex'); ?>
                        </p>
                    </td>
                </tr>

                <tr>
                    <th scope="row"><?php _e('Content Types', 'aiindex'); ?></th>
                    <td>
                        <fieldset>
                            <label>
                                <input type="checkbox" name="aiindex_include_posts" value="1"
                                    <?php checked(get_option('aiindex_include_posts', '1'), '1'); ?>>
                                <?php _e('Include Posts', 'aiindex'); ?>
                            </label><br>
                            <label>
                                <input type="checkbox" name="aiindex_include_pages" value="1"
                                    <?php checked(get_option('aiindex_include_pages', '1'), '1'); ?>>
                                <?php _e('Include Pages', 'aiindex'); ?>
                            </label>
                        </fieldset>
                        <p class="description">
                            <?php _e('Select which content types to include in the index.', 'aiindex'); ?>
                        </p>
                    </td>
                </tr>

                <tr>
                    <th scope="row">
                        <label for="aiindex_webhook_url"><?php _e('Webhook URL', 'aiindex'); ?></label>
                    </th>
                    <td>
                        <input type="url" name="aiindex_webhook_url" id="aiindex_webhook_url"
                            value="<?php echo esc_attr(get_option('aiindex_webhook_url')); ?>"
                            class="regular-text" placeholder="https://api.aiindex.dev/webhook">
                        <p class="description">
                            <?php _e('URL to send index updates to (optional).', 'aiindex'); ?>
                        </p>
                    </td>
                </tr>

                <tr>
                    <th scope="row">
                        <label for="aiindex_sync_frequency"><?php _e('Sync Frequency', 'aiindex'); ?></label>
                    </th>
                    <td>
                        <select name="aiindex_sync_frequency" id="aiindex_sync_frequency">
                            <option value="hourly" <?php selected(get_option('aiindex_sync_frequency', 'hourly'), 'hourly'); ?>>
                                <?php _e('Hourly', 'aiindex'); ?>
                            </option>
                            <option value="twicedaily" <?php selected(get_option('aiindex_sync_frequency'), 'twicedaily'); ?>>
                                <?php _e('Twice Daily', 'aiindex'); ?>
                            </option>
                            <option value="daily" <?php selected(get_option('aiindex_sync_frequency'), 'daily'); ?>>
                                <?php _e('Daily', 'aiindex'); ?>
                            </option>
                        </select>
                        <p class="description">
                            <?php _e('How often to sync the index with the webhook.', 'aiindex'); ?>
                        </p>
                    </td>
                </tr>

                <tr>
                    <th scope="row"><?php _e('Index URL', 'aiindex'); ?></th>
                    <td>
                        <code><?php echo esc_url(get_site_url() . '/ai-index.json'); ?></code>
                        <a href="<?php echo esc_url(get_site_url() . '/ai-index.json'); ?>" target="_blank" class="button button-small">
                            <?php _e('View Index', 'aiindex'); ?>
                        </a>
                        <p class="description">
                            <?php _e('Your AI index is accessible at this URL.', 'aiindex'); ?>
                        </p>
                    </td>
                </tr>
            </table>

            <p class="submit">
                <input type="submit" name="aiindex_save_settings" class="button button-primary"
                    value="<?php _e('Save Settings', 'aiindex'); ?>">
                <button type="button" class="button" id="aiindex-sync-now">
                    <?php _e('Sync Now', 'aiindex'); ?>
                </button>
            </p>
        </form>

    <?php elseif ($active_tab === 'policies'): ?>
        <div class="aiindex-policies-section">
            <h2><?php _e('AI Policy Controls (v1.1)', 'aiindex'); ?></h2>
            <p><?php _e('Configure how AI systems can interact with your content using simple toggles.', 'aiindex'); ?></p>

            <form method="post" action="">
                <?php wp_nonce_field('aiindex_settings_nonce'); ?>

                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="aiindex_block_training"><?php _e('Block Model Training', 'aiindex'); ?></label>
                        </th>
                        <td>
                            <label class="aiindex-toggle">
                                <input type="checkbox" name="aiindex_block_training" id="aiindex_block_training" value="1"
                                    <?php checked(get_option('aiindex_block_training', '0'), '1'); ?>>
                                <span class="aiindex-toggle-slider"></span>
                            </label>
                            <p class="description">
                                <?php _e('Prevent AI systems from using your content for model training. Sets policy.training="block".', 'aiindex'); ?>
                            </p>
                        </td>
                    </tr>

                    <tr>
                        <th scope="row">
                            <label for="aiindex_allow_retrieval_only"><?php _e('Allow Retrieval Only', 'aiindex'); ?></label>
                        </th>
                        <td>
                            <label class="aiindex-toggle">
                                <input type="checkbox" name="aiindex_allow_retrieval_only" id="aiindex_allow_retrieval_only" value="1"
                                    <?php checked(get_option('aiindex_allow_retrieval_only', '0'), '1'); ?>>
                                <span class="aiindex-toggle-slider"></span>
                            </label>
                            <p class="description">
                                <?php _e('Block training but allow retrieval for RAG/search. Sets policy.training="block", policy.retrieval="allow".', 'aiindex'); ?>
                            </p>
                        </td>
                    </tr>

                    <tr>
                        <th scope="row">
                            <label for="aiindex_require_signed_receipts"><?php _e('Require Signed Receipts', 'aiindex'); ?></label>
                        </th>
                        <td>
                            <label class="aiindex-toggle">
                                <input type="checkbox" name="aiindex_require_signed_receipts" id="aiindex_require_signed_receipts" value="1"
                                    <?php checked(get_option('aiindex_require_signed_receipts', '0'), '1'); ?>>
                                <span class="aiindex-toggle-slider"></span>
                            </label>
                            <p class="description">
                                <?php _e('Require cryptographic signatures on all indexing receipts. Sets receipts.require_signed=true.', 'aiindex'); ?>
                            </p>
                        </td>
                    </tr>

                    <tr>
                        <th scope="row">
                            <label for="aiindex_enable_render_fallback"><?php _e('Enable Render Fallback', 'aiindex'); ?></label>
                        </th>
                        <td>
                            <label class="aiindex-toggle">
                                <input type="checkbox" name="aiindex_enable_render_fallback" id="aiindex_enable_render_fallback" value="1"
                                    <?php checked(get_option('aiindex_enable_render_fallback', '0'), '1'); ?>>
                                <span class="aiindex-toggle-slider"></span>
                            </label>
                            <p class="description">
                                <?php _e('Enable edge rendering for dynamic content. Sets render_fallback.mode="edge".', 'aiindex'); ?>
                            </p>
                        </td>
                    </tr>

                    <tr>
                        <th scope="row"><?php _e('Generated Files', 'aiindex'); ?></th>
                        <td>
                            <p><code><?php echo esc_url(get_site_url() . '/ai-index.json'); ?></code></p>
                            <p><code><?php echo esc_url(get_site_url() . '/.well-known/aiindex-policy.json'); ?></code></p>
                            <p class="description">
                                <?php _e('Policy settings are saved to both files automatically.', 'aiindex'); ?>
                            </p>
                        </td>
                    </tr>
                </table>

                <p class="submit">
                    <input type="submit" name="aiindex_save_settings" class="button button-primary"
                        value="<?php _e('Save Policy Settings', 'aiindex'); ?>">
                    <button type="button" class="button" id="aiindex-regenerate-index">
                        <?php _e('Regenerate AI Index', 'aiindex'); ?>
                    </button>
                </p>
            </form>
        </div>

    <?php elseif ($active_tab === 'keys'): ?>
        <div class="aiindex-keys-section">
            <h2><?php _e('Cryptographic Keys', 'aiindex'); ?></h2>
            <p><?php _e('Generate and manage your signing keys for index verification.', 'aiindex'); ?></p>

            <?php
            $public_key = get_option('aiindex_public_key');
            $has_keys = !empty($public_key);
            ?>

            <?php if ($has_keys): ?>
                <div class="notice notice-success inline">
                    <p><?php _e('Keys are configured and ready to use.', 'aiindex'); ?></p>
                </div>

                <table class="form-table">
                    <tr>
                        <th scope="row"><?php _e('Public Key', 'aiindex'); ?></th>
                        <td>
                            <textarea readonly class="large-text code" rows="3"><?php echo esc_textarea($public_key); ?></textarea>
                            <p class="description">
                                <?php _e('Share this key with AI indexers for verification.', 'aiindex'); ?>
                            </p>
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><?php _e('Private Key', 'aiindex'); ?></th>
                        <td>
                            <code><?php _e('Hidden for security', 'aiindex'); ?></code>
                            <p class="description">
                                <?php _e('Your private key is stored securely and never displayed.', 'aiindex'); ?>
                            </p>
                        </td>
                    </tr>
                </table>

                <p>
                    <button type="button" class="button" id="aiindex-regenerate-keys">
                        <?php _e('Regenerate Keys', 'aiindex'); ?>
                    </button>
                    <span class="description">
                        <?php _e('Warning: This will invalidate existing signatures.', 'aiindex'); ?>
                    </span>
                </p>
            <?php else: ?>
                <div class="notice notice-warning inline">
                    <p><?php _e('No keys found. Generate keys to enable index signing.', 'aiindex'); ?></p>
                </div>

                <p>
                    <button type="button" class="button button-primary" id="aiindex-generate-keys">
                        <?php _e('Generate Keys', 'aiindex'); ?>
                    </button>
                </p>
            <?php endif; ?>

            <div id="aiindex-keys-result" style="margin-top: 20px;"></div>
        </div>

    <?php elseif ($active_tab === 'verification'): ?>
        <div class="aiindex-verification-section">
            <h2><?php _e('Domain Verification & Badge (v1.1)', 'aiindex'); ?></h2>
            <p><?php _e('Verify that your AI index is properly configured and view live verification status.', 'aiindex'); ?></p>

            <?php
            $verification_status = get_option('aiindex_verification_status', 'pending');
            $verified_at = get_option('aiindex_verified_at');
            $c2pa_status = get_option('aiindex_c2pa_status', 'pending');
            $merkle_status = get_option('aiindex_merkle_status', 'pending');
            ?>

            <div class="aiindex-verification-grid">
                <div class="aiindex-verification-card">
                    <div class="aiindex-verification-icon">
                        <?php if ($verification_status === 'verified'): ?>
                            <span class="dashicons dashicons-yes-alt" style="color: #4CAF50; font-size: 32px;"></span>
                        <?php else: ?>
                            <span class="dashicons dashicons-warning" style="color: #FF9800; font-size: 32px;"></span>
                        <?php endif; ?>
                    </div>
                    <h3><?php _e('Domain Verification', 'aiindex'); ?></h3>
                    <p class="aiindex-verification-status">
                        <?php echo $verification_status === 'verified' ? __('Verified', 'aiindex') : __('Not Verified', 'aiindex'); ?>
                    </p>
                    <?php if ($verified_at): ?>
                        <p class="aiindex-verification-time">
                            <?php printf(__('Updated: %s', 'aiindex'), human_time_diff(strtotime($verified_at), current_time('timestamp')) . ' ago'); ?>
                        </p>
                    <?php endif; ?>
                </div>

                <div class="aiindex-verification-card">
                    <div class="aiindex-verification-icon">
                        <?php if ($c2pa_status === 'verified'): ?>
                            <span class="dashicons dashicons-yes-alt" style="color: #4CAF50; font-size: 32px;"></span>
                        <?php else: ?>
                            <span class="dashicons dashicons-warning" style="color: #FF9800; font-size: 32px;"></span>
                        <?php endif; ?>
                    </div>
                    <h3><?php _e('C2PA Provenance', 'aiindex'); ?></h3>
                    <p class="aiindex-verification-status">
                        <?php echo $c2pa_status === 'verified' ? __('Verified', 'aiindex') : __('Pending', 'aiindex'); ?>
                    </p>
                </div>

                <div class="aiindex-verification-card">
                    <div class="aiindex-verification-icon">
                        <?php if ($merkle_status === 'verified'): ?>
                            <span class="dashicons dashicons-yes-alt" style="color: #4CAF50; font-size: 32px;"></span>
                        <?php else: ?>
                            <span class="dashicons dashicons-warning" style="color: #FF9800; font-size: 32px;"></span>
                        <?php endif; ?>
                    </div>
                    <h3><?php _e('Merkle Attestation', 'aiindex'); ?></h3>
                    <p class="aiindex-verification-status">
                        <?php echo $merkle_status === 'verified' ? __('Verified', 'aiindex') : __('Pending', 'aiindex'); ?>
                    </p>
                </div>

                <div class="aiindex-verification-card">
                    <div class="aiindex-verification-icon">
                        <span class="dashicons dashicons-admin-site-alt3" style="color: #2196F3; font-size: 32px;"></span>
                    </div>
                    <h3><?php _e('Live Badge', 'aiindex'); ?></h3>
                    <p>
                        <a href="#" id="aiindex-preview-badge" class="button">
                            <?php _e('Preview Badge', 'aiindex'); ?>
                        </a>
                    </p>
                </div>
            </div>

            <div class="aiindex-quick-actions">
                <h3><?php _e('Quick Actions', 'aiindex'); ?></h3>
                <p>
                    <button type="button" class="button button-primary" id="aiindex-verify-domain">
                        <?php _e('Verify Domain', 'aiindex'); ?>
                    </button>
                    <button type="button" class="button" id="aiindex-view-badge">
                        <?php _e('View Live Badge', 'aiindex'); ?>
                    </button>
                    <button type="button" class="button" id="aiindex-copy-embed">
                        <?php _e('Copy Embed Code', 'aiindex'); ?>
                    </button>
                </p>
            </div>

            <div class="aiindex-embed-code" style="margin-top: 20px; display: none;">
                <h4><?php _e('Badge Embed Code', 'aiindex'); ?></h4>
                <textarea readonly class="large-text code" rows="3" id="aiindex-badge-embed">[aiindex_badge style="detailed" show_count="true" show_verification="true"]</textarea>
                <p class="description">
                    <?php _e('Copy this shortcode to display the verification badge on any page or post.', 'aiindex'); ?>
                </p>
            </div>

            <div id="aiindex-verification-result" style="margin-top: 20px;"></div>
        </div>

    <?php elseif ($active_tab === 'analytics'): ?>
        <?php
        $receipts = new AIIndex_Receipts();
        $analytics = $receipts->get_analytics();
        ?>

        <div class="aiindex-analytics-section">
            <h2><?php _e('Receipt Analytics & Policy Dashboard (v1.1)', 'aiindex'); ?></h2>

            <div class="aiindex-analytics-grid">
                <div class="aiindex-analytics-card">
                    <div class="aiindex-analytics-value"><?php echo esc_html($analytics['last_7_days']); ?></div>
                    <div class="aiindex-analytics-label"><?php _e('Receipts (Last 7 Days)', 'aiindex'); ?></div>
                </div>

                <div class="aiindex-analytics-card">
                    <div class="aiindex-analytics-value" style="color: #4CAF50;">
                        <?php echo esc_html($analytics['allowed_count'] ?? 0); ?>
                    </div>
                    <div class="aiindex-analytics-label"><?php _e('Allowed Requests', 'aiindex'); ?></div>
                </div>

                <div class="aiindex-analytics-card">
                    <div class="aiindex-analytics-value" style="color: #F44336;">
                        <?php echo esc_html($analytics['denied_count'] ?? 0); ?>
                    </div>
                    <div class="aiindex-analytics-label"><?php _e('Denied Requests', 'aiindex'); ?></div>
                </div>

                <div class="aiindex-analytics-card">
                    <div class="aiindex-analytics-value" style="color: #FF9800;">
                        <?php echo esc_html($analytics['policy_violations'] ?? 0); ?>
                    </div>
                    <div class="aiindex-analytics-label"><?php _e('Policy Violations', 'aiindex'); ?></div>
                </div>
            </div>

            <?php if (!empty($analytics['by_indexer'])): ?>
                <h3><?php _e('Top AI Clients', 'aiindex'); ?></h3>
                <table class="wp-list-table widefat fixed striped">
                    <thead>
                        <tr>
                            <th><?php _e('AI Client', 'aiindex'); ?></th>
                            <th><?php _e('Receipt Count', 'aiindex'); ?></th>
                            <th><?php _e('Allowed', 'aiindex'); ?></th>
                            <th><?php _e('Denied', 'aiindex'); ?></th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($analytics['by_indexer'] as $indexer): ?>
                        <tr>
                            <td><strong><?php echo esc_html($indexer['indexer_name']); ?></strong></td>
                            <td><?php echo esc_html($indexer['count']); ?></td>
                            <td style="color: #4CAF50;"><?php echo esc_html($indexer['allowed'] ?? 0); ?></td>
                            <td style="color: #F44336;"><?php echo esc_html($indexer['denied'] ?? 0); ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>

            <div class="aiindex-dashboard-link" style="margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 8px;">
                <h3><?php _e('Full Analytics Dashboard', 'aiindex'); ?></h3>
                <p><?php _e('View detailed analytics, policy enforcement metrics, and compliance reports on the AIIndex dashboard.', 'aiindex'); ?></p>
                <p>
                    <a href="https://aiindex.org/dashboard?domain=<?php echo urlencode(parse_url(get_site_url(), PHP_URL_HOST)); ?>"
                       class="button button-primary" target="_blank">
                        <?php _e('Open Dashboard', 'aiindex'); ?>
                    </a>
                </p>
            </div>

            <p style="margin-top: 20px;">
                <a href="<?php echo admin_url('admin.php?page=aiindex-receipts'); ?>" class="button">
                    <?php _e('View All Receipts', 'aiindex'); ?>
                </a>
                <a href="<?php echo admin_url('admin-ajax.php?action=aiindex_export_receipts&nonce=' . wp_create_nonce('aiindex_admin_nonce')); ?>"
                   class="button">
                    <?php _e('Export to CSV', 'aiindex'); ?>
                </a>
            </p>
        </div>
    <?php endif; ?>
</div>
