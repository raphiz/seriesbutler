from pyseries.special_treatment import convert
from nose.tools import *


def test_vidbull():
    src = 'http://vidbull.com/embed-1kdvv4aj2beo-640x318.html'
    expected = 'vidbull: ignored!'
    assert_equals(expected, convert(src))


def test_vodlocker():
    src = 'http://vodlocker.com/embed-v4y2drplpx6v-640x360.html'
    expected = 'http://vodlocker.com/v4y2drplpx6v'
    assert_equals(expected, convert(src))


def test_playedto():
    src = 'http://played.to/embed-ouc43vsdvmgj-640x360.html'
    expected = 'http://played.to/ouc43vsdvmgj'
    assert_equals(expected, convert(src))
