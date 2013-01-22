# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 E.V.I.. (http://www.vernichon.fr) All Rights Reserved.
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
import netsvc
import pooler
import time
amort_form = '''<?xml version="1.0"?>
<form string="Immobiliser">
	<field name="duree"/>
	<field name="methode"/>
	<field name="methodefisc"/>
	<field name="facteur"/>
	<field name="cpt_amort"/>
	<field name="cpt_actif"/>
</form>'''

amort_fields = {
	'duree': {'string': 'Duree', 'type':'integer', 'required':True},
	'methode': {'string': 'Methode d\'amortissement', 'type': 'selection', 'selection':[('linear', 'Linéaire'),('degressif', 'Dégressif'),('exceptionnel','Exceptionnel')]},
	'methodefisc': {'string': 'Methode Fiscale', 'type': 'selection', 'selection':[(0,'30 Jours par mois / 360 jours par an'),(1,'Jour réels /365 par an')]},
	'facteur': {'string': 'Coefficient', 'type': 'float', 'required':False},
	'cpt_amort': {'string': 'Compte d\'immobilisation','type':'many2one', 'relation':'account.account', 'required':True},
	'cpt_actif': {'string': 'Compte Actif', 'type':'many2one', 'relation':'account.account', 'required':True},
}

amort_select_form = '''<?xml version="1.0"?>
<form string="Ligne à immobiliser">
	<separator string="Ligne de facture" colspan="4"/>
	<field name="line_ids"  nolabel="1"/>
</form>'''

amort_select_fields = {
	'line_ids': {'string': 'Lignes de facture', 'type':'one2many', 'relation':'account.invoice.line'},
}
def _init(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	print data,context
	ligne = pool.get('account.invoice.line').read(cr,uid,data['ids'][0])
	asset_controle = pool.get('asset.asset').search(cr,uid,[('lignefacture','=',ligne['id'])])
	if  asset_controle:
		 raise wizard.except_wizard('Ligne déjà immobilisé',
                        'Cette ligne de facture a déjà été '
                        'immobilisé:\n%s' % (asset_controle,))
	data['form']['cpt_actif'] =pool.get('account.account').search(cr,uid,[('code','=','681110')])[0]
	data['form']['cpt_amort'] =pool.get('account.account').search(cr,uid,[('code','=','208000')])[0]
	data['form']['methode']= 'linear'
	data['form']['methodefisc']= 1
	data['form']['duree']= 5
	data['form']['facteur']= 1
	print data
	return data['form']

def _selectionner(self, cr, uid, data, context):
	facture = pooler.get_pool(cr.dbname).get('account.invoice').read(cr,uid,data['ids'][0])
	ligne_ids = pooler.get_pool(cr.dbname).get('account.invoice.line').search(cr,uid,[('invoice_id','=',data['ids'][0])])
	print ligne_ids
	self.line_ids=ligne_ids
	return {'line_ids':ligne_ids}

def _amortir(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	print "data['form']" , data['form']
	print data
	journal_id = pool.get('account.journal').search(cr,uid,[('name','ilike','Amortissement%')])[0]
	data=data['form']
	for line in data['line_ids']:
		ligne = pool.get('account.invoice.line').read(cr,uid,line[1]) # lit les valeur de la ligne de facture
		
		print "type" , data['methode']
		print "Compte amort" , data['cpt_amort']
		print "Compte actif" , data['cpt_actif']
		print "duree",data['duree']
		print "facteur",data['facteur']
		print "Ligne ",ligne
		print "id",ligne['id']
		print "name",ligne['name']
		nom = ligne['name']
		base = float(ligne['quantity'])*float(ligne['price_unit'])
		data_amort={'name':nom ,'date': time.strftime('%Y-%m-%d'),'methode':data['methode'],'duree': data['duree'],'coefd':data['facteur'],'base':base,'lignefacture':ligne['id']}
		print data_amort
		asset_id=pool.get('asset.asset').create(cr, uid,data_amort)
		print asset_id
	return{}


class wizard_amortir(wizard.interface):
	states = {
		'init': {
			'actions': [_init],
			'result': {'type':'form', 'arch':amort_form, 'fields':amort_fields, 'state':[('end','Cancel'),('selectionner','Selectionner')]}
		},
		'selectionner': {
			'actions': [_selectionner],
			 'result': {'type' : 'form', 'arch': amort_select_form, 'fields':amort_select_fields, 'state':[('end','Cancel'),('amortir','Amortir')]}
			},
		'amortir': {
			'actions': [_amortir],
			'result': {'type' : 'state', 'state': 'end'}
			 
			}
	}
wizard_amortir('amortir')
