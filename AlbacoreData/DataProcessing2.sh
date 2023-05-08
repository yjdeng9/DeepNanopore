#! /bin/bash
python genProcessData.py -i /data/dengyongjie/m6aNanopore/datas/Basecalling_data/smallSampleData/GXB01133/BNP18L0066-0802-A/ -o /data/dengyongjie/m6aNanopore/datas/Processing_data/testMotif/positive/
python genProcessData.py -i /data/dengyongjie/m6aNanopore/datas/Basecalling_data/smallSampleData/GXB01184/BNP18L0039-0515/ -o /data/dengyongjie/m6aNanopore/datas/Processing_data/testMotif/negative/
#
# cd /data/dengyongjie/meDNA/scripts/LinuxModelScript/AlbacoreData
# cd /data/dengyongjie/meDNA/datas/Processing_data/Motifs/testData/meNew
# -i /data/dengyongjie/meDNA/datas/Basecalling_data/testData/meNew/ -o /data/dengyongjie/meDNA/datas/Processing_data/Motifs/testData/meNew/