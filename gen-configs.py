#!/usr/bin/env python
"""
Script to produce files for illustrating jet shape 
"""
from __future__ import print_function, division
import os
import subprocess
import numpy as np

# configure this to correspond to the directory where you have build
# fastjet (build should be in the same directory as the installation)
FJBUILD=os.environ["HOME"]+"/work/fastjet/fastjet-release/"

fjexec=FJBUILD+"/example/fastjet_timing_plugins"

def main():
    R   = 1.5
    pt1 = 100
    dRvals = [0.1*R*i for i in range(5,22,2)]
    pt2vals = [5, 25, 50, 75, 99]
    #dRvals = [0.5*R]
    #pt2vals = [25]

    root_commands = [".L jet-plots.C"]

    for dR in dRvals:
        for pt2 in pt2vals:
            p1 = PtRapPhiM(pt1, -dR/2, np.pi)
            p2 = PtRapPhiM(pt2, +dR/2, np.pi)

            #
            outbase = "dR-{:5.3f}-pt2-{:03.0f}".format(dR, pt2)
            outfile = "files/{}.dat".format(outbase)
            outpdf  = "plots/{}.pdf".format(outbase)
            p = subprocess.Popen(fjexec+" -incl 5.0 -antikt -R 1.5 -dense -root {}".
                                 format(outfile),
                                 stdin=subprocess.PIPE, shell=True)
            for pi in [p1,p2]:
                p.stdin.write(pi.__str__() + "\n")
            p.stdin.close()
            root_commands.append('C = showjets("{}","{}")'.format(
                          outfile,
                          "anti-k_{{t}}, R={}, #Delta R_{{12}}/R = {:4.2f}, p_{{t1}} = {}GeV, p_{{t2}} = {}GeV".format(R, dR/R, pt1, pt2)))
            root_commands.append('C->Print("{}");'.format(outpdf))
            root_commands.append('delete C;')

    # now prepare root to generate pdf files from the results
    rc = open('root-commands.txt','w')
    print ("\n".join(root_commands), file=rc)
    rc.close()

    subprocess.call("root -b < root-commands.txt", shell=True)


class LVector(object):
    "Class to holds a lorentz-vector, with very minimal functionality"
    def __init__(self, px, py, pz, E):
        self._vec = np.array([px,py,pz,E])

    def m2(self):
        return self.dot(self)

    def dot(self,other):
        return self._vec[3]*other._vec[3] - (self._vec[:3]*other._vec[:3]).sum()

    def __str__(self):
        return ("{} "*4).format(*self._vec)


def PtRapPhiM(pt, rap, phi, m = 0):
    "Returns a LVector with the specified pt, rapidity, azimuth and mass"
    px = pt * np.cos(phi)
    py = pt * np.sin(phi)
    mt = np.sqrt(m**2 + pt**2)
    pz = mt * np.sinh(rap)
    E  = mt * np.cosh(rap)
    return LVector(px, py, pz, E)


if __name__ == '__main__': main()
# 