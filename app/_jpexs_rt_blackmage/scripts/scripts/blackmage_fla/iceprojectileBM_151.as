package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol670")]
   public dynamic class iceprojectileBM_151 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var self:*;
      
      public var isOnGround:Boolean;
      
      public var isLeft:Boolean;
      
      public var newProjectile:*;
      
      public var keepNext:Boolean;
      
      public var character:*;
      
      public function iceprojectileBM_151()
      {
         super();
         addFrameScript(0,this.frame1,1,this.frame2,3,this.frame4,8,this.frame9,9,this.frame10,16,this.frame17,20,this.frame21,25,this.frame26,26,this.frame27,27,this.frame28,28,this.frame29,29,this.frame30,31,this.frame32,32,this.frame33,34,this.frame35,51,this.frame52,52,this.frame53,55,this.frame56);
      }
      
      public function toEnd(param1:*) : *
      {
         this.self.removeEventListener(SSF2Event.PROJ_DESTROYED,this.toEnd);
         this.self.stancePlayFrame("end");
      }
      
      public function shieldIt(param1:*) : *
      {
         this.flipIt(param1.data.receiver);
      }
      
      public function reverseIt(param1:*) : *
      {
         this.flipIt(param1.data.opponent);
      }
      
      public function flipIt(param1:*) : *
      {
         if(param1.getType() == "SSF2Character")
         {
            this.character = param1;
         }
         this.isLeft = !this.isLeft;
         this.self.updateAttackBoxStats(1,{"priority":-1});
         if(this.newProjectile != null && !this.keepNext)
         {
            this.newProjectile.destroy();
            this.shootIt();
         }
      }
      
      public function shootIt() : void
      {
         var _loc1_:* = this.self.getX();
         var _loc2_:* = this.self.getY();
         var _loc3_:* = 55;
         if(!this.isOnGround)
         {
            _loc3_ = 25;
         }
         if(this.isLeft)
         {
            _loc3_ *= -1;
         }
         this.character.fireProjectile(this.self.exportStats(),_loc1_ + _loc3_,_loc2_,true);
         this.newProjectile = this.character.getCurrentProjectile();
         if(this.isLeft)
         {
            this.newProjectile.stancePlayFrame("left");
         }
      }
      
      public function killIt() : void
      {
         if(!this.self.isOnGround() || this.self.getGlobalVariable("destroy") == "true")
         {
            this.self.destroy();
         }
      }
      
      public function landIt(param1:*) : void
      {
         this.self.stancePlayFrame("chibland");
         this.shootIt();
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:* = undefined;
         var _loc4_:Boolean = false;
         var _loc5_:Boolean = false;
         var _loc6_:* = undefined;
         var _loc7_:Boolean = false;
         var _loc8_:* = undefined;
         var _loc9_:* = 55;
         this.self = SSF2API.getProjectile(this);
         this.isOnGround = true;
         this.isLeft = false;
         this.keepNext = false;
         if(SSF2API.isReady() && this.self)
         {
            this.character = this.self.getOwner();
            this.visible = false;
            if(!this.self.isFacingRight())
            {
               this.self.updateAttackBoxStats(1,{"direction":95});
            }
            this.self.addEventListener(SSF2Event.PROJ_DESTROYED,this.toEnd);
            this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD,this.shieldIt);
            this.self.addEventListener(SSF2Event.REVERSE,this.reverseIt);
         }
      }
      
      internal function frame2() : *
      {
         this.self.createTimer(1,20,this.killIt,false);
      }
      
      internal function frame4() : *
      {
         if(!this.self.inState(PState.DEAD))
         {
            this.visible = true;
         }
      }
      
      internal function frame9() : *
      {
         SSF2API.getCamera().shake(3);
      }
      
      internal function frame10() : *
      {
         this.self.playSound("iceshoot2");
         this.shootIt();
      }
      
      internal function frame17() : *
      {
         this.keepNext = true;
      }
      
      internal function frame21() : *
      {
         this.self.setXSpeed(0);
         this.self.setYSpeed(0);
         this.self.updateProjectileStats({"maxgravity":0});
      }
      
      internal function frame26() : *
      {
         this.self.destroy();
      }
      
      internal function frame27() : *
      {
         this.self.setGlobalVariable("streamEndProjectile1",true);
         SSF2API.print("Stream 1 down!");
         this.self.destroy();
      }
      
      internal function frame28() : *
      {
         this.self = SSF2API.getProjectile(this);
         this.isOnGround = true;
         this.isLeft = true;
         this.keepNext = false;
         if(SSF2API.isReady() && this.self)
         {
            this.character = this.self.getOwner();
            this.visible = false;
            if(this.self.isFacingRight())
            {
               this.self.updateAttackBoxStats(1,{"direction":95});
            }
            this.self.addEventListener(SSF2Event.PROJ_DESTROYED,this.toEnd);
            this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD,this.shieldIt);
            this.self.addEventListener(SSF2Event.REVERSE,this.reverseIt);
         }
      }
      
      internal function frame29() : *
      {
         this.self.stancePlayFrame("start");
      }
      
      internal function frame30() : *
      {
         if(this.newProjectile != null && !this.keepNext)
         {
            this.newProjectile.destroy();
         }
      }
      
      internal function frame32() : *
      {
         if(this.self == null)
         {
            this.self = SSF2API.getProjectile(this);
         }
         this.self.stancePlayFrame("susloop");
      }
      
      internal function frame33() : *
      {
         this.self = SSF2API.getProjectile(this);
         this.isOnGround = true;
         this.isLeft = false;
         this.keepNext = false;
         if(SSF2API.isReady() && this.self)
         {
            this.character = this.self.getOwner();
            this.isLeft = !this.character.isFacingRight();
            this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD,this.shieldIt);
            this.self.addEventListener(SSF2Event.REVERSE,this.reverseIt);
            if(this.character.isOnGround())
            {
               this.visible = false;
               this.self.addEventListener(SSF2Event.PROJ_DESTROYED,this.toEnd);
            }
            else
            {
               this.isOnGround = false;
               this.self.updateProjectileStats({
                  "gravity":1,
                  "maxgravity":12
               });
               this.self.addEventListener(SSF2Event.GROUND_TOUCH,this.landIt);
               this.self.stancePlayFrame("chibair");
            }
         }
      }
      
      internal function frame35() : *
      {
         this.self.stancePlayFrame("start");
      }
      
      internal function frame52() : *
      {
         this.self.stancePlayFrame("chibair");
      }
      
      internal function frame53() : *
      {
         this.self.playSound("sfx_icehit_s");
      }
      
      internal function frame56() : *
      {
         this.self.destroy();
      }
   }
}

