package
{
   public class SSF2CustomMatch extends SSF2BaseAPIObject
   {
      public var matchData:Object;
      
      public function SSF2CustomMatch(param1:*)
      {
         super(param1);
         matchData = {};
      }
      
      override public function getType() : String
      {
         return "SSF2CustomMatch";
      }
      
      public function getGameSettings() : Object
      {
         return _api.getGameSettings();
      }
      
      public function matchSetup(param1:Object) : Object
      {
         return param1;
      }
   }
}

