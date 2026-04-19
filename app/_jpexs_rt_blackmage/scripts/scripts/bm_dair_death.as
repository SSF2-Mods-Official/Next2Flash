package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol720")]
   public dynamic class bm_dair_death extends MovieClip
   {
      public var stance:MovieClip;
      
      public function bm_dair_death()
      {
         super();
         addFrameScript(0,this.frame1);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         stop();
      }
   }
}

