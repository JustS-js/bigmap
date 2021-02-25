import sys
from io import BytesIO
import requests

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from distance import lonlat_coords


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('map.ui', self)
        # Настройка элементов меню
        self.radiobutton_group = QButtonGroup()
        self.radiobutton_group.addButton(self.rb_1)
        self.radiobutton_group.addButton(self.rb_2)
        self.radiobutton_group.addButton(self.rb_3)
        self.radiobutton_group.buttonClicked.connect(self._on_radio_button_clicked)

        self.btn_find.clicked.connect(self._on_btn_find_clicked)
        self.btn_reset.clicked.connect(self._on_btn_reset_clicked)
        self.checkBox.stateChanged.connect(self._on_checkbox_clicked)

        # Логические переменные
        self.toponym = None
        self.geocoder_api = 'https://geocode-maps.yandex.ru/1.x/'
        self.geocoder_apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
        self.geocoder_params = {
            'apikey': self.geocoder_apikey,
            'format': 'json'
        }

        self.static_api = 'https://static-maps.yandex.ru/1.x/'
        self.static_params = {
            'z': '13',
            'l': 'map',
            'll': '37.620070,55.753630',
            'size': '480,450',
        }

        self.spn = {
            0: 90,
            1: 89.6,
            2: 44.8,
            3: 22.4,
            4: 11.2,
            5: 5.6,
            6: 2.8,
            7: 1.4,
            8: 0.7,
            9: 0.4,
            10: 0.2,
            11: 0.1,
            12: 0.05,
            13: 0.03,
            14: 0.02,
            15: 0.01,
            16: 0.005,
            17: 0.002
        }

        self.metr = 0.000006
        self.wsim = self.metr * 450  # window size in metres

        # Настройки окна
        self.setFixedSize(720, 450)
        self.updateMap()

    def _on_checkbox_clicked(self):
        try:
            if self.toponym is not None:
                text = self.toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                try:
                    if self.checkBox.isChecked():
                        postcode = self.toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                        text = postcode + ' ' + text
                except Exception:
                    pass
                self.addressText.setPlainText(text)
        except Exception as e:
            print(e)

    def _on_btn_reset_clicked(self):
        try:
            self.toponym = None
            self.static_params.pop('pt', None)
            self.addressText.setPlainText('')
            self.updateMap()
        except Exception as e:
            print(e)

    def find_place(self):
        response = requests.get(self.geocoder_api, params=self.geocoder_params, timeout=0.4)
        json_resp = response.json()

        self.toponym = json_resp["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

        text = self.toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        try:
            if self.checkBox.isChecked():
                postcode = self.toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                text = postcode + ' ' + text
        except Exception:
            pass
        self.addressText.setPlainText(text)
        return list(map(float, self.toponym["Point"]["pos"].split()))

    def _on_btn_find_clicked(self):
        try:
            if self.lineToFind.text():
                self.geocoder_params['geocode'] = self.lineToFind.text()
                lon, lat = self.find_place()
                self.static_params['pt'] = f'{lon},{lat},pm2vvm'
                self.static_params['ll'] = f'{lon},{lat}'
                self.updateMap()
        except Exception as e:
            print(e)

    def _on_radio_button_clicked(self, button):
        if button.text() == 'Схема':
            self.static_params['l'] = 'map'
        elif button.text() == 'Спутник':
            self.static_params['l'] = 'sat'
        elif button.text() == 'Гибрид':
            self.static_params['l'] = 'sat,skl'
        self.updateMap()

    def _on_right_click(self, event):
        pass

    def _on_left_click(self, event):
        try:
            z = int(self.static_params['z'])
            x, y = list(map(float, self.static_params['ll'].split(',')))
            m_x, m_y = event.pos().x(), event.pos().y()
            if not 0 < m_x < 451:
                return
            delta_x = (x - self.spn[z] / 2)
            lon = ((x - delta_x) * m_x / 225) + delta_x
            print(lon, x)
            lat = y + (225 - m_y) * self.spn[z] * 0.0045 / 2
            self.geocoder_params['geocode'] = f'{lon},{lat}'
            self.find_place()
            self.static_params['pt'] = f'{lon},{lat},pm2vvm'
            self.updateMap()
        except Exception as e:
            print(e)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._on_left_click(event)
        elif event.button() == Qt.RightButton:
            self._on_right_click(event)

    def keyPressEvent(self, event):
        try:
            z = int(self.static_params['z'])
            x, y = list(map(float, self.static_params['ll'].split(',')))
            if event.key() == Qt.Key_PageUp:
                z += 1 if z < 17 else 0
                self.static_params['z'] = str(z)
                self.updateMap()
            elif event.key() == Qt.Key_PageDown:
                z += -1 if z > 0 else 0
                self.static_params['z'] = str(z)
                self.updateMap()
            elif event.key() == Qt.Key_Up:
                y += self.wsim * 2**(17 - z) if y + self.wsim * 2**(17 - z) < 90 else 0
                self.static_params['ll'] = f'{x},{y}'
                self.updateMap()
            elif event.key() == Qt.Key_Down:
                y -= self.wsim * 2**(17 - z) if y - self.wsim * 2**(17 - z) > -90 else 0
                self.static_params['ll'] = f'{x},{y}'
                self.updateMap()
            elif event.key() == Qt.Key_Right:
                x += self.wsim * 2**(17 - z) if x + self.wsim * 2**(17 - z) < 180 else 0
                self.static_params['ll'] = f'{x},{y}'
                self.updateMap()
            elif event.key() == Qt.Key_Left:
                x -= self.wsim * 2**(17 - z) if x - self.wsim * 2**(17 - z) > 0 else 0
                self.static_params['ll'] = f'{x},{y}'
                self.updateMap()
        except Exception as e:
            print(e)

    def updateMap(self):
        response = requests.get(self.static_api, params=self.static_params, timeout=0.4)

        pixmap = QPixmap()
        f = BytesIO(response.content)
        f.seek(0)
        pixmap.loadFromData(f.read())
        self.map.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
