from astroquery.irsa import Irsa


if __name__ == "__main__":
    wise_cats = {key: Irsa.list_catalogs()[key] for key in Irsa.list_catalogs().keys() if "wise" in key.lower()}
    tb = Irsa.query_region('WISE j113325.38-701141.1', catalog='allwise_p3as_psd', spatial='Cone', width=None,
                           polygon=None, get_query_payload=False, verbose=True, selcols=None)
    # what is the difference between 'WISE j113325.38-701141.1' and 'WISE j113325.38-701141.0'?
