# -*- coding:Utf-8 -*- 
##############################################################################
#
# Copyright (c) 2007 EVI (http://www.vernichon.fr) All Rights Reserved.
#
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

from osv import osv, fields
import time
import datetime
import pooler
class knowledge_folder(osv.osv):
	_name = "knowledge.folder"
	_description = 'knowledge folder'
	_columns = {
		'name':fields.char('Nom',size=254),
		'ref':fields.char('ref ox',size=12),
		'parent_id':fields.many2one('knowledge.folder','Dossier Parent')
	}
knowledge_folder()
class knowledge_knowledge(osv.osv):
	_name = "knowledge.knowledge"
	_description = 'knowledge'
	_columns = {
		'name': fields.char('Title', size=254, required=True, select=1),
		'connaissance':fields.text('Connaissance'),
		'dossier_id':fields.many2one('knowledge.folder','Dossier'),
		'redacteur':fields.many2one('res.users','redacteur'),
	}
	_defaults = {
		'redacteur':  lambda object,cr,uid,context: uid,
	}
	
knowledge_knowledge()

