from SPARQLWrapper import SPARQLWrapper

def get_dbpedia(sub,pre,obj):
    sparql = SPARQLWrapper(endpoint='http://ja.dbpedia.org/sparql', returnFormat='json')
    query = """
        PREFIX dbp-owl: <http://dbpedia.org/ontology/>
        PREFIX dbpj: <http://ja.dbpedia.org/resource/>
    """
    if sub[0]=='?':
        query = query + f"    SELECT {sub} WHERE "
    elif obj[0]=='?':
        query = query + f"    SELECT {obj} WHERE "
    elif pre[0]=='?':
        query = query + f"    SELECT {pre} WHERE "
    else:
        return None
    query = query + "{"+f" {sub} {pre} {obj} . "+"}"
    sparql.setQuery(query)
    results = sparql.query().convert()
    try:
        result = results['results']['bindings']
        #if type(result) is list:
        #    print(type(result))
        #    result = result[0]
        return result
    except:
        return None

if __name__ == '__main__':
    results = get_dbpedia(sub='dbpj:祭礼', pre='dbp-owl:wikiPageRedirects',obj='?re')
    #results2 = get_dbpedia(sub='dbpj:祭', pre='dbpedia-owl:wikiPageID',obj='?re')
    print(results)
    #print(results2)
    if results:
        for result in results:
            print(result)
    else:
        print('error')
