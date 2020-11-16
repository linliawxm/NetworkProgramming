import gzip
import lzma
import zipfile
import os
from datetime import datetime

#源文件
benchmark = {}
benchmark['OrgSize'] = os.path.getsize('alice_Large.txt')
with open('alice_Large.txt','rb') as f:
    textContent = f.read()

#gzip 压缩
gzipPara = []
gzipStartTime = datetime.now()
with gzip.open('alice_Large_gzip.gz', 'wb') as f:
    f.write(textContent)
gzipDuration = str(datetime.now() - gzipStartTime)
gzipSize = os.path.getsize('alice_Large_gzip.gz')
gzipRatio = '{:.2%}'.format(gzipSize/benchmark['OrgSize'])
gzipPara.append(gzipDuration)
gzipPara.append(gzipSize)
gzipPara.append(gzipRatio)

#gzip 解压缩
gunzipStartTime = datetime.now()
with gzip.open('alice_Large_gzip.gz', 'rb') as f:
    zipContent = f.read()
    with open('alice_Large_gzip_unzip.txt','w') as uf:
        uf.write(zipContent.decode("utf-8"))
gunzipDuration = str(datetime.now() - gunzipStartTime)
gunzipSize = os.path.getsize('alice_Large_gzip_unzip.txt')
gzipPara.append(gunzipDuration)
gzipPara.append(gunzipSize)

benchmark['gzip'] = gzipPara

#lzma 压缩
lzmaPara = []
lzmaStartTime = datetime.now()
with lzma.open('alice_Large_lzma.xz', 'wb') as f:
    f.write(textContent)
lzmaDuration = str(datetime.now() - lzmaStartTime)
lzmaSize = os.path.getsize('alice_Large_lzma.xz')
lzmaRatio = '{:.2%}'.format(lzmaSize/benchmark['OrgSize'])
lzmaPara.append(lzmaDuration)
lzmaPara.append(lzmaSize)
lzmaPara.append(lzmaRatio)
#lzma 解压缩
lzmaunzipStartTime = datetime.now()
with lzma.open('alice_Large_lzma.xz', 'rb') as f:
    zipContent = f.read()
    with open('alice_Large_lzma_unzip.txt','w') as uf:
        uf.write(zipContent.decode("utf-8"))
lzmaunzipDuration = str(datetime.now() - lzmaunzipStartTime)
lzmaunzipSize = os.path.getsize('alice_Large_lzma_unzip.txt')
lzmaPara.append(lzmaunzipDuration)
lzmaPara.append(lzmaunzipSize)

benchmark['lzma'] = lzmaPara

#zipfile 压缩
zipfilePara = []
zipfileStartTime = datetime.now()
with zipfile.ZipFile('alice_Large_zipfile.zip', 'w', zipfile.ZIP_DEFLATED) as f:
    f.write('alice_Large.txt')
zipfileDuration = str(datetime.now() - zipfileStartTime)
zipfileSize = os.path.getsize('alice_Large_zipfile.zip')
zipfileRatio = '{:.2%}'.format(zipfileSize/benchmark['OrgSize'])
zipfilePara.append(zipfileDuration)
zipfilePara.append(zipfileSize)
zipfilePara.append(zipfileRatio)
#zipfile 解压缩
zipfileunzipStartTime = datetime.now()
with zipfile.ZipFile('alice_Large_zipfile.zip', 'r') as zf:
    filepath = zf.extract(zf.namelist()[0], './zipfile/') #suppose only one file
zipfileunzipDuration = str(datetime.now() - zipfileunzipStartTime)
zipfileunzipSize = os.path.getsize('./zipfile/alice_Large.txt')
zipfilePara.append(zipfileunzipDuration)
zipfilePara.append(zipfileunzipSize)

benchmark['zipfile'] = zipfilePara

print(benchmark)
pass