package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol153")]
   public dynamic class blackmage_demieffect extends MovieClip
   {
      public function blackmage_demieffect()
      {
         super();
         addFrameScript(17,this.frame18);
      }
      
      internal function frame18() : *
      {
         stop();
         if(parent != null)
         {
            parent.removeChild(this);
         }
      }
   }
}

