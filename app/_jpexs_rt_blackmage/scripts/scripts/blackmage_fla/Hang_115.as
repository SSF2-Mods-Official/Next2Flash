package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1530")]
   public dynamic class Hang_115 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Hang_115()
      {
         super();
         addFrameScript(0,this.frame1,1,this.frame2,44,this.frame45);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:BlackMageExt = null;
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.setAttackEnabled(true,"b_forward");
            this.self.setAttackEnabled(true,"b_forward_air");
         }
      }
      
      internal function frame2() : *
      {
         this.self.attachEffect("ledgeGrab_gfx",{
            "x":this.self.flipX(0),
            "y":0,
            "scaleX":-0.4,
            "scaleY":-0.4
         });
      }
      
      internal function frame45() : *
      {
         this.self.stancePlayFrame("loop");
      }
   }
}

