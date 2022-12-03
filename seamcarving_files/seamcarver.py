#!/usr/bin/env python3

from picture import Picture

class SeamCarver(Picture):
    ## TO-DO: fill in the methods below
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
        raise NotImplementedError

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
