import csv
import os
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter

NS = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def load_rows(path='znt_datasheet.xlsx'):
    z = zipfile.ZipFile(path)
    ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    shared = []
    for si in ss_root.findall('a:si', NS):
        shared.append(''.join((t.text or '') for t in si.findall('.//a:t', NS)))

    sh = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    headers = {}
    rows = []
    for row in sh.findall('.//a:sheetData/a:row', NS):
        rnum = int(row.attrib['r'])
        rec = {}
        for c in row.findall('a:c', NS):
            ref = c.attrib.get('r', '')
            col = ''.join(ch for ch in ref if ch.isalpha())
            t = c.attrib.get('t')
            v = c.find('a:v', NS)
            value = ''
            if v is not None:
                raw = v.text or ''
                value = shared[int(raw)] if t == 's' else raw
            rec[col] = (value or '').strip()
        if rnum == 1:
            headers = rec
        else:
            rows.append(rec)
    return headers, rows


def profile(headers, rows):
    total = len(rows)
    missing = {col: sum(1 for r in rows if not r.get(col, '').strip()) for col in headers}
    unique = {
        'kelurahan': len({r.get('A', '').strip() for r in rows}),
        'kd_blok': len({r.get('B', '').strip() for r in rows}),
        'jalan_op': len({r.get('C', '').strip().upper() for r in rows}),
        'kd_znt': len({r.get('E', '').strip() for r in rows}),
    }
    year_counts = Counter(r.get('D', '').strip() for r in rows)

    rule_h_f_i = 0
    rule_f_j = 0
    for r in rows:
        f = float(r.get('F', 0))
        h = float(r.get('H', 0))
        i = float(r.get('I', 0))
        j = float(r.get('J', 0))
        if not (h <= f <= i):
            rule_h_f_i += 1
        if abs(f - j) > 1e-9:
            rule_f_j += 1

    key = Counter((r.get('A', ''), r.get('B', ''), r.get('C', '').upper(), r.get('E', '')) for r in rows)
    duplicate_keys = sum(1 for _, n in key.items() if n > 1)

    return {
        'total': total,
        'headers': headers,
        'missing': missing,
        'unique': unique,
        'year_counts': dict(year_counts),
        'viol_h_f_i': rule_h_f_i,
        'viol_f_j': rule_f_j,
        'duplicate_composite_keys': duplicate_keys,
    }


def load_kecamatan_mapping(path='analysis/kelurahan_kecamatan.csv'):
    if not os.path.exists(path):
        return None
    mapping = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            kelurahan = (row.get('kelurahan') or '').strip()
            kecamatan = (row.get('kecamatan') or '').strip()
            if kelurahan:
                mapping[kelurahan] = kecamatan
    return mapping


def write_kecamatan_template(rows, path='analysis/kelurahan_kecamatan_template.csv'):
    kelurahan_values = sorted({r.get('A', '').strip() for r in rows if r.get('A', '').strip()})
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['kelurahan', 'kecamatan'])
        for kel in kelurahan_values:
            writer.writerow([kel, ''])


def main():
    headers, rows = load_rows()
    p = profile(headers, rows)
    write_kecamatan_template(rows)

    mapping = load_kecamatan_mapping()
    mapped = 0
    missing_map = 0
    if mapping is not None:
        kelurahan_values = {r.get('A', '').strip() for r in rows}
        mapped = sum(1 for kel in kelurahan_values if mapping.get(kel))
        missing_map = len(kelurahan_values) - mapped

    lines = []
    lines.append('# Profil Data znt_datasheet.xlsx')
    lines.append('')
    lines.append(f"- Total baris data: **{p['total']}**")
    lines.append(f"- Kolom: **{len(p['headers'])}**")
    lines.append(f"- Tahun NIR: **{', '.join(sorted(p['year_counts'].keys()))}**")
    lines.append('')
    lines.append('## Header Kolom')
    for col in sorted(p['headers']):
        lines.append(f"- {col}: {p['headers'][col]}")
    lines.append('')
    lines.append('## Kualitas Data')
    for col in sorted(p['headers']):
        lines.append(f"- Missing {col} ({p['headers'][col]}): {p['missing'][col]}")
    lines.append(f"- Pelanggaran aturan H<=F<=I: {p['viol_h_f_i']}")
    lines.append(f"- Pelanggaran aturan F==J: {p['viol_f_j']}")
    lines.append(f"- Kunci duplikat (A,B,C,E): {p['duplicate_composite_keys']}")
    lines.append('')
    lines.append('## Cakupan Entitas')
    for k, v in p['unique'].items():
        lines.append(f"- {k}: {v}")
    lines.append('')
    lines.append('## Catatan GIS')
    lines.append('- Data ini bersifat **tabular** dan belum memiliki geometri (koordinat/poligon).')
    lines.append('- Untuk pemetaan ZNT pada GIS, perlu layer spasial tambahan (batas bidang/blok/zona).')
    lines.append('- Kolom KD ZNT + KD BLOK + KELURAHAN dapat dipakai sebagai kandidat kunci join ke layer spasial resmi.')
    lines.append('- Untuk agregasi dan pelaporan PBB-P2 lintas wilayah, **disarankan menambahkan kolom KECAMATAN**.')
    lines.append('')
    lines.append('## Kolom KECAMATAN (Enrichment)')
    if mapping is None:
        lines.append('- File mapping `analysis/kelurahan_kecamatan.csv` belum tersedia.')
        lines.append('- Template telah dibuat di `analysis/kelurahan_kecamatan_template.csv` (isi kolom kecamatan lalu simpan sebagai `kelurahan_kecamatan.csv`).')
    else:
        lines.append('- Sumber enrichment: `analysis/kelurahan_kecamatan.csv`.')
        lines.append(f'- Kelurahan terpetakan ke kecamatan: {mapped}')
        lines.append(f'- Kelurahan belum terpetakan: {missing_map}')

    with open('analysis/znt_datasheet_profile.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
