import os
import tempfile

import cv2


class imageManipulator:
    def __init__(self):
        model = "https://github.com/fannymonori/TF-LapSRN/raw/master/export/LapSRN_x4.pb"
        sys_temp = tempfile.gettempdir()
        model_path = os.path.join(sys_temp, "LapSRN_x4.pb")
        if not os.path.exists(model_path):
            print("Downloading model")
            import urllib.request
            urllib.request.urlretrieve(model, model_path)

        if not os.path.exists(model_path):
            print("Couldn't download the model")
            return

        self.superres = cv2.dnn_superres.DnnSuperResImpl_create()
        self.superres.readModel(model_path)
        self.superres.setModel("lapsrn", 4)

        self.superres.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.superres.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    def upscale_gray_4x(self, gray_image):
        enlarged = self.superres.upsample(cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR))
        return cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)