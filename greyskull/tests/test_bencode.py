# -*- coding: utf-8 -*-
"""
Bencode encoder unit tests
"""

from unittest import TestCase

from greyskull.bencode import bencode


class TestBencode(TestCase):
    def test_char(self):
        self.assertEqual(bencode(4), 'i4e')

    def test_zero(self):
        self.assertEqual(bencode(0), 'i0e')

    def test_negative(self):
        self.assertEqual(bencode(-10), 'i-10e')

    def test_long(self):
        self.assertEqual(bencode(12345678901234567890), 'i12345678901234567890e')

    def test_null_string(self):
        self.assertEqual(bencode(''), '0:')

    def test_string(self):
        self.assertEqual(bencode('abc'), '3:abc')

    def test_int(self):
        self.assertEqual(bencode('1234567890'), '10:1234567890')

    def test_empty_list(self):
        self.assertEqual(bencode([]), 'le')

    def test_char_list(self):
        self.assertEqual(bencode([1, 2, 3]), 'li1ei2ei3ee')

    def test_list_list(self):
        self.assertEqual(bencode([['Alice', 'Bob'], [2, 3]]), 'll5:Alice3:Bobeli2ei3eee')

    def test_empty_dict(self):
        self.assertEqual(bencode({}), 'de')

    def test_dict(self):
        self.assertEqual(bencode({'age': 25, 'eyes': 'blue'}), 'd3:agei25e4:eyes4:bluee')

    def test_compound_dict(self):
        self.assertEqual(bencode({'spam.mp3': {'author': 'Alice', 'length': 100000}}),
                         'd8:spam.mp3d6:author5:Alice6:lengthi100000eee')

    def test_raises_type_error(self):
        with self.assertRaises(TypeError):
            bencode({1: 'foo'})