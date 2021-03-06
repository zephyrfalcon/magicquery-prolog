# mksrc.py
# Generate Prolog source containing MtG card rules and properties.

import ConfigParser
import os
import re
import string
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import StringIO


def extract_data(xml):
    setnode = xml.find('set')
    cards = xml.findall('set/cards/card')
    return setnode, cards

def get_files_for_sets(sets, dir, suffix):
    files = os.listdir(dir)
    files = [fn for fn in files if fn.endswith(suffix)]
    if sets:
        files = [fn for fn in files if os.path.splitext(fn)[0] in sets]
    files = [os.path.join(dir, fn) for fn in files]
    return files

# extract power, toughness
def write_pt_rule(cardnode, cardname, f, attr):
    p = cardnode.find(attr)
    if p is not None:
        power = p.text
        if '*' in power:
            print "skipping", attr, "for now:", cardname, power
            return
        print >> f, "%s(%s, %s)." % (attr, cardname, topi(p.text))

def prolog_list_as_str(lst):
    s = string.join(lst, ", ")
    return "[%s]" % s

def write_types(cardnode, cardname, f):
    t = cardnode.find('type_oracle').text # must be present
    before, sep, after = t.partition("--")
    for s, name in [(before, "types"), (after, "subtypes")]:
        parts = s.strip().split()
        parts = [topi(p) for p in parts]
        typestr = prolog_list_as_str(parts)
        print >> f, "%s(%s, %s)." % (name, cardname, typestr)

def write_rarity(cardnode, cardname, f):
    r = cardnode.find('rarity').text
    rarities = {
        'R': 'rare',
        'U': 'uncommon',
        'C': 'common',
        'MR': 'mythic_rare',
        'L': 'basic_land'
    }
    print >> f, "rarity(%s, %s)." % (cardname, rarities.get(r, 'unknown'))

mana = {
    'B': 'black',
    'G': 'green',
    'R': 'red',
    'S': 'snow',
    'U': 'blue',
    'W': 'white',
    'X': 'x',
}

re_number = re.compile(r"^\d+$")

def write_manacost(cardnode, cardname, f):
    cost = []
    costnode = cardnode.find('manacost')
    if costnode is not None:
        for symnode in costnode.findall('symbol'):
            m = symnode.text
            if re_number.match(m):
                cost.append(m)
            elif len(m) == 1:
                manasym = mana[m]
                cost.append(manasym)
            elif len(m) == 2:
                raise NotImplementedError("hybrid mana")

    s = prolog_list_as_str(cost)
    print >> f, "cost(%s, %s)." % (cardname, s)

def gen_prolog_src(filename):
    print "Loading:", filename
    xml = ET.parse(filename)
    setnode, cards = extract_data(xml)

    # extract set data
    pl_shortname = name_to_prolog_identifier(setnode.find('shortname').text)

    out_filename = "cards_%s.pl" % pl_shortname
    f = open(out_filename, 'w')

    print >> f, "%% Card data for", pl_shortname
    print >> f, "%% Auto-generated by mksrc.py -- do not edit\n"

    print >> f, 'set(%s).' % pl_shortname
    print >> f, 'set_full_name(%s, "%s").' % (
                pl_shortname, setnode.find('name').text)
    print >> f, 'set_num_cards(%s, %s).' % (
                pl_shortname, setnode.find('number_of_cards').text)

    # extract card data
    for cardnode in cards:
        print >> f
        pl_card_name = name_to_prolog_identifier(cardnode.find('name').text)
        print >> f, 'card(%s, %s).' % (pl_shortname, pl_card_name)

        write_pt_rule(cardnode, pl_card_name, f, 'power')
        write_pt_rule(cardnode, pl_card_name, f, 'toughness')
        write_types(cardnode, pl_card_name, f)
        write_rarity(cardnode, pl_card_name, f)
        write_manacost(cardnode, pl_card_name, f)

    f.close()
    print "Written:", out_filename

VALID_IDENTIFIER_CHARS = string.lowercase + string.digits + "_"

def name_to_prolog_identifier(s):
    s = s.lower()
    s = s.replace(" ", "_")
    chars = [c for c in s if c in VALID_IDENTIFIER_CHARS]
    return string.join(chars, '')

topi = name_to_prolog_identifier # shorthand

if __name__ == "__main__":

    cp = ConfigParser.ConfigParser()
    cp.read("config.txt")
    xmldir = os.path.expanduser(cp.get('main', 'xmldir'))

    # for now, only generate source for M11
    filenames = get_files_for_sets(["M11"], xmldir, '.xml')

    for filename in filenames:
        gen_prolog_src(filename)

