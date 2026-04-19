package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1534")]
   public dynamic class Guard_119 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Guard_119()
      {
         super();
         addFrameScript(0,this.frame1,3,this.frame4,9,this.frame10);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:BlackMageExt = null;
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
      }
      
      internal function frame4() : *
      {
         this.self.stancePlayFrame("redo");
      }
      
      internal function frame10() : *
      {
         this.self.endAttack();
      }
   }
}

