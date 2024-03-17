from flask import Blueprint
import json
algs_bp = Blueprint('algs', __name__, url_prefix='/ifccd/algs')

@algs_bp.get('')
def algs_enquire():

    f = open('alg_all.json', 'r')
    content = f.read()
    a = json.loads(content)
    f.close()
    return a

