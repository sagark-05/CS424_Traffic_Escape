import pygame
import random
import json
from pathlib import Path
from game.player import Player,LANE_W
from game.traffic import Car,Raft,make_car

LANES=8
WIDTH=LANES*LANE_W
HEIGHT=600
FPS=60
BG=(60,60,60)
SAFE_LANE_TOP=HEIGHT//2-LANE_W//2
DAY_NIGHT_INTERVAL_MS=30000

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Traffic Escape")
        self.clock=pygame.time.Clock()
        self.font=pygame.font.SysFont("monospace",24,bold=True)
        self.hud_font=pygame.font.SysFont("monospace",18,bold=True)
        self.high_score_font=pygame.font.SysFont("monospace",14,bold=True)
        self.big_font=pygame.font.SysFont("monospace",44,bold=True)
        self.high_score_path=Path(__file__).resolve().parent.parent/"high_scores.json"
        self.high_scores=self._load_high_scores()
        self.reset()

    def _load_high_scores(self):
        try:
            data=json.loads(self.high_score_path.read_text(encoding="utf-8"))
            scores=data.get("scores",[]) if isinstance(data,dict) else []
            if not isinstance(scores,list):
                return []
            valid_scores=[score for score in scores if type(score) is int and score>=0]
            return sorted(valid_scores,reverse=True)[:5]
        except (OSError,json.JSONDecodeError):
            return []

    def _save_high_score(self):
        self.high_scores=sorted(self.high_scores+[self.score//10],reverse=True)[:5]
        try:
            self.high_score_path.write_text(
                json.dumps({"scores":self.high_scores},indent=2)+"\n",
                encoding="utf-8"
            )
        except OSError:
            pass

    def reset(self):
        self.player=Player(WIDTH//2+LANE_W//2,HEIGHT-80)
        self.cars=[]
        self.safe_lane=pygame.Rect(0,SAFE_LANE_TOP,WIDTH,LANE_W)
        raft_y=SAFE_LANE_TOP+(LANE_W-38)//2
        self.rafts=[Raft(12,raft_y,2,1),Raft(250,raft_y,3,1),Raft(498,raft_y,2,1)]
        self.riding_raft=None
        self.timer=0
        self.spawn_interval=50
        self.speed=3
        self.score=0
        self.lives=3
        self.game_over=False
        self.won=False
        self.score_recorded=False
        self.is_night=False
        self.day_night_started_at=pygame.time.get_ticks()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return False
            if event.type==pygame.KEYDOWN and event.key==pygame.K_r: self.reset()
        return True

    def update(self):
        if self.game_over or self.won: return
        self._update_day_night()
        keys=pygame.key.get_pressed()
        self.player.move(keys,0,WIDTH)
        life_lost=self._update_raft_lane()
        self.timer+=1
        if self.timer>=self.spawn_interval:
            lane=random.randint(0,LANES-1)
            self.cars.append(make_car(lane,HEIGHT,self.speed))
            self.timer=0
            self.spawn_interval=max(22,self.spawn_interval-0.2)
        hit_car=None
        active_cars=[]
        for c in self.cars:
            c.update()
            if c.rect.colliderect(self.safe_lane):
                continue
            if not life_lost and hit_car is None and c.rect.colliderect(self.player.rect):
                hit_car=c
            else:
                active_cars.append(c)
        if hit_car is not None:
            self._lose_life()
        self.cars=[c for c in active_cars if not c.off_screen(HEIGHT)]
        self.score+=1
        if self.score%300==0: self.speed=min(10,self.speed+0.5)
        if self.player.rect.top<=10:
            self.won=True
        if (self.game_over or self.won) and not self.score_recorded:
            self._save_high_score()
            self.score_recorded=True

    def _update_day_night(self):
        now=pygame.time.get_ticks()
        intervals=(now-self.day_night_started_at)//DAY_NIGHT_INTERVAL_MS
        if intervals:
            if intervals%2:
                self.is_night=not self.is_night
            self.day_night_started_at+=intervals*DAY_NIGHT_INTERVAL_MS

    def _update_raft_lane(self):
        for raft in self.rafts:
            raft.update(WIDTH)
        if not SAFE_LANE_TOP<=self.player.rect.centery<SAFE_LANE_TOP+LANE_W:
            self.riding_raft=None
            return False
        if self.riding_raft is not None and self._player_overlaps_raft(self.riding_raft):
            self.player.rect.x+=self.riding_raft.delta_x
            if not self._player_overlaps_raft(self.riding_raft):
                self.riding_raft=None
        else:
            self.riding_raft=None
        if self.riding_raft is None:
            self.riding_raft=next((raft for raft in self.rafts if self._player_overlaps_raft(raft)),None)
        if (self.riding_raft is None or self.player.rect.left<0 or
                self.player.rect.right>WIDTH):
            self._lose_life()
            return True
        return False

    def _player_overlaps_raft(self,raft):
        return self.player.rect.left<raft.rect.right and self.player.rect.right>raft.rect.left

    def _lose_life(self):
        self.lives-=1
        self.player=Player(WIDTH//2+LANE_W//2,HEIGHT-80)
        self.riding_raft=None
        if self.lives<=0:
            self.game_over=True

    def draw(self):
        night=self.is_night
        self.screen.fill((13,20,32) if night else BG)
        lane_color=(55,69,82) if night else (100,100,100)
        marking_color=(145,139,91) if night else (200,200,100)
        sidewalk_color=(58,67,78) if night else (150,130,110)
        water_color=(15,43,62) if night else (36,112,128)
        ripple_color=(38,82,105) if night else (80,155,165)
        # road markings
        for i in range(LANES+1):
            pygame.draw.line(self.screen,lane_color,(i*LANE_W,0),(i*LANE_W,HEIGHT),2)
        for y in range(0,HEIGHT,60):
            for i in range(LANES):
                pygame.draw.rect(self.screen,marking_color,pygame.Rect(i*LANE_W+LANE_W//2-3,y,6,30))
        # sidewalks
        pygame.draw.rect(self.screen,sidewalk_color,pygame.Rect(0,HEIGHT-50,WIDTH,50))
        pygame.draw.rect(self.screen,sidewalk_color,pygame.Rect(0,0,WIDTH,30))
        pygame.draw.rect(self.screen,water_color,self.safe_lane)
        for x in range(16,WIDTH,48):
            pygame.draw.line(self.screen,ripple_color,(x,SAFE_LANE_TOP+14),(x+18,SAFE_LANE_TOP+14),2)
            pygame.draw.line(self.screen,ripple_color,(x+22,SAFE_LANE_TOP+62),(x+40,SAFE_LANE_TOP+62),2)
        for c in self.cars: c.draw(self.screen,night)
        for raft in self.rafts: raft.draw(self.screen)
        self.player.draw(self.screen)
        hud=pygame.Rect(0,0,WIDTH,52)
        pygame.draw.rect(self.screen,(20,20,20),hud)
        mode="NIGHT" if night else "DAY"
        s=self.hud_font.render(f"Score: {self.score//10}  Lives: {self.lives}  {mode}  GOAL: reach top  R=Restart",True,(220,220,220))
        self.screen.blit(s,(6,4))
        scores="  ".join(f"{index+1}:{score}" for index,score in enumerate(self.high_scores))
        if not scores:
            scores="No scores yet"
        high_score_text=self.high_score_font.render(f"TOP 5  {scores}",True,(240,220,120))
        self.screen.blit(high_score_text,(6,32))
        if self.game_over:
            self._msg("CRASHED!",(220,60,60))
        if self.won:
            self._msg("YOU MADE IT!",(80,220,80))
        pygame.display.flip()

    def _msg(self,text,color):
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        ov.fill((0,0,0,150))
        self.screen.blit(ov,(0,0))
        m=self.big_font.render(text,True,color)
        sub=self.font.render("Press R to Restart",True,(200,200,200))
        self.screen.blit(m,(WIDTH//2-m.get_width()//2,HEIGHT//2-40))
        self.screen.blit(sub,(WIDTH//2-sub.get_width()//2,HEIGHT//2+20))
        heading=self.font.render("TOP 5 SCORES",True,(240,220,120))
        self.screen.blit(heading,(WIDTH//2-heading.get_width()//2,HEIGHT//2+58))
        for index in range(5):
            score=str(self.high_scores[index]) if index<len(self.high_scores) else "---"
            row=self.hud_font.render(f"{index+1}. {score}",True,(220,220,220))
            self.screen.blit(row,(WIDTH//2-row.get_width()//2,HEIGHT//2+88+index*22))

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
