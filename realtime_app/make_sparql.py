from SPARQLWrapper import SPARQLWrapper
#from pprint import pprint

def get_dbpedia(sub,pre,obj):
    sparql = SPARQLWrapper(endpoint='http://ja.dbpedia.org/sparql', returnFormat='json')
    query = """
        PREFIX dbp-owl: <http://dbpedia.org/ontology/>
        PREFIX dbpj: <http://ja.dbpedia.org/resource/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
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
        return result
    except:
        return None

def spql_get_superconcept(concept):
    results = get_dbpedia(sub='dbpj:' + concept, pre='dcterms:subject',obj='?re')
    if results:
        results = [x['re']['value'].split(':')[-1] for x in results]
        results = [x.split('_')[0] for x in results]
        results = [x for x in results if x!=concept and concept not in x]
        return results
    else:
        return []

def spql_fix_concept(concept):
    results = get_dbpedia(sub='dbpj:'+concept, pre='dbp-owl:wikiPageRedirects',obj='?re')
    if results:
        results = [x['re']['value'].split('/')[-1] for x in results]
        return results[0]
    else:
        if spql_have_dbpedia(concept):
            return concept
        else:
            return concept+'*'

def spql_have_dbpedia(concept):
    results = get_dbpedia(sub='dbpj:'+concept, pre='dbpedia-owl:wikiPageID',obj='?re')
    if results:
        return True
    else:
        return False

if __name__ == '__main__':
    #results = get_dbpedia(sub='dbpj:祭', pre='dbp-owl:wikiPageWikiLink',obj='?re')
    #results = get_dbpedia(sub='dbpj:祭', pre='dbpedia-owl:wikiPageID',obj='?re')
    print(spql_fix_concept(concept='祭'))
    print(spql_get_superconcept(concept='冷蔵庫'))
