#!/usr/bin/env python

import unittest

from gtp import pre_engine, pre_controller
from gtp import parse_message, parse_move
from gtp import gtp_boolean, gtp_list, gtp_color, gtp_vertex, gtp_move

from gtp import BLACK, WHITE, PASS, RESIGN
from gtp import Engine
from gtp import MinimalGame


class PreProcessingTest(unittest.TestCase):

    def test_pre_engine(self):
        self.assertEqual(pre_engine("foo\rbar"), "foobar")
        self.assertEqual(pre_engine("foo\nbar"), "foo\nbar")
        self.assertEqual(pre_engine("foo\tbar"), "foo bar")
        self.assertEqual(pre_engine("foo # bar"), "foo ")

    def test_pre_controller(self):
        self.assertEqual(pre_controller("foo\rbar"), "foobar")
        self.assertEqual(pre_controller("foo\nbar"), "foo\nbar")
        self.assertEqual(pre_controller("foo\tbar"), "foo bar")


class ParseTest(unittest.TestCase):

    def test_parse_message(self):
        self.assertEqual(parse_message("foo"), (None, "foo", None))
        self.assertEqual(parse_message("foo bar"), (None, "foo", "bar"))
        self.assertEqual(parse_message("1 foo"), (1, "foo", None))
        self.assertEqual(parse_message("1 foo bar"), (1, "foo", "bar"))
        self.assertEqual(parse_message("1"), (1, None, None))
        self.assertEqual(parse_message(""), (None, "", None))
        self.assertEqual(parse_message(" "), (None, "", None))

    def test_parse_move(self):
        self.assertEqual(parse_move("B D4"), (BLACK, (4, 4)))
        self.assertFalse(parse_move("C X"))
        self.assertFalse(parse_move("B 55"))
        self.assertFalse(parse_move("B dd"))
        self.assertFalse(parse_move("B X"))
        self.assertFalse(parse_move("B"))
        self.assertEqual(parse_move("WHITE q16 XXX"), (WHITE, (16, 16)))
        self.assertEqual(parse_move("black pass"), (BLACK, PASS))


class FormatTest(unittest.TestCase):

    def test_gtp_boolean(self):
        self.assertEqual(gtp_boolean(True), "true")
        self.assertEqual(gtp_boolean(False), "false")

    def test_gtp_list(self):
        self.assertEqual(gtp_list(["foo", "bar"]), "foo\nbar")

    def test_gtp_color(self):
        self.assertEqual(gtp_color(BLACK), "B")
        self.assertEqual(gtp_color(WHITE), "W")

    def test_gtp_vertex(self):
        self.assertEqual(gtp_vertex((4, 4)), "D4")
        self.assertEqual(gtp_vertex((16, 16)), "Q16")
        self.assertEqual(gtp_vertex(PASS), "pass")
        self.assertEqual(gtp_vertex(RESIGN), "resign")

    def test_gtp_move(self):
        self.assertEqual(gtp_move(BLACK, (3, 2)), "B C2")


class CommandsTest(unittest.TestCase):

    def setUp(self):
        self.engine = Engine(MinimalGame())

    def test_admin_commands(self):
        response = self.engine.send("foo\n")
        self.assertEqual(response, "? unknown command\n\n")

        response = self.engine.send("protocol_version\n")
        self.assertEqual(response, "= 2\n\n")
        response = self.engine.send("1 protocol_version\n")
        self.assertEqual(response, "=1 2\n\n")

        response = self.engine.send("2 name\n")
        self.assertEqual(response, "=2 gtp (python library)\n\n")

        response = self.engine.send("3 version\n")
        self.assertEqual(response, "=3 0.2\n\n")

        response = self.engine.send("4 known_command name\n")
        self.assertEqual(response, "=4 true\n\n")
        response = self.engine.send("5 known_command foo\n")
        self.assertEqual(response, "=5 false\n\n")

        response = self.engine.send("6 list_commands\n")
        self.assertEqual(
            response,
            "=6 boardsize\nclear_board\nfinal_score\ngenmove\nknown_command\n"
            "komi\nlist_commands\nname\nplay\nprotocol_version\nquit\n"
            "version\n\n")

        response = self.engine.send("99 quit\n")
        self.assertEqual(response, "=99\n\n")

    def test_core_play_commands(self):
        response = self.engine.send("7 boardsize 100")
        self.assertEqual(response, "?7 unacceptable size\n\n")
        response = self.engine.send("8 boardsize 19")
        self.assertEqual(response, "=8\n\n")
        response = self.engine.send("9 boardsize foo")
        self.assertEqual(response, "?9 non digit size\n\n")

        response = self.engine.send("9 clear_board")
        self.assertEqual(response, "=9\n\n")

        response = self.engine.send("10 komi 6.5")
        self.assertEqual(response, "=10\n\n")
        response = self.engine.send("11 komi foo")
        self.assertEqual(response, "?11 syntax error\n\n")

    def test_core_play(self):
        response = self.engine.send("12 play black D4")
        self.assertEqual(response, "=12\n\n")

        response = self.engine.send("13 genmove white")
        # test player will always return this
        self.assertEqual(response, "=13 pass\n\n")

        response = self.engine.send("14 play black Z25")
        self.assertEqual(response, "?14 illegal move\n\n")

        response = self.engine.send("15 play white D4")
        self.assertEqual(response, "?15 illegal move\n\n")

        response = self.engine.send("16 play black pass")
        self.assertEqual(response, "=16\n\n")

        response = self.engine.send("17 genmove orange")
        self.assertEqual(response, "?17 unknown player: orange\n\n")

        response = self.engine.send("18 final_score")
        self.assertEqual(response, "=18 ?\n\n")


if __name__ == "__main__":
    unittest.main()
