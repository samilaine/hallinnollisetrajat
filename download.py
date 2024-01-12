#
# Download Finnish Commune Boundary data (shapefiles).
#
# To run this, you need to obtain an API key from the National Land Survey of Finland.
# Instructions: https://www.maanmittauslaitos.fi/en/rajapinnat/api-avaimen-ohje
#

import requests
import sys

from datetime import date
from http.client import responses
from os import environ, path
from random import randint
from tempfile import gettempdir
from time import sleep

api_key = environ['NLS_API_KEY']

r = requests.post(
      'https://avoin-paikkatieto.maanmittauslaitos.fi/tiedostopalvelu/ogcproc/v1/processes/hallinnolliset_aluejaot_vektori_koko_suomi/execution',
      auth = (api_key, ''),
      json = {
        'id': 'hallinnolliset_aluejaot_vektori_koko_suomi',
        'inputs': {
          'fileFormatInput': 'kaikki',
          'dataSetInput': 'kuntajako_4500k',
          'yearInput': date.today().year
        }
      }
    )

r.raise_for_status()
if r.status_code != 201:
  print(f'{r.status_code} {responses[r.status_code]}\n')
  print(r.content)
  sys.exit(1)

try:
  j = r.json()
except Exception as ex:
  print('Unable to parse response as JSON. See response below:\n\n',
        file = sys.stderr)
  print(r.raw, file = sys.stderr)
  print('\n\n')
  sys.exit(2)

if 'status' in j and j['status'].lower() == 'accepted':
  if 'links' in j and len(j['links']) > 0:
    status_url = j['links'][0]['href']
  else:
    print('Unable to extract a URL from the response.',
          file = sys.stderr)
    sys.exit(3)

result_urls = []
while True:
  r = requests.get(status_url, auth = (api_key, ''))
  r.raise_for_status()

  try:
    j = r.json()
  except Exception as ex:
    print('Unable to parse response as JSON. See response below:\n\n',
          file = sys.stderr)
    print(r.raw, file = sys.stderr)
    print('\n\n')
    sys.exit(4)

  if 'status' in j and j['status'].lower() == 'failed':
    msg = j.get('message', None)
    print(f'Error: "{msg}"', file = sys.stderr)
    break

  if 'status' in j and j['status'].lower() == 'successful':
    if 'links' in j and len(j['links']) > 0:
      for l in j['links']:
        if 'href' in l:
          result_urls.append(l['href'])
      break
    else:
      print('No results URL in the response. See response below:\n\n',
            file = sys.stderr)
      print(r.raw, file = sys.stderr)
      print('\n\n')
      sys.exit(4)

  sleep(randint(3,11))

for result_url in result_urls:
  print(result_url)
  r = requests.get(result_url, auth = (api_key, ''))
  r.raise_for_status()

  try:
    j = r.json()
  except Exception as ex:
    print('Unable to parse response as JSON. See response below:\n\n',
          file = sys.stderr)
    print(r.raw, file = sys.stderr)
    print('\n\n')
    sys.exit(5)

  if 'results' in j:
    for result in j['results']:
      if ('path' in result and
          'format' in result and
          result['format'].lower() == 'geopackage'):
        pathname = path.join(gettempdir(), result['path'].split('/')[-1])
        req = requests.get(result['path'], auth = (api_key, ''))
        req.raise_for_status()

        with open(pathname, 'wb') as output:
          output.write(req.content)

        print(f'Received: {pathname}')

# end of file.
