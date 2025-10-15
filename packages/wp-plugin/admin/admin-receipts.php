<?php
/**
 * Receipts list page template
 */

// Security check
if (!defined('WPINC')) {
    die;
}

$receipts_manager = new AIIndex_Receipts();

// Pagination
$page = isset($_GET['paged']) ? max(1, intval($_GET['paged'])) : 1;
$per_page = 20;
$offset = ($page - 1) * $per_page;

$receipts = $receipts_manager->get_receipts($per_page, $offset);
$total = $receipts_manager->get_receipt_count();
$total_pages = ceil($total / $per_page);

?>

<div class="wrap">
    <h1 class="wp-heading-inline"><?php _e('Indexing Receipts', 'aiindex'); ?></h1>

    <a href="<?php echo admin_url('admin-ajax.php?action=aiindex_export_receipts&nonce=' . wp_create_nonce('aiindex_admin_nonce')); ?>"
       class="page-title-action">
        <?php _e('Export to CSV', 'aiindex'); ?>
    </a>

    <hr class="wp-header-end">

    <?php if (empty($receipts)): ?>
        <div class="notice notice-info">
            <p><?php _e('No receipts found. Receipts will appear here when AI indexers process your content.', 'aiindex'); ?></p>
        </div>
    <?php else: ?>
        <table class="wp-list-table widefat fixed striped">
            <thead>
                <tr>
                    <th style="width: 20%;"><?php _e('Receipt ID', 'aiindex'); ?></th>
                    <th style="width: 30%;"><?php _e('Content URL', 'aiindex'); ?></th>
                    <th style="width: 15%;"><?php _e('Indexer', 'aiindex'); ?></th>
                    <th style="width: 15%;"><?php _e('Indexed At', 'aiindex'); ?></th>
                    <th style="width: 10%;"><?php _e('Status', 'aiindex'); ?></th>
                    <th style="width: 10%;"><?php _e('Actions', 'aiindex'); ?></th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($receipts as $receipt): ?>
                <tr>
                    <td>
                        <code><?php echo esc_html(substr($receipt['receipt_id'], 0, 20)); ?>...</code>
                    </td>
                    <td>
                        <a href="<?php echo esc_url($receipt['content_url']); ?>" target="_blank">
                            <?php echo esc_html(wp_trim_words($receipt['content_url'], 8, '...')); ?>
                        </a>
                    </td>
                    <td>
                        <?php if ($receipt['indexer_name']): ?>
                            <strong><?php echo esc_html($receipt['indexer_name']); ?></strong>
                            <?php if ($receipt['indexer_url']): ?>
                                <br><a href="<?php echo esc_url($receipt['indexer_url']); ?>" target="_blank" class="description">
                                    <?php _e('View indexer', 'aiindex'); ?>
                                </a>
                            <?php endif; ?>
                        <?php else: ?>
                            <span class="description"><?php _e('Unknown', 'aiindex'); ?></span>
                        <?php endif; ?>
                    </td>
                    <td>
                        <?php echo esc_html(date_i18n(get_option('date_format') . ' ' . get_option('time_format'), strtotime($receipt['indexed_at']))); ?>
                    </td>
                    <td>
                        <span class="aiindex-status aiindex-status-<?php echo esc_attr($receipt['verification_status']); ?>">
                            <?php echo esc_html(ucfirst($receipt['verification_status'])); ?>
                        </span>
                    </td>
                    <td>
                        <button type="button" class="button button-small aiindex-view-receipt"
                                data-receipt-id="<?php echo esc_attr($receipt['id']); ?>">
                            <?php _e('View', 'aiindex'); ?>
                        </button>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>

        <?php if ($total_pages > 1): ?>
        <div class="tablenav">
            <div class="tablenav-pages">
                <span class="displaying-num">
                    <?php printf(_n('%s receipt', '%s receipts', $total, 'aiindex'), number_format_i18n($total)); ?>
                </span>
                <?php
                echo paginate_links(array(
                    'base' => add_query_arg('paged', '%#%'),
                    'format' => '',
                    'prev_text' => __('&laquo;'),
                    'next_text' => __('&raquo;'),
                    'total' => $total_pages,
                    'current' => $page
                ));
                ?>
            </div>
        </div>
        <?php endif; ?>
    <?php endif; ?>
</div>

<!-- Receipt Detail Modal -->
<div id="aiindex-receipt-modal" style="display:none;">
    <div class="aiindex-modal-overlay"></div>
    <div class="aiindex-modal-content">
        <span class="aiindex-modal-close">&times;</span>
        <h2><?php _e('Receipt Details', 'aiindex'); ?></h2>
        <div id="aiindex-receipt-details"></div>
    </div>
</div>

<script>
jQuery(document).ready(function($) {
    $('.aiindex-view-receipt').on('click', function() {
        var receiptId = $(this).data('receipt-id');
        // In a real implementation, this would fetch and display full receipt details
        $('#aiindex-receipt-modal').fadeIn();
    });

    $('.aiindex-modal-close, .aiindex-modal-overlay').on('click', function() {
        $('#aiindex-receipt-modal').fadeOut();
    });
});
</script>
