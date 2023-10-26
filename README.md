# ugo
*The family of bots for ITS operations*

### User guide and caveats

Note: this is a well working but very quickly written code. Much can be improved. 


#### Mattermost

`UGo Home` is the team where the bot posts messages. 

Posting is done through mattermost incoming webhooks. 

#### ITS QC

The QC object is retrieved by `getObject2.C` root macro. The argument of the macro is a text file where the quality summary is dumped. In `ugo.py` this file is called `objectreport.txt`.

**You need to have a QualityControl environment loaded**.

#### ugo.py

Ugo checks the presence of new runs querying the bookkeping. When new runs are found, it also check the global ITS QC quality. Everything is posted in the mattermost channel Ugo-QC. 

`ugo.py` shall be executed every approx. 5 minutes. At each cycle it reads cached information from previous cycle and updates them. This is done by saving plain text files:

- lastrun.txt (contains run number checked in the previous cycle)
- lastquality.txt (contains QC quality from the last cycle check)
- qcneeded.txt (according to outcome of the last cycle, the boolean in this file instructs ugo to check or skip the QC check in the current cycle)


The QC quality is dumped and overwritten in `objectreport.txt` by the root macro at each cycle. Moreover, the stdout of the root macro is appended to `getobject_stdout.out`.

This is a suggestion for the bash loop calling `ugo.py`:

```
python3 ugo.py start

while true
do
python3 ugo.py | tee ugo.log
sleep 285
until [ -f RUN ]
do
     sleep 2
done
done
```

It needs the presence of a dummy file called `RUN`. By removing it, the loop can be paused and one can freely work on `ugo.py`.

When `ugo.py` is run with `start` option it posts a welcome message and reinitializes the cache txt files.

#### mrbeam.py

*This is even a more immature piece of code!*

MrBeam parses the information from LHC page 1 and post changes of message, fill condition and machine status. The parsing is done on the information poste on https://lhcstatus2.ovh/ . Official LHC source would be better. 

`mrbeam.py` shall be run in loop with any desired frequency, keeping in mind that https://lhcstatus2.ovh/ is not very frequently updated. `vistars.json` and `vistars-last.json` are parsed at each cycle. That's a suggestion on how to run it:

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