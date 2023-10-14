import streamlit as st
from typing import List, Dict, Union
from src.helper import (
    read_image, grid_apply, 
    segment_green_area, area_plant_calculation
    )

def expert_system(result: Dict[str, Union[str, List[str]]]):
    image_ori = read_image()
    grid_image = grid_apply(image = image_ori)
    segmented_area, area_square = segment_green_area(image = image_ori, grid_image = grid_image)
    stable_grid_area, length_grid_area = area_plant_calculation(image = image_ori, grid_image = grid_image)
    return segmented_area, area_square, stable_grid_area, length_grid_area

def data_mining(total_area_square: int, total_grid: int, size_per_grid: int):
    pass

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
        st.success("Total Area Square: {:,} Pixel Value".format(area_square))
        st.success(f"Total Planting Area: {length_grid_area}, Length per Planting: {stable_grid_area} Pixel Value")
        st.image(segmented_area)
    else:
        st.warning("Harap isi form diatas dan Tekan 'Kirim'...")

if __name__ == "__main__":
    interface()