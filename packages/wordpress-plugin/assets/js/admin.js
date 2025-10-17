/**
 * IAIndex Admin JavaScript
 */

(function($) {
    'use strict';

    $(document).ready(function() {

        /**
         * Domain Verification
         */
        $('#iaindex-verify-domain').on('click', function(e) {
            e.preventDefault();

            var $button = $(this);
            var $spinner = $button.next('.spinner');
            var $result = $('#iaindex-verification-result');

            // Show loading state
            $button.prop('disabled', true).addClass('loading');
            $spinner.addClass('is-active');
            $result.empty();

            // Make AJAX request
            $.ajax({
                url: iaindexAjax.ajaxurl,
                type: 'POST',
                data: {
                    action: 'iaindex_verify_domain',
                    nonce: iaindexAjax.nonce
                },
                success: function(response) {
                    if (response.success) {
                        $result.html(
                            '<div class="notice notice-success inline">' +
                            '<p><span class="dashicons dashicons-yes-alt"></span> ' +
                            response.data.message +
                            '</p></div>'
                        );

                        // Reload page after 2 seconds to update verification status
                        setTimeout(function() {
                            location.reload();
                        }, 2000);
                    } else {
                        $result.html(
                            '<div class="notice notice-error inline">' +
                            '<p><span class="dashicons dashicons-dismiss"></span> ' +
                            response.data.message +
                            '</p></div>'
                        );
                    }
                },
                error: function(xhr, status, error) {
                    $result.html(
                        '<div class="notice notice-error inline">' +
                        '<p><span class="dashicons dashicons-dismiss"></span> ' +
                        'Error: ' + error +
                        '</p></div>'
                    );
                },
                complete: function() {
                    $button.prop('disabled', false).removeClass('loading');
                    $spinner.removeClass('is-active');
                }
            });
        });

        /**
         * Index Generation
         */
        $('#iaindex-generate-index').on('click', function(e) {
            e.preventDefault();

            var $button = $(this);
            var $spinner = $button.next('.spinner');
            var $result = $('#iaindex-generation-result');

            // Show loading state
            $button.prop('disabled', true).addClass('loading');
            $spinner.addClass('is-active');
            $result.empty();

            // Make AJAX request
            $.ajax({
                url: iaindexAjax.ajaxurl,
                type: 'POST',
                data: {
                    action: 'iaindex_generate_index',
                    nonce: iaindexAjax.nonce
                },
                success: function(response) {
                    if (response.success) {
                        var data = response.data.data;
                        $result.html(
                            '<div class="notice notice-success inline">' +
                            '<p><span class="dashicons dashicons-yes-alt"></span> ' +
                            response.data.message +
                            '</p>' +
                            '<ul style="margin: 10px 0 0 30px;">' +
                            '<li><strong>Entries:</strong> ' + data.entries_count + '</li>' +
                            '<li><strong>File:</strong> <code>' + data.file + '</code></li>' +
                            '<li><strong>URL:</strong> <a href="' + data.wellknown_url + '" target="_blank">' + data.wellknown_url + '</a></li>' +
                            '</ul>' +
                            '</div>'
                        );

                        // Reload page after 2 seconds to update stats
                        setTimeout(function() {
                            location.reload();
                        }, 3000);
                    } else {
                        $result.html(
                            '<div class="notice notice-error inline">' +
                            '<p><span class="dashicons dashicons-dismiss"></span> ' +
                            response.data.message +
                            '</p></div>'
                        );
                    }
                },
                error: function(xhr, status, error) {
                    $result.html(
                        '<div class="notice notice-error inline">' +
                        '<p><span class="dashicons dashicons-dismiss"></span> ' +
                        'Error: ' + error +
                        '</p></div>'
                    );
                },
                complete: function() {
                    $button.prop('disabled', false).removeClass('loading');
                    $spinner.removeClass('is-active');
                }
            });
        });

        /**
         * Toggle password visibility for API key
         */
        $('#iaindex_api_key').after(
            '<button type="button" class="button button-secondary" id="iaindex-toggle-api-key" style="margin-left: 10px;">' +
            '<span class="dashicons dashicons-visibility"></span>' +
            '</button>'
        );

        $('#iaindex-toggle-api-key').on('click', function(e) {
            e.preventDefault();
            var $input = $('#iaindex_api_key');
            var $icon = $(this).find('.dashicons');

            if ($input.attr('type') === 'password') {
                $input.attr('type', 'text');
                $icon.removeClass('dashicons-visibility').addClass('dashicons-hidden');
            } else {
                $input.attr('type', 'password');
                $icon.removeClass('dashicons-hidden').addClass('dashicons-visibility');
            }
        });

        /**
         * Confirm before regenerating index if posts exist
         */
        var entriesCount = $('.iaindex-stat-value:contains("Entries")').length;
        if (entriesCount > 0) {
            $('#iaindex-generate-index').on('click', function(e) {
                if (!confirm('This will regenerate the entire index. Continue?')) {
                    e.stopImmediatePropagation();
                    return false;
                }
            });
        }

        /**
         * Auto-hide success messages after 5 seconds
         */
        setTimeout(function() {
            $('.notice.notice-success').fadeOut('slow');
        }, 5000);

        /**
         * Copy to clipboard functionality
         */
        $('code').on('click', function() {
            var text = $(this).text();
            var $temp = $('<input>');
            $('body').append($temp);
            $temp.val(text).select();
            document.execCommand('copy');
            $temp.remove();

            // Show copied message
            var $this = $(this);
            var originalText = $this.text();
            $this.text('Copied!').css('background', '#d4edda');
            setTimeout(function() {
                $this.text(originalText).css('background', '');
            }, 2000);
        });

        /**
         * Add tooltip to clickable code elements
         */
        $('code').attr('title', 'Click to copy').css('cursor', 'pointer');
    });

})(jQuery);
