package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1535")]
   public dynamic class Stunned_120 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Stunned_120()
      {
         super();
         addFrameScript(0,this.frame1,25,this.frame26);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:BlackMageExt = null;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.playSound("bm_Dizzy");
            this.self.setGlobalVariable("jab",false);
         }
      }
      
      internal function frame26() : *
      {
         this.self.stancePlayFrame("again");
      }
   }
}

