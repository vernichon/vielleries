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
class account_move_line(osv.osv):
        _inherit = 'account.move.line'
        _columns = {
                            'asset_id': fields.many2one('asset.immobilisation', 'Asset'),
            }
        def create(self, cr, uid,  vals, context=None,check=True):
            print vals
            pool = pooler.get_pool(cr.dbname)
            id=super(account_move_line,self).create(cr, uid, vals,context,check)

            compte = pool.get('account.account').read(cr,uid,vals['account_id'])
            ncompte=int(compte['code'][:2])
            if ncompte>=20 and ncompte <=27:
                print "cree immo"
                asset = pool.get('asset.immobilisation')
                asset_record= {'name':vals['name'],'nordre':vals['date']+'-'+str(id),'date':vals['date'],'compteimmo':vals['account_id'],'base':vals['debit']}
                asset.create(cr,uid,asset_record)

            return id


account_move_line()

#class account_move_line(osv.osv):
#    _inherit = "account.move.line"
#    _columns = {
#                'asset_id':fields.integer('Numero d\'immobilisation'),
#            }
#account_move_line()
#class account_invoice_line(osv.osv):
#    _inherit = "account.invoice.line"
#    def write(self, cr, uid, ids, vals, context=None):
#        super(account_invoice_line,self).write( cr, uid, ids, vals, context)
#        pool = pooler.get_pool(cr.dbname)
#        ligne = pool.get('account.invoice.line').read(cr,uid,ids[0])
#        data={}
#        data ['ids']=ids
#        act_ids=pool.get('account.account').search(cr,uid,[('code','like','2%')])
#        
#        if ligne['account_id'][0] in act_ids:
#            from wizard.amortir_line import _amortir
#            data['form']={}
#            data['form']['cpt_actif'] =pool.get('account.account').search(cr,uid,[('code','=','68111')])[0]
#            data['form']['cpt_amort'] =pool.get('account.account').search(cr,uid,[('code','=','208')])[0]
#            data['form']['methode']= 'linear'
#            data['form']['duree']= 5
#            data['form']['facteur']= 1
#            _amortir(self,cr,uid,data,context)
#            
#    def create(self, cr, uid,  vals, context=None):
#        ids=super(account_invoice_line,self).create( cr, uid, vals, context)
#        ids=[ids]
#        pool = pooler.get_pool(cr.dbname)
#        ligne = pool.get('account.invoice.line').read(cr,uid,ids[0])
#        data={}
#        data ['ids']=ids
#        act_ids=pool.get('account.account').search(cr,uid,[('code','like','2%')])
#        
#        if ligne['account_id'][0] in act_ids:
#            from wizard.amortir_line import _amortir
#            data['form']={}
#            data['form']['cpt_actif'] =pool.get('account.account').search(cr,uid,[('code','=','68111')])[0]
#            data['form']['cpt_amort'] =pool.get('account.account').search(cr,uid,[('code','=','208')])[0]
#            data['form']['methode']= 'linear'
#            data['form']['duree']= 5
#            data['form']['facteur']= 1
#            _amortir(self,cr,uid,data,context)  
#                
#        
#account_invoice_line()

""" Brouillons"""
class asset_simulation(osv.osv):
    _name = 'asset.simulation'
    _description = 'Asset'
    def _get_period(self, cr, uid, context={}):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False
    def valider(self, cr, uid, ids, context={}):
        pool = pooler.get_pool(cr.dbname)
        date=pool.get('account.fiscalyear').read(cr,uid,context['fy_id'])['date_stop']
        print "date ",date
        annee_courante=int(date[:4])
        for id  in ids:
            immo_sim = pool.get('asset.simulation').read(cr, uid,id )
            
            entree_sim_id=pool.get('asset.simulation.amort').search(cr,uid,[('asset_id','=',id),('name','=',str(annee_courante-1))])
            print "entree_sim_id ", entree_sim_id,annee_courante-1
            entree_sim=pool.get('asset.simulation.amort').read(cr, uid,entree_sim_id )
            if entree_sim :
                entree_sim=entree_sim[0]
                print "entree sim ",entree_sim
                immo ={'name':immo_sim['name'],'nordre':immo_sim['nordre'],'compteimmo':immo_sim['compteimmo'][0],'compteamort':immo_sim['compteamort'][0],'comptedepreciation':immo_sim['comptedepreciation'][0],
                       'journal_id':immo_sim['journal_id'][0],'comptefournisseur':immo_sim['comptefournisseur'][0],'date':immo_sim['date'],'base':immo_sim['base'],'methode':immo_sim['methode'],
                       'duree':immo_sim['duree'],'coef':immo_sim['coefd']}
                print "immo ",immo
                immo_id = pool.get('asset.immobilisation').create(cr, uid,immo )
                achats={'asset_id':immo_id,'date':immo_sim['date'],'operation':'Achats','credit':immo_sim['base'],'debit':0.0,'vnc':immo_sim['base'],'drestante':immo_sim['duree']}
                achats_id = pool.get('asset.amortissement').create(cr, uid,achats )
                dureerestante=0.0
                annee=int(immo['date'][0:4])
                mois=int(immo['date'][5:7])
                if immo['methodefisc']=='1' :
                    dureeamorti = (((datetime.datetime(int(date[0:4]),int(date[5:7]),int(date[8:10]))-datetime.datetime(annee,mois,jour)).days+1)/365.0)-1
                else:
                    dureeamorti=((((int(date[0:4])-annee)*360)+((12-mois)*30))/360.0)-1
                dureerestante =immo['duree']-dureeamorti
                date_cumul='31.12.'+str(annee_courante-1)
                print date_cumul
                cumul={'asset_id':immo_id,'date':date_cumul,'operation':'Cumul','credit':0,'debit':(immo_sim['base']-entree_sim['vresiduelle']),'vnc':entree_sim['vresiduelle'],'drestante':dureerestante}
                cumul_id = pool.get('asset.amortissement').create(cr, uid,cumul )
        #for asset_calc in pool.getself.browse(cr, uid, ids, context):
        #    print asset_calc,context

    def calculer(self, cr, uid, ids, context={}):
        pool = pooler.get_pool(cr.dbname)
        entree=pool.get('asset.simulation.amort').search(cr,uid,[('asset_id','=',ids[0])])
        pool.get('asset.simulation.amort').unlink(cr, uid,entree )
        for asset_calc in self.browse(cr, uid, ids, context):
            if asset_calc['methode'] == 'linear':    # méthode linéaire
                print "Linéaire"
                cumul = 0
                base=asset_calc['base']
                residuel = base # residuel = valeur d'acquisition
                annuite = 0
                for an in range(int(asset_calc['date'][:4]), int(asset_calc['date'][:4])+asset_calc['duree']+1):
                    methode="Linéaire"
                    vcndeb=residuel       # valeur comptable nette = résiduel
                    residuelprecedent=residuel
                    txl=1.0/int(asset_calc['duree']) # taux linéaire = 1 /duree amort 
                    txd=1.0/int(asset_calc['duree'])*float(asset_calc['coefd'])    
                    
                    annee=int(asset_calc['date'][0:4]) 
                    mois=int(asset_calc['date'][5:7])
                    jour=int(asset_calc['date'][8:10])
                    if asset_calc['methodefisc']=='1' :
                        nbrjour=365 #(datetime.datetime(annee,12,31)-datetime.datetime(annee,1,1)).days+1
                    else:
                        nbrjour = 360
                    if an==int(asset_calc['date'][:4]):  # première année calcul prorata temporis
                        print "Methode Fiscale ",asset_calc['methodefisc']
                        if asset_calc['methodefisc']== '0':
                            #ecartj=((datetime.datetime(annee,mois+1,1)- datetime.timedelta(days=1))-datetime.datetime(annee,mois,jour)).days
                            ecartm = 12-mois+1
                            ecart = (ecartm*30)#-ecartj
                            print "Ecart ",ecartm,ecart
                        else:
                            ecart =(datetime.datetime(annee,12,31)-datetime.datetime(annee,mois,jour)).days+1
                            if ecart > 365:
                                ecart= 365
                            print "Ecart", ecart
                        
                        annuite =base * txl * ecart/nbrjour
                        cumul=cumul+annuite
                        residuel=residuel-annuite
                        print "Première année" ,an, annuite,cumul,residuel,ecart
                    #elif an==int(asset_calc['date'][:4])+int(asset_calc['duree']):
                    #    ecart =((datetime.datetime(annee,12,31)-datetime.datetime(annee,mois,jour)).days)+1
                    #    annuite =base * txl * (nbrjour-ecart)/nbrjour
                    #    cumul=cumul+annuite
                    #    residuel=residuel-annuite
                    #    print "Dernière année", an, annuite,cumul,residuel,ecart
                    else:
                        annuite =asset_calc['base'] * 1 / asset_calc['duree']
                        if annuite > residuel:
                            annuite=residuel
                        cumul=cumul+annuite
                        residuel=residuel-annuite
                        print an, annuite,cumul,residuel,ecart
                    vcnfin=residuelprecedent-annuite # valeur nette comptable fin = residuel - annuité
                    vresiduelle=asset_calc['base'] -cumul
                    data_amort={'name':an ,'vresiduelle':vresiduelle,'vcnfin':vcnfin,'vcndebut':vcndeb,'asset_id':asset_calc['id'],'methode':methode,'txd':txd,'txl':txl,'annuites':annuite,'cumul':cumul}
                    pool.get('asset.simulation.amort').create(cr, uid,data_amort)
                    if residuel == 0:
                        break 
                    
            if asset_calc['methode'] == 'degressif':
                print "degressif"
                    
                cumul = 0
                base=asset_calc['base']
                residuel = base
                annuite = 0
                for an in range(int(asset_calc['date'][:4]), int(asset_calc['date'][:4])+asset_calc['duree']):
                    vcndeb=residuel
                    residuelprecedent=residuel
                    txd=1.0/int(asset_calc['duree'])*float(asset_calc['coefd']) # taux dégressif = 1 /duree amort * coef dégressif
                    dureeRestante=int(asset_calc['date'][:4])+asset_calc['duree']-an
                    txl=1.0/dureeRestante
                    annee=int(asset_calc['date'][0:4])
                    mois=int(asset_calc['date'][5:7])
                    jour=int(asset_calc['date'][8:10])
                    if asset_calc['methodefisc']==1 :
                        nbrjour=(datetime.datetime(annee,12,31)-datetime.datetime(annee,1,1)).days+1
                    else:
                        nbrjour = 360
                    if an==int(asset_calc['date'][:4]): # première année calcul prorata temporis
                        methode="Dégressif"
                        ecart =(datetime.datetime(annee,12,31)-datetime.datetime(annee,mois,jour)).days
                        print "ecart",ecart,txl,txd
                        annuite =base *  txd*ecart/12.0
                        cumul=cumul+annuite
                        residuel=residuel-annuite
                        print an, annuite,cumul,residuel
                    elif txd>txl:
                        methode="Dégressif"
                        ecart =(datetime.datetime(annee,12,31)-datetime.datetime(annee,mois,jour)).days
                        annuite =residuel* txd
                        cumul=cumul+annuite
                        residuel=residuel-annuite
                        print an, annuite,cumul,residuel
                    else:
                        methode="Linéaire"
                        annuite =residuel* txl
                        cumul=cumul+annuite
                        residuel=residuel-annuite
                    #else:
                    #   annuite =asset_calc['base'] * 1 / asset_calc['duree']
                    #   cumul=cumul+annuite
                    #   residuel=residuel-annuite
                    #   print an, annuite,cumul,residuel
                    vcnfin=residuelprecedent-annuite
                    vresiduelle=asset_calc['base'] -cumul
                    data_amort={'name':an ,'vcnfin':vcnfin,'vcndebut':vcndeb,'asset_id':asset_calc['id'],'methode':methode,'txd':txd,'txl':txl,'annuites':annuite,'cumul':cumul,'vresiduelle':vresiduelle}    
                    pool.get('asset.simulation.amort').create(cr, uid,data_amort)  
        return False
    _columns = {
        'name': fields.char('Désignation', size=64, required=True, select=1),
        'nordre':fields.integer('Numéro d\'ordre'),
        'compteimmo':fields.many2one('account.account', 'Compte d\'immobilisation',required=True),
        'compteamort':fields.many2one('account.account', 'Compte d\'amortissement'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'comptedepreciation':fields.many2one('account.account', 'Compte de depreciation'),
        'comptefournisseur':fields.many2one('account.account', 'Compte Fournisseur',required=True),
        'date': fields.date('Date d\'acquisition', required=True, select=1),
        'base': fields.float('Coût d\'acquisition',required=True),
        'methode': fields.selection([('linear','Linéaire'),('degressif','Dégressif'),('exceptionnel','Exceptionnel')], 'Type d\'amortissement', required=True),
        'methodefisc': fields.selection([('0','30 Jours par mois / 360 jours par an'),('1','Jour réels /365 par an')], 'Méthode Fiscale', required=True),
        'coefd': fields.float('Coefficient Dégressif',required=True),
        'duree':fields.integer('Durée'),
        'amortissement':fields.one2many('asset.simulation.amort', 'asset_id','Amortissement'),
        'lignefacture':fields.many2one('account.invoice.line', 'Ligne de facture'),
        'notes': fields.char('Notes',size=256)
    }
    _defaults = {
        'coefd':  lambda *a:1,
        'methode':lambda *a: 'linear',
        'methodefisc':lambda *a: 1,
    }
    
asset_simulation()

class asset_simulation_amort(osv.osv):
    _name = 'asset.simulation.amort'
    _description = 'Asset'
    def _get_period(self, cr, uid, context={}):
        print context
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False

    _columns = {
        'name': fields.char('Annee', size=64, required=True, select=1),
        'asset_id': fields.many2one('asset.simulation', 'Asset'),
         'methode': fields.char('Type d\'ammortissement', size=32),
        'txl': fields.float('Taux Lineaire', required=True),
        'txd': fields.float('Taux Degressif',required=True),
        'vcndebut': fields.float('Valeur Comptable Nette Debut'),
        'vcnfin': fields.float('Valeur Comptable Nette Fin'),
        'vresiduelle': fields.float('Valeur Résiduelle'),
        'annuites': fields.float('Annuites'),
        'cumul': fields.float('Cumul'),
    }
asset_simulation_amort()


""" Reel """
class asset_immobilisation(osv.osv):
    _name = 'asset.immobilisation'
    _description = 'Immobilisation'
    
    def _get_period(self, cr, uid, context={}):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False
    def valider(self, cr, uid, ids, context={}):
        pool = pooler.get_pool(cr.dbname)
        for asset_calc in self.browse(cr, uid, ids, context):
            print asset_calc,context
    
    def comptabiliser(self, cr, uid, id, fy_id):
        print "comptabiliser"
        pool = pooler.get_pool(cr.dbname)
        date= pool.get('account.fiscalyear').read(cr,uid,fy_id)['date_stop']
        periode = pool.get('account.period').search(cr,uid,[('fiscalyear_id','=',fy_id),('date_stop','=',date)])[0]
        mouvements=pool.get('asset.amortissement').search(cr,uid,[('asset_id','=',id),('date','=',date)])
        if mouvements :
            immobilisation=pool.get('asset.immobilisation').read(cr,uid,id)
            amortissement=pool.get('asset.amortissement').read(cr,uid,mouvements[0])
            print amortissement
            print immobilisation
            account_move_obj = self.pool.get('account.move')
            account_move_line_obj = self.pool.get('account.move.line')
            move_id = account_move_obj.create(cr, uid, {'ref':immobilisation['name'],'journal_id': immobilisation['journal_id'][0],'period_id': periode})
            account_move_line_obj.create(cr, uid, {'name':immobilisation['name'],'move_id':move_id,'date':date,'journal_id': immobilisation['journal_id'][0],'period_id': periode,'account_id':immobilisation['compteamort'][0],
                                                   'credit':amortissement['debit'],'debit':0})
            account_move_line_obj.create(cr, uid, {'name':immobilisation['name'],'move_id':move_id,'date':date,'journal_id': immobilisation['journal_id'][0],'period_id': periode,'account_id':immobilisation['comptedepreciation'][0],
                                                   'debit':amortissement['debit'],'credit':0})

        print id
        
    def amortir(self, cr, uid, id, fy_id):
        
        pool = pooler.get_pool(cr.dbname)
        date= pool.get('account.fiscalyear').read(cr,uid,fy_id)['date_stop']
        mouvements=pool.get('asset.amortissement').search(cr,uid,[('asset_id','=',id)])
        immobilisation=pool.get('asset.immobilisation').read(cr,uid,id)
        annee=int(immobilisation['date'][0:4])
        mois=int(immobilisation['date'][5:7])
        jour=int(immobilisation['date'][8:10])
        dureerestante=0.0
        if immobilisation['methodefisc']=='1' :
            dureeamorti = (((datetime.datetime(int(date[0:4]),int(date[5:7]),int(date[8:10]))-datetime.datetime(annee,mois,jour)).days+1)/365.0)-1
        else:
            dureeamorti=((((int(date[0:4])-annee)*360)+((12-mois)*30))/360.0)-1
            
        print "Duree amorti ",dureeamorti
        dureerestante =immobilisation['duree']-dureeamorti
        residuel = 0
        for  mouvement_id in mouvements:
            mouvement = pool.get('asset.amortissement').read(cr,uid,mouvement_id)
            residuel=residuel+mouvement['credit']-mouvement['debit']
        print residuel
        
        if immobilisation['methode'] == 'linear':
            txl=1.0/dureerestante
            annuite =residuel * 1 / dureerestante
            if annuite > residuel:
                annuite=residuel
            if dureerestante <1 :
                dureerestante =0.0
            else:
                dureerestante= dureerestante-1
            pool.get('asset.amortissement').create(cr, uid,{'drestante':dureerestante,'operation':'Amortissement','debit':annuite,'vnc':residuel-annuite,'asset_id':id,'date':date})  
            0
            
        #    
        #pool.get('asset.simulation.amort').unlink(cr, uid,entree )
        #for asset_calc in self.browse(cr, uid, ids, context):
        #    if asset_calc['methode'] == 'linear':    # méthode linéaire
        #        print "Linéaire"
        #        cumul = 0
        #        base=asset_calc['base']
        #        residuel = base # residuel = valeur d'acquisition
        #        annuite = 0
        #        for an in range(int(asset_calc['date'][:4]), int(asset_calc['date'][:4])+asset_calc['duree']+1):
        #            methode="Linéaire"
        #            vcndeb=residuel       # valeur comptable nette = résiduel
        #            residuelprecedent=residuel
        #            txl=1.0/int(asset_calc['duree']) # taux linéaire = 1 /duree amort 
        #            txd=1.0/int(asset_calc['duree'])*float(asset_calc['coefd'])    
        #            
        #            annee=int(asset_calc['date'][0:4]) 
        #            mois=int(asset_calc['date'][5:7])
        #            jour=int(asset_calc['date'][8:10])
        #            if asset_calc['methodefisc']==1 :
        #                nbrjour=365 #(datetime.datetime(annee,12,31)-datetime.datetime(annee,1,1)).days+1
        #            else:
        #                nbrjour = 360
        #            if an==int(asset_calc['date'][:4]):  # première année calcul prorata temporis
        #                print "Methode Fiscale ",asset_calc['methodefisc']
        #                if asset_calc['methodefisc']== '0':
        #                    #ecartj=((datetime.datetime(annee,mois+1,1)- datetime.timedelta(days=1))-datetime.datetime(annee,mois,jour)).days
        #                    ecartm = 12-mois+1
        #                    ecart = (ecartm*30)#-ecartj
        #                    print "Ecart ",ecartm,ecart
        #                else:
        #                    ecart =(datetime.datetime(annee,12,31)-datetime.datetime(annee,mois,jour)).days+1
        #                    if ecart > 365:
        #                        ecart= 365
        #                    print "Ecart", ecart
        #                
        #                annuite =base * txl * ecart/nbrjour
        #                cumul=cumul+annuite
        #                residuel=residuel-annuite
        #                print "Première année" ,an, annuite,cumul,residuel,ecart
        #            #elif an==int(asset_calc['date'][:4])+int(asset_calc['duree']):
        #            #    ecart =((datetime.datetime(annee,12,31)-datetime.datetime(annee,mois,jour)).days)+1
        #            #    annuite =base * txl * (nbrjour-ecart)/nbrjour
        #            #    cumul=cumul+annuite
        #            #    residuel=residuel-annuite
        #            #    print "Dernière année", an, annuite,cumul,residuel,ecart
        #            else:
        #                annuite =asset_calc['base'] * 1 / asset_calc['duree']
        #                if annuite > residuel:
        #                    annuite=residuel
        #                cumul=cumul+annuite
        #                residuel=residuel-annuite
        #                print an, annuite,cumul,residuel,ecart
        #            vcnfin=residuelprecedent-annuite # valeur nette comptable fin = residuel - annuité
        #            vresiduelle=asset_calc['base'] -cumul
        #            data_amort={'name':an ,'vresiduelle':vresiduelle,'vcnfin':vcnfin,'vcndebut':vcndeb,'asset_id':asset_calc['id'],'methode':methode,'txd':txd,'txl':txl,'annuites':annuite,'cumul':cumul}
        #            pool.get('asset.simulation.amort').create(cr, uid,data_amort)
        #            if residuel == 0:
        #                break 
        #            
        #    if asset_calc['methode'] == 'degressif':
        #        print "degressif"
        #            
        #        cumul = 0
        #        base=asset_calc['base']
        #        residuel = base
        #        annuite = 0
        #        for an in range(int(asset_calc['date'][:4]), int(asset_calc['date'][:4])+asset_calc['duree']):
        #            vcndeb=residuel
        #            residuelprecedent=residuel
        #            txd=1.0/int(asset_calc['duree'])*float(asset_calc['coefd']) # taux dégressif = 1 /duree amort * coef dégressif
        #            dureeRestante=int(asset_calc['date'][:4])+asset_calc['duree']-an
        #            txl=1.0/dureeRestante
        #            annee=int(asset_calc['date'][0:4])
        #            mois=int(asset_calc['date'][5:7])
        #            jour=int(asset_calc['date'][8:10])
        #            if asset_calc['methodefisc']==1 :
        #                nbrjour=(datetime.datetime(annee,12,31)-datetime.datetime(annee,1,1)).days+1
        #            else:
        #                nbrjour = 360
        #            if an==int(asset_calc['date'][:4]): # première année calcul prorata temporis
        #                methode="Dégressif"
        #                ecart =(datetime.datetime(annee,12,31)-datetime.datetime(annee,mois,jour)).days
        #                print "ecart",ecart,txl,txd
        #                annuite =base *  txd*ecart/12.0
        #                cumul=cumul+annuite
        #                residuel=residuel-annuite
        #                print an, annuite,cumul,residuel
        #            elif txd>txl:
        #                methode="Dégressif"
        #                ecart =(datetime.datetime(annee,12,31)-datetime.datetime(annee,mois,jour)).days
        #                annuite =residuel* txd
        #                cumul=cumul+annuite
        #                residuel=residuel-annuite
        #                print an, annuite,cumul,residuel
        #            else:
        #                methode="Linéaire"
        #                annuite =residuel* txl
        #                cumul=cumul+annuite
        #                residuel=residuel-annuite
        #            #else:
        #            #   annuite =asset_calc['base'] * 1 / asset_calc['duree']
        #            #   cumul=cumul+annuite
        #            #   residuel=residuel-annuite
        #            #   print an, annuite,cumul,residuel
        #            vcnfin=residuelprecedent-annuite
        #            vresiduelle=asset_calc['base'] -cumul
        #            data_amort={'name':an ,'vcnfin':vcnfin,'vcndebut':vcndeb,'asset_id':asset_calc['id'],'methode':methode,'txd':txd,'txl':txl,'annuites':annuite,'cumul':cumul,'vresiduelle':vresiduelle}    
        #            pool.get('asset.simulation.amort').create(cr, uid,data_amort)  
        return False
    
    _columns = {
        'name': fields.char('Désignation', size=64, required=True, select=1),
        'nordre':fields.char('Numéro d\'ordre',size=32),
        'compteimmo':fields.many2one('account.account', 'Compte d\'immobilisation',required=True),
        'compteamort':fields.many2one('account.account', 'Compte d\'amortissement',required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'comptedepreciation':fields.many2one('account.account', 'Compte de depreciation',required=True),
        'comptefournisseur':fields.many2one('account.account', 'Compte Fournisseur',required=True),
        'date': fields.date('Date d\'acquisition', required=True, select=1),
        'base': fields.float('Coût d\'acquisition',required=True),
        'methode': fields.selection([('linear','Linéaire'),('degressif','Dégressif'),('exceptionnel','Exceptionnel')], 'Type d\'amortissement', required=True),
        'methodefisc': fields.selection([('0','30 Jours par mois / 360 jours par an'),('1','Jour réels /365 par an')], 'Méthode Fiscale', required=True),
        'coef': fields.float('Coefficient',required=True),
        'duree':fields.integer('Durée'),
        'mouvement':fields.one2many('asset.amortissement', 'asset_id','Amortissement'),
        'vresiduelle':fields.float('Valeur Résiduelle'),
        'notes': fields.char('Notes',size=256)
    }
    _defaults = {
        'coef':  lambda *a:1,
        'methode':lambda *a: 'linear',
        'methodefisc':lambda *a: 1,
    }
    _order = "nordre"
    
asset_immobilisation()

class asset_amortissement(osv.osv):
    _name = 'asset.amortissement'
    _description = 'asset.amortissement'
        
    _columns = {
        'asset_id': fields.many2one('asset.immobilisation', 'Immobilisation'),
        'date': fields.date('Date', required=True, select=1),
        'operation':fields.char('Opérations',size=128),
        'credit':fields.float('Crédit'),
        'debit':fields.float('Débit'),
        'vnc':fields.float('Valeur Nette Comptable'),
        'drestante':fields.float('Durée restante'),
    }
asset_amortissement()
        
