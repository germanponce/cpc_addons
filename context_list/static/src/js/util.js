odoo.define('web.ListViewPlus', function (require) {
	/**
	 * @namespace
	 */
	"use strict";
	
	var data = require('web.data');
	var ListView = require('web.ListView');
	
	ListView.include(/** @lends instance.web.ListView# */{
		init: function() {
			var self = this;
			this._super.apply(this, arguments);
		},
		sidebar_eval_context: function () {
			return $.when(this.build_eval_context());
		},
		build_eval_context: function() {
			var a_dataset = this.dataset;
			return new data.CompoundContext(a_dataset.get_context());
		},
	})
});