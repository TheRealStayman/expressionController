import cv2
import mediapipe as mp
import numpy as np


def heron(h_a, h_b, h_c):
    s = (h_a + h_b + h_c) / 2
    area = (s * (s - h_a) * (s - h_b) * (s - h_c)) ** 0.5
    return area


def distance3d(coord1, coord2):
    x1 = coord1[0]
    x2 = coord2[0]
    y1 = coord1[1]
    y2 = coord2[1]
    z1 = coord1[2]
    z2 = coord2[2]
    a = (x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2
    d = a ** 0.5
    return d


def areatriangle3d(coord1, coord2, coord3):
    adist = distance3d(coord1, coord2)
    bdist = distance3d(coord2, coord3)
    cdist = distance3d(coord3, coord1)
    ares = heron(adist, bdist, cdist)
    return ares


class Face:
    def __init__(self, image, face_landmarks, thresholds):
        self.mesh = FaceMesh(image, face_landmarks)
        self.thresholds = thresholds

        # Detect how big the face is
        face_size_area = areatriangle3d(self.mesh.facemesh_coords[54], self.mesh.facemesh_coords[93],
                                        self.mesh.facemesh_coords[389])

        # The area above each eyebrow as measured by triangles
        # Left side of Face
        l_eyebrow_area = (areatriangle3d(self.mesh.facemesh_coords[9], self.mesh.facemesh_coords[151],
                                         self.mesh.facemesh_coords[337]) +
                          areatriangle3d(self.mesh.facemesh_coords[9], self.mesh.facemesh_coords[336],
                                         self.mesh.facemesh_coords[337]) +
                          areatriangle3d(self.mesh.facemesh_coords[336], self.mesh.facemesh_coords[337],
                                         self.mesh.facemesh_coords[299]) +
                          areatriangle3d(self.mesh.facemesh_coords[336], self.mesh.facemesh_coords[299],
                                         self.mesh.facemesh_coords[296]) +
                          areatriangle3d(self.mesh.facemesh_coords[296], self.mesh.facemesh_coords[299],
                                         self.mesh.facemesh_coords[334]) +
                          areatriangle3d(self.mesh.facemesh_coords[299], self.mesh.facemesh_coords[334],
                                         self.mesh.facemesh_coords[333]) +
                          areatriangle3d(self.mesh.facemesh_coords[333], self.mesh.facemesh_coords[334],
                                         self.mesh.facemesh_coords[293]) +
                          areatriangle3d(self.mesh.facemesh_coords[333], self.mesh.facemesh_coords[298],
                                         self.mesh.facemesh_coords[293]) +
                          areatriangle3d(self.mesh.facemesh_coords[301], self.mesh.facemesh_coords[298],
                                         self.mesh.facemesh_coords[293]) -
                          areatriangle3d(self.mesh.facemesh_coords[8], self.mesh.facemesh_coords[9],
                                         self.mesh.facemesh_coords[285]) -
                          areatriangle3d(self.mesh.facemesh_coords[9], self.mesh.facemesh_coords[336],
                                         self.mesh.facemesh_coords[285]) -
                          areatriangle3d(self.mesh.facemesh_coords[8], self.mesh.facemesh_coords[417],
                                         self.mesh.facemesh_coords[285]))
        # Right Side of Face
        r_eyebrow_area = (areatriangle3d(self.mesh.facemesh_coords[71], self.mesh.facemesh_coords[63],
                                         self.mesh.facemesh_coords[68]) +
                          areatriangle3d(self.mesh.facemesh_coords[104], self.mesh.facemesh_coords[63],
                                         self.mesh.facemesh_coords[68]) +
                          areatriangle3d(self.mesh.facemesh_coords[104], self.mesh.facemesh_coords[63],
                                         self.mesh.facemesh_coords[105]) +
                          areatriangle3d(self.mesh.facemesh_coords[105], self.mesh.facemesh_coords[104],
                                         self.mesh.facemesh_coords[69]) +
                          areatriangle3d(self.mesh.facemesh_coords[105], self.mesh.facemesh_coords[66],
                                         self.mesh.facemesh_coords[69]) +
                          areatriangle3d(self.mesh.facemesh_coords[66], self.mesh.facemesh_coords[69],
                                         self.mesh.facemesh_coords[107]) +
                          areatriangle3d(self.mesh.facemesh_coords[107], self.mesh.facemesh_coords[69],
                                         self.mesh.facemesh_coords[108]) +
                          areatriangle3d(self.mesh.facemesh_coords[107], self.mesh.facemesh_coords[108],
                                         self.mesh.facemesh_coords[9]) +
                          areatriangle3d(self.mesh.facemesh_coords[108], self.mesh.facemesh_coords[9],
                                         self.mesh.facemesh_coords[151]) -
                          areatriangle3d(self.mesh.facemesh_coords[9], self.mesh.facemesh_coords[107],
                                         self.mesh.facemesh_coords[55]) -
                          areatriangle3d(self.mesh.facemesh_coords[9], self.mesh.facemesh_coords[8],
                                         self.mesh.facemesh_coords[55]) -
                          areatriangle3d(self.mesh.facemesh_coords[193], self.mesh.facemesh_coords[8],
                                         self.mesh.facemesh_coords[55]))
        # Total area
        total_eyebrow_area = l_eyebrow_area + r_eyebrow_area

        self.process = FaceProcessor(face_size_area, l_eyebrow_area, r_eyebrow_area, total_eyebrow_area, self.thresholds)

    def draw(self):
        self.mesh.draw()


def get_facemesh_coords(landmark_list, img):
    # Extract FaceMesh landmark coordinates into 468x3 NumPy array.
    alt_h, alt_w = img.shape[:2]  # grab width and height from image
    xyz = [(landmark.x, landmark.y, landmark.z) for landmark in landmark_list.landmark]

    return np.multiply(xyz, [alt_w, alt_h, alt_w]).astype(int)


class FaceMesh:
    def __init__(self, image, face_landmarks):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_face_mesh = mp.solutions.face_mesh

        self.face_list = []
        self.image = image
        self.face_landmarks = face_landmarks

        self.facemesh_coords = get_facemesh_coords(face_landmarks, image)

        self.show_wireframe = True

    def draw(self):
        if self.show_wireframe:
            self.mp_drawing.draw_landmarks(
                image=self.image,
                landmark_list=self.face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_tesselation_style())
            self.mp_drawing.draw_landmarks(
                image=self.image,
                landmark_list=self.face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_contours_style())
        # To draw irises
        # self.mp_drawing.draw_landmarks(
        #     image=image,
        #     landmark_list=self.face_landmarks,
        #     connections=self.mp_face_mesh.FACEMESH_IRISES,
        #     landmark_drawing_spec=None,
        #     connection_drawing_spec=self.mp_drawing_styles
        #     .get_default_face_mesh_iris_connections_style())

        # Collect the face landmark locations
        for idx, lm in enumerate(self.face_landmarks.landmark):
            h, w, c = self.image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            self.face_list.append((cx, cy))
            # Put numbers in each point, used for testing purposes.
            # itr = 0
            # for point in self.face_list:
            #     cv2.putText(self.image, str(itr), point, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 0)
            #     itr += 1


class FaceProcessor:
    def __init__(self, size, lbrow, rbrow, totbrow, thresholds):
        self.thresholds = thresholds

        # 36 and above is down, ~33 is neutral, 27 and below is up
        self.up_down_score = (totbrow / size) * 100

        # 13.5 and below is up
        self.l_score = (lbrow / rbrow) * 10

        # Below 13.65 is up
        self.r_score = (rbrow / lbrow) * 10

    # 0 is up, 1 is down, 2 is left, and 3 is right
    def set_threshold(self, thresh_id, value):
        self.thresholds[thresh_id] = value

    # 0 is up, 1 is down, 2 is left, and 3 is right
    def get_threshold(self, thresh_id):
        return self.thresholds[thresh_id]

    # 0 is neutral, 1 is up, 2 is down, 3 is right, 4 is left
    def get_output(self):
        if self.thresholds[0] is not None:
            if self.up_down_score < self.thresholds[0]:
                return 1
            elif self.up_down_score > self.thresholds[1]:
                return 2
            elif self.r_score < self.thresholds[3]:
                return 3
            elif self.l_score < self.thresholds[2]:
                return 4
            else:
                return 0
