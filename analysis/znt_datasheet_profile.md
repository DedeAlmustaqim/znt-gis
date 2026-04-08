# Profil Data znt_datasheet.xlsx

- Total baris data: **16357**
- Kolom: **10**
- Tahun NIR: **2024**

## Header Kolom
- A: KELURAHAN
- B: KD BLOK
- C: JALAN OP
- D: THN NIR ZNT
- E: KD ZNT
- F: NIR
- G: KLS TANAH
- H: NJOP MINIMAL
- I: NJOP MAKSIMAL
- J: NILAI PER M2 TANAH

## Kualitas Data
- Missing A (KELURAHAN): 0
- Missing B (KD BLOK): 0
- Missing C (JALAN OP): 0
- Missing D (THN NIR ZNT): 0
- Missing E (KD ZNT): 0
- Missing F (NIR): 0
- Missing G (KLS TANAH): 0
- Missing H (NJOP MINIMAL): 0
- Missing I (NJOP MAKSIMAL): 0
- Missing J (NILAI PER M2 TANAH): 0
- Pelanggaran aturan H<=F<=I: 0
- Pelanggaran aturan F==J: 173
- Kunci duplikat (A,B,C,E): 173

## Cakupan Entitas
- kelurahan: 102
- kd_blok: 23
- jalan_op: 9027
- kd_znt: 136

## Catatan GIS
- Data ini bersifat **tabular** dan belum memiliki geometri (koordinat/poligon).
- Untuk pemetaan ZNT pada GIS, perlu layer spasial tambahan (batas bidang/blok/zona).
- Kolom KD ZNT + KD BLOK + KELURAHAN dapat dipakai sebagai kandidat kunci join ke layer spasial resmi.
- Untuk agregasi dan pelaporan PBB-P2 lintas wilayah, **disarankan menambahkan kolom KECAMATAN**.

## Kolom KECAMATAN (Enrichment)
- File mapping `analysis/kelurahan_kecamatan.csv` belum tersedia.
- Template telah dibuat di `analysis/kelurahan_kecamatan_template.csv` (isi kolom kecamatan lalu simpan sebagai `kelurahan_kecamatan.csv`).
