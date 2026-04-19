package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1522")]
   public dynamic class DodgeRoll_109 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var effect:*;
      
      public function DodgeRoll_109()
      {
         super();
         addFrameScript(0,this.frame1,1,this.frame2,2,this.frame3,8,this.frame9,15,this.frame16);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:BlackMageExt = null;
         var _loc4_:* = undefined;
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
      }
      
      internal function frame2() : *
      {
         this.effect = this.self.attachEffect("global_dust_heavy",{
            "scaleX":0.8,
            "scaleY":0.8
         });
         this.effect.scaleX = -this.effect.scaleX;
      }
      
      internal function frame3() : *
      {
         this.self.setIntangibility(true);
      }
      
      internal function frame9() : *
      {
         this.self.setIntangibility(false);
      }
      
      internal function frame16() : *
      {
         this.self.endAttack();
      }
   }
}

