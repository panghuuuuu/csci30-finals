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
        energy_matrix = [[self.energy(i, 0) for i in range(width)]]
        for j in range(1, height):
            row = []
            for i in range(width):
                # Leftmost column
                if i == 0:
                    neighbors = [energy_matrix[j-1][0], energy_matrix[j-1][1]]
                    row.append(self.energy(0, j) + min(neighbors))

                # Center columns
                elif i > 0 and i < width-1:
                    neighbors = [energy_matrix[j-1][i-1], energy_matrix[j-1][i], energy_matrix[j-1][i+1]]
                    row.append(self.energy(i, j) + min(neighbors))

                # Rightmost column
                else:
                    neighbors = [energy_matrix[j-1][i-1], energy_matrix[j-1][i]]
                    row.append(self.energy(width-1, j) + min(neighbors))
            energy_matrix.append(row)

        # Last row
        prev_index = energy_matrix[-1].index(min(energy_matrix[-1]))
        indexes = [prev_index]
        for j in range(height-2, -1, -1):
            j1, j2 = prev_index-1, prev_index+2
            if prev_index > 0 and prev_index < width-1:
                neighbors = energy_matrix[j][j1:j2]
            elif prev_index == 0:
                neighbors = [sys.maxsize] + energy_matrix[j][:2]
            else:
                neighbors = energy_matrix[j][j1:]
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
        width = self._width
        height = self._height
        seam_len = len(seam)
        if width == 1:
            raise SeamError("Can't shrink the image horizontally")
        elif self.check_invalid_seam(seam) == False:
            raise SeamError("Invalid seam")
        elif height != seam_len:
            raise SeamError("Attempted to remove seam with wrong length")
        else: 
            for j in range(height):
                for i in range(seam[j], width-1):
                    self[i, j] = self[i + 1, j]
                del self[width-1, j]
            self._width -= 1

    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a horizontal seam from the picture
        '''
        width = self._width
        height = self._height
        seam_len = len(seam)
        
        if height == 1:
            raise SeamError("Can't shrink the image horizontally")
        elif self.check_invalid_seam(seam) == False:
            raise SeamError("Invalid seam")
        elif width != seam_len:
            raise SeamError("Attempted to remove seam with wrong length")
        else: 
            sc = SeamCarver(self.picture().rotate(90, expand=True))
            sc.remove_vertical_seam(seam[::-1])

            self._width = sc.height()
            self._height = sc.width()
            self.clear()
            for j in range(self._height):
                for i in range(self._width):
                    self[i, j] = sc[j, (sc._height-1) - i]

    def check_invalid_seam(self, seam: list[int]):
        for i in range(len(seam)-1):
            x = abs(seam[i] - seam[i+1])
            if  x > 1:
                return False
        return True

class SeamError(Exception):
    pass
