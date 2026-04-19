package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol118")]
   public dynamic class trail_bmage_bair extends MovieClip
   {
      public function trail_bmage_bair()
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

