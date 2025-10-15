<?php
/**
 * AIIndex Badge Shortcode
 *
 * Usage: [aiindex_badge]
 */

function aiindex_badge_shortcode($atts) {
    // Parse attributes
    $atts = shortcode_atts(array(
        'style' => 'default', // default, minimal, detailed
        'show_count' => 'true',
        'show_status' => 'true',
        'show_verification' => 'false' // v1.1: show all verification types
    ), $atts, 'aiindex_badge');

    // Get verification status
    $verification_status = get_option('aiindex_verification_status', 'pending');
    $verified_at = get_option('aiindex_verified_at');
    $c2pa_status = get_option('aiindex_c2pa_status', 'pending');
    $merkle_status = get_option('aiindex_merkle_status', 'pending');

    // Get receipt count
    $receipts = new AIIndex_Receipts();
    $receipt_count = $receipts->get_receipt_count();

    // Build badge HTML
    ob_start();
    ?>
    <div class="aiindex-badge aiindex-badge-<?php echo esc_attr($atts['style']); ?>">
        <?php if ($verification_status === 'verified'): ?>
            <div class="aiindex-badge-icon aiindex-badge-verified">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 0L12.2451 6.90983H19.5106L13.6327 11.1803L15.8779 18.0902L10 13.8197L4.12215 18.0902L6.36729 11.1803L0.489435 6.90983H7.75486L10 0Z" fill="#4CAF50"/>
                    <path d="M7 10L9 12L13 8" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div class="aiindex-badge-content">
                <div class="aiindex-badge-title">
                    <?php _e('AI Index Verified', 'aiindex'); ?>
                </div>
                <?php if ($atts['show_count'] === 'true' && $receipt_count > 0): ?>
                    <div class="aiindex-badge-count">
                        <?php printf(_n('%d indexing receipt', '%d indexing receipts', $receipt_count, 'aiindex'), $receipt_count); ?>
                    </div>
                <?php endif; ?>
                <?php if ($atts['show_status'] === 'true' && $verified_at): ?>
                    <div class="aiindex-badge-date">
                        <?php printf(__('Verified %s', 'aiindex'), human_time_diff(strtotime($verified_at), current_time('timestamp'))); ?>
                    </div>
                <?php endif; ?>
                <?php if ($atts['show_verification'] === 'true'): ?>
                    <div class="aiindex-badge-verifications">
                        <div class="aiindex-verification-item">
                            <span class="<?php echo $verification_status === 'verified' ? 'verified' : 'pending'; ?>">
                                <?php echo $verification_status === 'verified' ? '✓' : '○'; ?>
                            </span>
                            <?php _e('Domain', 'aiindex'); ?>
                        </div>
                        <div class="aiindex-verification-item">
                            <span class="<?php echo $c2pa_status === 'verified' ? 'verified' : 'pending'; ?>">
                                <?php echo $c2pa_status === 'verified' ? '✓' : '○'; ?>
                            </span>
                            <?php _e('C2PA', 'aiindex'); ?>
                        </div>
                        <div class="aiindex-verification-item">
                            <span class="<?php echo $merkle_status === 'verified' ? 'verified' : 'pending'; ?>">
                                <?php echo $merkle_status === 'verified' ? '✓' : '○'; ?>
                            </span>
                            <?php _e('Merkle', 'aiindex'); ?>
                        </div>
                    </div>
                <?php endif; ?>
            </div>
        <?php else: ?>
            <div class="aiindex-badge-icon aiindex-badge-pending">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="10" cy="10" r="9" stroke="#FFA500" stroke-width="2"/>
                    <path d="M10 6V10L13 13" stroke="#FFA500" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <div class="aiindex-badge-content">
                <div class="aiindex-badge-title">
                    <?php _e('AI Index Pending', 'aiindex'); ?>
                </div>
            </div>
        <?php endif; ?>
    </div>

    <style>
    .aiindex-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 12px 16px;
        background: #fff;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        max-width: 300px;
    }

    .aiindex-badge-verified {
        border-color: #4CAF50;
    }

    .aiindex-badge-icon {
        flex-shrink: 0;
    }

    .aiindex-badge-content {
        flex: 1;
    }

    .aiindex-badge-title {
        font-weight: 600;
        font-size: 14px;
        color: #333;
        margin-bottom: 2px;
    }

    .aiindex-badge-count,
    .aiindex-badge-date {
        font-size: 12px;
        color: #666;
        line-height: 1.4;
    }

    .aiindex-badge-minimal {
        padding: 8px 12px;
        gap: 8px;
    }

    .aiindex-badge-minimal .aiindex-badge-icon svg {
        width: 16px;
        height: 16px;
    }

    .aiindex-badge-minimal .aiindex-badge-title {
        font-size: 13px;
    }

    .aiindex-badge-detailed {
        max-width: 400px;
        padding: 16px 20px;
    }

    .aiindex-badge-verifications {
        display: flex;
        gap: 12px;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #e0e0e0;
    }

    .aiindex-verification-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        color: #666;
    }

    .aiindex-verification-item span {
        font-weight: bold;
        font-size: 14px;
    }

    .aiindex-verification-item span.verified {
        color: #4CAF50;
    }

    .aiindex-verification-item span.pending {
        color: #999;
    }
    </style>
    <?php
    return ob_get_clean();
}
