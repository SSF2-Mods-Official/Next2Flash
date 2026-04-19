package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol191")]
   public dynamic class blackmage_dsmash_ice extends MovieClip
   {
      public function blackmage_dsmash_ice()
      {
         super();
         addFrameScript(16,this.frame17);
      }
      
      internal function frame17() : *
      {
         stop();
         if(parent)
         {
            parent.removeChild(this);
         }
      }
   }
}

