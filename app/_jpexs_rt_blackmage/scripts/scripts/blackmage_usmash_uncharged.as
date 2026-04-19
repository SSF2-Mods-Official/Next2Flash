package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol212")]
   public dynamic class blackmage_usmash_uncharged extends MovieClip
   {
      public function blackmage_usmash_uncharged()
      {
         super();
         addFrameScript(13,this.frame14);
      }
      
      internal function frame14() : *
      {
         stop();
         if(parent)
         {
            parent.removeChild(this);
         }
      }
   }
}

