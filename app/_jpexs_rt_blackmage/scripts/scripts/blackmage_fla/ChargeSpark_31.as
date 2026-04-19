package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol163")]
   public dynamic class ChargeSpark_31 extends MovieClip
   {
      public function ChargeSpark_31()
      {
         super();
         addFrameScript(4,this.frame5);
      }
      
      internal function frame5() : *
      {
         stop();
         parent.removeChild(this);
      }
   }
}

