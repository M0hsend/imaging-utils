module load global/cluster

qsub -pe openmpi 16 -q medium.q -l release=rhel6 /home/ssg37927/DAWN_snapshot/mpi-test/src/mpijob_test_ana.sh