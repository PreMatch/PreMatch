import unittest
from core_interface import *

class RosterTest(unittest.TestCase):
    roster: Roster

    def setUp(self):
        self.roster = Roster([])

    def iteration(self):
