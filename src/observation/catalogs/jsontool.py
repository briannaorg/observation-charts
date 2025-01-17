# -*- coding: utf-8 -*- 
# Copyright 2010-2014 Will Barton. 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions
# are met:
# 
#   1. Redistributions of source code must retain the above copyright 
#      notice, this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright 
#      notice, this list of conditions and the following disclaimer in the 
#      documentation and/or other materials provided with the distribution.
#   3. The name of the author may not be used to endorse or promote products
#      derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL
# THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 

import argparse
import re

from objects import OBJECT_TYPES, CelestialObject, NGCCatalog, HYGStarCatalog
from constellations import ConstellationCatalog, Constellation

import json

class CatalogEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, CelestialObject):
            # Custom JSON format
            o = {
                    "id": o.id,
                    "magnitude": o.magnitude,
                    "type": OBJECT_TYPES[o.type],
                    "coordinates": [
                            o.ra.degrees if not self.args.invert_ra else 360 - o.ra.degrees, 
                            o.dec.degrees
                        ],
                    "size": [o.size.major, o.size.minor] \
                            if o.size is not None else [],
                    "angle": o.angle if o.angle is not None else 0,
                }

            return o

        return json.JSONEncoder.default(self, o)


    
class CatalogsGeoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, CelestialObject):
            # GEOJSON feature
            feature = {
                    "type": "Feature", 
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                                o.ra.degrees if not self.args.invert_ra else 360 - o.ra.degrees, 
                                o.dec.degrees
                            ],
                    },
                    "properties": {
                        "id": o.id,
                        "magnitude": o.magnitude,
                        "type": OBJECT_TYPES[o.type],
                        "size": [
                            o.size.major,
                            o.size.minor
                        ] if o.size is not None else [],
                        "angle": o.angle if o.angle is not None else 0,
                        "aliases": o.aliases,
                    },
                }
            if self.args.includename:
                feature['properties']['name'] = o.id

            return feature

        if isinstance(o, Constellation):
            lines = []
            for line in o.lines:
                points = []
                for p in line.positions:
                    points.append([
                            p.ra.degrees if not self.args.invert_ra else 360 - p.ra.degrees, 
                            p.dec.degrees])
                lines.append(points)
            
            feature = {
                    "type": "Feature", 
                    "geometry": {
                        "type": "MultiLineString", 
                        "coordinates": lines,
                    },
                    "properties": {
                        "id": o.abbr,
                        "abbr": o.abbr,
                        "name": o.name,
                    }
                }

            return feature

        return json.JSONEncoder.default(self, o)


def main():
    parser = argparse.ArgumentParser(description='Output GeoJSON for each of the given celestial catalogs.')
    # parser.add_argument('output', type=str, help='specifies the output file')
    parser.add_argument('--ngc', type=str, 
            help="specifies the NGC catalog file path")
    parser.add_argument('--hyg', type=str, 
            help="specifies the NGC catalog file path")
    parser.add_argument('--out', type=str, 
            help="specifies the output json file path")
    
    parser.add_argument('--magnitude', type=int, default=5,
            help="limit output to the specified magnitude")

    parser.add_argument('--constellations', type=str, 
            help="specifies the constellations file path")

    parser.add_argument('--specifically', type=str, default='.*',
            help="a regular expression that matches specific object ids or aliases to include")

    parser.add_argument('--indent', type=int,
            help="specifies that the output should be pretty-printed and the indent level")
    parser.add_argument('--invert-ra', action="store_true", default=False,
            help="invert the right ascension coordinates (useful for projections that expect longitude/latitude)")
    parser.add_argument('--geojson', action="store_true", default=False,
            help="output in GeoJSON Feature format")
    parser.add_argument('--includename', action="store_true", default=False,
            help="include the object id as its name in the output")
    
    args = parser.parse_args()

    json_args = {}
    if args.indent:
        json_args = {'sort_keys':True, 'indent':args.indent}

    objects = []

    specifically = re.compile(args.specifically)

    if args.hyg:
        hyg_catalog = HYGStarCatalog(open(args.hyg))
        objects.extend([ o for o in hyg_catalog.values() 
            if (o.magnitude <= args.magnitude) and 
                (specifically.search(o.id) or
                specifically.search(''.join(o.aliases)))])

    if args.ngc:
        ngc_catalog = NGCCatalog(open(args.ngc))
        for o in ngc_catalog.values():
            if (o.magnitude <= args.magnitude) and \
                    any([specifically.search(a) for a in o.aliases]):
                print("APPENDING", o.aliases)
                objects.append(o)

    if args.constellations:
        const_catalog = ConstellationCatalog(open(args.constellations))
        objects.extend([o for o in const_catalog.values() 
            if (specifically.search(o.abbr))])
    
    json_string = ""
    if args.geojson:
        collection = {
            "type": "FeatureCollection", 
            "features": objects,
        }
        json_encoder = CatalogsGeoJSONEncoder(**json_args)
        json_encoder.args = args
        json_string = json_encoder.encode(collection)
    else:
        json_encoder = CatalogEncoder(**json_args)
        json_encoder.args = args
        json_string = json_encoder.encode(objects)


    print(len(objects), "objects")
    
    if args.out:
        outfile = open(args.out, 'w')
        outfile.write(json_string)
        outfile.close()
    else:
        print(json_string)

    return


if __name__ == "__main__":
    main()
