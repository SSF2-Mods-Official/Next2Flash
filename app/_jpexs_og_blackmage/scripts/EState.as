package
{
   public class EState
   {
      public static const IDLE:uint = 0;
      
      public static const DEAD:uint = 1;
      
      private static var statesArr:Array = [];
      
      statesArr.push("IDLE");
      statesArr.push("DEAD");
      
      public function EState()
      {
         super();
      }
      
      public static function toString(param1:uint) : String
      {
         return param1 >= 0 && param1 < statesArr.length ? statesArr[param1] : "null";
      }
   }
}

