package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1512")]
   public dynamic class ItemBubbleBounce_101 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var hand:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var speed:*;
      
      public var bounceSpeed:*;
      
      public function ItemBubbleBounce_101()
      {
         super();
         addFrameScript(0,this.frame1,12,this.frame13,13,this.frame14,25,this.frame26);
      }
      
      public function setSpeed(param1:* = null) : *
      {
         if(this.speed < 30)
         {
            this.speed += 3;
         }
         if(this.bounceSpeed < 30)
         {
            this.bounceSpeed += 1.5;
         }
         this.self.setYSpeed(this.speed);
      }
      
      public function bounce(param1:* = null) : *
      {
         this.self.resetJumps();
         this.self.destroyTimer(this.setSpeed);
         this.self.removeEventListener(SSF2Event.GROUND_TOUCH,this.bounce);
         this.self.removeEventListener(SSF2Event.ATTACK_CONNECT,this.bounce);
         if(this.self.getCharacterStat("jumpSpeedList") != null && this.getJumpSpeed() > this.bounceSpeed)
         {
            this.bounceSpeed = this.getJumpSpeed();
         }
         if(this.self.getCharacterStat("jumpSpeedMidair") > this.bounceSpeed)
         {
            this.bounceSpeed = this.self.getCharacterStat("jumpSpeedMidair");
         }
         this.self.setYSpeed(-this.bounceSpeed);
         SSF2API.playSound("sonic_shieldwater_bounce");
         this.self.stancePlayFrame("bounce");
      }
      
      public function getJumpSpeed() : Number
      {
         var _loc1_:* = this.self.getCharacterStat("jumpSpeedList").split(",");
         return Number(_loc1_[0]);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:MovieClip = null;
         var _loc6_:MovieClip = null;
         var _loc7_:BlackMageExt = null;
         var _loc8_:* = undefined;
         var _loc9_:* = undefined;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         this.speed = 0;
         this.bounceSpeed = 0;
         if(SSF2API.isReady() && Boolean(this.self))
         {
            this.self.createTimer(1,-1,this.setSpeed);
            this.self.addEventListener(SSF2Event.ATTACK_CONNECT,this.bounce);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH,this.bounce);
         }
      }
      
      internal function frame13() : *
      {
         this.self.stancePlayFrame("fallLoop");
      }
      
      internal function frame14() : *
      {
         this.self.updateAttackStats({
            "xSpeedCap":-1,
            "xSpeedAccel":0,
            "xSpeedAccelAir":0,
            "xSpeedDecay":0,
            "xSpeedDecayAir":0
         });
      }
      
      internal function frame26() : *
      {
         this.self.endAttack();
      }
   }
}

