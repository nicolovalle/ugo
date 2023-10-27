# ugo
*The family of bots for ITS operations*

### User guide and caveats

Note: this is a well working but very quickly written code. Much can be improved. 


#### Mattermost

`UGo Home` is the team where the bot posts messages. This is done through [mattermost incoming webhooks](https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/).


#### ITS QC

The [QC global quality object](http://ali-qcdb-gpn.cern.ch:8083/browse/qc/ITS/MO/ITSQualityTask/QualitySummary) is retrieved by the root macto `getObject2.C`. The argument of the macro is a text file where the quality summary is dumped. In `ugo.py`, this file is called `objectreport.txt`. To let the script executing `getObject2.C` **you need to have a QualityControl environment loaded**.

#### ugo.py

Ugo checks the presence of new runs querying the [bookkeping api](https://ali-bookkeeping.cern.ch/api/runs). When a new runs is found, it checks the global ITS QC quality. Everything is posted in the mattermost channel `Ugo-QC`. 

In the current implementation, `ugo.py` shall be executed every 5 minutes to be consistent with the posted messages. At each cycle the script reads cached information from previous cycle and updates them. This is done by updating plain txt files:

- `lastrun.txt` (it contains run number checked in the previous cycle)
- `lastquality.txt` (it contains QC quality from the last cycle check)
- `qcneeded.txt` (according to the outcome of the last cycle, the boolean in this file instructs ugo to check or to skip the QC checks in the current cycle)


The QC quality is overwritten in the file `objectreport.txt` at each cycle by the root macro. Moreover, the stdout of the root macro is appended to `getobject_stdout.out` (it can become large!).

This is a suggestion for the bash loop calling `ugo.py`. You can redirect the output to a file to have a well-structured log history.

```
python3 ugo.py start

while true
do
    python3 ugo.py 
    sleep 285
    until [ -f RUN ]
    do
        sleep 2
    done
done
```

It needs the presence of a dummy file called `RUN`. By removing it, the loop can be paused and one can freely work on `ugo.py`.

When `ugo.py` is run with `start` option it posts a welcome message and it reinitializes the cache txt files.

#### mrbeam.py

*This is a more immature piece of code!*

MrBeam is supposed to parse the information from LHC page 1 and to post changes of message, fill condition and machine status. Currently, the parsing is done on the information uploaded to https://lhcstatus2.ovh/. An official LHC source would be more convenient.

`mrbeam.py` shall be run in loop with any desired frequency, keeping in mind that https://lhcstatus2.ovh/ has an updating frequency of (probably) about 2 minutes. `vistars.json` and `vistars-last.json` are parsed at each cycle. That's a suggestion on how to run it:

```
while true
do
   rm -f vistars-last.json
   mv vistars.json vistars-last.json
   curl -O https://lhcstatus2.ovh/vistars.json
   python3 mrbeam.py
   sleep 119
   until [ -f RUN1 ]
   do
       sleep 2
   done
done
```

It needs the presence of a dummy file called `RUN1`. By removing it, the loop can be paused and one can freely work on `mrbeam.py`.
