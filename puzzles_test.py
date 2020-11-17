from puzzles import Puzzles


class TestPuzzles(object):
    def test_puzzle1_1(self):
        assert 3406342 == Puzzles().puzzle1_1()

    def test_puzzle1_2(self):
        assert 5106629 == Puzzles().puzzle1_2()

    def test_puzzle2_1(self):
        assert 30 == Puzzles().puzzle2_1(1, 1, programFile='input-data/input-day2-intcode-program-test.txt')
        assert 4462686 == Puzzles().puzzle2_1(12, 2)
        assert 19690720 == Puzzles().puzzle2_1(59, 36)

    def test_puzzle2_2(self):
        assert 1202 == Puzzles().puzzle2_2(4462686)
        assert 5936 == Puzzles().puzzle2_2(19690720)

    def test_puzzle3_1(self):
        assert 0 == Puzzles().puzzle3_1()
