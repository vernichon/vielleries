##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import pooler

asset_end_arch = '''<?xml version="1.0"?>
<form string="Compute assets">
	<separator string="Generated entries" colspan="4"/>
	<field name="move_ids" readonly="1" nolabel="1"/>
</form>'''

asset_end_fields = {
	'move_ids': {'string':'Entries', 'type': 'one2many', 'relation':'account.move'},
}


asset_ask_form = '''<?xml version="1.0"?>
<form string="Compute assets">
	<field name="period_id"/>
</form>'''

asset_ask_fields = {
	'period_id': {'string': 'Period', 'type': 'many2one', 'relation':'account.period', 'required':True},
}

def _asset_compute(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	print "pool"
	ass_obj = pool.get('account.asset.asset')
	print "ass_obj", context
	ids = ass_obj.search(cr, uid, [('state','=','normal')])#, context)
	print "IDS ASSET", ids
	ids_create = []
	for asset in ass_obj.browse(cr, uid, ids, context):
		ids_create += ass_obj._compute_entries(cr, uid, asset, data['form']['period_id'], context)
	print ids_create	
	self.move_ids = ids_create
	return {'move_ids': ids_create}

def _asset_open(self, cr, uid, data, context):
	value = {
		'name': 'Created moves',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'res_model': 'account.move',
		'view_id': False,
		'type': 'ir.actions.act_window'
	}
	if data['form']['move_ids']:
		value['domain']= "[('id','in',["+','.join(map(str,self.move_ids))+"])]"
	else:
		value['domain']= "[('id','=', False)]"
	print value
	return value

def _get_period(self, cr, uid, data, context={}):
	pool = pooler.get_pool(cr.dbname)
	ids = pool.get('account.period').find(cr, uid, context=context)
	period_id = False
	if len(ids):
		period_id = ids[0]
	return {'period_id': period_id}

class wizard_asset_compute(wizard.interface):
	states = {
		'init': {
			'actions': [_get_period],
			'result': {'type':'form', 'arch':asset_ask_form, 'fields':asset_ask_fields, 'state':[
				('end','Cancel'),
				('asset_compute','Compute assets')
			]}
		},
		'asset_compute': {
			'actions': [_asset_compute],
			'result': {'type' : 'form', 'arch': asset_end_arch, 'fields':asset_end_fields, 'state':[
				('end','Close'),
				('asset_open','Open entries')
			]}
		},
		'asset_open': {
			'actions': [],
			'result': {'type':'action', 'action': _asset_open,  'state':'end'}
		}
	}
wizard_asset_compute('account.asset.compute')


