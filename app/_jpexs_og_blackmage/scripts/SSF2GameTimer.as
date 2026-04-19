package
{
   import flash.display.MovieClip;
   
   public class SSF2GameTimer extends SSF2BaseAPIObject
   {
      public function SSF2GameTimer(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2GameTimer";
      }
      
      public function getCurrentTime() : int
      {
         return _api.getCurrentTime();
      }
      
      public function setCurrentTime(param1:int) : void
      {
         _api.setCurrentTime(param1);
      }
      
      public function start() : void
      {
         _api.start();
      }
      
      public function restart() : void
      {
         _api.restart();
      }
      
      public function stop() : void
      {
         _api.stop();
      }
      
      public function getMC() : MovieClip
      {
         return _api.getMC();
      }
      
      public function setEndGameOptions(param1:Object) : void
      {
         _api.setEndGameOptions(param1);
      }
   }
}

