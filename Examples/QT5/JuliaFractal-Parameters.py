from PyQt5 import QtOpenGL, QtWidgets
import ModernGL as GL
import struct

context = {
	'width' : 800,
	'height' : 600,
}

class QGLControllerWidget(QtOpenGL.QGLWidget):
	def __init__(self, format = None):
		super(QGLControllerWidget, self).__init__(format, None)

	def initializeGL(self):
		try:
			GL.InitializeModernGL()
			GL.Viewport(0, 0, context['width'], context['height'])

			vert = GL.NewVertexShader('''
				#version 330

				in vec2 vert;
				out vec2 tex;

				void main() {
					gl_Position = vec4(vert, 0.0, 1.0);
					tex = vert / 2.0 + vec2(0.5, 0.5);
				}
			''')

			frag = GL.NewFragmentShader('''
				#version 330
				
				in vec2 tex;
				out vec4 color;

				uniform float scale;
				uniform vec2 center;
				uniform int iter;

				void main() {
					vec2 z = vec2(5.0 * (tex.x - 0.5), 3.0 * (tex.y - 0.5));
					vec2 c = vec2(1.33 * (tex.x - 0.5) * scale - center.x, (tex.y - 0.5) * scale - center.y);

					int i;
					for(i = 0; i < iter; i++) {
						vec2 v = vec2((z.x * z.x - z.y * z.y) + c.x, (z.y * z.x + z.x * z.y) + c.y);
						if (dot(v, v) > 4.0) break;
						z = v;
					}

					float cm = fract((i == iter ? 0.0 : float(i)) * 10 / iter);
					color = vec4(fract(cm + 0.0 / 3.0), fract(cm + 1.0 / 3.0), fract(cm + 2.0 / 3.0), 1.0);
				}
			''')

			prog, iface = GL.NewProgram([vert, frag])
			context['center'] = iface['center']
			context['scale'] = iface['scale']

			vbo = GL.NewVertexBuffer(struct.pack('8f', -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0))
			context['vao'] = GL.NewVertexArray(prog, vbo, '2f', ['vert'])

			GL.Uniform1i(iface['iter'], 100)
			GL.Uniform1f(iface['scale'], 1.0)
			GL.Uniform2f(iface['center'], 0.3, 0.2)

			context['mx'] = 0
			context['my'] = 0
			context['s'] = 1
			
		except GL.Error as error:
			print(error)
			exit(1)

	def paintGL(self):
		GL.Clear(240, 240, 240)
		GL.Uniform2f(context['center'], context['mx'], context['my'])
		GL.Uniform1f(context['scale'], context['s'])
		GL.RenderTriangleStrip(context['vao'], 4)

class QTWithGLTest(QtWidgets.QMainWindow):
	def __init__(self, parent = None):
		super(QTWithGLTest, self).__init__(parent)

		fmt = QtOpenGL.QGLFormat()
		fmt.setVersion(3, 3)
		fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
		fmt.setSampleBuffers(True)

		self.setFixedSize(context['width'], context['height'])
		self.widget = QGLControllerWidget(fmt)
		self.setCentralWidget(self.widget)
		self.show()

app = QtWidgets.QApplication([])
window = QTWithGLTest()
window.show()
app.exec_()