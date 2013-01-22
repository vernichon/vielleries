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
import datetime

from report import report_sxw
class factures(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(factures, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'periode':self.periode,
            'lesfactures':self.lesfactures,
            'total':self.total,
        })
        self.context = context
        return None
    
    def periode(self,form):
        return self.pool.get('account.period').read(self.cr, self.uid,form['periode'],['name'])['name']

    def total(self,form):
        total=0
        fact_ids=self.pool.get('account.invoice').search(self.cr, self.uid,[('period_id','=',form['periode'])])
        res=[]
        for fact in fact_ids:
            fact_lu=  self.pool.get('account.invoice').read(self.cr, self.uid,fact,[])
            total=total+fact_lu['amount_total']
        return total

    def lesfactures(self,form):
        fact_ids=self.pool.get('account.invoice').search(self.cr, self.uid,[('period_id','=',form['periode'])])
        res=[]
        for fact in fact_ids:
            fact_lu=  self.pool.get('account.invoice').read(self.cr, self.uid,fact,[])
            res.append({'amount_total':fact_lu['amount_total'],'name':fact_lu['name'],'date_invoice':fact_lu['date_invoice']})

        res.sort(lambda x, y: cmp(x['name'],y['name']))
        return res

    
report_sxw.report_sxw('report.saintjoseph.factures.report', 'account.invoice','addons/saintjoseph/report/factures.rml', parser=factures, header=False)

