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

class bilan(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(bilan, self).__init__(cr, uid, name, context)
		self.localcontext.update( {
			'time': time,
			'annee': self._annee,
			'chargement': self.chargement,
			'set_variable': self.set_variable,
			'resultat': resultat(cr,uid,name,context)
		})
		self.context = context
		
	def chargement(self,form):
			requete = "select name,definition,exceptions,valeur,type,somme from report_account_fr_parametres where somme = 'f' and report = 'bilan'"
			self.cr.execute(requete)
			resultats =self.cr.dictfetchall()
			for champresultat in resultats:
				self.donnees(form,eval(champresultat['definition']),champresultat['name'],eval(champresultat['exceptions']),champresultat['type'],champresultat['valeur'])
			requete = "select name,definition,exceptions,valeur,type,somme from report_account_fr_parametres where somme = 't' and report = 'bilan'"
			self.cr.execute(requete)
			resultats =self.cr.dictfetchall()
			#print "requete somme",resultats
			for champresultat in resultats:
				variable=champresultat['name']
				res =self.somme(eval(champresultat['definition']))
				self.set_variable(variable,res)
				
			print "Fin chargement des variables"

			
	def _annee(self,form):
		print form
		return self.pool.get('account.fiscalyear').read(self.cr, self.uid, form['fiscalyear'])['date_start'][:4]
	
	def set_variable(self,variable,valeur):
		self.localcontext.update({variable:valeur})
		#print "set variable ",variable,valeur
		#return valeur

	def get_variable(self,variable):
		return self.localcontext[variable]

	def somme(self,variables):
		res=0
		for variable in variables:
			res=res +self.localcontext[variable]
		return int(round(res))

	# comptes : comptes a additionner
	#type : S = solde D = debit C = credit
	# variable: variable ou stoker la valeur
	#exeption : compte a exclure
	#champ  valeur  a retourner solde,debit,credit
	def donnees(self, form,comptes,variable="x",exception=[],type="S",champ="solde"):
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
		if type== "S":
			compte_recherche="("
			for compte in comptes:
				compte_recherche += "numero like '"+compte+"%'  or "
			compte_recherche = compte_recherche[:-3]+")"
			if len(exception)>0:
				compte_recherche = compte_recherche+" and ("
				for compte in exception:
					compte_recherche += "numero not like '"+compte+"%'  and "
				compte_recherche = compte_recherche[:-4]+")"
			requete = "select sum("+champ+") as resultat  from report_account_fr_lignes where "+compte_recherche+" and period_id "+str(periode)
			#print requete
			self.cr.execute(requete)
			res = self.cr.dictfetchall()[0]['resultat']
		if type == "D" or type == "C":
			print "Comptes : ", comptes
			for compte in comptes:
				exceptions=""
				#print "exception ", len(exception), exception
				if  exception:
					exceptions="and "
					for compte_except in exception:
						exceptions += "numero not like '"+compte_except+"%'  and "
					exceptions = exceptions[:-4]
				requete = "select sum("+champ+") as resultat,numero  from report_account_fr_lignes where numero like '"+compte+"%' "+exceptions+" and period_id "+str(periode) +" group by numero"
		#		print requete
				self.cr.execute(requete)
				resultats =self.cr.dictfetchall()
		#		print "Resultats ",resultats,
				for resultat in resultats:
					#print "resultat",resultat['resultat'],type
					if type == "D" and (resultat['resultat'] < 0.0):
					#	print "res ",res
						res+= resultat['resultat']
					#	print "res debit"
					if type == "C" and resultat['resultat'] > 0.0:
						res+= resultat['resultat']
					#	print "res credit"
		if not res:
			res=0.0
		
		self.set_variable(variable, res)
		return int(round(res))

	

report_sxw.report_sxw('report.report.account.fr.bilan', 'report.account.fr.lignes','addons/report_account_fr/report/bilan.rml', parser=bilan, header=False)

