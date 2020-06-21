import sys
sys.path.append("/home/coljac/build/coltools")
import json
import pandas as pd
import coltools as ct
# import urllib.request as request
import os
import shlex
import shutil
import urllib.parse
import requests
from config import config
import time
import numpy as np
import re
import ast

# TODO: ~ in search of oracle text

brackets_regex = re.compile(r"\([^)]*\)", re.IGNORECASE)

def remove_brackets(string):
    string = brackets_regex.sub("", string)
    return string

class Cards(object):
    def __init__(self, database="csv"):
        # if not os.path.exists("cards.json"):
        #     self.fetch_cards(query="f:s")

        if database == "csv":
            self.cards = self.load_cards_from_csv()
        elif database == "json":
            self.cards = self.load_cards_from_json_file()
            self.cards.to_csv("allcards.csv")
        elif database == "fetch":
            self.cards = self.fetch_cards(query="f:s")
            self.cards.to_csv("cards.csv")

        self.unique = True
        self.regex = False
        self.abbrev_to_property = {"t":"type_line", "type":"type_line",
                                  "r":"rarity", "s":"set", "set":"set", "set_name":"set_name",
                                   "o": "oracle_text",
                                   "oracle_text": "oracle_text",
                                   "n": "name", "c": "colors", "cmc": "cmc_num"}
        self.abbrev_to_value = {"u":"uncommon", "m": "mythic", "c":"common"}

    def load_cards_from_csv(self):
        df = pd.read_csv("cards.csv", index_col="id")
        # df = pd.read_csv("allcards.csv", index_col="id")
        # df = pd.read_csv("/home/coljac/Downloads/allcards.csv", index_col="id")
        df['oracle_text'] = df['oracle_text'].replace(np.nan, '', regex=True)
        return df

    def load_cards_from_json_file(self):
        return self.load_cards_from_json(json.load(
            open("/home/coljac/Downloads/allcards.json", "r")))
            # open("/home/coljac/Downloads/somecards.json", "r")))

    def load_cards_from_json(self, json, query=False, make_fake=True):
        if query:
            cards = json['data']
            # self.cards = json.load(open("cards.json", "r"))['data']
        else:
            cards = json
            # self.cards = json.load(open("cards.json", "r"))

        df = pd.DataFrame.from_records(cards)
        if "id" in df.columns:
            df = df.set_index("id")
        df['parent'] = np.nan
        colors = "UBWRGCM" # colorless multi
        if not "card_faces" in df:
            df['card_faces'] = None

        for color in colors:
            df[color] = color in df.colors

        if make_fake:
            for i, row in df[(df['layout'] != "normal") & (~df['card_faces'].isnull())].iterrows():
                try:
                    sides = row['card_faces']
                    if len(sides) < 1:
                        continue
                    # df.loc[i, "searchable_oracle_text"] = remove_brackets(sides[0]['oracle_text'] + "//" + sides[1]['oracle_text'])
                    # df.loc[i, "searchable_type_line"] = sides[0]['type_line'] + "//" + sides[1]['type_line']
                    # Broken?
                    # for color in colors:
                    #     for side in sides:
                    #         if "colors" in side:
                    #             has_col = color in side['colors']
                    #             if has_col:
                    #                 df.loc[i, color] = has_col

                    # if False:
                    for x, side in enumerate(sides):
                        fake_card = sides[x]
                        fake_card['id'] = i + "_" + str(x)
                        fake_card['parent'] = i
                        fake_card['legalities'] = row['legalities']
                        fake_card['set'] = row['set']
                        fake_card['card_faces'] = None
                        for c in colors:
                            fake_card[c] = c in fake_card['mana_cost']
                        df = df.append(pd.DataFrame([fake_card]).set_index("id"), sort=False)
                except Exception as e:
                    raise(e)
        # df['power'] = df['power'].astype(int, errors='coerce')
        for column in ["power", "toughness", "cmc", "loyalty"]:
            if column not in df.columns:
                df[column] = ""
            # df[column] = df[column].astype(float)
            df[column + "_num"] = pd.to_numeric(df[column], errors='coerce')



        legalities = df.iloc[0].legalities
        for legality in legalities.keys():
            df[legality] = False
        df = df.replace(np.nan, '', regex=True)
        N = len(df)
        x = 0
        # df['oracle_text'] = ""
        # df['type_line'] = ""
        for i, row in df.iterrows():
            x+=1
            ct.progbar(x, N)
            color_count = 0
            if type(row['colors']) == list:
                for color in colors:
                  has_col = color in row['colors']
                  df.loc[i, color] = has_col
                  if has_col:
                      color_count += 1
                df.loc[i, 'M'] = color_count > 1
                df.loc[i, 'C'] = color_count == 0
            # if i == "303d51ab-b9c4-4647-950f-291daabe7b81":
            for legality in legalities:
                df.loc[i, legality] = (row['legalities'][legality] == "legal")
            df.loc[i, "oracle_text"] = remove_brackets(row['oracle_text'])
            # df.loc[i, "type_line"] = row['type_line']

        # for col in ['color_identity', 'colors', 'multiverse_ids',
        #             'all_parts', 'card_faces']:
        #     if col in df.columns:
        #         df[col] = df[col].astype(str)
        df.to_csv("tmp.csv")
        df = pd.read_csv("tmp.csv", index_col="id")
        df['oracle_text'] = df['oracle_text'].replace(np.nan, '', regex=True)
        return df


    def fetch_cards(self, query="f:s", cached=True, make_fake=True):
        page = 1
        df = None
        while True:
            print("\nFetching page ", page)
            if not cached:
                url = "https://api.scryfall.com/cards/search?q=" + urllib.parse.quote_plus(query) + "&page=" + str(page)
                r = requests.get(url, stream=True)
                r.raw.decode_content = True
                batch = self.load_cards_from_json(json.loads(r.text), query=True,
                                                  make_fake=make_fake)
                with open("cards" + str(page) + ".json", 'w') as f:
                    f.write(r.text)
                    # shutil.copyfileobj(r.raw, f)
            else:
                content = ct.fas("json/cards" + str(page) + '.json')
                batch = self.load_cards_from_json(json.loads(content), query=True,
                                                  make_fake=make_fake)
            time.sleep(0.1)
            if df is None:
                df = batch
            else:
                df = pd.concat([df, batch], sort=False)
            if len(batch) < 175:
                break
            page += 1
        return df


    def fetch_image(cardid, url, size="large"):
        filename = config.get("images_dir") + size + "/" + cardid + ".jpg"
        if os.path.exists(filename):
            return
        r = requests.get(url, stream=True)
        r.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


    def fetch_images(self, df, size="large"):
        N = len(df)
        c = 1
        if not os.path.exists(config.get("images_dir") + size):
            os.mkdir(config.get("images_dir") + size)
        for i, row in df.iterrows():
            ct.progbar(c, N)
            c += 1
            try:
                try:
                    faces = ast.literal_eval(row['card_faces'])
                    for face in faces:
                        cardid = face['id']
                        url = ast.literal_eval(face['image_uris'])[size]
                        self.fetch_image(cardid, url, size=size)
                except:
                    cardid = str(i)
                    url = ast.literal_eval(row['image_uris'])[size]
                    Cards.fetch_image(cardid, url, size=size)
            except Exception as e:
                print(i, e)


    ####  Searching

    def search_on(self, criteria, sort=["color_identity", "cmc", "name"],
                  returns="cards"): # cards | spells | both
        if not self.is_valid(criteria):
            raise Exception("Malformed search")
        criteria = criteria.lower()
        search_process = [self.cards]

        tokens = shlex.split(criteria)
        N = len(tokens)
        i = 0
        while i < N:
            token = tokens[i]
            if token.startswith("("):
                subsearch = token[1:]
                while True:
                    i += 1
                    nexttok = tokens[i]
                    if nexttok.endswith(")"):
                        subsearch += " " + (nexttok[:-1])
                        break
                    else:
                        subsearch += " " + nexttok
                results = self.search_on(subsearch)

                search_process.append(results)
            elif token == "and":
                pass
            elif token == "or":
                search_process.append("or")
            else:
                results = self.do_search(token)
                search_process.append(results)
            i += 1

        results = search_process[0]
        operator = "and"
        for i in range(1, len(search_process)):
            if type(search_process[i]) == str and search_process[i] == "and":
                operator = "and"
            elif type(search_process[i]) == str and search_process[i] == "or":
                operator = "or"
            else:
                results = self.apply_operator(operator, results, search_process[i])
                operator = "and"


        if returns == "cards":
            results = results[results.parent.isnull()]
        # elif returns == "spells":

        results = results.drop_duplicates()
        if self.unique:
            # results = results.sort_values('collector_number', ascending=False) \
            #     drop_duplicates('name').sort_index()
            results = results.drop_duplicates('name').sort_index()

        results = results.sort_values(by=sort)
        return results

    def do_search(self, search, on=None):
        try:
            search = search.lower()
            if on is None:
                on = self.cards

            operators = [":", "!=", "==", ">=", "<=", "<", ">", "="]
            op = None

            for o in operators:
                if o in search:
                    field, val = search.split(o)
                    op = o
                    break

            if op is None:
                field = "name"
                op = ":"
                val = search

            invert = False
            if field.startswith("-"):
                invert = True
                field = field[1:]

            field_name = self.abbrev_to_property.get(field, field)

            if field_name is None:
                raise Exception("Unknown field " + field)

            results = self.search_op(on, field_name, op, val, invert=invert)
            return results
        except:
            raise Exception("Invalid search.")


    def search_op(self, results, field_name, op, val, invert=False):
        if field_name == "colors":
            if op == ":" or op == "=":
                for c in val:
                    results = results[results[c.upper()]]
            elif op == ">":
                results = self.search_op(results, field_name, "=", val)
                extras = []
                for color in [c for c in "URGWBC" if c not in val.upper()]:
                    extras.append(results[results[color]])
                results = pd.concat(extras, sort=False)
            elif op == "<":
                hasall = self.search_op(results, field_name, "=", val)
                extras = []
                for color in val.upper() + "C":
                    extras.append(results[results[color]])
                extras.append(results[~(results.U | results.R | results.G |
                          results.B | results.W | results.C)])
                results = pd.concat(extras, sort=False)
                for color in [c for c in "URGWB" if c not in val.upper()]:
                    results = results[~results[color]]
                results = results[~results.index.isin(hasall.index)]
            elif op == ">=":
                hasall = self.search_op(results, field_name, "=", val)
                results = self.search_op(results, field_name, ">", val)
                results = self.cards.loc[results.index.union(hasall.index)]
            elif op == "<=":
                hasall = self.search_op(results, field_name, "=", val)
                results = self.search_op(results, field_name, "<", val)
                results = self.cards.loc[results.index.union(hasall.index).unique()]
            elif op == "!=":
                hasall = self.search_op(results, field_name, "=", val)
                results = self.cards.loc[results.index.difference(hasall.index)]
        elif field_name == "cmc_num":
            if op == "=" or op == ":":
                op = "=="
            expr = "results[results['%s'] %s %d]" % ("cmc_num", op, int(val))
            results = eval(expr)
        elif field_name == "oracle_text":
            results = results[results.oracle_text.str.lower().str.contains(val, regex=self.regex)]
        elif field_name == "set_name":
            results = results[results.set_name.str.lower() == val]
        elif field_name == "set":
            results = results[results.set.str.lower() == val]
        elif field_name == "type_line":
            results = results[results.type_line.str.lower().str.contains(val, regex=self.regex)]
        elif field_name == "name":
            results = results[results.name.str.lower().str.contains(val, regex=self.regex)]
        else:
            raise Exception("Invalid search:" + field_name) # + str(field_name, op, val))

        if invert:
            results = self.cards.loc[self.cards.index.difference(results.index)]

        parents = results[~results.parent.isnull()]['parent'].values
        results = results[results.parent.isnull()]
        results = pd.concat([results, self.cards.loc[parents]])
        results = results.drop_duplicates()
        return results


    def do_sort(self, results, by=None):
        if by is None:
            return sorted(results)
        return results

    def apply_operator(self, operator, operand1, operand2):
        if operator == "and":
            return self.cards.loc[operand1.index.intersection(operand2.index)]
        else:
            return self.cards.loc[operand1.index.union(operand2.index)]

    def is_valid(self, search_string):
        bracket_count = 0
        for c in search_string:
            if c == "(":
                bracket_count += 1
            elif c == ")":
                bracket_count -= 1
                if bracket_count < 0:
                    return False
        return bracket_count == 0



class Card(object):
    def __init__(self, id, name, colors, oracle_text):
        self.id = id
        self.name = name
        self.colour = set(colors)
        self.oracle_text = oracle_text
        self.image_file = config.get("images_dir") + "large/" + self.id + ".jpg"


# carddb = cards.cards
if __name__ == "__main__":
    # cards = Cards(database="fetch")
    # cards = Cards(database="json")
    cards = Cards(database="csv")
    # search = "f:s"
    search = 's:grn c<=BU'
    results = cards.search_on(search)
    print("%d cards, %d matched." % (len(cards.cards), len(results)))

    reference = pd.read_csv("reference.csv", index_col="id")
    # reference = cards.fetch_cards(query=search + " f:s unique:cards", make_fake=False, cached=False)
    # reference = cards.fetch_cards(query="f:s " + search, cached=False, make_fake=False)
    # reference.to_csv("reference.csv")
    print("Reference: " + str(len(reference)))

    print("\nIn reference, not in my results")
    for i,row in reference.iterrows():
        found = results[results['name'] == row['name']]
        count = len(found)
        if count != 1:
            print(row['name'], count)
    print("--")
    print("in results, not in reference")
    for i,row in results.iterrows():
        found = reference[reference['name'] == row['name']]
        count = len(found)
        if count != 1:
            print(row['name'])

