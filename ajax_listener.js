(function () {
    'use strict';
    var $;
    waitForjQuery();


    // Wait for jQuery to be available
    function waitForjQuery() {
        if (typeof jQuery !== 'undefined') {
        $ = jQuery;
        bindToAjax();
        } else {
        setTimeout(waitForjQuery, 500);
        }
    }


    function bindToAjax() {
        $(document).bind('ajaxComplete', function (evt, jqXhr, opts) {
            var signup_resource = '/wp-admin/admin-ajax.php';
            var requested_url = opts.url;
            var response = jqXhr.responseJSON;


            if (requested_url.indexOf(signup_resource) !== -1 && response && response.success === true) {
                 // Perform dataLayer.push()
                dataLayer.push({
                    'event': 'lead_form_completed',
                    'attributes': {
                        'time': evt.timeStamp || ''
                    }
                });
                console.log('lead_form_completed');
            } else {
                console.log('lead_form_not_completed');
            };
        });
    };
})();
