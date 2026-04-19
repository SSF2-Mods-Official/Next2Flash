package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1317")]
   public dynamic class Walk_14 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Walk_14()
      {
         super();
         addFrameScript(0,this.frame1,4,this.frame5,13,this.frame14,17,this.frame18);
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
      
      internal function frame5() : *
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
      
      internal function frame14() : *
      {
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_step_s2");
         }
         else
         {
            this.self.playSound("bm_footstep");
         }
      }
      
      internal function frame18() : *
      {
         this.self.stancePlayFrame("loop");
      }
   }
}

