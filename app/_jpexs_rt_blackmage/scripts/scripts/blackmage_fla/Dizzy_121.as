package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1540")]
   public dynamic class Dizzy_121 extends MovieClip
   {
      public var dizzy_stars:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Dizzy_121()
      {
         super();
         addFrameScript(0,this.frame1,25,this.frame26);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:BlackMageExt = null;
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

