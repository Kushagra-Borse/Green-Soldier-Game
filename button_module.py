import pygame

class Button():
    def __init__(self, x, y, image, scale):
        self.image = image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width()*scale), int(self.image.get_height()*scale)))
        self.rect.topleft = (x ,y)
        self.clicked = False

    def draw(self,surface):
        action = False

        mouse_position = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_position):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, self.rect)

        return action