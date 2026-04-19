package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1541")]
   public dynamic class Sleep_124 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Sleep_124()
      {
         super();
         addFrameScript(0,this.frame1,19,this.frame20);
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.attachEffect("BM_Zz",{
               "x":this.self.flipX(10),
               "y":-26
            });
            this.self.setGlobalVariable("jab",false);
            this.self.clearEffectsOnStateChange();
         }
         if(parent && SSF2API.isReady() && Boolean(this.self))
         {
            this.self.playSound("fall_asleep");
         }
      }
      
      internal function frame20() : *
      {
         this.self.stancePlayFrame("again");
      }
   }
}

