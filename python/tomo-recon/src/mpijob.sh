#!/bin/bash
MPIRUN=/dls_sw/prod/tools/RHEL6-x86_64/openmpi/1-6-5/prefix/bin/mpirun
PYTHON=/dls_sw/prod/tools/RHEL6-x86_64/defaults/bin/dls-python
wdir=/home/ssg37927/Desktop/Imaging-tools/imaging-utils/python/tomo-recon/src/

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$uniqslots*2"`

echo "Processes running are : ${processes}"

$MPIRUN -np ${processes} \
        --hostfile ${UNIQHOSTS} \
        --wd ${wdir} \
        --tag-output \
        $PYTHON ${wdir}/tomo-recon.py