from numpy import *

def diamond_square(lod = 5, rough = 0.35, falloff = None):
    if falloff == None:
        falloff = lambda x, n: x**n

    n = 0
    size = int(pow(2, lod) + 1)

    hmap = random.random( (size, size) )
    
    step = size - 1
    while step >= 2:
        halfstep = step/2
        weight = falloff(rough, n)

        #diamond
        for i in range( 0, size-1, step ):
            for j in range( 0, size-1, step ):
                average = ( 
                    hmap[i, j] + 
                    hmap[i+step, j+step] + 
                    hmap[i+step, j] + 
                    hmap[i, j+step]
                ) / 4
                
                hmap[i+halfstep, j+halfstep] = (
                    average + hmap[i+halfstep, j+halfstep] * weight
                )
   #square
        for i in range( 0, size, halfstep ):
            j = (i+halfstep)%step
            while j < size:
                average = (
                    hmap[(i-halfstep+size)%size, j] +
                    hmap[(i+halfstep)%size, j] +
                    hmap[i, (j-halfstep+size)%size] +
                    hmap[i, (j+halfstep)%size] 
                ) / 4

                hmap[i, j] = hmap[i, j] * weight + average

        
                j += step
        
        n = n + 1
        step = step/2

    return hmap


def tiling_diamond_square(lod = 5, rough = 0.35, falloff = None):
    if falloff == None:
        falloff = lambda x, n: x**n

    n = 0
    size = int(pow(2, lod) + 1)

    hmap = random.uniform( -1, 1, (size, size) )

    hmap[0,0] = hmap[size-1,0] = hmap[0,size-1] = hmap[size-1,size-1]
    
    step = size - 1
    while step >= 2:
        halfstep = step/2
        weight = falloff(rough, n)

        #diamond
        for i in range( 0, size-1, step ):
            for j in range( 0, size-1, step ):
                average = ( 
                    hmap[i, j] + 
                    hmap[i+step, j+step] + 
                    hmap[i+step, j] + 
                    hmap[i, j+step]
                ) / 4
                
                hmap[i+halfstep, j+halfstep] = (
                    hmap[i+halfstep, j+halfstep] * weight + average
                )
   #square
        for i in range( 0, size-1, halfstep ):
            j = (i+halfstep)%step
            while j < size-1:
                average = (
                    hmap[(i-halfstep+size)%size, j] +
                    hmap[(i+halfstep)%size, j] +
                    hmap[i, (j-halfstep+size)%size] +
                    hmap[i, (j+halfstep)%size] 
                ) / 4

                hmap[i, j] = hmap[i, j] * weight + average

                if i == 0:
                    hmap[size-1, j] = hmap[i, j]
                if j == 0:
                    hmap[i, size-1] = hmap[i, j]
        
                j += step
        
        n = n+1
        step = step/2

    return hmap

    

    
