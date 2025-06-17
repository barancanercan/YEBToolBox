import streamlit as st
import pandas as pd
from .trend_analyzer import TrendAnalyzer
import io
import plotly.express as px

def run_trends_app():
    # st.set_page_config(
    #     page_title="Google Trends Analizi Uygulaması",
    #     page_icon="📈",
    #     layout="wide", # Daha geniş bir görünüm için layout 'wide' olarak ayarlandı
    #     initial_sidebar_state="expanded"
    # )

    st.title("📈 Google Trends Veri Analizi")
    st.markdown("Bu uygulama, yüklediğiniz Google Trends verilerini analiz ederek anahtar kelimelerin günlük ve genel arama eğilimlerini, zirve noktalarını ve ortalama arama hacimlerini interaktif grafiklerle görselleştirir.")

    st.header("Veri Yükleme")
    uploaded_file = st.file_uploader("Analiz etmek istediğiniz Google Trends verilerini içeren bir CSV dosyası yükleyin.", type=["csv"])

    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, skiprows=2)
            st.success("CSV dosyası başarıyla yüklendi!")
            with st.expander("Yüklenen Verinin İlk 5 Satırını Görüntüle"):
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"Dosya yüklenirken bir hata oluştu: {e}")
            st.info("Lütfen dosyanın doğru CSV formatında olduğundan ve 'Zaman' sütununun bulunduğundan emin olun.")
    elif st.button("Örnek Veri 'ornekdata.csv' Kullan"):
        try:
            df = pd.read_csv("ornekdata.csv", skiprows=2)
            st.success("Örnek veri 'ornekdata.csv' başarıyla yüklendi!")
            with st.expander("Örnek Verinin İlk 5 Satırını Görüntüle"):
                st.dataframe(df.head())
        except FileNotFoundError:
            st.error("`ornekdata.csv` dosyası bulunamadı. Lütfen projenin kök dizininde olduğundan emin olun.")
        except Exception as e:
            st.error(f"Örnek veri yüklenirken bir hata oluştu: {e}")

    if df is not None and not df.empty:
        # 'Zaman' sütununu datetime objesine dönüştür, analiz ve filtreleme için gerekli
        df['Zaman'] = pd.to_datetime(df['Zaman'], format='%Y-%m-%dT%H')

        st.markdown("---")
        st.header("2. Zaman Aralığı Seçimi ve Analiz")

        # Zaman aralığı seçimi için min/max değerleri
        min_datetime_data = df['Zaman'].min()
        max_datetime_data = df['Zaman'].max()

        col1, col2 = st.columns(2)

        with col1:
            # Başlangıç tarihi varsayılan olarak verinin en eski tarihi
            start_date_input = st.date_input("Başlangıç Tarihi", min_datetime_data.date())
            # Başlangıç saati varsayılan olarak verinin en eski saati
            start_time_input = st.time_input("Başlangıç Saati", min_datetime_data.time())

        with col2:
            # Bitiş tarihi varsayılan olarak verinin en yeni tarihi
            end_date_input = st.date_input("Bitiş Tarihi", max_datetime_data.date())
            # Bitiş saati varsayılan olarak verinin en yeni saati
            end_time_input = st.time_input("Bitiş Saati", max_datetime_data.time())

        # Tarih ve saat girdilerini birleştir
        from datetime import datetime, time
        start_datetime_filter = datetime.combine(start_date_input, start_time_input)
        end_datetime_filter = datetime.combine(end_date_input, end_time_input)

        # Seçilen zaman aralığına göre DataFrame'i filtrele
        filtered_df = df[(df['Zaman'] >= start_datetime_filter) & (df['Zaman'] <= end_datetime_filter)]

        # 'Tarih' ve 'Saat' sütunlarını burada oluştur
        filtered_df['Tarih'] = filtered_df['Zaman'].dt.date
        filtered_df['Saat'] = filtered_df['Zaman'].dt.hour

        if filtered_df.empty:
            st.warning("Seçilen tarih aralığında veri bulunamadı. Lütfen farklı bir aralık seçin.")
        else:
            search_columns = [col for col in filtered_df.columns if col not in ['Zaman', 'Tarih', 'Saat']]
            if search_columns:
                filtered_df['Toplam Aranma'] = filtered_df[search_columns].sum(axis=1)
            
            analyzer = TrendAnalyzer(filtered_df)

            st.subheader("Analiz Sonuçları")
            
            st.write("Aşağıda seçilen zaman aralığına göre anahtar kelimelerin ortalama aranma sayıları ve günlük en yüksek zirve noktaları bulunmaktadır.")

            st.markdown("**Ortalama Aranma Sayıları**")
            avg_counts = analyzer.get_average_search_counts()
            if avg_counts:
                avg_df = pd.DataFrame([avg_counts]).T.reset_index()
                avg_df.columns = ['Parametre', 'Ortalama Değer']
                st.dataframe(avg_df)
            else:
                st.info("Ortalama aranma sayıları hesaplanamadı.")

            st.markdown("**Günlük En Yüksek Zirve Noktaları**")
            overall_daily_peaks_df = analyzer.get_overall_daily_peaks()

            if not overall_daily_peaks_df.empty:
                st.dataframe(overall_daily_peaks_df)
            else:
                st.info("Günlük genel zirve saatleri bulunamadı. Yeterli veri veya arama hacmi olmayabilir.")

            st.markdown("---")
            st.header("Görsel Analizler")

            # Toplam Aranma Hacmi Grafiği
            search_columns = [col for col in filtered_df.columns if col not in ['Zaman', 'Tarih', 'Saat']]
            if search_columns:
                fig_total = px.line(filtered_df, x='Zaman', y='Toplam Aranma',
                                    title='Toplam Aranma Hacmi (Tüm Liderler)',
                                    labels={'Zaman': 'Tarih ve Saat', 'Toplam Aranma': 'Toplam Aranma Hacmi'},
                                    hover_data={'Zaman': '|%Y-%m-%d %H:%M', 'Toplam Aranma': True})
                
                # Genel ortalama çizgisini ekle
                general_average = analyzer.get_average_search_counts().get('Genel Ortalama', 0)
                fig_total.add_hline(y=general_average, line_dash="dash", line_color="red", annotation_text=f"Ortalama: {general_average:.2f}", 
                                    annotation_position="bottom right", annotation_font_color="red")

                # Mutlak zirve noktasını (en tepe nokta) ekle
                if not filtered_df.empty:
                    max_total_value = filtered_df['Toplam Aranma'].max()
                    max_total_time = filtered_df[filtered_df['Toplam Aranma'] == max_total_value]['Zaman'].iloc[0]
                    
                    fig_total.add_annotation(
                        x=max_total_time,
                        y=max_total_value,
                        text=f"Zirve ({int(max_total_value)})",
                        showarrow=True,
                        arrowhead=1,
                        ax=20,
                        ay=-40,
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="purple",
                        borderwidth=1,
                        borderpad=4,
                        font=dict(color="purple", size=10)
                    )

                fig_total.update_layout(hovermode="x unified", xaxis_rangeslider_visible=True) # Zaman kaydırıcısını etkinleştir
                st.plotly_chart(fig_total, use_container_width=True)
            else:
                st.info("Toplam aranma hacmi grafiği oluşturulamadı. Lider arama sütunları bulunamadı.")

            # Lider Bazında Aranma Hacmi ve Zirve Noktaları Grafikleri
            st.subheader("Liderlere Göre Aranma Hacmi ve Zirve Noktaları")
            for leader_col in search_columns:
                fig_leader = px.line(filtered_df, x='Zaman', y=leader_col,
                                     title=f'{leader_col} Aranma Hacmi',
                                     labels={'Zaman': 'Tarih ve Saat', leader_col: 'Aranma Hacmi'},
                                     hover_data={'Zaman': '|%Y-%m-%d %H:%M', leader_col: True})

                # Liderin ortalama çizgisini ekle
                leader_average = analyzer.get_average_search_counts().get(f'{leader_col} Ortalaması', 0)
                fig_leader.add_hline(y=leader_average, line_dash="dash", line_color="blue", annotation_text=f"Ort: {leader_average:.2f}", 
                                     annotation_position="bottom right", annotation_font_color="blue")

                # Mutlak zirve noktasını (en tepe nokta) ekle
                if not filtered_df.empty:
                    max_leader_value = filtered_df[leader_col].max()
                    max_leader_time = filtered_df[filtered_df[leader_col] == max_leader_value]['Zaman'].iloc[0]
                    
                    fig_leader.add_annotation(
                        x=max_leader_time,
                        y=max_leader_value,
                        text=f"Zirve ({int(max_leader_value)})",
                        showarrow=True,
                        arrowhead=1,
                        ax=20,
                        ay=-40,
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="red",
                        borderwidth=1,
                        borderpad=4,
                        font=dict(color="red", size=10)
                    )
                fig_leader.update_layout(hovermode="x unified", xaxis_rangeslider_visible=True) # Zaman kaydırıcısını etkinleştir
                st.plotly_chart(fig_leader, use_container_width=True) 