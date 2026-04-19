package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1473")]
   public dynamic class FThrow_77 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var attackBox2:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var touchBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function FThrow_77()
      {
         super();
         addFrameScript(0,this.frame1,2,this.frame3,15,this.frame16,16,this.frame17,25,this.frame26);
      }
      
      internal function frame1() : *
      {
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.playSound("bm_Aero_start1");
            this.self.playSound("bm_Aero_start2");
         }
      }
      
      internal function frame3() : *
      {
         this.self.fireProjectile("bm_fthrowProj");
      }
      
      internal function frame16() : *
      {
         this.self.updateAttackStats({"refreshRate":50});
         this.self.updateAttackBoxStats(2,{
            "damage":3,
            "direction":25,
            "selfHitStun":1,
            "hasEffect":true
         });
         this.self.refreshAttackID();
      }
      
      internal function frame17() : *
      {
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_step_s1");
         }
         else
         {
            this.self.playSound("bm_footstep");
         }
      }
      
      internal function frame26() : *
      {
         this.self.endAttack();
      }
   }
}

