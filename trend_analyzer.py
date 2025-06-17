import pandas as pd
from datetime import datetime, timedelta

class TrendAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._preprocess_data()

    def _preprocess_data(self):
        # 'Zaman' sütununu datetime objelerine dönüştür
        # CSV'nin başında fazladan satırlar olduğu için skiprows uygulaması kaldırıldı, artık veri Streamlit tarafında doğru okunuyor.
        self.df['Zaman'] = pd.to_datetime(self.df['Zaman'], format='%Y-%m-%dT%H')
        # Lider sütunlarını sayısal değere dönüştür, hataları NaN yap
        for col in self.df.columns:
            if col != 'Zaman':
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0) # NaN değerleri 0 ile doldur
        
        # Tarih ve Saat sütunlarını burada oluştur, böylece diğer metotlar kullanabilir
        self.df['Tarih'] = self.df['Zaman'].dt.date
        self.df['Saat'] = self.df['Zaman'].dt.hour

    def get_daily_peak_hours(self):
        # Her gün için en yüksek arama yapılan 1 saatlik aralığı bul
        # Önce 'Tarih' sütununu oluştur
        self.df['Tarih'] = self.df['Zaman'].dt.date
        self.df['Saat'] = self.df['Zaman'].dt.hour

        peak_hours_data = []

        # Her tarih ve lider için en yüksek saati bul
        for date in self.df['Tarih'].unique():
            daily_df = self.df[self.df['Tarih'] == date]
            for col in self.df.columns:
                if col not in ['Zaman', 'Tarih', 'Saat']:
                    max_value = daily_df[col].max()
                    if max_value > 0: # Sadece pozitif arama hacmi olanları dikkate al
                        peak_hour_row = daily_df[daily_df[col] == max_value]
                        if not peak_hour_row.empty:
                            # Aynı max değere sahip birden fazla saat varsa ilkini al
                            peak_hour = peak_hour_row['Saat'].iloc[0]
                            peak_hours_data.append({
                                'Tarih': date,
                                'Lider': col,
                                'Peak Saat Aralığı': f"{peak_hour:02d}:00-{peak_hour+1:02d}:00",
                                'Peak Değer': int(max_value)
                            })
        return pd.DataFrame(peak_hours_data)

    def get_average_search_counts(self):
        # Toplam ve lider başına ortalama aranma sayısını göster
        average_data = {}

        # Her lider için ortalama
        for col in self.df.columns:
            if col not in ['Zaman', 'Tarih', 'Saat']:
                average_data[f'{col} Ortalaması'] = self.df[col].mean()

        # Tüm liderlerin toplam ortalaması
        search_columns = [col for col in self.df.columns if col not in ['Zaman', 'Tarih', 'Saat']]
        if search_columns:
            average_data['Genel Ortalama'] = self.df[search_columns].values.flatten().mean()
        else:
            average_data['Genel Ortalama'] = 0

        return average_data

    def get_outliers(self, column_name):
        """IQR metodunu kullanarak aykırı değerleri (zirveleri) tespit eder."""
        Q1 = self.df[column_name].quantile(0.25)
        Q3 = self.df[column_name].quantile(0.75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR

        # Sadece üst aykırı değerleri (zirveleri) alıyoruz
        outliers = self.df[(self.df[column_name] > upper_bound)]
        return outliers

    def get_overall_daily_peaks(self):
        daily_total_peaks = []
        # Ensure 'Toplam Aranma' column exists before proceeding
        if 'Toplam Aranma' not in self.df.columns:
            # This case should ideally not happen if streamlit_trend_app.py pre-calculates it
            # But as a fallback or for direct usage of TrendAnalyzer, calculate it
            search_columns = [col for col in self.df.columns if col not in ['Zaman', 'Tarih', 'Saat']]
            if search_columns:
                self.df['Toplam Aranma'] = self.df[search_columns].sum(axis=1)
            else:
                return pd.DataFrame() # No search columns to calculate total

        for date in self.df['Tarih'].unique():
            daily_df = self.df[self.df['Tarih'] == date]
            if not daily_df.empty:
                max_total_value = daily_df['Toplam Aranma'].max()
                # Find the row(s) with the max value
                peak_rows = daily_df[daily_df['Toplam Aranma'] == max_total_value]
                if not peak_rows.empty:
                    # Take the first one if multiple hours have the same max value
                    peak_time_obj = peak_rows['Zaman'].iloc[0]
                    daily_total_peaks.append({
                        'Tarih': date,
                        'Zirve Zamanı': peak_time_obj.strftime('%H:%M'),
                        'Zirve Değeri': int(max_total_value)
                    })
        return pd.DataFrame(daily_total_peaks) 