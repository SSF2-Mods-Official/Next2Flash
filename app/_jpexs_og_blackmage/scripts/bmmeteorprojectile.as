package
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol598")]
   public dynamic class bmmeteorprojectile extends MovieClip
   {
      public var stance:MovieClip;
      
      public function bmmeteorprojectile()
      {
         super();
         addFrameScript(0,this.frame1);
      }
      
      internal function frame1() : *
      {
         stop();
      }
   }
}

