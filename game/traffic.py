import pygame
import random

LANE_W=80
COLORS=[(220,60,60),(220,140,40),(140,60,180),(60,180,80),(180,180,40),(60,80,200)]

class Car:
    def __init__(self, lane_x, y, direction, speed):
        self.rect=pygame.Rect(lane_x+10,y,60,80)
        self.direction=direction  # 1=down, -1=up
        self.speed=speed
        self.color=random.choice(COLORS)

    def update(self):
        self.rect.y+=self.direction*self.speed

    def off_screen(self,height):
        return self.rect.top>height+100 or self.rect.bottom<-100

    def draw(self,screen,night=False):
        if night:
            beam_length=180
            beam_width=110
            beam=pygame.Surface((beam_width,beam_length),pygame.SRCALPHA)
            start_y=0 if self.direction==1 else beam_length
            end_y=beam_length if self.direction==1 else 0
            for light_x in (beam_width//2-16,beam_width//2+16):
                pygame.draw.polygon(beam,(255,232,150,52),[
                    (light_x-4,start_y),(light_x+4,start_y),
                    (light_x+30,end_y),(light_x-30,end_y)
                ])
            beam_y=self.rect.bottom if self.direction==1 else self.rect.top-beam_length
            screen.blit(beam,(self.rect.centerx-beam_width//2,beam_y))
        pygame.draw.rect(screen,self.color,self.rect,border_radius=8)
        pygame.draw.rect(screen,(180,220,240),pygame.Rect(self.rect.x+8,self.rect.y+10,44,22),border_radius=4)
        for wx in [self.rect.x+6,self.rect.right-16]:
            for wy in [self.rect.y+4,self.rect.bottom-16]:
                pygame.draw.rect(screen,(30,30,30),pygame.Rect(wx,wy,10,12),border_radius=3)
        if night:
            front_y=self.rect.bottom-2 if self.direction==1 else self.rect.top+2
            for light_x in (self.rect.x+14,self.rect.right-14):
                pygame.draw.circle(screen,(255,247,190),(light_x,front_y),4)

def make_car(lane_idx,height,speed):
    x=lane_idx*LANE_W
    direction=1 if lane_idx%2==0 else -1
    y=-90 if direction==1 else height+10
    return Car(x,y,direction,speed)

class Raft:
    def __init__(self,x,y,speed,direction=1,width=130):
        self.rect=pygame.Rect(x,y,width,38)
        self.speed=speed
        self.direction=direction
        self.delta_x=0

    def update(self,screen_width):
        old_x=self.rect.x
        self.rect.x+=self.speed*self.direction
        if self.rect.left<=0:
            self.rect.left=0
            self.direction=1
        elif self.rect.right>=screen_width:
            self.rect.right=screen_width
            self.direction=-1
        self.delta_x=self.rect.x-old_x

    def draw(self,screen):
        pygame.draw.rect(screen,(115,72,38),self.rect,border_radius=8)
        for segment in range(1,4):
            x=self.rect.left+self.rect.width*segment//4
            pygame.draw.line(screen,(175,125,72),(x,self.rect.top+5),(x,self.rect.bottom-5),3)
