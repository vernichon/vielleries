##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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

from osv import fields
from osv import osv
import ir
import pooler


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    
    _columns = {
        'calculate_price': fields.boolean('Compute price'),
    }

    _defaults = {
        'calculate_price': lambda w,x,y,z: False,
    }

    def compute_price(self, cr, uid, ids, *args):
        for prod_id in ids:
            bom_ids = pooler.get_pool(cr.dbname).get('mrp.bom').search(cr, uid, [('product_id', '=', prod_id)])
            if bom_ids:
                for bom in pooler.get_pool(cr.dbname).get('mrp.bom').browse(cr, uid, bom_ids):
                    print bom
                    self._calc_price(cr, uid, bom)
        return True
                    
    def _calc_price(self, cr, uid, bom):
        if not bom.product_id.calculate_price:
            return bom.product_id.list_price
        else:
            price = 0
            if bom.bom_lines:
                for sbom in bom.bom_lines:
                    price += self._calc_price(cr, uid, sbom) * sbom.product_qty
            else:
                bom_obj = pooler.get_pool(cr.dbname).get('mrp.bom')
                no_child_bom = bom_obj.search(cr, uid, [('product_id', '=', bom.product_id.id), ('bom_id', 'is', None)])
                if no_child_bom:
                    other_bom = bom_obj.browse(cr, uid, no_child_bom)[0]
                    price += bom.product_qty * self._calc_price(cr, uid, other_bom)
                else:
                    price += bom.product_qty * bom.product_id.list_price
                
            if bom.routing_id:
                for wline in bom.routing_id.workcenter_lines:
                    wc = wline.workcenter_id
                    cycle = wline.cycle_nbr
                    hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) *  (wc.time_efficiency or 1.0)
                    price += wc.costs_cycle * cycle + wc.costs_hour * hour
            if bom.bom_lines:
                self.write(cr, uid, [bom.product_id.id], {'list_price' : price})
            return price
product_product()
