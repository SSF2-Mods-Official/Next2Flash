package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol631")]
   public dynamic class bm_misstext extends MovieClip
   {
      public function bm_misstext()
      {
         super();
         addFrameScript(21,this.frame22);
      }
      
      internal function frame22() : *
      {
         stop();
         parent.removeChild(this);
      }
   }
}

