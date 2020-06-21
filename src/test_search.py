import unittest
from cards import Cards

class TestSearchResults(unittest.TestCase):
    def setUp(self):
        self.cards = Cards(database="csv")

    def do_search(self, search):
        results = self.cards.search_on(search)
        return len(results), results

    def test_cmc(self):
        l, results = self.do_search("cmc=1")
        self.assertEqual(126, l)
        l, results = self.do_search("cmc:1")
        self.assertEqual(126, l)
        l, results = self.do_search("cmc>1")
        self.assertEqual(1073, l)
        l, results = self.do_search("cmc<3")
        self.assertEqual(459, l)
        l, results = self.do_search("cmc<=3")
        self.assertEqual(743, l)
        l, results = self.do_search("cmc>=5")
        self.assertEqual(274, l)

    def test_name(self):
        l, results = self.do_search("Knight")
        self.assertEqual(16, l)
        l, results = self.do_search("name:knight")
        self.assertEqual(16, l)
        l, results = self.do_search("n:knight")
        self.assertEqual(16, l)
        l, results = self.do_search("n:kNiGhT")
        self.assertEqual(16, l)
        l, results = self.do_search("island")
        self.assertEqual(1, l)
        l, results = self.do_search("knight malice")
        self.assertEqual(1, l)
        l, results = self.do_search("knight of malice")
        self.assertEqual(1, l)

    def test_oracle(self):
        l, results = self.do_search("o:taPped")
        self.assertEqual(70, l)
        l, results = self.do_search("o:token")
        self.assertEqual(119, l)
        l, results = self.do_search('o:"indestructible" o:"target"')
        self.assertEqual(5, l, 'o:"indestructible" o:"target"')
        l, results = self.do_search('o:"destroy target"')
        self.assertEqual(58, l)
        l, results = self.do_search('o:"destroy" o:target')
        self.assertEqual(63, l)
        l, results = self.do_search('s:grn o:+2/+2')
        self.assertEqual(6, l)


    def test_compound(self):
        l, results = self.do_search("o:token cmc=1")
        self.assertEqual(6, l, "o:token cmc=1")
        l, results = self.do_search("n:demon cmc>3")
        self.assertEqual(2, l)

    def test_type(self):
        l, results = self.do_search("t:instant")
        self.assertEqual(150, l)
        l, results = self.do_search("t:merfolk")
        self.assertEqual(44, l)
        l, results = self.do_search("type:wizard")
        self.assertEqual(50, l)
        l, results = self.do_search("type:'merfolk shaman'")
        self.assertEqual(12, l)

    def test_set(self):
        l, results = self.do_search("set:dom")
        self.assertEqual(265, l)
        l, results = self.do_search("set:grn")
        self.assertEqual(268, l)

    # def test_format(self):
    #     l, results = self.do_search("f:s")
    #     self.assertEqual(1248, l)

    def test_colours(self):
        l, results = self.do_search("c:BW")
        self.assertEqual(10, l)
        l, results = self.do_search("c>WU")
        self.assertEqual(3, l)
        l, results = self.do_search("c>=wU")
        self.assertEqual(11, l)
        l, results = self.do_search("c:U")
        self.assertEqual(255, l)
        # l, results = self.do_search("c<UWR")
        # self.assertEqual(773, l)
        l, results = self.do_search("c:M")  #
        self.assertEqual(165, l)
        l, results = self.do_search("c:c") #
        self.assertEqual(159, l)
        l, results = self.do_search("s:grn c<=bu")
        self.assertEqual(107, l)
        # l, results = self.do_search("c<=c") #
        # self.assertEqual(159, l)
        # l, results = self.do_search("c<=wr") #
        # self.assertEqual(555, l)



if __name__ == '__main__':
    unittest.main()
