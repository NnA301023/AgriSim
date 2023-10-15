import streamlit as st
from typing import List, Dict, Union
from src.helper import (
    read_image, grid_apply, 
    segment_green_area, area_plant_calculation, 
    load_metadata_plant
    )

def expert_system(result: Dict[str, Union[str, List[str]]], grid_size: int = 10, scale: int = 50):
    image_ori = read_image()
    grid_image = grid_apply(image = image_ori, grid_size = grid_size)
    segmented_area, area_square, _ = segment_green_area(image = image_ori, grid_image = grid_image)
    stable_grid_area, length_grid_area = area_plant_calculation(image = grid_image)
    
    area_square_meter = area_square / scale
    grid_size_meter = grid_size / scale
    stable_grid_area_meter = stable_grid_area * grid_size_meter
    
    return segmented_area, area_square_meter, stable_grid_area_meter, length_grid_area

def data_mining(total_grid: int, size_per_grid: int, plant_selected: List[str]):
    result = None
    metadata = load_metadata_plant()
    area_plant = total_grid * size_per_grid # m²
    metadata_filter = metadata[metadata['Tanaman'].isin(plant_selected)].reset_index(drop = True)
    print(metadata_filter)
    result = metadata_filter[['Tanaman']]
    result['Masa Panen (hari)'] = metadata_filter['Masa Panen (hari)']
    result['Biaya Bibit (Rp)'] = area_plant * metadata_filter["Harga Bibit (Rp/m2)"]
    result['Hasil Panen (Rp)'] = area_plant * metadata_filter["Hasil Panen (kg/m2)"] * metadata_filter["Harga Jual (Rp/kg)"]
    result['Keuntungan'] = result.apply(lambda x: x['Hasil Panen (Rp)'] - x['Biaya Bibit (Rp)'], axis = 1)
    result = result.sort_values(by = "Keuntungan").reset_index(drop = True)
    return result

def interface():

    st.header("Agriculture Simulation v.0.1")

    col1, col2 = st.columns(2)
    with col1:
        nama_petani = st.text_input("Nama Petani", placeholder = "Mas Alif")
    with col2:
        lokasi = st.text_input("Lokasi", placeholder = "Karawang")

    col3, col4 = st.columns(2)
    with col3:
        long = st.text_input("Longitude", placeholder = "-6.3253499")
    with col4:
        lat = st.text_input("Latitude", placeholder = "107.3027687,534")

    list_komoditas = ["Padi", "Jagung", "Kedelai", "Kacang Tanah", "Ubi Kayu", "Ubi Jalar"]
    komoditas_terpilih = st.multiselect("Pilih Jenis Tanaman", options = list_komoditas)

    if st.button("Kirim") and lokasi != "" and len(komoditas_terpilih) != 0:
        result = {
            "nama_petani" : nama_petani, 
            "lokasi" : lokasi, 
            "long" : long,
            "lat" : lat, 
            "komoditas_terpilih" : komoditas_terpilih
        }
        with st.spinner(text = "Sistem Expert Berjalan..."):
            segmented_area, area_square, stable_grid_area, length_grid_area = expert_system(result = result)
            area_square_ha = area_square / 10000

        # Data Mining Section
        table_summaries = data_mining(stable_grid_area, length_grid_area, komoditas_terpilih)

        # Computer Vision Section
        st.success("Total Area Square: {:,} hektar".format(area_square_ha))
        st.success("Total Planting Area: {:,} with Length per Planting: {} m\u00b2".format(length_grid_area, stable_grid_area))
        komoditas_tidak_tersedia = list(set(komoditas_terpilih) - set(table_summaries['Tanaman'].tolist()))
        if len(komoditas_tidak_tersedia) != 0:
            st.error(f"Untuk komoditas: {', '.join(komoditas_tidak_tersedia)} tidak disarankan ditanam di daerah {lokasi}")
        st.table(table_summaries)
        st.image(segmented_area)
    else:
        st.warning("Harap isi form diatas dan Tekan 'Kirim'...")

if __name__ == "__main__":
    interface()