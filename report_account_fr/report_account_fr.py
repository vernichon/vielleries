##############################################################################
#
# Copyright (c) 2007 EVI All Rights Reserved.
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
import time
from osv import osv, fields

class lignes(osv.osv):
	_name = "report.account.fr.lignes"
	_description = "Lignes"
	_auto = False
	_order = "annee,mois,numero"
	_columns = {
		'name': fields.many2one('account.account', 'Compte',select=True, readonly=True),
		'numero': fields.char('Numero de compte',size=64,readonly=True),
		'designation': fields.char('Designation',size=64,readonly=True,select=True),
		'debit': fields.float('Debit',readonly=True),
		'credit': fields.float('Credit',readonly=True),
		'annee': fields.char('annee',size=4,readonly=True,select=True),
		'mois': fields.char('mois',size=2,readonly=True,select=True),
	}
	def init(self, cr):
		cr.execute("""
			create or replace view report_account_fr_lignes as (
			SELECT min(line.id) as id, account_id as name,period_id, comptes.name as designation, comptes.code as numero , substring(date from 1 for 4) as annee, substring(date from 6 for 2) as mois, sum(debit)  AS debit, sum(credit) as credit ,sum(credit)-sum(debit) as solde 
			 FROM account_move_line line left join account_account comptes on (line.account_id = comptes.id) group by annee, mois,period_id,account_id,comptes.code,comptes.name )
		""")
lignes()

class parametres(osv.osv):
	_name = 'report.account.fr.parametres'
	_description = "Parametre de bilan"
	_columns = {
		'name': fields.char('variable', size=18),
		'report':fields.selection([('bilan','Bilan'),('resultat','Compte de resultat')],'Type de rappport'),
		'definition':fields.char('definition', size=256),
		'exceptions':fields.char('exceptions', size=256),
		'type':fields.selection([('S','Solde'),('D','Debit'),('C','Credit')],'Type de champ'),
		'valeur':fields.selection([('solde','Solde'),('debit','Debit'),('credit','Credit')],'valeur du champ'),
		'somme':fields.boolean('Somme')
	}
	_defaults = {
		'type': lambda *a: 'S',
		'valeur':lambda *a: 'solde',
		'somme':lambda *a: False,
		'exceptions':lambda *a:'[]'
		
	}
parametres()
