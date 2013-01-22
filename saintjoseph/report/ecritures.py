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

class ecritures(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ecritures, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'journal':self.journal,
            'periode':self.periode,
            'sum_debit':self.sum_debit,
            'sum_credit':self.sum_credit,
            'solde':self.solde,
        })
        self.context = context
        return None
    def journal(self,o):
        return  self.pool.get('account.journal').read(self.cr, self.uid, o.journal_id[0]['id'])['name']
    def periode(self,o):
        return  self.pool.get('account.period').read(self.cr, self.uid, o.period_id[0]['id'])['name']
    def sum_debit(self,o):
        somme = 0.0
        for line in o:
            somme= somme + line['debit']
        return somme
    def sum_credit(self,o):
        somme = 0.0
        for line in o:
            somme= somme + line['credit']
        return somme
    def solde(self,o):
        return self.sum_debit(o)-self.sum_credit(o)

    
report_sxw.report_sxw('report.saintjoseph.ecritures.report', 'account.move.line','addons/saintjoseph/report/ecritures.rml', parser=ecritures, header=False)

