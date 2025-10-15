/**
 * AIIndex Admin JavaScript
 */

(function($) {
    'use strict';

    $(document).ready(function() {

        // Generate Keys
        $('#aiindex-generate-keys, #aiindex-regenerate-keys').on('click', function(e) {
            e.preventDefault();

            var $button = $(this);
            var originalText = $button.text();

            if (!confirm(aiindex_admin.strings.confirm_generate || 'Are you sure you want to generate new keys?')) {
                return;
            }

            $button.addClass('aiindex-loading').text(aiindex_admin.strings.generating);

            $.ajax({
                url: aiindex_admin.ajax_url,
                type: 'POST',
                data: {
                    action: 'aiindex_generate_keys',
                    nonce: aiindex_admin.nonce
                },
                success: function(response) {
                    if (response.success) {
                        $('#aiindex-keys-result')
                            .removeClass('error')
                            .addClass('success')
                            .html('<strong>' + aiindex_admin.strings.success + '</strong><br>' + response.data.message)
                            .slideDown();

                        // Reload page after 2 seconds to show new keys
                        setTimeout(function() {
                            location.reload();
                        }, 2000);
                    } else {
                        $('#aiindex-keys-result')
                            .removeClass('success')
                            .addClass('error')
                            .html('<strong>' + aiindex_admin.strings.error + '</strong><br>' + response.data.message)
                            .slideDown();
                    }
                },
                error: function() {
                    $('#aiindex-keys-result')
                        .removeClass('success')
                        .addClass('error')
                        .html('<strong>' + aiindex_admin.strings.error + '</strong><br>An error occurred.')
                        .slideDown();
                },
                complete: function() {
                    $button.removeClass('aiindex-loading').text(originalText);
                }
            });
        });

        // Verify Domain
        $('#aiindex-verify-domain').on('click', function(e) {
            e.preventDefault();

            var $button = $(this);
            var originalText = $button.text();

            $button.addClass('aiindex-loading').text(aiindex_admin.strings.verifying);

            $.ajax({
                url: aiindex_admin.ajax_url,
                type: 'POST',
                data: {
                    action: 'aiindex_verify_domain',
                    nonce: aiindex_admin.nonce
                },
                success: function(response) {
                    if (response.success) {
                        $('#aiindex-verification-result')
                            .removeClass('error')
                            .addClass('success')
                            .html('<strong>' + aiindex_admin.strings.success + '</strong><br>' + response.data.message)
                            .slideDown();

                        // Reload page after 2 seconds to update status
                        setTimeout(function() {
                            location.reload();
                        }, 2000);
                    } else {
                        $('#aiindex-verification-result')
                            .removeClass('success')
                            .addClass('error')
                            .html('<strong>' + aiindex_admin.strings.error + '</strong><br>' + response.data.message)
                            .slideDown();
                    }
                },
                error: function() {
                    $('#aiindex-verification-result')
                        .removeClass('success')
                        .addClass('error')
                        .html('<strong>' + aiindex_admin.strings.error + '</strong><br>An error occurred.')
                        .slideDown();
                },
                complete: function() {
                    $button.removeClass('aiindex-loading').text(originalText);
                }
            });
        });

        // Sync Now
        $('#aiindex-sync-now').on('click', function(e) {
            e.preventDefault();

            var $button = $(this);
            var originalText = $button.text();

            $button.addClass('aiindex-loading').prop('disabled', true).text('Syncing...');

            $.ajax({
                url: aiindex_admin.ajax_url,
                type: 'POST',
                data: {
                    action: 'aiindex_sync_now',
                    nonce: aiindex_admin.nonce
                },
                success: function(response) {
                    if (response.success) {
                        alert(response.data.message);
                    } else {
                        alert('Error: ' + response.data.message);
                    }
                },
                error: function() {
                    alert('An error occurred while syncing.');
                },
                complete: function() {
                    $button.removeClass('aiindex-loading').prop('disabled', false).text(originalText);
                }
            });
        });

        // Auto-hide success messages after 5 seconds
        setTimeout(function() {
            $('.notice.notice-success').fadeOut();
        }, 5000);
    });

})(jQuery);
