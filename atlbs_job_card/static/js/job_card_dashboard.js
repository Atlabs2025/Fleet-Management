// File: static/src/js/job_card_dashboard.js

odoo.define('atlbs_job_card.job_card_dashboard', function (require) {
    'use strict';

    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');

    const JobCardDashboard = AbstractAction.extend({
        template: 'job_card_dashboard.template',
        start: function () {
            return this._super();
        }
    });

    core.action_registry.add('job_card_dashboard_view', JobCardDashboard);

    return JobCardDashboard;
});
