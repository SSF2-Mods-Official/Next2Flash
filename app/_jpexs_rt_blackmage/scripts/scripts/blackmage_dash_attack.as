package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol217")]
   public dynamic class blackmage_dash_attack extends MovieClip
   {
      public function blackmage_dash_attack()
      {
         super();
         addFrameScript(18,this.frame19);
      }
      
      internal function frame19() : *
      {
         stop();
         if(parent)
         {
            parent.removeChild(this);
         }
      }
   }
}

