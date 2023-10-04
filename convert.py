#
# Convert a single file containing the Finnish Commune Boundary data into
# a valid FeatureCollection.
#
# Boundary data as a shapefile can be obtained from:
#
# https://www.maanmittauslaitos.fi/paikkatiedon-tiedostopalvelu
# https://www.maanmittauslaitos.fi/paikkatiedon-tiedostopalvelu/tekninen-kuvaus
#

from sys import argv
import geopandas

output_path = '.'.join(argv[1].split('.')[:-1]) + '.json'
data = geopandas.read_file(argv[1]).to_json(to_wgs84 = True)

with open(output_path, 'w') as output_file:
    output_file.write(data)

# end of file.
