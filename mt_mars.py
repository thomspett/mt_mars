SCREEN_SIZE = (800, 600)

import time

from math import radians, pow
from numpy import *
from random import uniform

from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *

from gameobjects.matrix44 import *
from gameobjects.vector3 import *

from noise import *

def resize(width, height):
    
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(width)/height, .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    
    glEnable(GL_DEPTH_TEST)
    
    glShadeModel(GL_SMOOTH)
    glClearColor(0.5, 0.5, 0.5, 0.0)

    glEnable(GL_COLOR_MATERIAL)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)        
    glLight(GL_LIGHT0, GL_POSITION,  (500., 500., 150., 1.))    
    glLight(GL_LIGHT0, GL_DIFFUSE,  (0.8, 0.7, 0.6, 1.))    
    glLight(GL_LIGHT0, GL_AMBIENT,  (0.2, 0.2, 0.4, 1.))    
    glLight(GL_LIGHT0, GL_SPECULAR,  (1.0, 1.0, 1.0, 1.))    

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
#antialiasing
    glEnable(GL_LINE_SMOOTH)
    glEnable (GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint (GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint (GL_POLYGON_SMOOTH_HINT, GL_NICEST)

class Mesh(object):
    def __init__(self, rough=0.35, width = 100.0, height=30.0):
        self.rough = rough
        self.height = height
        self.width = width
     #   self.parts = parts = 5
     #   self.heightmap = tiling_diamond_square(parts, rough)*height
     #   self.size = asarray(self.heightmap.shape)
     #   print self.size
     #   self.xy_coords()
     #   self.prerender()
        self.parts = 0
        self.size = asarray( (2, 2) )
        self.heightmap = zeros( self.size )
        self.xy_coords()
        self.prerender()

    def xy_coords(self):
        width = self.width
        self.x_coords = linspace(0, width, self.size[0])
        self.y_coords = linspace(0, width, self.size[1])

    def iterate(self):
        time0 = time.time()    
        print 'iterating heightmap'
        self.diamond_square()
        time1 = time.time()
        time2 = time1-time0
        print 'finished after %.2f seconds' % time2
        print 'prerendering geometry'
        self.xy_coords()
        self.prerender()
        time0 =time.time()
        time2 = time0 -time1
        print 'geometry ready %.2f seconds' % time2
        
    def diamond_square(self):
        x, y = self.size
        newsize = self.size*2 - 1
        h = self.height

        #randnum = x*y - 1
        #randors = (random.random(randnum) - 0.5) * self.height
        #randcunt = 0

        oldmap = self.heightmap
        newmap = zeros( newsize )

        for i in range(x):
            for j in range(y):
                newmap[i*2, j*2] = oldmap[i, j]
        #diamond
        x, y = newsize
        print newsize
        rough, parts = self.rough, self.parts
        for i in range(1, x-1, 2):
            for j in range(1, y-1, 2):
                if newmap[i, j] == 0:
          #          print 'hei [%d, %d]' % (i, j)
                    newmap[i, j] = ( 
                        newmap[i-1, j-1] + 
                        newmap[i-1, j+1] + 
                        newmap[i+1, j-1] + 
                        newmap[i+1, j+1]
                    ) / 4 + uniform(-h, h) * pow(rough, parts)
                    #) / 4 + randors[randcunt] * pow(rough, parts)
                    #randcunt += 1
         #       else:
                    #print 'diamondslut [%d, %d]' % (i, j)
        #square
        for i in range(1, x-1 ):
            for j in range(1, y-1 ):
                if newmap[i, j] == 0:
        #            print 'hallo [%d, %d]' % (i, j)
                    newmap[i, j] += (
                        newmap[i, j-1] +
                        newmap[i, j+1] +
                        newmap[i+1, j] +
                        newmap[i-1, j]
                    ) / 4 + uniform(-h, h) * pow(rough, parts)
                    #) / 4 + randors[randcunt] * pow(rough, parts)
                    #randcunt += 1
        #        else:
                    5
                    #print 'squarefuck [%d, %d]' % (i, j)

 
        self.parts += 1
        self.size = newsize
        self.heightmap = newmap
        self.xy_coords()


    def prerender(self):
        h = self.heightmap
        x = self.x_coords
        y = self.y_coords
        #c = self.colormap
        
        n_x = len(x)
        n_y = len(y)
        n_vertices = n_x * n_y
        n_faces = (n_x - 1)*(n_y - 1)*2

        vertices = [] #array of vertices
        vertex_indices = [] #index array
        vertex_normals = [] #array of averaged normals to vertices
        vertex_colors = []
        
        #all on the way to weighted normals
        face_normals = [] #array of normals to faces
        vertex_faces = [] #array of array faces shared by vertices
    
        #j * n_x + i
        #
        #0, 1, 2, 3, ... , n_x-1
        #n_x, n_x+1, ... , 2*n_x-1
        #2*n_x, ... , 3*n_x-1

#make vertex array and prepare *neighbourhood*
        for i in range( n_x ):
            for j in range( n_y ):
                vertices.append( (x[i], y[j], h[i,j]) )
                vertex_faces.append([])

#make index array (face-vertex)
        for j in range( n_x - 1 ):
            for i in range( n_y - 1 ):
                k = j*n_x + i
                vertex_indices.append( ( k + 1, k, k + n_x + 1 ) )
                vertex_indices.append( ( k + n_x + 1, k, k + n_x ) )

#make vertex-face array
        for face in range(n_faces):
            for index in vertex_indices[face]:
                vertex_faces[index].append(face)

#make face-normals            
        for face in vertex_indices:
            vertex0 = vertices[face[0]]
            vertex1 = vertices[face[1]]
            vertex2 = vertices[face[2]]

            vector0 = Vector3(vertex0)
            vector1 = Vector3(vertex1)
            vector2 = Vector3(vertex2)

            normal = (vector1-vector0).cross(vector2-vector1)
            normal.normalize()
            face_normals.append( normal )

#make averaged vertex normals
        for vertex in vertex_faces:
            fnormals = [face_normals[i] for i in vertex]
            n = 0
            summa = Vector3()
            for vec in fnormals:
                summa += vec
                n += 1
            vnormal = summa / n
            vnormal.normalize()
            vertex_normals.append( tuple( vnormal ) )
            
#colors temp  
        
        #maxi = h[1:-2,1:-2].max()
        #mini = h[1:-2,1:-2].min()
        maxi = h.max()
        mini = h.min()
        mag = maxi - mini
        for vertex in vertices:
            color = ( vertex[2] - mini ) / mag
            if color < 0.:
                color = 0.
            #color = Vector3(vertex)
            #color.normalize()
            #color = (asarray(color) + 1) / 2
            #vertex_colors.append( tuple( color ) )
            vertex_colors.append( (color**2, color, (2*color-1)**2) )
            

        self.vertex_indices = asarray(vertex_indices)
        self.vertices = asarray(vertices)
        self.vertex_normals = asarray(vertex_normals)
        self.vertex_colors = asarray(vertex_colors)
        self.n_vertices = n_vertices
        self.n_faces = n_faces
        print n_vertices
        print n_faces


    def render(self):


        vertices = self.vertices
        indices = self.vertex_indices
        normals = self.vertex_normals
        colors = self.vertex_colors
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        glVertexPointerd( vertices )
        glNormalPointerd( normals )
        glColorPointerd( colors )
        glDrawElementsui( GL_TRIANGLES, indices )


    def drawAxis(self):
        glBegin(GL_LINES)
        #glLineWidth(3.)
        glColor( (0.,0.,0.) )
        glVertex((0.,0.,0.))
        glVertex((1000.,0.,0.))
        glVertex((0.,0.,0.))
        glVertex((0.,1000.,0.))
        glVertex((0.,0.,0.))
        glVertex((0.,0.,1000.))
        glEnd()
       

    def drawNormals(self):
        self.drawAxis()
        vertices = self.vertices
        normals = self.vertex_normals
        glColor( (0.,0.,0.) )
        glBegin(GL_LINES)
        for i in range(self.n_vertices):
            x0, y0, z0 = vertices[i]
            vx, vy, vz = normals[i]
            #vx, vy, vz = vx*3, vy*3, vz*3
            x1, y1, z1 = x0+vx, y0+vy, z0+vz         
            glVertex( (x0,y0,z0) )
            glVertex( (x1,y1,z1) )
        glEnd()

            

class Map(object):
    
    def __init__(self):
        
        self.mesh = Mesh()
        self.drawNormals = 0
        self.drawWire = 0
        self.display_list = None

    def iterate(self):
        self.mesh.iterate()
        
    
    def render(self):
        if self.drawWire:        
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) 
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) 
           
        if self.display_list is None:
            time0 = time.time()    
            print 'compiling displaylist'
            # Create a display list
            self.display_list = glGenLists(1)                
            glNewList(self.display_list, GL_COMPILE)
            
            # Draw the cubes
            self.mesh.render()
            # End the display list
            glEndList()
            time1 =  time.time()
            comptime = time1-time0
            print 'displaylist done in %.2f seconds' % comptime
        else:
            
            # Render the display list            
            glCallList(self.display_list)
                    
       # self.mesh.render()
        if self.drawNormals:
            self.mesh.drawNormals()


def run():
    
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE|OPENGL|DOUBLEBUF)
    
    resize(*SCREEN_SIZE)
    init()
    
    clock = pygame.time.Clock()    
    time = 0

    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)    
    #glMaterial(GL_FRONT, GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))    
    #glMaterial(GL_FRONT, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))

    # This object renders the 'map'
    map = Map()        

    # Camera transform matrix
    camera_matrix = Matrix44()
    camera_matrix.translate = (0.0, 0.0, 10.0)

    # Initialize speeds and directions
    rotation_direction = Vector3()
    rotation_speed = radians(30.0)
    movement_direction = Vector3()
    movement_speed = 10.0    

    while True:
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return                
            
            if event.type == KEYUP and event.key == K_i:
                map.iterate()
                map.display_list = None

            if event.type == KEYUP and event.key == K_o:
                map.mesh = Mesh()
                map.display_list = None
                print 'reset'

            if event.type == KEYUP and event.key == K_m:
                map.drawWire = not map.drawWire
                #ap.display_list = None
                print 'Wireframe %s' % map.drawWire 


            if event.type == KEYUP and event.key == K_n:
                map.drawNormals = not map.drawNormals
                #ap.display_list = None
                print 'Norms %s' % map.drawNormals

        # Clear the screen, and z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
                        
        time_passed = clock.tick(30)
        time_passed_seconds = time_passed / 1000.
        
        pressed = pygame.key.get_pressed()
        
        # Reset rotation and movement directions
        rotation_direction.set(0.0, 0.0, 0.0)
        movement_direction.set(0.0, 0.0, 0.0)
        
        # Modify direction vectors for key presses
        if pressed[K_LEFT]:
            rotation_direction.y = +1.0
        elif pressed[K_RIGHT]:
            rotation_direction.y = -1.0
        if pressed[K_UP]:
            rotation_direction.x = -1.0
        elif pressed[K_DOWN]:
            rotation_direction.x = +1.0
        if pressed[K_e]:
            rotation_direction.z = -1.0
        elif pressed[K_q]:
            rotation_direction.z = +1.0            
        if pressed[K_w]:
            movement_direction.z = -1.0
        elif pressed[K_s]:
            movement_direction.z = +1.0
        if pressed[K_a]:
            movement_direction.x = -1.0
        elif pressed[K_d]:
            movement_direction.x = +1.0       
        if pressed[K_f]:
            movement_direction.y = -1.0
        elif pressed[K_r]:
            movement_direction.y = +1.0
    
        
        # Calculate rotation matrix and multiply by camera matrix    
        rotation = rotation_direction * rotation_speed * time_passed_seconds
        rotation_matrix = Matrix44.xyz_rotation(*rotation)        
        camera_matrix *= rotation_matrix
        
        # Calcluate movment and add it to camera matrix translate
        heading = Vector3(camera_matrix.forward)
        up = Vector3(camera_matrix.up)
        left = up.cross(heading)
        movement = (heading * movement_direction.z + 
                    left * movement_direction.x +
                    up * movement_direction.y) * movement_speed                    
        camera_matrix.translate += movement * time_passed_seconds
        
        # Upload the inverse camera matrix to OpenGL
        glLoadMatrixd(camera_matrix.get_inverse().to_opengl())
                
        # Light must be transformed as well
        time += time_passed_seconds
        lightx, lighty, lightz = 500., 500., 150.
        v = .5
        lightz = lightz * (cos(v * time * 0.41)/2 + 1)
        lightx = lightx * sin(v * time)
        lighty = lighty * cos(v * time)
        glLight(GL_LIGHT0, GL_POSITION,  (lightx, lighty, lightz, 1.0)) 
                
        # Render the map
        map.render()
        
                
        # Show the screen
        pygame.display.flip()

run()
