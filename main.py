from PyQt5.QtGui import *
from PyQt5.QtCore import *
from designGui import *
import cv2
import pyrealsense2 as rs
import numpy as np

# We want the points object to be persistent so we can display the
# last cloud when a frame drops
points = rs.points()
# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Create a pipeline
pipeline = rs.pipeline()
# Create a config and configure the pipeline to stream
config = rs.config()
config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)
# Start streaming
profile = pipeline.start(config)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Usamos la funcion QPoint() para guardar la posicion del mouse
        self.click_position = QPoint()
        # Se configura la ventana
        self.pushButton_2.hide()
        self.pushButton_4.clicked.connect(lambda: self.showMinimized())
        self.pushButton.clicked.connect(self.control_btn_cerrar)
        self.pushButton_2.clicked.connect(self.control_btn_normal)
        self.pushButton_3.clicked.connect(self.control_btn_maximizar)

        # Se elimina la barra de titulo por default
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Size grip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        # Movimiento de la ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        self.start_video()

    def control_btn_cerrar(self):
        self.close()
        #cap.release()
        self.label.clear()
        pipeline.stop()

    def control_btn_normal(self):
        self.showNormal()
        self.pushButton_2.hide()
        self.pushButton_3.show()

    def control_btn_maximizar(self):
        self.showMaximized()
        self.pushButton_3.hide()
        self.pushButton_2.show()

    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    def mousePressEvent(self, event):
        self.click_posicion = event.globalPos()

    def mover_ventana(self, event):
        if self.isMaximized() == False:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.click_posicion)
                self.click_posicion = event.globalPos()
                event.accept()
        if event.globalPos().y() <= 5 or event.globalPos().x() <= 5:
            self.showMaximized()
            self.pushButton_3.hide()
            self.pushButton_2.show()
        else:
            self.showNormal()
            self.pushButton_2.hide()
            self.pushButton_3.show()

    def start_video(self):
        self.Work = Work()
        self.Work.start()
        self.Work.Imageupd.connect(self.Imageupd_slot)

    def Imageupd_slot(self, Image):
        self.label.setPixmap(QPixmap.fromImage(Image))

class Work(QThread):
    Imageupd = pyqtSignal(QImage)

    def run(self):
        self.hilo_corriendo = True
        #cap = cv2.VideoCapture(0)
        while self.hilo_corriendo:
            # Get frameset of color and depth
            frames = pipeline.wait_for_frames()
            ir1_frame = frames.get_infrared_frame(1)  # Left IR Camera, it allows 1, 2 or no input
            image = np.asanyarray(ir1_frame.get_data())
            im_np = image.copy()
            # Detect the faces
            faces = face_cascade.detectMultiScale(image, 1.1, 4)
            # Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(im_np, (x, y), (x + w, y + h), (255, 0, 0), 2)
            flip = cv2.flip(im_np, 1)
            # frameu = imutils.resize(flip, width=640, height=480)
            # print(str(flip.shape[1]))
            convertir_QT = QImage(flip.data, flip.shape[1], flip.shape[0], QImage.Format_Grayscale8)
            # pic = convertir_QT.scaled(640, 480, Qt.KeepAspectRatio)
            #self.label.setPixmap(QPixmap.fromImage(convertir_QT))
            self.Imageupd.emit(convertir_QT)

    def stop(self):
        self.hilo_corriendo = False
        self.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyApp()
    window.show()
    app.exec_()