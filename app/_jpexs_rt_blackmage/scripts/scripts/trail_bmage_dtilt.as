package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol102")]
   public dynamic class trail_bmage_dtilt extends MovieClip
   {
      public function trail_bmage_dtilt()
      {
         super();
         addFrameScript(6,this.frame7);
      }
      
      internal function frame7() : *
      {
         stop();
         if(parent)
         {
            parent.removeChild(this);
         }
      }
   }
}

