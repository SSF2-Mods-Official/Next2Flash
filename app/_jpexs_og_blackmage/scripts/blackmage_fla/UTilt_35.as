package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1337")]
   public dynamic class UTilt_35 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var attackBox2:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function UTilt_35()
      {
         super();
         addFrameScript(0,this.frame1,1,this.frame2,13,this.frame14,14,this.frame15);
      }
      
      internal function frame1() : *
      {
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.attachEffect("global_spark",{
               "x":this.self.flipX(-7),
               "y":-13
            });
         }
      }
      
      internal function frame2() : *
      {
         this.self.attachEffect("global_dust_light");
         this.self.playAttackSound(1);
         this.self.addEffectToList(this.self.attachEffect("trail_bmage_utilt",{
            "scaleX":1.4,
            "scaleY":1.4,
            "parentLock":true,
            "syncHitStun":true
         }));
         this.self.clearEffectsOnStateChange();
         this.self.setXSpeed(this.self.getXSpeed() * 0.75);
      }
      
      internal function frame14() : *
      {
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_step_s1");
         }
      }
      
      internal function frame15() : *
      {
         this.self.endAttack();
      }
   }
}

