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
import tools
import xml
class report_fr_rml_parse(report_sxw.rml_parse):
        def _add_header(self, node):
                nom=self.__class__.__name__
                try:
                    rml_head = tools.file_open('custom/'+nom+'.header.rml',subdir='addons/report_account_fr/report').read()
                except:
                    rml_head = tools.file_open('custom/corporate_rml_header.rml').read()
                head_dom = xml.dom.minidom.parseString(rml_head)
                node2 = head_dom.documentElement
                for tag in node2.childNodes:
                    if tag.nodeType==tag.ELEMENT_NODE:
                        found = self._find_node(node, tag.localName)
                        if found:
                           if tag.hasAttribute('position') and (tag.getAttribute('position')=='inside'):
                                found.appendChild(tag)
                           else:
                                found.parentNode.replaceChild(tag, found)
                return True
