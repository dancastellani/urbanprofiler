# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$Jul 30, 2014 9:21:42 PM$"

class ApplicationExecption(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)