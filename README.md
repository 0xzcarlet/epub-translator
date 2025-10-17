# epub-translator

CLI tool untuk menerjemahkan buku EPUB dari Bahasa Inggris ke Bahasa Indonesia. Tool ini
mendukung daftar kosakata yang tidak boleh diterjemahkan sehingga nama hewan atau benda unik
bisa tetap dipertahankan apa adanya.

## Fitur

- Menerjemahkan konten EPUB menggunakan model `Helsinki-NLP/opus-mt-en-id`.
- Menyediakan daftar default kata yang tidak diterjemahkan (hewan, benda unik, istilah fantasi).
- Mendukung file glossary (TXT/JSON) untuk menambahkan daftar kata yang tidak boleh diterjemahkan.
- Pengaturan batch size dan panjang maksimum token untuk mengontrol proses inferensi.
- Penambahan metadata sederhana pada EPUB hasil terjemahan.

## Instalasi
## Mulai dari Git Clone

Ikuti langkah berikut jika Anda ingin memulai dari repositori Git:

1. Clone repositori ini dan masuk ke dalam direktori proyek:

   ```bash
   git clone https://github.com/<username>/epub-translator.git
   cd epub-translator
   ```

2. (Opsional) Buat dan aktifkan virtual environment agar dependensi terisolasi:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate    # Windows PowerShell
   ```

3. Instal dependensi menggunakan `pip`:

   ```bash
   pip install .
   ```

   > **Catatan:** dependensi `torch` cukup besar. Anda bisa memilih versi yang sesuai dengan
   > perangkat keras dengan mengikuti panduan [PyTorch](https://pytorch.org/).




## Penggunaan

```bash
epub-translator input.epub --output output.id.epub \
  --glossary glossary.txt \
  --preserve "Eldoria" --preserve "Fenrir"
```

### Opsi CLI Penting

- `input`: path menuju file EPUB sumber (wajib).
- `-o/--output`: path untuk EPUB hasil terjemahan. Defaultnya akan membuat berkas baru dengan
  menambahkan suffix `.id.epub`.
- `--glossary`: path ke file glossary tambahan. Bisa menggunakan teks biasa (satu kata per baris)
  atau JSON array.
- `--preserve`: menambahkan kata yang harus dipertahankan langsung dari argumen CLI.
- `--no-default-glossary`: menonaktifkan daftar kata bawaan.
- `--model`: ganti model HuggingFace yang ingin digunakan.
- `--batch-size`: jumlah node teks yang diterjemahkan sekaligus.
- `--max-length`: panjang maksimum token pada model terjemahan.
- `--log-level`: tingkat logging.

## Glossary

Anda bisa membuat file glossary dengan format berikut:

```text
# komentar menggunakan tanda pagar
Fenrir
Mjolnir
```

Atau gunakan JSON:

```json
["Fenrir", "Mjolnir"]
```

## Pengujian

Jalankan unit test dasar:

```bash
pytest
```
