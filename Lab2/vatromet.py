from random import *
from pyrr import Vector3
import numpy as np
from pyglet.gl import *

class Cestica:
    def __init__(self, poz, brzina=0):
        self.pozicija = poz.copy()
        if brzina != 0:
            self.brzina = Vector3([brzina, brzina, brzina])
        else:
            #x = zoom in(+)/zoom out(-)
            #y = gore(+)/dolje(-)
            #z = lijevo(+)/desno(-)
            self.brzina = Vector3([randint(-5,5), randint(-5,5), randint(-5,5)])
        self.zivotni_vijek = 180

    def update(self, dt):
        self.pozicija += self.brzina
        self.zivotni_vijek -= 1

class SustavCestica:

    def __init__(self, tekstura, broj_cestica=1, velicina_cestica=100):
        self.cestice = []
        self.tekstura = tekstura
        self.velicina_cestica = velicina_cestica
        self.stvoriCesticu(broj_cestica)
        self.brojac = 0

    def stvoriCesticu(self, broj_cestica):
        for i in range(0, broj_cestica):
            if i % 2 == 0:
                c = Cestica([0, 0, 1000])
            else:
                c = Cestica([0, 0, -1000])
            self.cestice.append(c)

    def update(self, dt):
        self.brojac += 1
        for c in self.cestice:
            c.update(dt)
            if c.zivotni_vijek <= 0:
                self.cestice.remove(c)
        if self.brojac % 90 == 0:
            self.stvoriCesticu(randint(1, 15))
            #self.stvoriCesticu(1)

    def crtaj(self):
        glEnable(self.tekstura.target)
        glBindTexture(self.tekstura.target, self.tekstura.id)

        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)

        glPushMatrix()
        for c in self.cestice:
            matrix = (GLfloat * 16)()
            glGetFloatv(GL_MODELVIEW_MATRIX, matrix)
            matrix = list(matrix)
            CameraUp = np.array([matrix[1], matrix[5], matrix[9]])
            CameraRight = np.array([matrix[0], matrix[4], matrix[8]])
            velicina = self.velicina_cestica

            v1 = c.pozicija + CameraRight * velicina + CameraUp * (-velicina)
            v2 = c.pozicija + CameraRight * velicina + CameraUp * velicina
            v3 = c.pozicija + CameraRight * (-velicina) + CameraUp * (-velicina)
            v4 = c.pozicija + CameraRight * (-velicina) + CameraUp * velicina

            glBegin(GL_QUADS)
            #donji lijevi kut (-,-)
            glTexCoord2f(0, 0)
            glVertex3f(v3[0], v3[1], v3[2])
            #donji desni (-, +)
            glTexCoord2f(1, 0)
            glVertex3f(v4[0], v4[1], v4[2])
            #gornji desni (+, +)
            glTexCoord2f(1, 1)
            glVertex3f(v2[0], v2[1], v2[2])
            #gornji lijevi (+, -)
            glTexCoord2f(0, 1)
            glVertex3f(v1[0], v1[1], v1[2])

            glEnd()
        glDisable(GL_BLEND)
        glPopMatrix()
        glDisable(self.tekstura.target)

class Window(pyglet.window.Window):
    global pyglet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(600, 400)
        self.POV = 60
        self.source = [0, 0, 0]
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)

        tekstura = pyglet.image.load('cestica.bmp').get_texture()

        self.SusCes = SustavCestica(tekstura, 10)
        #self.sus2 = SustavCestica(tekstura, 20)

    def update(self, dt):
        self.SusCes.update(dt)

    def on_draw(self):
        self.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        camera_position = [2500, 0, 0]
        lookAt = [0, 0, 0]

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.POV, self.width / self.height, 0.05, 10000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(camera_position[0],   camera_position[1], camera_position[2],
                  lookAt[0],            lookAt[1],          lookAt[2],
                  0.0,                  1.0,                0.0)
        glPushMatrix()
        self.SusCes.crtaj()
        glPopMatrix()
        glFlush()


if __name__ == '__main__':
    window = Window(width=1080, height=720, caption='VATROMET', resizable=True)
    pyglet.app.run()