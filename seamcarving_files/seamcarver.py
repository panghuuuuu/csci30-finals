#!/usr/bin/env python3

from picture import Picture
from PIL import Image
import sys
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
        width = Picture.width(self)
        height = Picture.height(self)
        

        # Create a matrix with the cumulative sum
        pixel_matrix = [[self.energy(i, 0) for i in range(width)]]
        for j in range(1, height):
            row = []
            for i in range(width):
                # Leftmost column
                if i == 0:
                    neighbors = [pixel_matrix[j-1][0], pixel_matrix[j-1][1]]
                    row.append(self.energy(0, j) + min(neighbors))

                # Center columns
                elif i > 0 and i < width-1:
                    neighbors = [pixel_matrix[j-1][i-1], pixel_matrix[j-1][i], pixel_matrix[j-1][i+1]]
                    row.append(self.energy(i, j) + min(neighbors))

                # Rightmost column
                else:
                    neighbors = [pixel_matrix[j-1][i-1], pixel_matrix[j-1][i]]
                    row.append(self.energy(width-1, j) + min(neighbors))
            pixel_matrix.append(row)

        # Last row
        prev_index = pixel_matrix[-1].index(min(pixel_matrix[-1]))
        indexes = [prev_index]
        for j in range(height-2, -1, -1):
            j1, j2 = prev_index-1, prev_index+2
            if prev_index > 0 and prev_index < width-1:
                neighbors = pixel_matrix[j][j1:j2]
            elif prev_index == 0:
                neighbors = [sys.maxsize] + pixel_matrix[j][:2]
            else:
                neighbors = pixel_matrix[j][j1:]
            prev_index += neighbors.index(min(neighbors))-1
            indexes.append(prev_index)
        return indexes[::-1]

    def find_horizontal_seam(self) -> list[int]:
        '''
        Return a sequence of indices representing the lowest-energy
        horizontal seam
        '''
        sc = SeamCarver(Picture.picture(self).transpose(Image.ROTATE_90))
        return sc.find_vertical_seam()[::-1] 
         
    def remove_vertical_seam(self, seam: list[int]):
        '''
        Remove a vertical seam from the picture
        '''
        width = Picture.width(self)
        height = Picture.height(self) 
        seam_len = len(seam)
        if self._width  == 1:
            raise SeamError("Can't shrink the image vertically")
        elif self.check_invalid_seam(seam) == False:
            raise SeamError("Invalid seam")
        elif height != seam_len:
            raise SeamError("Attempted to remove seam with wrong length")
        else: 
            for j in range(height):
                for i in range(seam[j], width-1):
                    self[i, j] = self[i+1, j]
                del self[width-1, j]
            self._width -= 1

    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a horizontal seam from the picture
        '''
        width = Picture.width(self)
        height = Picture.height(self)
        seam_len = len(seam)
    
        if height == 1:
            raise SeamError("Can't shrink the image horizontally")
        elif self.check_invalid_seam(seam) == False:
            raise SeamError("Invalid seam")
        elif width != seam_len:
            raise SeamError("Attempted to remove seam with wrong length")
        else: 
            for i in range(width):
                #Find which column times row to be deleted based on the seam
                j = seam[i]
                while j < height - 1:
                    self[i, j] = self[i, j + 1]
                    j += 1

            for i in range(width):
                del self[i, height - 1]

            self._height -= 1
    
    def check_invalid_seam(self, seam: list[int]):
        for i in range(len(seam)-1):
            x = abs(seam[i] - seam[i+1])
            if  x > 1:
                return False
        return True

class SeamError(Exception):
    pass
