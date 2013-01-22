##############################################################################
#
# Copyright (c) 2007 Intermediasud All Rights Reserved.
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
import imssaga
import time
from osv import osv, fields

logs={}
imssaga.set_bdb_addr('213.190.68.3')
def _ims_type_get(self, cr, uid, context={}):
	obj = self.pool.get('ims.type')
	ids = obj.search(cr, uid, [])
	res = obj.read(cr, uid, ids, ['name'], context)
	return [(r['name'],r['name']) for r in res]



def affich_packet_callback(oid_box,keys,data):
	print "call back "
	return 0

imssaga.set_urgent_callback(affich_packet_callback)




def _ims_type_offre_get(self, cr, uid, context={}):
	obj = self.pool.get('ims.type.offre')
	ids = obj.search(cr, uid, [])
	res = obj.read(cr, uid, ids, ['name'], context)
	return [(r['name'],r['name']) for r in res]


def _ims_type_contrat_get(self, cr, uid, context={}):
	obj = self.pool.get('ims.type.contrat')
	ids = obj.search(cr, uid, [])
	res = obj.read(cr, uid, ids, ['name'], context)
	return [(r['name'],r['name']) for r in res]
class ims_urlaccess(osv.osv):
	_name = 'ims.urlaccess'
	_columns = {
		'date':fields.date('Date'),
		'username':fields.char('Nom d\'utilisateur', size=18,  select=True),
		'name':fields.char('URL', size=256,  select=True),
		'categorie':fields.char('Categorie', size=128,  select=True),
		'nom':fields.char('Nom', size=128,  select=True),
		'prenom':fields.char('Prenom', size=128,  select=True),
		'service':fields.char('Service', size=128,  select=True),
		'fonction':fields.char('Fonction', size=128,  select=True),
		'motif':fields.text('Motif de la demande', size=128,  select=True),
		'autorisation':fields.boolean('Autoriser', size=128,  select=True),
	}
ims_urlaccess()
class crm_case(osv.osv):
	_name = 'crm.case'
	_inherit = 'crm.case'
	_columns = {
		'appel':fields.many2one('res.partner.address', 'Initiateur', select=True),	
		'site':fields.many2one('ims.site', 'Site'),	
		'duree':fields.float('Duree'),
		}
	def __history(self, cr, uid, cases, keyword, history=False, email=False, context={}):
		for case in cases:
			data = {
				'name': keyword,
				'som': case.som.id,
				'canal_id': case.canal_id.id,
				'user_id': uid,
				'case_id': case.id
				
			}
			obj = self.pool.get('crm.case.log')
			if history and case.description:
				obj = self.pool.get('crm.case.history')
				data['description'] = case.description
				data['duree']=case.duree
				data['email'] = email or \
						(case.user_id and case.user_id.address_id and \
							case.user_id.address_id.email) or False
			obj.create(cr, uid, data, context)
		return True
crm_case()

class crm_case_history(osv.osv):
	_name = 'crm.case.history'
	_inherit = 'crm.case.history'
	_columns = {
		'duree':fields.float('Duree')
		}
crm_case_history()
class res_partner(osv.osv):
	_name = 'res.partner'
	_inherit = 'res.partner'
	_columns = {
		'mandat': fields.char('Nr Mandat', size=128,  select=True),
		'foncclient': fields.char('Fonction Client', size=128,  select=True),
		'statusclient': fields.char('Status Client', size=128,  select=True),
		'typeclient': fields.char('Type Client', size=128,  select=True),
		'etatclient':fields.selection([('acceptee','ACCEPTEE'),('refusee','REFUSEE'),('en attente','EN ATTENTE')], 'Etat Client'),
		'codeape':fields.char('Code Ape',size=12,select = True),
		'site':fields.one2many('ims.site', 'partner_id','Site'),	
		'contrat':fields.one2many('ims.contrat', 'partner_id','Contrat'),	
	}
	_defaults = {
		'etatclient': lambda *a: 'en attente',
	}
res_partner()

class res_partner_address(osv.osv):
	_name = 'res.partner.address'
	_inherit = 'res.partner.address'
	_columns = {
		'type': fields.selection( [ ('default','Default'),('invoice','Invoice'), ('delivery','Delivery'), ('contact','Contact'), ('other','Other') ,('signataire','Signataire')],'Address Type'),
	}
res_partner_address()
class ims_type_contrat(osv.osv):
	_name = 'ims.type.contrat'
	_columns = {
		'name': fields.char('Type Contrat', size=128, required=True, select=True)
	}
ims_type_contrat()

class ims_type_offre(osv.osv):
	_name = 'ims.type.offre'
	_columns = {
		'name': fields.char('Type offre', size=128, required=True, select=True)
	}
ims_type_offre()
class ims_contrat(osv.osv):
	_name = 'ims.contrat'
	_columns = {
		'name':fields.char('Identifiant Contrat', required=True,size=128,  select=True),
		'partner_id':fields.many2one('res.partner', 'Client',  select=True),	
		'sites':fields.many2many('ims.site','contrat_site_rel','contrat_id','site_id','Sites'),
		'site_id':fields.many2one('ims.site', 'Site'),
		'signataire':fields.many2one('res.partner.address', 'Signataire',  select=True),	
		'id_avenant':fields.many2one('ims.contrat','Avenant',select=True),
		'type_contrat':fields.selection(_ims_type_contrat_get, 'Type Contrat', size=32),
		'duree_contrat':fields.char('Duree Contrat', size=128),
		'date_debut_ave':fields.date('Date debut avenant'),
		'date_fin_ave':fields.date('Date fin avenant'),
		'date_abon':fields.date('Date Abonnement'),
		'objet_contrat':fields.char('Commentaire', size=256),
		'date_signature':fields.date('Date Signature'),
		'offre':fields.selection(_ims_type_offre_get, 'Type Offre', size=32),
		'apa':fields.many2one('res.partner', 'Apporteur affaire', ondelete='cascade', select=True),	
		'date_resil':fields.date('Date Resiliation'),
		'date_install':fields.date('Date Installation'),
		'date_effective':fields.date('Date Effective Installation'),
		'suivi':fields.text("suivi"),
		'mouvement':fields.one2many('stock.move', 'contrat_id','Site'),
	}
ims_contrat()

class ims_site(osv.osv):
	_name = 'ims.site'
	_recname = 'codesite'
	_columns = {
		'partner_id': fields.many2one('res.partner', 'Client', required=True, ondelete='cascade', select=True),	
		'name': fields.char('Nom du site', size=128,  select=True),
		'codesite': fields.char('Code du site', size=128, required=True, select=True),
		'ape': fields.char('Code Ape', size=4,  select=True),
		'street': fields.char('Adresse ', size=128),
		'street2': fields.char('Adresse 2', size=128),
		'bp': fields.char('Boite Postale', change_default=True, size=24),
		'zip': fields.char('Code Postal', change_default=True, size=24),
		'city': fields.char('Ville', size=128),
		'state_id': fields.many2one("res.country.state", 'Etat', domain="[('country_id','=',country_id)]"),
		'country_id': fields.many2one('res.country', 'Pays'),
		'email': fields.char('E-Mail', size=64),
		'phone': fields.char('Telephone', size=64),
		'phonecontact': fields.char('Telephone Abonne', size=64),
		'contract_id':fields.many2one('ims.contrat','ID Contrat'),
		'stock':fields.many2one('stock.location','Stock'),
		'mouvement':fields.one2many('stock.move', 'site_id','Mouvements'),
		'contrats':fields.many2many('ims.contrat','contrat_site_rel','site_id','contrat_id','Contrats'),
	}
ims_site()

class stock_move(osv.osv):
	_name = 'stock.move'
	_inherit = 'stock.move'
	_columns = {
		'site_id':fields.many2one('ims.site', 'Site'),
		'contrat_id':fields.many2one('ims.contrat', 'Contrat'),
		'mac_adress':fields.char('Mac Adress', size=128),
		'garantie':fields.char('Garantie', size=128),

	}
stock_move()
class ims_box(osv.osv):
	_name = 'ims.box'
	_inherit = 'product.product'
	_columns = {
		'attributs': fields.one2many('ims.attribut','box_id', 'Attribut', required=True, select=True),
		'logs': fields.one2many('ims.log','box_id', 'Log',  select=True),
		'identifiant': fields.char('Identifiant (OID)', size=128,  select=True),
		'date_reception':fields.date('Date de reception'),
		'client':fields.many2one('res.partner', 'Client',  select=True),	
		'site':fields.many2one('ims.site', 'Site',  select=True),	
		'fournisseur':fields.many2one('res.partner', 'Fournisseur',  select=True),	
	}
	_defaults = {
		'date_reception': lambda *a: time.strftime('%Y-%m-%d'),
	}
	def log_box(self, cr, uid, ids, context={}):
		box_oid=[]
		print uid
		print ids
		print context
		for box in self.browse(cr, uid, ids, context):
			oid_box=box.identifiant
			for val in oid_box.split('.'):
				box_oid.append(int(val))
			tabattribut=ims_box.liste_cles(self,cr,uid,ids,oid_box)
			tabcle = [eval(cle) for cle in tabattribut.keys()] # change les string en liste
			print "tabcle : "+str(tabcle)
			ret=[]
			print "Appelle Get avec : "+str(box_oid)+" "+str(tabcle)
			try:
				ret = imssaga.get(box_oid,tabcle)
				if ret:
					print "Retour Get " +str(ret)
				else:
					print "Erreur de Get"
			except Exception,e:
				print "Erreur log_box "+str(e)
			x=0
			print str(ret)
			for ligne in ret[1]:
				boxid=ids[0]
				attribut=ret[1][x]
				valeur=ret[2][x]
				print "attribut" + str(attribut)
				print str(boxid)+" "+str(tabattribut[str(attribut)])+" "+str(valeur)
				requete = "update ims_attribut set valeursaga='"+str(valeur)+"' where id="+tabattribut[str(attribut)]
				print requete
				cr.execute(requete)
				x=x+1
		return 0
	
	def liste_cles(self,cr,uid,ids,box,context={}):
		tabcle={}
		for box in self.browse(cr, uid, ids, context):
			for attribut in  box.attributs:
				attrib_id=str(attribut).split(',')[1].split(')')[0]
				cr.execute('select name,valeur from ims_attribut where id = '+attrib_id)
				retour=cr.fetchone()
				def_id= retour[0]
				cr.execute("select imsoid from ims_def_attribut where id = "+str(def_id))
				retour=cr.fetchone()
				oid=retour[0]
				cle=[]
				for val in str(oid).split('.'):
					cle.append(int(val))
				tabcle[str(cle)]=attrib_id
		return(tabcle)


	def valid_box(self, cr, uid, ids, context={}):
		box_oid=[]
		for box in self.browse(cr, uid, ids, context):
			for val in box.identifiant.split('.'):
				box_oid.append(int(val))
			print "Box ID " + str(box_oid)
			tabvaleur=[]
			tabcle=[]
			for attribut in  box.attributs:
				attrib_id=str(attribut).split(',')[1].split(')')[0]
				cr.execute('select name,valeur from ims_attribut where id = '+attrib_id)
				retour=cr.fetchone()
				def_id= retour[0]
				valeur = retour[1]
				cr.execute("select name,imsoid from ims_def_attribut where id = "+str(def_id))
				retour=cr.fetchone()
				name = retour[0]
				oid=retour[1]
				cle=[]
				for val in str(oid).split('.'):
					cle.append(int(val))
				tabcle.append(cle)
				tabvaleur.append(str(valeur))
		try:
			print "appelle imssaga.set avec " +str(box_oid)+" "+str(tabcle)+" "+str(tabvaleur)
			ret=imssaga.set(box_oid,tabcle,tabvaleur)
			if ret:
				print "Retour imssaga.set "+str(ret) 
		except Exception,e:
			print "Erreur Valid_Box "+str(e)
		return 1			

ims_box()

class ims_log(osv.osv):
	_name = 'ims.log'
	_columns = {
		'name': fields.char('Log', size=128,  select=True),
		'box_id':fields.many2one('ims.box','Ref Box',select=True),
		'log': fields.char('Valeur', size=256,  select=True),
	}
	_defaults = {
		'name': lambda *a: 'log',
	}
ims_log()
class ims_def_attribut(osv.osv):
	_name = 'ims.def.attribut'
	_columns = {
		'name': fields.char('Attribut', size=128, required=True, select=True),
		'designation': fields.char('Designation', size=128, required=True, select=True),
		'typeattribut': fields.selection(_ims_type_get, 'Type', size=32),
		'taille': fields.char('Taille', size=10, select=True),
		'imsoid': fields.char('OID', size=128, required=True, select=True),
		'defaut': fields.char('Valeur par defaut', size=128),
		'valeur': fields.char('Valeur', size=128)
	}
	_defaults = {
	}
ims_def_attribut()
	
class ims_attribut(osv.osv):
	_name = 'ims.attribut'
	_columns = {
		'name': fields.many2one('ims.def.attribut','Attribut',select=True),
		'box_id':fields.many2one('ims.box','Ref Box',select=True),
		'valeur': fields.char('Valeur', size=128),
		'valeursaga':fields.char('valeur base', size=128),
	}
	_defaults = {
	}
ims_attribut()




class ims_type(osv.osv):
	_name = 'ims.type'
	_columns = {
		'name': fields.char('Type Attribut', size=128, required=True, select=True)
	}
ims_type()

class report_category_client(osv.osv):
    _name = "report.category.client"
    _description = "Categorie Client"

    _auto = False
    _columns = {
        'name': fields.many2one('res.partner.category', 'Categorie', readonly=True),
	'client': fields.many2one('res.partner', 'Client', readonly=True),
        
    }
    _order = 'name'
    def init(self, cr):
        cr.execute("""
            create or replace view report_category_client as (
                SELECT cat.id, cat.id as name, p.id AS client
   FROM res_partner_category cat
   LEFT JOIN res_partner_category_rel rel ON rel.category_id = cat.id
   RIGHT JOIN res_partner p ON rel.partner_id = p.id 
  WHERE p.id > 1 group by cat.id,p.id
            )
        """)
report_category_client()



