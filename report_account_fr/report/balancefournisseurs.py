# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 EVI.  All Rights Reserved.
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
from report import report_sxw
from resultat import resultat
from rml_parse import report_fr_rml_parse
class balancefournisseurs(report_fr_rml_parse):
	totalclasse={}
	
	def __init__(self, cr, uid, name, context):
		super(balancefournisseurs, self).__init__(cr, uid, name, context)
		self.localcontext.update( {
			'time': time,
			'annee': self._annee,
			'lignes': self.lignes,
			'debut': self._debut,
			'fin': self._fin,
			'totalclasse': self.totalclasse
		})
		self.context = context
		
	def _annee(self,form):
		return self.pool.get('account.fiscalyear').read(self.cr, self.uid, form['fiscalyear'])['date_start'][:4]
	def _debut(self,form):
		return self.pool.get('account.fiscalyear').read(self.cr, self.uid, form['fiscalyear'])['date_start']
	def _fin(self,form):
		return self.pool.get('account.fiscalyear').read(self.cr, self.uid, form['fiscalyear'])['date_stop']
	def lignes(self, form,classe=None):
		classe='401'
		self.totalclasse['debit']=0
		self.totalclasse['credit']=0
		self.totalclasse['sdebit']=0
		self.totalclasse['scredit']=0
		ctx = self.context.copy()
		#print comptes,variable,exception,type,champ
		annee = self.pool.get('account.fiscalyear').read(self.cr, self.uid, form['fiscalyear'])['date_start'][:4]
#		if len(form['periods'][0][2]) >1:
#			periode= " in "+str(tuple(x for x in  form['periods'][0][2]))
#		elif len(form['periods'][0][2]) == 0:
		yperiode=self.pool.get('account.period').search(self.cr, self.uid,[('fiscalyear_id','=',form['fiscalyear'])])
		periode= " in "+str(tuple(x for x in  yperiode))
#		else:
#			periode = " = "+str(form['periods'][0][2][0])
		
		res=0.0
		if classe:
			requete = "select numero,sum(debit) as debit,sum(credit) as credit,designation,sum(solde) as solde  from report_account_fr_lignes where numero like '"+classe+"%' and period_id "+str(periode) +" group by numero,designation order by numero " 
			self.cr.execute(requete)
			res = self.cr.dictfetchall()
			for ecriture in res:
				self.totalclasse['debit']=self.totalclasse['debit'] +ecriture['debit']
				self.totalclasse['credit']=self.totalclasse['credit'] +ecriture['credit']
				if ecriture['solde'] < 0 :
					ecriture['sdebit'] = ecriture['solde']
					ecriture['scredit'] = 0
					self.totalclasse['sdebit']=	self.totalclasse['sdebit']+ecriture['sdebit']
				elif ecriture['solde'] > 0 :
					ecriture['scredit'] = ecriture['solde']
					ecriture['sdebit'] = 0
					self.totalclasse['scredit']=	self.totalclasse['scredit']+ecriture['scredit']
				else:
					ecriture['sdebit'] = 0
					ecriture['scredit'] = 0
			self.totalclasse['sdebit']=-self.totalclasse['sdebit']		
		return (res)

	

report_sxw.report_sxw('report.report.account.fr.balancefournisseurs', 'report.account.fr.lignes','addons/report_account_fr/report/balancefournisseurs.rml', parser=balancefournisseurs,header=True)

