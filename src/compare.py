import os
import sys
import coltools as ct


def main(argv):
    collection = {"Mountain": 99, "Swamp": 99, "Forest": 99, "Island": 99, "Plains": 99}
    mtga_cards = ct.fal("/home/coljac/Downloads/mtga_cards_g.csv")
    for line in mtga_cards[1:]:
        name = line.split('"')[1]
        toks = line.split(",")
        qty = int(toks[-1])
        name = name.replace('"', "")
        collection[name] = int(qty)

    decklist = ct.fal(argv[0])
    decklist_cards = {}
    needed = {}
    for line in decklist:
        if len(line) == 0:
            continue
        qty = line.split(" ")[0].replace("x", "").replace("X", "")
        cardname = " ".join(line.split(" ")[1:-2])
        decklist_cards[cardname] = int(qty)

        needed = int(qty)
        have = collection.get(cardname, 0)
        if have < needed:
            print("%d/%d %s" % ((needed - have), needed, cardname))
        # print("%d/%d %s" % (have, needed, cardname))


if __name__ == "__main__":
    main(sys.argv[1:])
