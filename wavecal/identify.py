#!/usr/bin/env python

import optparse

def parse_args():
    # Parse command line arguments
    usage = '%prog [options] linepos linelist'
    p = optparse.OptionParser(usage=usage, version='test')
    p.add_option('--trim', '-t', action='store_true', dest='trim', default='',
                help='Trim the line list to speed things up')
    p.add_option('--cwlen', action='store', dest='approx_cwlen', default=None,
                 help='Approximate central wavelength')
    p.add_option('--disp', action='store', dest='approx_disp', default=None,
                 help='Approximate dispersion')
    p.add_option('--crpix', action='store', dest='crpix', default=None,
                 help='Central pixel')
    
    (options, args) = p.parse_args()
    
    if len(args) != 2:
        errmsg ='\nUSAGE ERROR:'
        p.print_help()
        raise SystemExit, errmsg
    
    if options.trim:
        errmsg = ''
        if options.approx_cwlen == None:
            errmsg = '\nApproximate central wavelength missing.'
        if options.approx_disp == None:
            errmsg += '\nApproximate dispersion missing.'
        if options.crpix == None:
            errmsg += '\nCentral pixel position missing.'
        if errmsg != '':
            p.print_help()
            raise SystemExit, errmsg
        
    
    return (options, args)


def calc_triangles (positions, all=False):
    triangles = []
    if all:
        print ('here')
        for i in range(len(positions)):
            for j in range(i+1, len(positions)):
                for k in range(j+1, len(positions)):
                    for l in range(k+1, len(positions)):
                        #print (i,j,k)
                        a = positions[j]-positions[i]
                        b = positions[k]-positions[j]
                        c = positions[l]-positions[k]
                        #size = a+b+c
                        #c = a+b
                        x = a / b
                        y = b / c
                        z = a / c
                        #print (x,y)
                        triangles.append((positions[i], positions[j], positions[k], positions[l], x, y, z))
    else:
        print ('else')
        for i in range(len(positions)-3):
            a = positions[i+1]-positions[i]
            b = positions[i+2] - positions[i+1]
            #c = a+b
            c = positions[i+3] - positions[i+2]
            #size = a+b+c
            x = a / b
            y = b /c
            z = a / c
            triangles.append((positions[i], positions[i+1], positions[i+2], positions[i+3], x, y, z))
            
    return triangles

def trim_linelist (linelist, cwlen, dispersion, crpix):
    # Given approximate central wavelength, dispersion, and central pixel
    # trim the line list.  This might help speed things up, at least during
    # the development phase.
    
    #wlen1 = cwlen - (dispersion * crpix)
    #wlen2 = cwlen + (dispersion * crpix)
    wlen1 = 4000
    wlen2 = 6700
    
    linelist = [ wlen for wlen in linelist if wlen > wlen1 and wlen < wlen2 ]
    
    return(linelist)

if __name__ == '__main__':
    (options, args) = parse_args()
    if options.trim:
        approx_cwlen = float(options.approx_cwlen)
        approx_dispersion = float(options.approx_disp)
        crpix = int(options.crpix)
    
    linepos = []
    f = open(args[0], 'r')
    for line in f.readlines():
        linepos.append(float(line.split()[0]))
    f.close()
    
    linelist = []
    f = open(args[1], 'r')
    for line in f.readlines():
        if line.split()[0] != '#':
            linelist.append(float(line.split()[0]))
    f.close()
    if options.trim:
        linelist = trim_linelist(linelist, approx_cwlen, approx_dispersion, crpix)
        f = open('trimmedlinelist.dat','w')
        for value in linelist:
            f.write(str(value)+'\n')
        f.close()
    linelist.reverse()
    
    postriangles = calc_triangles(linepos)
    listtriangles = calc_triangles(linelist, all=True)
    
    postriangles_str = []
    for l in postriangles:
        newstr = ''
        for x in l:
            newstr += str(x)+'\t'
        newstr += '\n'
        postriangles_str.append(newstr)

    listtriangles_str = []
    for l in listtriangles:
        newstr = ''
        for x in l:
            newstr += str(x)+'\t'
        newstr += '\n'
        listtriangles_str.append(newstr)
            
    f = open('postriangles.dat', 'w')
    f.writelines(postriangles_str)
    f.close()
    f = open('listtriangles.dat', 'w')
    f.writelines(listtriangles_str)
    f.close()
    
    matches = {}
    for (p1, p2, p3, p4, px, py, pz) in postriangles:
        matches[p1] = []
        matches[p2] = []
        matches[p3] = []
        matches[p4] = []
    for (p1, p2, p3, p4, px, py, pz) in postriangles:
        for (l1, l2, l3, l4, lx, ly, lz) in listtriangles:
            dx = abs(px-lx)
            dy = abs(py-ly)
            dz = abs(pz-lz)
            if (dx < (0.01*px) and dy < (0.01*py) and dz < (0.01*pz)):
                matches[p1].append(l1)
                matches[p2].append(l2)
                matches[p3].append(l3)
                matches[p4].append(l4)

    # check if the most frequent match is the correct one
    #  Answer:  No.  Not with the current measurements
    for key in sorted(matches.iterkeys()):
        if len(matches[key]) != 0:
            count=1
            mode = matches[key][0]
            for value in matches[key]:
                c = matches[key].count(value)
                if c > count:
                    count = c
                    mode = value
            print (key, mode)

    #matches[545.68].sort()
    f = open('matches.dat','w')
    #f.write(str(matches[545.68]))
    for key in sorted(matches.iterkeys()):
        f.write(str(key)+str(matches[key])+'\n')
    f.close()
    