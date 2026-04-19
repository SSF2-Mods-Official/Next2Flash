package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol628")]
   public dynamic class bm_bthrowrock extends MovieClip
   {
      public var stance:MovieClip;
      
      public function bm_bthrowrock()
      {
         super();
         addFrameScript(0,this.frame1);
      }
      
      internal function frame1() : *
      {
         stop();
      }
   }
}

