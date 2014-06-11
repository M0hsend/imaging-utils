#!/bin/bash
module load global/cluster
module load python/ana

wdir=/home/ssg37927/Desktop/Imaging-tools/imaging-utils/python/tomo-recon/src

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$uniqslots*2"`

echo "Processes running are : ${processes}"

mpirun -np ${processes} \
       --hostfile ${UNIQHOSTS} \
       python ${wdir}/tomo-recon.py $@