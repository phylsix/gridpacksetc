# gridpacksetc

## Notes
The workhorse is script `gridpack_generation.sh` or `submit_gridpack_generation.sh`
of [cms-sw/genproductions](https://github.com/cms-sw/genproductions).

`submit.py` here is sort of a wrapper to remove redundant keystokes.
However, as parameters are highly model-dependent, to make everything working
smoothly for your model, one need to take care of the following things:

1. **cards template**
e.g. [cards/dp_mumu](https://github.com/phylsix/GridPacker/tree/sidm-branch/cards/dp_mumu)

It contains 4 .dat files:
```
${templateName}_run_card.dat
${templateName}_proc_card.dat
${templateName}_customizecards.dat
${templateName}_extramodels.dat
```
`run_card.dat` and `proc_card.dat` should be from interactive MadGraph running with a model.

`customizecards.dat` should tell the model parameters one wants to change. Instead of setting a specific number, we write a placeholder in template cards so we can replace them with what we want.

`extramodels.dat` should be the name of one's model file.

2. **model file**

The model file should be put in a public downloadable place.

`gridpack_generation.sh` will download extramodel from https://cms-project-generators.web.cern.ch/cms-project-generators . However, if you did not upload your model into this place yet(like me), `submit.py` will replace this url to the url pointing to your model. e.g. [here](https://github.com/phylsix/GridPacker/blob/sidm-branch/submit.py#L29)

3. **parameters**

`submit.py` will use template card to make individual cards by replacing placeholers with concrete numbers you set.

In https://github.com/phylsix/GridPacker/blob/sidm-branch/submit.py#L150-L162
```
    template = 'SIDMmumu_Mps-XMASS_MZp-MED_ctau-DLENGTH'
    
    mps = 200
    med = 1.2
    #dw  = 6.6e-15
    epsilon = 2.36e-5
    tempDir = 'dp_mumu'

    #ctau = round(2e-14/dw, 2)
    ctau = 0.08 * (0.1/med) * (1e-4/epsilon)**2 * 0.1 #cm
    rawParams = {'XMASS': mps, 'MED': med, 'EPSILON': epsilon}
    tagParams = {'XMASS': stringfy_friendly(mps), 'MED': stringfy_friendly(med), 'DLENGTH': stringfy_friendly(ctau)}
    tag = format_template(template, tagParams)
```
Above, I create a string which will be used for the naming of the generated gridpack. Then I specify parameter values.

4. **submit method**

In https://github.com/phylsix/GridPacker/blob/sidm-branch/submit.py#L166-L167
```
    #run_gridpack_generation(tag)
    lsf_submit(tag)
```
There are 2 ways working, 
- `run_gridpack_generation(tag)` will do the job interactively, calling `gridpack_generation.sh`
- `lsf_submit(tag)` will submit the job to CERN lxbatch, calling `submit_gridpack_generation.sh`

One can choose either one by commenting out the other.

## Instructions
**step1: clone genproductions repo**
```
git clone git@github.com:cms-sw/genproductions.git genproductions -b mg26x
# or clone the master branch, which is based on mg24x.
# Both branches get official support
# (I use mg26x branch because mg24x is not working for SIDM model)
# git clone git@github.com:cms-sw/genproductions.git
```

**step2: clone GridPacker repo**
```
cd genproductions/bin/MadGraph5_aMCatNLO/
git clone https://github.com/phylsix/GridPacker.git GridPacker -b sidm-branch
cd GridPacker
```

**step3: go through parameter settings**
```
# after setting parameters..
./submit.py
```

## Reference Twiki:
1. https://twiki.cern.ch/twiki/bin/view/CMS/QuickGuideMadGraph5aMCatNLO
2. https://twiki.cern.ch/twiki/bin/viewauth/CMS/GeneratorMain#How_to_produce_gridpacks
3. https://twiki.cern.ch/twiki/bin/viewauth/CMS/Moriond18MC
