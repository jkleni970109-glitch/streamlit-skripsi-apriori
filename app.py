import streamlit as st
import pandas as pd
from style import load_css
import re #mencari atau mengganti pola(angka desimal data brg)
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules


# Konfigurasi halaman
st.set_page_config(
    page_title="Sistem Rekomendasi Produk Apotek",
    page_icon="💊",
    layout="wide"
)
load_css()

# Judul
st.title("💊 Sistem Rekomendasi Produk Apotek")

st.write("""
Selamat datang pada aplikasi pencarian pola pembelian pelanggan.
""")

# Upload file Excel
uploaded_file = st.file_uploader(
    "Upload File Excel",
    type=["xlsx", "xls"]
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    obat_keras = pd.read_excel("data/Data_Produk_Obat_Keras.xlsx") #membaca daftar obat keras
    daftar_obat_keras = set(
        obat_keras["Barang"]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    st.success("File berhasil diupload")
    st.subheader("Informasi Dataset")
    st.write("Nama file:", uploaded_file.name)
    st.write("Jumlah baris:", len(df))
    st.write("Jumlah kolom:", len(df.columns))
    st.subheader("Preview Data")
    st.dataframe(df.head(30))
    st.subheader("Seleksi Kolom")
    kolom_transaksi = st.selectbox(
        "Pilih Kolom Nomor Transaksi",
        df.columns
    )
    kolom_barang = st.selectbox(
        "Pilih Kolom Barang",
        df.columns
    )

    #Membuat parameter
    st.subheader("Parameter Apriori")

    support = st.number_input(
        "Minimum Support",
        min_value=0.001,
        max_value=1.000,
        value=0.001,
        step=0.001,
        format="%.3f",
        help="Nilai minimum support untuk mencari frequent itemsets."
    )
    confidence = st.number_input(
        "Minimum Confidence",
        min_value=0.10,
        max_value=1.00,
        value=0.30,
        step=0.05,
        format="%.2f",
        help="Nilai minimum confidence untuk membentuk association rules."
    )
    st.write("Support yang digunakan :", support)
    st.write("Confidence yang digunakan :", confidence)

    #Proses Data
    if st.button("Analisis Data"):
        data = df[[kolom_transaksi, kolom_barang]].copy()
        st.success("Kolom berhasil dipilih")
        jumlah_awal = len(data)
        data = data.dropna()

        data[kolom_barang] = data[kolom_barang].astype(str).str.strip()
        data[kolom_transaksi] = data[kolom_transaksi].astype(str).str.strip()
        data[kolom_barang] = data[kolom_barang].apply( 
            lambda x: re.sub(r'(?<=\d),(?=\d)', '.', x) #normalisasi angka desimal
        )
        jumlah_akhir = len(data)
        
        st.subheader("Hasil Preprocessing")
        st.write("Jumlah data sebelum preprocessing :", jumlah_awal)
        st.write("Jumlah data sesudah preprocessing :", jumlah_akhir)
        st.write("Data yang dihapus :", jumlah_awal - jumlah_akhir)

        st.subheader("Data Setelah Preprocessing")
        st.dataframe(data.head(20))
    
        #Memisahkan barang yang hanya dipisahkan koma
        st.subheader("Data Transaksi Per Produk")
        split_data = data.copy()
        split_data[kolom_barang] = split_data[kolom_barang].str.split(",")
        split_data = split_data.explode(kolom_barang) 

        #menghapus spasi berlebih setelah split kolom dilakukan
        split_data[kolom_barang] = split_data[kolom_barang].str.strip().str.replace(r"\s+", " ", regex=True)
        split_data = split_data[split_data[kolom_barang] != ""]
        st.write("Jumlah baris :", len(split_data))
        split_data = split_data.reset_index(drop=True)
        st.dataframe(split_data.head(10))

       #filter layanan cek
       
        layanan = [
            "CEK ASAM URAT",
            "CEK GULA DARAH",
            "CEK KOLESTEROL"
        ]
        # Ambil data layanan cek
        data_layanan = split_data[
            split_data[kolom_barang].isin(layanan)
        ].copy()
        st.subheader("Data Layanan Kesehatan")
        st.write("Jumlah data layanan :", len(data_layanan))
        st.dataframe(data_layanan.head(10))

        # Menghapus layanan cek dari data transaksi
        split_data = split_data[
            ~split_data[kolom_barang].isin(layanan)
        ].copy()

        st.subheader("Data Transaksi Tanpa Layanan Kesehatan ")
        st.write("Jumlah baris :", len(split_data))
        st.dataframe(split_data.head(10))

        split_data[kolom_barang] = (
            split_data[kolom_barang]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        #1. Produk yang cocok dengan daftar obat keras
        cocok = split_data[
            split_data[kolom_barang].isin(daftar_obat_keras)
        ]

        st.subheader("Produk Teridentifikasi sebagai Obat Keras")
        st.write("Jumlah item yang cocok :", len(cocok))
        st.dataframe(cocok.head(20))

        # 2. Hapus obat keras
        split_data = split_data[
            ~split_data[kolom_barang].isin(daftar_obat_keras)
        ]

        frekuensi = split_data[kolom_barang].value_counts()
        
        st.subheader("Frekuensi Setiap Produk")
        st.dataframe(frekuensi.reset_index().rename(columns={
            "index": "Barang",
            "count": "Frekuensi"
        }))

        #Membuat matriks biner
        st.subheader("Tampilan Data")
        basket = pd.crosstab(
            split_data[kolom_transaksi],
            split_data[kolom_barang]
        )
        basket = (basket > 0).astype(int)
        st.write("Jumlah transaksi :", basket.shape[0])
        st.write("Jumlah produk :", basket.shape[1])
        st.dataframe(basket.head(50))

        #Frequent itemsets
        st.subheader("Produk dengan Frekuensi Tinggi")
         
        frequent_itemsets = apriori(
            basket,
            min_support=support,
            use_colnames=True,
            max_len=2
        )

        frequent_itemsets = frequent_itemsets.sort_values(
             by="support",
            ascending=False
        )

        frequent_itemsets["jumlah_item"] = frequent_itemsets["itemsets"].apply(len)

        frequent_1 = frequent_itemsets[
            frequent_itemsets["jumlah_item"] == 1
        ].copy()

        frequent_2 = frequent_itemsets[
            frequent_itemsets["jumlah_item"] == 2
        ].copy()

        frequent_2["Item 1"] = frequent_2["itemsets"].apply(lambda x: sorted(list(x))[0])
        frequent_2["Item 2"] = frequent_2["itemsets"].apply(lambda x: sorted(list(x))[1])

        st.subheader("Daftar Produk Terlaris")
        st.write("Jumlah :", len(frequent_1))
        st.dataframe(frequent_1[["support","itemsets"]])

        st.subheader("Kombinasi Produk")
        st.write("Jumlah :", len(frequent_2))
        st.dataframe(frequent_2[["support","Item 1","Item 2"]])


        #Association rules
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=confidence
        )
        #memilih kolom yang akan digunakan
        rules = rules[
            [ 
                "antecedents",
                "consequents",
                "support",
                "confidence",
                "lift"
            ]
        ]
        
        #Mengurutkan berdasarkan lift
        rules = rules.sort_values(
            by="lift",
            ascending=False
        )

        st.write("Minimum Confidence :", confidence)
        st.write("Jumlah Rules :", len(rules))
        st.dataframe(rules.head(50))


        st.subheader("Rekomendasi untuk Tata Letak dan Strategi Bundling dari Hasil Pola Pembelian")

        if rules.empty:
            st.warning("Belum ditemukan aturan asosiasi yang memenuhi nilai minimum confidence.")
        else:
            rekomendasi = []

            for _, row in rules.iterrows():
                item1 = ", ".join(list(row["antecedents"]))
                item2 = ", ".join(list(row["consequents"]))

                rekomendasi.append({
                    "Rekomendasi":
                        f"Letakkan atau Bundling {item1} dengan {item2} karena sering dibeli secara bersamaan.",
                    "Confidence": f"{row['confidence']*100:.2f}%",
                    "Lift": round(row["lift"], 2)
                })

            rekom_df = pd.DataFrame(rekomendasi)

            st.dataframe(
                rekom_df,
                use_container_width=True,
                hide_index=True
            )
        
