#! /usr/bin/env python

# Official twiki:
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/QuickGuideMadGraph5aMCatNLO
import os,sys

def replace_gridpack_generation():
    '''
        official gridpack_generation.sh load extra models
        from central afs directory. One needs to write 
        permission to put his/her UFO there. This is of
        course doable, by submitting request:
        https://twiki.cern.ch/twiki/bin/view/CMS/GeneratorWebRepo

        But for private production and avoid such hassle,
        the workaround is download it from a controllable place.
        The benefit is to keep most other part intact, while 
        minimum changes if official production is desired.
    '''
    cwd = os.getcwd()
    os.chdir( cwd+'/../' )
    if not os.path.isfile('gridpack_generation.sh'):
        sys.exit('gridpack_generation.sh Not exist!! exiting..')
    if not os.path.isfile('gridpack_generation.sh.bkp'):
        # backing up
        cmd = 'cp gridpack_generation.sh gridpack_generation.sh.bkp'
        os.system(cmd)

        replaceWith = 'wget --no-check-certificate https://wsi.web.cern.ch/wsi/mc/$model'
        toBeReplaced = 'wget --no-check-certificate https://cms-project-generators.web.cern.ch/cms-project-generators/$model'
        cmd = 'sed -i "s#%s#%s#g" gridpack_generation.sh' % (toBeReplaced, replaceWith)
        print cmd
        os.system(cmd)
    else:
        print 'gridpack_generation.sh already replaced.'
    os.chdir(cwd)

def format_template(template, paramMap):
    for p in paramMap:
        template = template.replace(p, paramMap[p])
    return template

def stringfy_friendly(num):
    '''
        0.4 -> '0p4'
        125 -> '125'
    '''
    return str(num).replace('.', 'p') if '.' in str(num) else str(num)

def create_parametrized_cards(tempDir, tag, params):
    '''
        copying template cards folder into MadGraph5_aMCatNLO/cards
        with parametrization
    '''
    cwd = os.getcwd()
    os.chdir('cards')
    if os.path.isdir(tag):
        os.system('cp -r {0}/* {1}'.format(tempDir, tag))
    else:
        os.system('cp -r {0} {1}'.format(tempDir, tag))
    os.chdir(tag)
    for f in os.listdir(os.getcwd()):
        if 'custom' in f:
            program_customizedcard(f, params)
            target = tag+'_customizedcards.dat'
        elif 'proc' in f:
            program_proccard(f, tag)
            target = tag+'_proc_card.dat'
        elif 'extramodels' in f:
            target = tag+'_extramodels.dat'
        elif 'run_card' in f:
            target = tag+'_run_card.dat'
        elif 'param_card' in f:
            target = tag+'_param_card.dat'
        else:
            sys.exit('unknown card exist! --> {0}'.format(f))
        cmd = 'mv {0} {1}'.format(f, target)
        os.system(cmd)

    os.chdir(cwd)
    if not os.path.isdir('../cards/'+tag):
        cmd = 'cp -r cards/{0} ../cards/'.format(tag)
    else:
        cmd = 'cp -r cards/{0}/* ../cards/{0}'.format(tag)
    os.system(cmd)

def program_customizedcard(f, params):
    for p in params:
        cmd = 'sed -i "s#%s#%s#g" %s' % (p, str(params[p]), f)
        os.system(cmd)

def program_proccard(f, tag):
    inf = open(f, 'r')
    otf = open(f+'.tmp', 'w')
    for line in inf:
        if line.split()[0] == 'output':
            line = ' '.join([line.split()[0], tag, line.split()[-1]])
        otf.write(line)
    inf.close()
    otf.close()
    os.system('mv {0} {1}'.format(f+'.tmp', f))

def run_gridpack_generation(tag):
    '''
    ./gridpack_generation.sh <name of process card without _proc_card.dat>
    <folder containing cards relative to current location>
    '''
    cwd = os.getcwd()
    os.chdir(cwd+'/../')
    if os.path.isdir(tag):
        print "Remenant exists! Cleaning.. ",
        os.system('rm -rf '+tag)
        print "Cleaned!"
    cmd = './gridpack_generation.sh {0} cards/{0} 1nd'.format(tag)
    os.system(cmd)
    os.chdir(cwd)

def lsf_submit(tag):
    '''
    ./submit_gridpack_generation.sh <memoryInMBytes> <diskInMBytes>
    <queueForMasterJob> <name of process card without _proc_card.dat> <folder
    containing cards relative to current location> <queue>
    '''
    cwd = os.getcwd()
    os.chdir(cwd+'/../')
    cmd = './submit_gridpack_generation.sh 15000 15000 {0} cards/{0} 2nw'.format(tag)
    os.system(cmd)
    os.chdir(cwd)

if __name__ == "__main__":
    replace_gridpack_generation()
    template = 'psZpMuMu_Mps-XMASS_MZp-MED_ctau-DLENGTH'
    
    dm = 50
    med = 4e-1
    dw = 2e-12
    tempDir = 'dp_mumu'

    dl = (dm/med)*(2e-14/dw)
    rawParams = {'XMASS': dm, 'MED': med, 'DWIDTH': dw}
    tagParams = {'XMASS': stringfy_friendly(dm), 'MED': stringfy_friendly(med), 'DLENGTH': stringfy_friendly(dl)}
    tag = format_template(template, tagParams)

    create_parametrized_cards(tempDir, tag, rawParams)
    os.system('ls -alrth ../cards')
    run_gridpack_generation(tag)
    #lsf_submit(tag)

