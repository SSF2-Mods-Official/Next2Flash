package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1330")]
   public dynamic class FTilt_27 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var attackBox2:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function FTilt_27()
      {
         super();
         addFrameScript(0,this.frame1,2,this.frame3,3,this.frame4,14,this.frame15);
      }
      
      internal function frame1() : *
      {
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
      }
      
      internal function frame3() : *
      {
         this.self.addEffectToList(this.self.attachEffect("trail_bmage_ftilt",{
            "scaleX":1.4,
            "scaleY":1.4,
            "parentLock":true,
            "syncHitStun":true
         }));
         this.self.clearEffectsOnStateChange();
      }
      
      internal function frame4() : *
      {
         this.self.playAttackSound(1);
         this.self.attachEffect("global_dust_light");
      }
      
      internal function frame15() : *
      {
         this.self.endAttack();
      }
   }
}

