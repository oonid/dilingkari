__author__ = 'oonarfiandwi'

from flask import Flask
import simplejson as json

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/indonesia', methods=['POST'])
def get_indonesia():
    indonesia_users = [  # manual entry of array of users
        {
            'displayName': 'Enda Nasution',
            'id': '107625144935146230047',
        },
        {
            'displayName': 'Widi Asmoro',
            'id': '106601693943516044496',
        },
        {
            'displayName': 'Onno Purbo',
            'id': '118252948887947024512'
        },
        {
            'displayName': 'oon arfiandwi (OonID)',
            'name': {'givenName': 'oon', 'familyName': 'arfiandwi'},
            'id': '102354805749063623353'
        }
    ]
    return json.dumps(indonesia_users)