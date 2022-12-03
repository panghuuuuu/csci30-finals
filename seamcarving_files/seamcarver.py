#!/usr/bin/env python3

from picture import Picture

class SeamCarver(Picture):
    def energy(self, i: int, j: int) -> float:
        '''
        Return the energy of pixel at column i and row j
        '''

        if 0 <= i < self.width() and 0 <= j < self.height():
            Rx = abs(self[(i-1) % self.width(),j][0] - self[(i+1) % self.width(),j][0])
            Gx = abs(self[(i-1) % self.width(),j][1] - self[(i+1) % self.width(),j][1])
            Bx = abs(self[(i-1) % self.width(),j][2] - self[(i+1) % self.width(),j][2])
            dX = ((Rx**2) + (Gx**2) + (Bx**2))

            Ry = abs(self[i,(j-1) % self.height()][0] - self[i,(j+1) % self.height()][0])
            Gy = abs(self[i,(j-1) % self.height()][1] - self[i,(j+1) % self.height()][1])
            By = abs(self[i,(j-1) % self.height()][2] - self[i,(j+1) % self.height()][2])
            dY = ((Ry**2) + (Gy**2) + (By**2))

            return (dX+dY)
        else: #If selected pixel is out of bounds
            raise IndexError("Selected pixel is out of bounds")
            

    def find_vertical_seam(self) -> list[int]:
        '''
        Return a sequence of indices representing the lowest-energy
        vertical seam
        '''
        # Get the energy of all the pixels 
        width = Picture.width(self)
        height = Picture.height(self)
        pixel_matrix = [[0]*width for i in range(height)]
        dirs = [[0]*width for i in range(height)]

        for i in range(height):
            for j in range(width):
                pixel_matrix[i][j] = self.energy(j,i)
        last_row = pixel_matrix[height-1]

        # Changing to the cumulative pixels        
        # for i in range(width):
        #     pixel_matrix
        # for i in range(height-1, 1, -1):
        #     for j in range(1, width):
        #         j1, j2 = max(1, j-1), min(j+1, width) 
        path = []
        
        return path

    def find_horizontal_seam(self) -> list[int]:
        '''
        Return a sequence of indices representing the lowest-energy
        horizontal seam
        '''
        
        raise NotImplementedError

    def remove_vertical_seam(self, seam: list[int]):
        '''
        Remove a vertical seam from the picture
        '''
        if self.width()==1:
            raise SeamError("Can't shrink the image vertically")

    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a horizontal seam from the picture
        '''
        if self.height()==1 :
            raise SeamError("Can't shrink the image horizontally")

class SeamError(Exception):
    pass
