odoo.define('mrp_repair_wes.warn_message', function(require){
	"use strict";
	
	var core = require('web.core');
	
	function ActionShowWarn(parent, action){
		var params = action.params;
		
		if(params){
			parent.do_warn(params.title, params.text, params.sticky);
		}
		return {'type':'ir.actions.act_window_close'};
	}
	core.action_registry.add("action_warn", ActionShowWarn);
	
	function ActionShowNotify(parent, action){
		var params = action.params;
		
		if(params){
			parent.do_notify(params.title, params.text, params.sticky);
		}
		return {'type':'ir.actions.act_window_close'};
	}
	core.action_registry.add("action_notify", ActionShowNotify);
});