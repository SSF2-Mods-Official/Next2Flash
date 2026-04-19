package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1323")]
   public dynamic class Helpless_20 extends MovieClip
   {
      public var hand:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function Helpless_20()
      {
         super();
         addFrameScript(0,this.frame1,5,this.frame6);
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
      }
      
      internal function frame6() : *
      {
         this.self.stancePlayFrame("redo");
      }
   }
}

