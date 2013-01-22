import time
from osv import osv, fields

class compte_annuel(osv.osv):
    _name = "compte.annuel"
    _description = "Compte Annuel"
    _auto = False
    _order = "annee,name"
    _columns = {
		'name': fields.many2one('account.account', 'Compte', readonly=True),
		'debit': fields.float('Debit',readonly=True),
		'credit': fields.float('Credit',readonly=True),
		'annee': fields.char('annee',size=4,readonly=True),
    }
    def init(self, cr):
        cr.execute("""
            create or replace view compte_annuel as (
                SELECT min(account_move_line.id) as id, account_id as name, substring(date from 1 for 4) as annee, sum(debit)  AS debit, sum(credit) as credit
   FROM account_move_line group by annee, account_id 
            )
        """)
compte_annuel()

