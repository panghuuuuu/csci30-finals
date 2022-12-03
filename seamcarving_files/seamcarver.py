#!/usr/bin/env python3

from picture import Picture

class SeamCarver(Picture):
    ## TO-DO: fill in the methods below
    def energy(self, i: int, j: int) -> float:
        '''
        Return the energy of pixel at column i and row j
        '''

        if i < self.width() and j < self.height():
            Rx = abs(self[i-1,j][0] - self[i+1,j][0])
            Gx = abs(self[i-1,j][1] - self[i+1,j][1])
            Bx = abs(self[i-1,j][2] - self[i+1,j][2])
            dX = ((Rx**2) + (Gx**2) + (Bx**2))

            Ry = abs(self[i,j-1][0] - self[i,j+1][0])
            Gy = abs(self[i,j-1][1] - self[i,j+1][1])
            By = abs(self[i,j-1][2] - self[i,j+1][2])
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
        raise NotImplementedError

    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a horizontal seam from the picture
        '''
        raise NotImplementedError

class SeamError(Exception):
    pass
