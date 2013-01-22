{
	"name" : "Account FR  Report",
	"version" : "0.9",
	"depends" : ["account", "base"],
	"author" : "Eric Vernichon",
	"description": """Etat comptables 	""",
	"category" : "Generic Modules/Accounting",
	"init_xml" : [  "report.account.fr.parametres.csv"
	],
	"demo_xml" : [
	],
	"update_xml" : [
		"report_account_fr_report.xml",
		"report_account_fr_view.xml"
	],
	"active": False,
	"installable": True
}
