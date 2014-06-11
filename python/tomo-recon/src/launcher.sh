module load global/cluster

qsub -pe openmpi 16 -q medium.q -l release=rhel6 /home/ssg37927/Desktop/Imaging-tools/imaging-utils/python/tomo-recon/src/mpijob.sh /home/ssg37927/Desktop/Imaging-tools/imaging-utils/python/tomo-recon/test_data/24737.nxs