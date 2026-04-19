package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol95")]
   public dynamic class trail_bmage_jab1 extends MovieClip
   {
      public function trail_bmage_jab1()
      {
         super();
         addFrameScript(5,this.frame6);
      }
      
      internal function frame6() : *
      {
         stop();
         if(parent)
         {
            parent.removeChild(this);
         }
      }
   }
}

