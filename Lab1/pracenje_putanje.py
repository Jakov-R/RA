from pyglet.gl import *
import numpy as np
from numpy.linalg import norm
from pyglet.window import key

window = None
animIndex = 0
timer = 0
showTangents = False

filename = 'teddy.obj'
bspline = 'bspline.obj'

class Camera:
    def __init__(self, pos=(0, 0, 0), lookAt=(0, 0, 0)):
        self.pos = list(pos)
        self.lookAt = list(lookAt)

    def get_postion(self):
        return self.pos

    def get_lookAt(self):
        return self.lookAt

    def compute_rotation(self, s, e):
        #os = se (vek)
        os_rot = np.cross(s, e)
        #se (skalar)
        se = np.dot(s, e)
        #norme: |s|,|e|
        sN = np.linalg.norm(s)
        eN = np.linalg.norm(e)

        #phi = se / |s||e|
        kut_rot = np.rad2deg(np.arccos(se / (sN * eN)))

        return os_rot, kut_rot


class BSpline:
    def __init__(self):
        self.resolution = 20
        self.load_spline(bspline)
        self.compute_scale()
        self.calc_spline()

    def load_spline(self, file):
        self.vertices = []
        obj_data = open(file, 'r')
        for line in obj_data:
            if line.startswith("v"):
                split = line.split()
                self.vertices.append(list(map(float, split[1:4])))
            if line.startswith('f'):
                continue
            if line.startswith("g"):
                continue
            if line.startswith("#"):
                continue

    def compute_scale(self):
        x_max, x_min = float("-inf"), float("inf")
        y_max, y_min = float("-inf"), float("inf")
        z_max, z_min = float("-inf"), float("inf")

        for v in self.vertices:
            if v[0] < x_min:
                x_min = v[0]
            if v[0] > x_max:
                x_max = v[0]
            if v[1] < y_min:
                y_min = v[1]
            if v[1] > y_max:
                y_max = v[1]
            if v[2] < z_min:
                z_min = v[2]
            if v[2] > z_max:
                z_max = v[2]

        self.center_x = (x_max + x_min) / 2
        self.center_y = (y_max + y_min) / 2
        self.center_z = (z_max + z_min) / 2

        scale_x = x_max - x_min
        scale_y = y_max - y_min
        scale_z = z_max - z_min

        self.scale = max([scale_x, scale_y, scale_z])

    def get_center(self):
        return self.center_x, self.center_y, self.center_z

    def get_scale(self):
        return self.scale

    def calc_segment_t(self, i_segment, t):
        #t^3, t^2, t, 1
        T = np.array([t * t * t, t * t, t, 1])

        #matrica iz uputa (1.2)
        B = 1 / 6 * np.array([[-1, 3, -3, 1],
                              [3, -6, 3, 0],
                              [-3, 0, 3, 0],
                              [1, 4, 1, 0]])

        control_points = self.vertices
        #r(i-1), r(i), r(i+1), r(i+2)
        R = np.array([control_points[i_segment - 1],
                      control_points[i_segment],
                      control_points[i_segment + 1],
                      control_points[i_segment + 2]])
        TB = np.dot(T, B)
        #TBR = tocka krivulje
        TBR = np.dot(TB, R)

        #RACUNANJE TANGENTE
        #t^2, t, 1
        Tt = [t * t, t, 1]

        #matrica iz uputa (1.4)
        Bt = 1 / 2 * np.array([[-1, 3, -3, 1],
                               [2, -4, 2, 0],
                               [-1, 0, 1, 0]])

        # r(i-1), r(i), r(i+1), r(i+2)
        Rt = np.array([control_points[i_segment - 1],
                       control_points[i_segment],
                       control_points[i_segment + 1],
                       control_points[i_segment + 2]])

        TBt = np.dot(Tt, Bt)
        TBRt = np.dot(TBt, Rt)
        #TBRt = smjer tangente

        return TBR, TBRt

    def calc_spline(self):
        self.segments = []
        self.tangets = []
        for index in range(1, self.vertices.__len__() - 3 + 1):
            for t in np.linspace(0, 1, self.resolution):
                points, tangents = self.calc_segment_t(index, t)
                self.segments.append(points)
                self.tangets.append(tangents)

    def getTangentData(self, point, index):
        data = [(point[0]) / self.scale,
                (point[1]) / self.scale,
                (point[2]) / self.scale,
                (point[0] + self.tangets[index][0]) / self.scale,
                (point[1] + self.tangets[index][1]) / self.scale,
                (point[2] + self.tangets[index][2]) / self.scale]
        return data

    def define_drawing(self):
        global animIndex, showTangents
        self.batch = pyglet.graphics.Batch()

        line_points = []
        line_color = []
        index = 0
        for iIndex, point in enumerate(self.segments):
            line_points.append((point[0]) / self.scale)
            line_points.append((point[1]) / self.scale)
            line_points.append((point[2]) / self.scale)
            line_color.append(0.8)
            line_color.append(0.8)
            line_color.append(0.8)
            if (showTangents):
                self.batch.add(2,
                               GL_LINES,
                               None,
                               ('v3f', self.getTangentData(point, index)),
                               ('c3d', [1, 0, 0, 1, 0, 0]))

            index += 1
        self.batch.add(int(line_points.__len__() / 3),
                       GL_LINE_STRIP,
                       None,
                       ('v3f', line_points), ('c3d', line_color))

    def draw(self):
        self.batch.draw()


class Model:
    def __init__(self):
        self.load_model(filename)
        self.compute_scale()
        self.location = [0, 0, 0]

    def load_model(self, filename):
        self.vertices = []
        self.polygons = []

        obj_data = open(filename, 'r')
        for line in obj_data:
            if line.startswith("v"):
                split = line.split()
                self.vertices.append(list(map(float, split[1:4])))
            if line.startswith('f'):
                split = line.split()
                self.polygons.append(list(map(int, split[1:4])))
            if line.startswith("g"):
                continue
            if line.startswith("#"):
                continue

    def compute_scale(self):
        x_max, x_min = float("-inf"), float("inf")
        y_max, y_min = float("-inf"), float("inf")
        z_max, z_min = float("-inf"), float("inf")

        for v in self.vertices:
            if v[0] < x_min:
                x_min = v[0]
            if v[0] > x_max:
                x_max = v[0]

            if v[1] < y_min:
                y_min = v[1]
            if v[1] > y_max:
                y_max = v[1]

            if v[2] < z_min:
                z_min = v[2]
            if v[2] > z_max:
                z_max = v[2]

        self.center_x = (x_max + x_min) / 2
        self.center_y = (y_max + y_min) / 2
        self.center_z = (z_max + z_min) / 2

        scale_x = x_max - x_min
        scale_y = y_max - y_min
        scale_z = z_max - z_min

        self.scale = max([scale_x, scale_y, scale_z])

    def get_center(self):
        return self.center_x, self.center_y, self.center_z

    def get_scale(self):
        return self.scale

    def define_drawing(self):
        self.batch = pyglet.graphics.Batch()

        for pol in self.polygons:
            V1 = self.vertices[pol[0] - 1]
            V2 = self.vertices[pol[1] - 1]
            V3 = self.vertices[pol[2] - 1]

            self.batch.add(3, GL_TRIANGLES, None,
                           ('v3f', (V1[0], V1[1], V1[2], V2[0], V2[1], V2[2], V3[0], V3[1], V3[2])),
                           ('c3f', (0, 0, 1, 0, 0, 1, 0, 0, 1)))

    def draw(self):
        self.batch.draw()


class Window(pyglet.window.Window):
    global pyglet

    def __init__(self, *args, **kwargs):
        global animIndex, timer
        super().__init__(*args, **kwargs)
        self.set_minimum_size(600, 600)
        self.POV = 45
        pyglet.clock.schedule(self.update)
        self.model = Model()
        self.spline = BSpline()
        self.camera = Camera((1, 1, 1), (0, 0, 0.5))

        self.model.define_drawing()
        self.spline.define_drawing()

    def on_key_press(self, key, modifiers):
        global showTangents
        if key == pyglet.window.key.S:
            self.camera.lookAt[1] += 0.1
        elif key == pyglet.window.key.W:
            self.camera.lookAt[1] -= 0.1
        elif key == pyglet.window.key.A:
            self.camera.lookAt[0] += 0.1
        elif key == pyglet.window.key.D:
            self.camera.lookAt[0] -= 0.1
        elif key == pyglet.window.key.I:
            self.camera.lookAt[2] += 0.1
        elif key == pyglet.window.key.O:
            self.camera.lookAt[2] -= 0.1
        elif key == pyglet.window.key.T:
            showTangents = not showTangents

    def update(self, dt):
        global animIndex, timer
        self.spline.define_drawing()
        timer = timer + 1 / 60
        if timer > 1:
            timer = 0
            animIndex += 1
            if animIndex >= self.spline.vertices.__len__() - 3 + 1:
                animIndex = 0

    def animate(self, i_seg):
        global animIndex, timer
        #pocetna orijentacija
        s = np.array([0, 0, 1])

        segment_point, segment_tangents = self.spline.calc_segment_t(animIndex, timer)

        os_rot, kut_rot = self.camera.compute_rotation(s, segment_tangents)

        glPushMatrix()
        spline_scale = self.spline.get_scale()
        glTranslatef(segment_point[0] / spline_scale, segment_point[1] / spline_scale, segment_point[2] / spline_scale)
        glScalef(1 / 150, 1 / 150, 1 / 150)
        glRotatef(kut_rot, os_rot[0], os_rot[1], os_rot[2])
        self.model.draw()
        glPopMatrix()

    def on_draw(self):
        global animIndex
        self.clear()
        camera_positon = self.camera.get_postion()
        lookAt = self.camera.get_lookAt()

        glPushMatrix()
        self.animate(animIndex)
        glPopMatrix()

        glPushMatrix()
        self.spline.draw()
        glPopMatrix()

        glPushMatrix()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.POV, self.width / self.height, 0.05, 1000)
        gluLookAt(camera_positon[0], camera_positon[1], camera_positon[2],
                  lookAt[0], lookAt[1], lookAt[2],
                  0.0, 1.0, 0.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glFrontFace(GL_CCW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glPopMatrix()


if __name__ == '__main__':
    width = 600
    height = 600
    window = Window(width=width, height=height, caption='PRACENJE PUTANJE', resizable=True)
    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    glClearColor(0.0, 0.0, 0.0, 1)

    glFrontFace(GL_CCW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    pyglet.app.run()