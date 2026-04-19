package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1316")]
   public dynamic class Lose_13 extends MovieClip
   {
      public function Lose_13()
      {
         super();
         addFrameScript(49,this.frame50);
      }
      
      internal function frame50() : *
      {
         gotoAndPlay("redo");
      }
   }
}

