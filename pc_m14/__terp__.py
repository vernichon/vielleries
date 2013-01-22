#
# Plan comptable M14l pour les communes de 500 Habitants et plus.
#
# source : http://www.colloc.minefi.gouv.fr/colo_struct_fina_loca/comp_loca/m14_1er.html
# 
{
	"name" : "France - Plan comptable M14",
	"version" : "0.2",
	"author" : "Eric Vernichon",
	"category" : "Localisation/Account charts",
	"website": "http://www.vernichon.fr",
	"depends" : ["base", "account", "account_chart"],
	"init_xml" : [],
	"update_xml" : ["../account_chart/account_chart.xml", "m14.xml",],
	"demo_xml" : [],
	"installable": True
}
