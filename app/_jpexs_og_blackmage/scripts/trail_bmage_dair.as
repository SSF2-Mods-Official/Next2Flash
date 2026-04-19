package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol112")]
   public dynamic class trail_bmage_dair extends MovieClip
   {
      public function trail_bmage_dair()
      {
         super();
         addFrameScript(8,this.frame9);
      }
      
      internal function frame9() : *
      {
         stop();
         if(parent)
         {
            parent.removeChild(this);
         }
      }
   }
}

