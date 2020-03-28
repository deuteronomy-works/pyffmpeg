# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 13:19:41 2020

"""
import os
from subprocess import check_output

class option():


    """
    """


    def __init__(self, opt):
        self.ffmpeg_file
        if opt == 'i':
            self.start = self._com_i

    def start(self):
        pass

    def _com_i(self, i, o):

        """
        """

        if not os.path.exists(o):
            check_output([
                self.ffmpeg_file, '-i',
                i,
                o
                ], shell=True)

        return o
