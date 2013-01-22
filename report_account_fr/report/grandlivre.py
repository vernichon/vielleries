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

class grandlivre(report_fr_rml_parse):
	listecomptes={}
	totalcompte={}
	def __init__(self, cr, uid, name, context):
		super(grandlivre, self).__init__(cr, uid, name, context)
		self.localcontext.update( {
			'time': time,
			'annee': self._annee,
			'lignes': self.lignes,
			'debut': self._debut,
			'fin': self._fin,
			'listecomptes':self.listecomptes,
			'totalcompte':self.totalcompte,
			
		})
		self.context = context
		
	def _annee(self,form):
		return self.pool.get('account.fiscalyear').read(self.cr, self.uid, form['fiscalyear'])['date_start'][:4]
	
	def _debut(self,form):
		return self.pool.get('account.fiscalyear').read(self.cr, self.uid, form['fiscalyear'])['date_start']
	
	def _fin(self,form):
		return self.pool.get('account.fiscalyear').read(self.cr, self.uid, form['fiscalyear'])['date_stop']
	
	def nomjournal(self,journal_id):
		return self.pool.get('account.journal').read(self.cr, self.uid, journal_id)['name']
	def nomcompte(self,journal_id):
		return self.pool.get('account.account').read(self.cr, self.uid, journal_id)['name']	
	def listecomptes(self, form):
		if len(form['comptes'][0][2]) >1:
			comptes= tuple(x for x in  form['comptes'][0][2])
			comptes=self.pool.get('account.account').read(self.cr, self.uid,comptes)
			comptes =tuple({'id':x['id'],'code':x['code'],'name':x['name']} for x in  comptes)
		elif  len(form['comptes'][0][2]) ==1:
			comptes=(self.pool.get('account.account').read(self.cr, self.uid,form['comptes'][0][2][0]),)
			print comptes
			comptes =tuple({'id':x['id'],'code':x['code'],'name':x['name']} for x in  comptes)
			
		else:
			comptes=self.pool.get('account.account').read(self.cr, self.uid,self.pool.get('account.account').search(self.cr, self.uid,[]))
			comptes =tuple({'id':x['id'],'code':x['code'],'name':x['name']} for x in  comptes)
		return comptes
		
	def lignes(self, form,compte):
		self.totalcompte['debit']=0
		self.totalcompte['credit']=0
		ctx = self.context.copy()
		#print comptes,variable,exception,type,champ
		annee = self.pool.get('account.fiscalyear').read(self.cr, self.uid, form['fiscalyear'])['date_start'][:4]
		if len(form['periods'][0][2]) >1:
			periode= " in "+str(tuple(x for x in  form['periods'][0][2]))
		elif len(form['periods'][0][2]) == 0:
			yperiode=self.pool.get('account.period').search(self.cr, self.uid,[('fiscalyear_id','=',form['fiscalyear'])])
			periode= " in "+str(tuple(x for x in  yperiode))
		else:
			periode = " = "+str(form['periods'][0][2][0])
		
		res=0.0
		
		requete = "select *  from account_move_line line  where account_id  =  "+str(compte )+" and period_id "+str(periode) +" order by account_id,date" 
		#~ print requete
		self.cr.execute(requete)
		res = self.cr.dictfetchall()
		soldeprog=0
		
		for ecriture in res:
			
			ecriture['journal']=self.nomjournal(ecriture['journal_id'])
			#~ print ecriture
			#~ self.totalclasse['debit']=self.totalclasse['debit'] +ecriture['debit']
			#~ self.totalclasse['credit']=self.totalclasse['credit'] +ecriture['credit']
			
			if ecriture['debit'] <> 0 :
				self.totalcompte['debit']=self.totalcompte['debit']+ ecriture['debit'] 
				ecriture['soldeprog']=soldeprog- ecriture['debit'] 
				
			elif ecriture['credit'] <> 0 :
				self.totalcompte['credit']=self.totalcompte['credit']+ecriture['credit']
				ecriture['soldeprog']=soldeprog+ecriture['credit']
				
			else:
				ecriture['soldeprog']=soldeprog
				#~ print ecriture
			soldeprog=ecriture['soldeprog']
			
			#~ else:
				#~ ecriture['sdebit'] = 0
				#~ ecriture['scredit'] = 0
		        print soldeprog	
		#~ self.totalclasse['sdebit']=-self.totalclasse['sdebit']		
		return (res)

	

report_sxw.report_sxw('report.report.account.fr.grandlivre', 'account.account','addons/report_account_fr/report/grandlivre.rml', parser=grandlivre,header=True)

