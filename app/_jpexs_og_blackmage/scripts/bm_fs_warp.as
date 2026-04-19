package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol730")]
   public dynamic class bm_fs_warp extends MovieClip
   {
      public function bm_fs_warp()
      {
         super();
         addFrameScript(10,this.frame11);
      }
      
      internal function frame11() : *
      {
         stop();
         if(parent != null)
         {
            parent.removeChild(this);
         }
      }
   }
}

