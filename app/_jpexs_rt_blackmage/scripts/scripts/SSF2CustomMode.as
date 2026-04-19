package
{
   public class SSF2CustomMode extends SSF2BaseAPIObject
   {
      public function SSF2CustomMode(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2CustomMode";
      }
      
      final public function getInitialGameSettings() : *
      {
         return _api.getInitialGameSettings();
      }
      
      public function getModeSettings() : Object
      {
         return _api.getModeSettings();
      }
      
      public function getStageClass() : Class
      {
         return null;
      }
      
      public function getStageMC() : Class
      {
         return null;
      }
      
      public function handleMatchComplete() : void
      {
      }
      
      public function getSummary() : String
      {
         return _api.getSummary();
      }
      
      final public function startMatch(param1:*) : void
      {
         _api.startMatch(param1);
      }
      
      final public function saveModeData(param1:Object) : Boolean
      {
         return _api.saveModeData(param1);
      }
      
      final public function endMode(param1:Object) : void
      {
         _api.endMode(param1);
      }
   }
}

