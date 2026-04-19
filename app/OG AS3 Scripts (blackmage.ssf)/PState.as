// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//PState

package 
{
    public class PState 
    {

        public static const IDLE:uint = 0;
        public static const DEAD:uint = 1;

        private static var statesArr:Array = [];

        {
            statesArr.push("IDLE");
            statesArr.push("DEAD");
        }


        public static function toString(_arg_1:uint):String
        {
            return (((_arg_1 >= 0) && (_arg_1 < statesArr.length)) ? statesArr[_arg_1] : "null");
        }


    }
}//package 

