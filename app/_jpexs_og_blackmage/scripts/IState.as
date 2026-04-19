package
{
   public class IState
   {
      public static const IDLE:uint = 0;
      
      public static const HOLD:uint = 1;
      
      public static const TOSS:uint = 2;
      
      public static const DEAD:uint = 3;
      
      private static var statesArr:Array = [];
      
      statesArr.push("IDLE");
      statesArr.push("HOLD");
      statesArr.push("TOSS");
      statesArr.push("DEAD");
      
      public function IState()
      {
         super();
      }
      
      public static function toString(param1:uint) : String
      {
         return param1 >= 0 && param1 < statesArr.length ? statesArr[param1] : "null";
      }
   }
}

