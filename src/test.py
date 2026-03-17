from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000")
print(client.admin.command("ping"))
db = client["fisiodesk"]
print("pazienti:", db.pazienti.count_documents({}))
print("schede:", db.schede_valutazione.count_documents({}))
print("trattamenti:", db.diario_trattamenti.count_documents({}))
print("eventi:", db.eventi_calendario.count_documents({}))
