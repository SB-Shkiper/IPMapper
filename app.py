import sys
import folium
import stealth_requests as requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, \
    QHBoxLayout, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
import webbrowser


class OSINTMap(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Map")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.map_view = QWebEngineView()
        self.layout.addWidget(self.map_view)

        self.search_layout = QHBoxLayout()
        self.layout.addLayout(self.search_layout)

        self.ip_label = QLabel("Enter IP address:")
        self.search_layout.addWidget(self.ip_label)

        self.ip_input = QLineEdit()
        self.search_layout.addWidget(self.ip_input)

        self.get_ip_button = QPushButton("Get IP Info")
        self.get_ip_button.clicked.connect(self.get_ip_info)
        self.search_layout.addWidget(self.get_ip_button)

        self.coord_label = QLabel("Enter coordinates (latitude, longitude):")
        self.search_layout.addWidget(self.coord_label)

        self.coord_input = QLineEdit()
        self.search_layout.addWidget(self.coord_input)

        self.open_map_button = QPushButton("Open Google Maps")
        self.open_map_button.clicked.connect(self.open_google_maps)
        self.search_layout.addWidget(self.open_map_button)

        self.save_button = QPushButton("Save map to HTML")
        self.save_button.clicked.connect(self.save_map)
        self.search_layout.addWidget(self.save_button)

        self.map_file = 'map.html'
        self.map_center = [0, 0]
        self.create_map()

    def create_map(self):
        self.map = folium.Map(location=self.map_center, zoom_start=2)
        self.update_map_view()

    def update_map_view(self):
        self.map_view.setHtml(self.map._repr_html_())

    def get_ip_info(self):
        ip_address = self.ip_input.text().strip()
        if ip_address:
            info = self.fetch_ip_info(ip_address)
            if "error" not in info:
                lat = info.get('latitude')
                lon = info.get('longitude')
                if lat and lon:
                    self.add_point_to_map(lat, lon, info)

    def fetch_ip_info(self, ip_address):
        url = f"https://ipapi.co/{ip_address}/json/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                return {"error": data['reason']}

            return data
        except requests.RequestException:
            return {}

    def add_point_to_map(self, lat, lon, info):
        tooltip_text = f"IP: {info.get('ip')}<br>" \
                       f"City: {info.get('city')}<br>" \
                       f"Region: {info.get('region')}<br>" \
                       f"Country: {info.get('country')}<br>" \
                       f"Latitude: {lat}<br>" \
                       f"Longitude: {lon}"

        folium.Marker([lat, lon], tooltip=tooltip_text).add_to(self.map)
        self.map_center = [lat, lon]
        self.map.location = self.map_center
        self.update_map_view()
        self.ip_input.clear()

    def open_google_maps(self):
        coords = self.coord_input.text().strip().split(',')
        if len(coords) == 2:
            try:
                lat = float(coords[0].strip())
                lon = float(coords[1].strip())
                url = f"https://www.google.com/maps/@{lat},{lon},15z"
                webbrowser.open(url)
            except ValueError:
                pass

    def save_map(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Map", "", "HTML Files (*.html);;All Files (*)",
                                                   options=options)
        if file_name:
            self.map.save(file_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OSINTMap()
    window.show()
    sys.exit(app.exec_())
