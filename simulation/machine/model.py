from simulation.physics.axis import Axis
from simulation.sensors.virtual import product_sensor,in_seal_zone
from simulation.faults.catalog import FAULTS

class Machine:
    """Kinematic model in mm; no heat, material deformation or safety validation."""
    def __init__(self,recipe=None):
        self.recipe=recipe or dict(product_length=60,bag_pitch=120,speed=10,film_offset=0,seal_offset=0)
        self.axes=[Axis() for _ in range(5)]; self.axes[3].position=40
        self.products=[]; self.faults=set(); self.time=0.; self.ack=0; self.reject_ack=0
        self.packages=0; self.rejects=0; self.last_cut=False; self.follow_time=0.; self.events=[]
        self.reseed()
    @property
    def seal_x(self): return 4*self.recipe['bag_pitch']
    def reseed(self):
        pitch=self.recipe['bag_pitch']; self.products=[dict(id=i,x=pitch/2+i*pitch,packed=False) for i in range(4)]
        self.next_id=4
    def inject(self,name,on):
        if name not in FAULTS: raise ValueError(name)
        if on: self.faults.add(name)
        else: self.faults.discard(name)
        if on and name=='product_missing': self.products=[]
        if on and name=='double_feed' and self.products:
            self.products.append(dict(id=self.next_id,x=self.products[0]['x']+10,packed=False)); self.next_id+=1
        if on and name=='product_in_seal_zone':
            self.products.append(dict(id=self.next_id,x=self.seal_x,packed=False)); self.next_id+=1
        if not on and name in ['product_missing','arrival_delay','sensor_stuck_off','sensor_stuck_on','double_feed','product_in_seal_zone']:
            # Virtual manual clearing/reloading, explicitly only while stopped in HMI.
            self.reseed()
            if name!='sensor_stuck_on': self.products[0]['x']=120
    def inputs(self,commands,dt,out):
        f=self.faults; sensor=product_sensor(self.products,120,self.recipe['product_length'])
        if 'sensor_stuck_on' in f: sensor=True
        if 'sensor_stuck_off' in f: sensor=False
        r=self.recipe
        vals=dict(I_StartPB=commands.get('start',0),I_StopPB=commands.get('stop',0),I_ResetPB=commands.get('reset',0),I_Mode=commands.get('mode',2),I_ColdReset=commands.get('cold',0),
          I_GuardClosed='guard_open' not in f,I_EStopOK='estop' not in f,I_ProductPresent=sensor,
          I_FilmMark=(self.axes[1].position%r['bag_pitch'])<4,I_FilmEnd='film_end' in f,
          I_EndSealHome=self.axes[3].position>=39,I_ProductInSealZone=('product_in_seal_zone' in f) or (out.get('Q_EndSealEnable',0)>0 and in_seal_zone(self.products,self.seal_x,r['product_length'])),
          I_AxisError=20 if 'axis_following_error' in f else (max(abs(a.error) for a in self.axes) if self.follow_time>.6 else 0),
          I_FilmError=self.axes[1].error+(20 if 'film_position_error' in f else 0),
          I_DoubleFeed=any(abs(a['x']-b['x'])<r['product_length'] for i,a in enumerate(self.products) for b in self.products[i+1:]),
          I_Jam='jam' in f,I_PackagedAck=self.ack,I_RejectAck=self.reject_ack,
          I_FilmPosition=self.axes[1].position,I_ProductPosition=self.products[0]['x'] if self.products else -1000,
          I_EndSealActual=self.axes[3].position,I_ProductLength=r['product_length'],I_BagPitch=r['bag_pitch'],I_PackagingSpeed=r['speed'],
          I_FilmOffset=r['film_offset'],I_SealOffset=r['seal_offset'],I_Dt=dt,
          I_InfeedActual=self.axes[0].position,I_CenterActual=self.axes[2].position,I_DischargeActual=self.axes[4].position)
        return vals
    def step(self,out,dt):
        self.ack=0; self.reject_ack=0; self.time+=dt
        keys=['Q_InfeedTarget','Q_FilmTarget','Q_CenterTarget','Q_EndSealTarget','Q_DischargeTarget']
        deltas=[]
        for i,(a,key) in enumerate(zip(self.axes,keys)):
            freeze=('axis_following_error' in self.faults and i==0) or ('jam' in self.faults and i==4)
            gain=1
            if 'film_slip' in self.faults and i==1:
                # Slip caps actual web velocity: target error accumulates rather
                # than a position servo silently catching up through the slip.
                nominal=out.get('Q_Speed',0)*.4
                actual_target=min(out.get(key,a.position),a.position+nominal*dt)
                delta=a.step(actual_target,dt,freeze)
                a.target=out.get(key,a.position); a.error=a.target-a.position
            else: delta=a.step(out.get(key,a.position),dt,freeze,gain)
            deltas.append(delta)
        self.follow_time=self.follow_time+dt if max(abs(a.error) for a in self.axes)>8 else 0
        for p in self.products: p['x']+=deltas[0 if p['x']<self.seal_x/2 else (1 if p['x']<self.seal_x else 4)]
        cut=out.get('Q_CutterEnable',0)>0
        if cut and not self.last_cut:
            candidates=[p for p in self.products if self.seal_x<=p['x']<self.seal_x+self.recipe['bag_pitch'] and not p['packed']]
            safe=not in_seal_zone(self.products,self.seal_x,self.recipe['product_length']) and self.axes[3].position<8
            if len(candidates)==1 and safe:
                candidates[0]['packed']=True; self.ack=1; self.packages+=1
                self.events.append(dict(t=round(self.time,3),event='packaged',product=candidates[0]['id'],film=self.axes[1].position,jaw=self.axes[3].position))
            else: self.reject_ack=1; self.rejects+=1
        self.last_cut=cut
        self.products=[p for p in self.products if p['x']<self.seal_x+3.5*self.recipe['bag_pitch']]
        if out.get('Q_InfeedRun',0) and not {'product_missing','arrival_delay'}&self.faults:
            if not self.products or min(p['x'] for p in self.products)>=self.recipe['bag_pitch']*1.5:
                self.products.append(dict(id=self.next_id,x=self.recipe['bag_pitch']/2,packed=False)); self.next_id+=1
    def state(self):
        sensor=product_sensor(self.products,120,self.recipe['product_length'])
        if 'sensor_stuck_on' in self.faults: sensor=True
        if 'sensor_stuck_off' in self.faults: sensor=False
        return dict(time=self.time,products=self.products,axes=[a.state() for a in self.axes],faults=sorted(self.faults),recipe=self.recipe,packages=self.packages,rejects=self.rejects,product_sensor=sensor,seal_x=self.seal_x)
