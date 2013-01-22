##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: synchronize.py 5003 2006-12-27 09:01:28Z ced $
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

import sys
if sys.version_info[:2] < (2, 4):
	from sets import Set as set

import time
import ldap
import ldap.modlist

import wizard
import pooler



def terp2ldap(data):
	res = {}
	for ldap_name, terp in LDAP_TERP_MAPPER.items():
		if callable(terp) and terp(data):
			res[ldap_name] = [terp(data)]
		elif isinstance(terp, basestring) and data[terp]:
			res[ldap_name] = ['%s' % data[terp]]
	return res

def get_lastname(dico):
	lnames = dico['name'].split(' ', 1)[1:]
	if lnames:
		return ' '.join(lnames)
	else:
		return dico['name']

def get_street(dico):
	return ' '.join([dico[x] for x in ('street', 'street2') if dico[x]])

def get_name(attribute):
	def func(dico):
		return dico[attribute][1]
	return func
def get_modifytime():
	return time.strftime("%Y%m%d%H%M%SZ")
field_mapper = {
		'cn': 'name',
		'sn': 'name',
		'displayName': 'name',
		'mail': 'email',
		'telephoneNumber': 'phone',
		'o':'o',
		'street': 'street',
		'postalcode': 'zip',
		'l': 'city',
		'modifyTimestamp':'modifytime'

		}

LDAP_TERP_MAPPER = {
		'displayName': 'name',
		'mail': 'email',
		'o': get_name('partner_id'),
		'telephoneNumber': 'phone',
		'street': get_street,
		'postalcode': 'zip',
		'l': 'city',
		'cn': 'name',
		'sn': get_lastname,
		'uid': 'id',
		}


class sync_ldap(wizard.interface):
	
	_login_arch = '''<?xml version="1.0" ?>
	<form string="LDAP Credentials">
		<field name="ldap_host"  colspan="4" />
	</form>
	'''

	_login_fields = {
			'ldap_host': {'string':'Serveur Ldap','type':'many2one','relation':'server_ldap.server'},
		}
	def _do_sync(self, cr, uid, data, context):
		ldap_server = pooler.get_pool(cr.dbname).get('server_ldap.server').read(cr,uid,data['form']['ldap_host'])
		l = ldap.open(ldap_server['server_ldap'])
		l.simple_bind_s(ldap_server['bind_dn'], ldap_server['password'])
		ldap_objs = dict(l.search_s(ldap_server['base_dn'], ldap.SCOPE_ONELEVEL, 'objectclass=*', LDAP_TERP_MAPPER.keys()))
		address = pooler.get_pool(cr.dbname).get('res.partner.address')
		terp_objs = dict([('uid='+str(x['id'])+','+ldap_server['base_dn'], x) for x in address.read(cr, uid, address.search(cr, uid, [])) ])
		print "terp objs ",terp_objs
		ldap_set = [x for x in ldap_objs.keys()]
		print "ldap objets ",ldap_set
		terp_set = terp_objs.keys()
		for to_delete in ldap_set:
			if to_delete in terp_set:      
				continue                                         # la valeur ldap existe dans terp
			print "A Supprimer ", to_delete
			l.delete(to_delete) # la valeur ldap n'existe pas dans terp supression dans ldap
		for to_add in terp_set:
			if to_add in ldap_set:
				continue     # la valeur terp existe dans ldap
			new_dn = to_add #'uid=%s,%s' % (to_add, ldap_server['base_dn'])  #  il est necessaire de le creer dans tiny
			print "new dn ",new_dn
			ldap_data = {'objectclass' : ['organizationalPerson', 'inetOrgPerson']}
			ldap_data.update(terp2ldap(terp_objs[to_add]))
			print "ldap_data ",ldap.modlist.addModlist(ldap_data)
			l.add_s(new_dn, ldap.modlist.addModlist(ldap_data))
			id_add = new_dn.split(',')[0].split('=')[1]
			print "id_add ",id_add
			print "new_dn ",new_dn
			address.write(cr, uid, [int(id_add)], {'dn' : new_dn})
		for to_update in terp_set:
			if to_update not in ldap_set:
				continue               # l'attribut exite dans  ldap
			current_dn = to_update   #  il est necessaire de le modifier dans ldap
			modlist = ldap.modlist.modifyModlist(ldap_objs[current_dn], terp2ldap(terp_objs[to_update]))
			if modlist:
				l.modify_s(current_dn, modlist)
		return {}

	states = {
		'init' : {
			'actions' : [],
			'result' : {
				'type' : 'form',
				'arch' : _login_arch,
				'fields' : _login_fields,
				'state' : (('end', 'Cancel'),('sync', 'Synchronize'))
				},
		},
		'sync' : {
			'actions' : [ _do_sync ],
			'result' : { 'type' : 'state', 'state' : 'end' },
		},
	}


sync_ldap('sync_ldap')

class ldap_sync(wizard.interface):
	
	_login_arch = '''<?xml version="1.0" ?>
	<form string="LDAP Credentials">
		<field name="ldap_host"  colspan="4" />
		
	</form>
	'''

	_login_fields = {
			'ldap_host': {'string':'Serveur Ldap','type':'many2one','relation':'server_ldap.server'},
		}
	def _do_sync(self, cr, uid, data, context):
		ldap_server = pooler.get_pool(cr.dbname).get('server_ldap.server').read(cr,uid,data['form']['ldap_host'])
		l = ldap.open(ldap_server['server_ldap'])
		l.simple_bind_s(ldap_server['bind_dn'], ldap_server['password'])
		ldap_objs = l.search_s(ldap_server['base_dn'], ldap.SCOPE_ONELEVEL, 'objectclass=*', field_mapper.keys())
		for obj in ldap_objs:
			address = pooler.get_pool(cr.dbname).get('res.partner.address')
			partner = pooler.get_pool(cr.dbname).get('res.partner')
			if obj[1].has_key('displayName'): # si displayName exite prendre displayName comme nom
				name = obj[1]['displayName'][0]
			else:							# sinon prendre cn
				name = obj[1]['cn'][0]
			
			uid_liste= l.search_s(str(obj[0]), ldap.SCOPE_SUBTREE, 'objectclass=*',['uid'])
			res=""
			if uid_liste[0][1].has_key('uid'):
				uid_recherche = [int(x) for x in uid_liste[0][1]['uid']][0]
				
				print "recherche uid: ",uid_recherche
				res=address.search(cr, uid,[('id','=',uid_recherche)])
			else:
				print "recherche adresse de : ",name
				res=address.search(cr, uid,[('name','=',name)])
			print "adresse tiny = ",res
			if not res:
				print "resultat de  recherche ldap ",obj[1]
				if obj[1].has_key('o'):
					partner_id=partner.search(cr, uid,[('name','=',obj[1]['o'][0])])
					print "recherche partner",obj[1]['o'][0],partner_id
					if not partner_id:
						partner_id=partner.create(cr,uid,{'name':obj[1]['o'][0]})
					else:
						partner_id=partner_id[0]
					
					data={}
					for champ in field_mapper.keys():
						if obj[1].has_key(champ) and champ <> "o":
							data.update({field_mapper[champ]:obj[1][champ][0]})
					data.update({'partner_id':partner_id})
					data.update({'name':name})
					data.update({'dn':obj[0]})
						
					print "data pour creation addresse = ",data
					address_id=address.create(cr,uid,data)
					print "Adresse tiny créé",address_id
					dn=str(obj[0])
					#~ uids= l.search_s(dn, ldap.SCOPE_SUBTREE, 'objectclass=*',['uid'])     # Supressions des uid existant
					#~ if uids[0][1].has_key('uid'):
						#~ for uid in uids[0][1]['uid']:
							#~ print "uid a supprimer ",uid,dn
							#~ l.modify_s(dn,[(1, 'uid', uid)])
						#~ print l.search_s(dn, ldap.SCOPE_SUBTREE, 'objectclass=*',['uid']) 
					
					#~ l.modify_s(dn,[(0, 'uid',[str(address_id)])])
					newrdn='uid='+str(address_id)
					l.modrdn(dn,newrdn,0)
				else:
					print "Société non renseigné dans ldap"
			else:
				print  "l'adresse existe"
		return {}

	states = {
		'init' : {
			'actions' : [],
			'result' : {
				'type' : 'form',
				'arch' : _login_arch,
				'fields' : _login_fields,
				'state' : (('end', 'Cancel'),('sync', 'Synchronize'))
				},
		},
		'sync' : {
			'actions' : [ _do_sync ],
			'result' : { 'type' : 'state', 'state' : 'end' },
		},
	}


ldap_sync('ldap_sync')

# vim:noexpandtab:
