package
{
   public class TState
   {
      public static const IDLE:uint = 0;
      
      public static const BROKEN:uint = 1;
      
      public static const DEAD:uint = 2;
      
      private static var statesArr:Array = [];
      
      statesArr.push("IDLE");
      statesArr.push("BROKEN");
      statesArr.push("DEAD");
      
      public function TState()
      {
         super();
      }
      
      public static function toString(param1:uint) : String
      {
         return param1 >= 0 && param1 < statesArr.length ? statesArr[param1] : "null";
      }
   }
}

