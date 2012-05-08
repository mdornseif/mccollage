mccollage
=========

Merge several mine craft levels into one.

mccollage uses the excelent [pymclevel][1] library to merge several worlds into on
non-overlapping world. The results will have rough chunk borders. This could be
improved by using something like the algorythims in [mcmerge][2].

The process is extremely slow on the new minecravt "Anvil" level format.
See below on how to solve the issue with raw computing power.

To use it check the requirements of [mcedit][]/[pymclevel][1].
Basically you need numpy und PyYaml.


Simple Usage
============

To add SomeWorld to MainWorld make a backup of MainWorld first:

    cp ~/Library/Application\ Support/minecraft/saves/MainWorld \
        ~/Library/Application\ Support/minecraft/saves/MainWorld.bak

Then start conversion:

    python mccollage.py ~/Library/Application\ Support/minecraft/saves/MainWorld \
        ~/Library/Application\ Support/minecraft/saves/SomeWorld

This might take a vew minutes and a few Gigabytes (!) of RAM.


Batch Collage of many Levels
============================

TBD


Using a gib EC2 Server for doing the merge
==========================================

Start an instance with 68 GB Ram:

    ec2-run-instances  --instance-type m2.4xlarge --key YOURKEYNAME ami-1de8d369

Check `ec2-describe-instances | grep m2.4xlarge` untill you know the IP-Address of the machine, then SSH into it and install required packages:

    ssh -i ~/.ssh/YOURKEYNAME ubuntu@EC2IP
    sudo apt-get install python-numpy python-yaml python-cairo git rsync
    
Then rsync your stuff to the machine and run mccollage there.

Finally Shut down all the large instances - they are expensive!

    ec2-describe-instances | egrep m2.4xlarge | cut -f2 | xargs ec2-terminate-instances
