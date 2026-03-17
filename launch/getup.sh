docker cp data/pazienti.json fisiodesk-mongodb:/tmp/pazienti.json
docker cp data/schede_valutazione.json fisiodesk-mongodb:/tmp/schede_valutazione.json
docker cp data/diario_trattamenti.json fisiodesk-mongodb:/tmp/diario_trattamenti.json
docker cp data/eventi_calendario.json fisiodesk-mongodb:/tmp/eventi_calendario.json

docker exec -it fisiodesk-mongodb bash -lc 'mongoimport --host localhost --db fisiodesk --collection pazienti --file /tmp/pazienti.json --jsonArray'
docker exec -it fisiodesk-mongodb bash -lc 'mongoimport --host localhost --db fisiodesk --collection schede_valutazione --file /tmp/schede_valutazione.json --jsonArray'
docker exec -it fisiodesk-mongodb bash -lc 'mongoimport --host localhost --db fisiodesk --collection diario_trattamenti --file /tmp/diario_trattamenti.json --jsonArray'
docker exec -it fisiodesk-mongodb bash -lc 'mongoimport --host localhost --db fisiodesk --collection eventi_calendario --file /tmp/eventi_calendario.json --jsonArray'
