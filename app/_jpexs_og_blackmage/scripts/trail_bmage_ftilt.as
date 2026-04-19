package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol96")]
   public dynamic class trail_bmage_ftilt extends MovieClip
   {
      public function trail_bmage_ftilt()
      {
         super();
         addFrameScript(7,this.frame8);
      }
      
      internal function frame8() : *
      {
         stop();
         if(parent)
         {
            parent.removeChild(this);
         }
      }
   }
}

