# 🌳 Deforestation Monitoring Tool

![Project Banner](https://via.placeholder.com/1200x300.png?text=Deforestation+Monitoring+Tool)

<p align="center">
  <img src="https://img.shields.io/badge/Status-Completed-brightgreen" />
  <img src="https://img.shields.io/badge/Web-App-blue" />
  <img src="https://img.shields.io/badge/QGIS-Analysis-green" />
  <img src="https://img.shields.io/badge/NDVI-Supported-lightgrey" />
</p>

> **A full-stack solution for detecting and visualizing deforestation using Google Earth Engine and QGIS with Sentinel-2 and Landsat-8 imagery.**

---

## 📌 Overview
This project consists of two integrated modules:

- 🌐 **Web App**: A Flask + Google Earth Engine-powered platform to generate NDVI maps based on user input (coordinates, radius, year).
- 🛰️ **QGIS Analysis**: A QGIS project that provides time-series NDVI comparison for Mumbai, Navi Mumbai, and Thane between 2016 and 2024.

---

## 🗂 Repository Structure
```bash
deforestation-monitoring-tool/
├── web-app/               # Flask Web Application
│   ├── backend/           # Python + GEE logic
│   ├── frontend/         # HTML templates
│
├── qgis-analysis/         # NDVI Analysis using QGIS
│   ├── sentinel/          # Sentinel-2 imagery & project
│   ├── landsat/           # Landsat-8 imagery & project
│   └── stats_and_charts/  # CSVs & Graphs
│
├── report/                # Final Report and Presentation
│   ├── Mini_Project_Report.pdf
│   └── Presentation_Slides.pptx
│
├── LICENSE
└── README.md
```

---

## 🚀 Technologies Used
| Module         | Technology/Tool                |
|----------------|---------------------------------|
| Web App        | Python, Flask, Folium, GEE API |
| GIS Analysis   | QGIS, NDVI, Raster Tools        |
| Data Sources   | Sentinel-2, Landsat-8           |
| Output Format  | HTML, TIFF, PNG, CSV            |

---

## ⚙️ Installation
### 🔧 Web App
```bash
git clone https://github.com/<username>/deforestation-monitoring-tool.git
cd deforestation-monitoring-tool/web-app/backend
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate for Windows
pip install -r requirements.txt
earthengine authenticate
flask run
```
Visit `http://127.0.0.1:5000` in your browser.

### 🛰 QGIS Analysis
1. Open `.qgz` files from the `qgis-analysis/` folder in QGIS Desktop.
2. Load 2016 and 2024 TIFF files.
3. Use raster calculator for NDVI difference.
4. Review output layers, export graphs and stats.

---

## 🎯 Features
- 🗺 Generate dynamic NDVI maps based on location, radius, and year.
- 📊 Statistical summaries of vegetation health and loss.
- 📍 Region-wise QGIS projects for Mumbai Metropolitan areas.
- 📈 Visual charts and CSV outputs for change detection.

---

## 📸 Screenshots
<p float="left">
  <img src="https://via.placeholder.com/400x250.png?text=Web+Map" width="45%" />
  <img src="https://via.placeholder.com/400x250.png?text=QGIS+NDVI+Comparison" width="45%" />
</p>

---

## 📁 Sample Output
- HTML Map (Folium)
- NDVI Raster Files
- Comparative Charts (2016 vs 2024)
- Ground Truth Reference

---

## 🤝 Contributing
We welcome contributions!
```bash
git checkout -b feature/your-feature
# Make changes
git commit -m "Add your feature"
git push origin feature/your-feature
```
Open a Pull Request with your description.

---

## 📄 License
This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for more.

---

## 👤 Authors
- **Anish Ganesh Bandal**  
  BTech IT, Vidyalankar Institute of Technology

---

## 📬 Contact
📧 anishbandal@email.com  
🔗 [GitHub Profile](https://github.com/AnishBandal)

