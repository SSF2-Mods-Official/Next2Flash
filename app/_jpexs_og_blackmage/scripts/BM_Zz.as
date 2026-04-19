package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol505")]
   public dynamic class BM_Zz extends MovieClip
   {
      public function BM_Zz()
      {
         super();
         addFrameScript(27,this.frame28);
      }
      
      internal function frame28() : *
      {
         stop();
         parent.removeChild(this);
      }
   }
}

