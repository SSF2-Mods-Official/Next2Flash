package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol688")]
   public dynamic class bm_waterSpout_strong extends MovieClip
   {
      public var stance:MovieClip;
      
      public function bm_waterSpout_strong()
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

