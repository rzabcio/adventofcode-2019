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
        assert 6 == Puzzles().puzzle3_1(descFile='input-data/input-day3-wires-test1.txt')
        assert 159 == Puzzles().puzzle3_1(descFile='input-data/input-day3-wires-test2.txt')
        assert 135 == Puzzles().puzzle3_1(descFile='input-data/input-day3-wires-test3.txt')
        # assert 1285 == Puzzles().puzzle3_1(descFile='input-data/input-day3-wires.txt')

    def test_puzzle3_2(self):
        assert 30 == Puzzles().puzzle3_2(descFile='input-data/input-day3-wires-test1.txt')
        assert 610 == Puzzles().puzzle3_2(descFile='input-data/input-day3-wires-test2.txt')
        assert 410 == Puzzles().puzzle3_2(descFile='input-data/input-day3-wires-test3.txt')
        # assert 1258 == Puzzles().puzzle3_2(descFile='input-data/input-day3-wires.txt')

    def test_puzzle4_1(self):
        assert 1 == Puzzles().puzzle4_1(start=111111, end=111111)
        assert 0 == Puzzles().puzzle4_1(start=223450, end=223450)
        assert 0 == Puzzles().puzzle4_1(start=123789, end=123789)

    def test_puzzle4_2(self):
        assert 1 == Puzzles().puzzle4_2(start=112233, end=112233)
        assert 0 == Puzzles().puzzle4_2(start=123444, end=123444)
        assert 1 == Puzzles().puzzle4_2(start=111122, end=111122)
        assert 876 == Puzzles().puzzle4_2()
        
        assert 0 == Puzzles().puzzle4_2(start=111111, end=111111)
        assert 1 == Puzzles().puzzle4_2(start=112222, end=112222)
        assert 0 == Puzzles().puzzle4_2(start=123455, end=123455)
        assert 1 == Puzzles().puzzle4_2(start=122255, end=122255)
