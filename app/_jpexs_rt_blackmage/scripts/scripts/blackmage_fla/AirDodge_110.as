package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1528")]
   public dynamic class AirDodge_110 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function AirDodge_110()
      {
         super();
         addFrameScript(0,this.frame1,2,this.frame3,14,this.frame15,23,this.frame24);
      }
      
      public function dodgeLand(param1:* = null) : *
      {
         this.self.toLand();
         this.self.stancePlayFrame("dodgeland");
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:BlackMageExt = null;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
      }
      
      internal function frame3() : *
      {
         this.self.setIntangibility(true);
         this.self.addEventListener(SSF2Event.GROUND_TOUCH,this.dodgeLand);
      }
      
      internal function frame15() : *
      {
         this.self.setIntangibility(false);
      }
      
      internal function frame24() : *
      {
         this.self.endAttack();
      }
   }
}

