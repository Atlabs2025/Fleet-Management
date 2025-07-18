odoo.define('atlbs_job_card.hide_sidebar', function (require) {
    "use strict";

    const WebClient = require('web.WebClient');

    WebClient.include({
        show_application: function () {
            this._super.apply(this, arguments);
            const hash = window.location.hash;
            if (hash.includes('action=action_job_card_management') || hash.includes('action=531')) {
                const sidebar = document.querySelector('.o_menu_sidebar');
                const content = document.querySelector('.o_action_manager');
                if (sidebar && content) {
                    sidebar.style.display = 'none';
                    content.style.marginLeft = '0';
                }
            }
        }
    });
});
