import csv
import json
import os
import shutil
import errno
from tinydb import TinyDB, Query


def mkdir(path):
    """mkdir, fail silently"""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def clean(value):
    """Clean the input of special characters"""
    return value \
        .replace('\n', '') \
        .replace('&', 'and')


def get_unique(field):
    """Get a set of the unique values in the DB"""
    return {x[field] for x in db.search(Query()[field] != '')}


def create_api(field, options):
    """Get the values from the DB, and write them to a file"""
    locations = 'docs/{}'.format(field)
    mkdir(field)

    for option in options:
        path = '{}/{}'.format(locations,
                              option.replace(' ', '-').replace('/', '-'))
        mkdir(path)
        with open('{}/index.json'.format(path), 'w') as f:
            f.write(json.dumps({'data': db.search(Query()[field] == option)}, indent=2))

    with open('{}/index.json'.format(locations), 'w') as f:
        cleaned_options = [
            o.replace(' ', '-').replace('/', '-') for o in options
        ]
        f.write(json.dumps({'data': cleaned_options}, indent=2))


if os.path.exists('docs'):
    shutil.rmtree('docs')

# Start with a fresh db
if os.path.exists('db.json'):
    os.remove('db.json')

mkdir('docs')
db = TinyDB('db.json')

csvfile = open('data.csv', 'r')

# Get the fieldnames from the first line of the csv
fieldnames = csvfile.readline().replace('\n', '').split(',')

reader = csv.DictReader(csvfile, fieldnames)

# Add the data to the DB, cleaning as we go
for row in reader:
    data = {}
    for key, value in row.iteritems():
        data[clean(key.lower())] = clean(value)
    db.insert(data)


create_api('area', get_unique('area'))
create_api('borough', get_unique('borough'))
create_api('clients', get_unique('clients'))


# Write all the data down, into a single file
with open('docs/index.json', 'w') as f:
    f.write(json.dumps({'data': db.all()}, indent=2))
