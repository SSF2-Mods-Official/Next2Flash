// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//CState

package 
{
    public class CState 
    {

        public static const IDLE:uint = 0;
        public static const ENTRANCE:uint = 1;
        public static const REVIVAL:uint = 2;
        public static const WALK:uint = 3;
        public static const RUN:uint = 4;
        public static const JUMP_CHAMBER:uint = 5;
        public static const JUMP_RISING:uint = 6;
        public static const JUMP_FALLING:uint = 7;
        public static const LAND:uint = 8;
        public static const ATTACKING:uint = 9;
        public static const LEDGE_ROLL:uint = 10;
        public static const ITEM_TOSS:uint = 11;
        public static const CROUCH:uint = 12;
        public static const GRABBING:uint = 13;
        public static const INJURED:uint = 14;
        public static const FLYING:uint = 15;
        public static const DODGE_ROLL:uint = 16;
        public static const AIR_DODGE:uint = 17;
        public static const SIDESTEP_DODGE:uint = 18;
        public static const LEDGE_HANG:uint = 19;
        public static const LEDGE_CLIMB:uint = 20;
        public static const ROLL:uint = 21;
        public static const SHIELDING:uint = 22;
        public static const STUNNED:uint = 23;
        public static const DIZZY:uint = 24;
        public static const TUMBLE_FALL:uint = 25;
        public static const CRASH_LAND:uint = 26;
        public static const CRASH_GETUP:uint = 27;
        public static const CARRY:uint = 28;
        public static const SWIMMING:uint = 29;
        public static const LADDER:uint = 30;
        public static const EDGE_LEAN:uint = 31;
        public static const WALL_CLING:uint = 32;
        public static const FROZEN:uint = 33;
        public static const TAUNT:uint = 34;
        public static const KIRBY_STAR:uint = 35;
        public static const CAUGHT:uint = 36;
        public static const STAR_KO:uint = 37;
        public static const SCREEN_KO:uint = 38;
        public static const PITFALL:uint = 39;
        public static const SLEEP:uint = 40;
        public static const EGG:uint = 41;
        public static const DEAD:uint = 42;
        public static const GLIDING:uint = 43;
        public static const SKID:uint = 44;
        public static const HOVER:uint = 45;
        public static const JUMP_MIDAIR_RISING:uint = 46;
        public static const DISABLED:uint = 47;
        public static const DASH:uint = 48;
        public static const TURN:uint = 49;
        public static const TECH_GROUND:uint = 50;
        public static const TECH_ROLL:uint = 51;
        public static const SHIELD_DROP:uint = 52;
        public static const BARREL:uint = 53;
        public static const DASH_INIT:uint = 54;
        public static const HEAVY_LAND:uint = 55;
        public static const STAMINA_KO:uint = 56;
        public static const ITEM_PICKUP:uint = 57;
        public static const LOCKED:uint = 58;

        private static var statesArr:Array = [];

        {
            statesArr.push("IDLE");
            statesArr.push("ENTRANCE");
            statesArr.push("REVIVAL");
            statesArr.push("WALK");
            statesArr.push("RUN");
            statesArr.push("JUMP_CHAMBER");
            statesArr.push("JUMP_RISING");
            statesArr.push("JUMP_FALLING");
            statesArr.push("LAND");
            statesArr.push("ATTACKING");
            statesArr.push("LEDGE_ROLL");
            statesArr.push("ITEM_TOSS");
            statesArr.push("CROUCH");
            statesArr.push("GRABBING");
            statesArr.push("INJURED");
            statesArr.push("FLYING");
            statesArr.push("DODGE_ROLL");
            statesArr.push("AIR_DODGE");
            statesArr.push("SIDESTEP_DODGE");
            statesArr.push("LEDGE_HANG");
            statesArr.push("LEDGE_CLIMB");
            statesArr.push("ROLL");
            statesArr.push("SHIELDING");
            statesArr.push("STUNNED");
            statesArr.push("DIZZY");
            statesArr.push("TUMBLE_FALL");
            statesArr.push("CRASH_LAND");
            statesArr.push("CRASH_GETUP");
            statesArr.push("CARRY");
            statesArr.push("SWIMMING");
            statesArr.push("LADDER");
            statesArr.push("EDGE_LEAN");
            statesArr.push("WALL_CLING");
            statesArr.push("FROZEN");
            statesArr.push("TAUNT");
            statesArr.push("KIRBY_STAR");
            statesArr.push("CAUGHT");
            statesArr.push("STAR_KO");
            statesArr.push("SCREEN_KO");
            statesArr.push("PITFALL");
            statesArr.push("SLEEP");
            statesArr.push("EGG");
            statesArr.push("DEAD");
            statesArr.push("GLIDING");
            statesArr.push("SKID");
            statesArr.push("HOVER");
            statesArr.push("JUMP_MIDAIR_RISING");
            statesArr.push("DISABLED");
            statesArr.push("DASH");
            statesArr.push("TURN");
            statesArr.push("TECH_GROUND");
            statesArr.push("TECH_ROLL");
            statesArr.push("SHIELD_DROP");
            statesArr.push("BARREL");
            statesArr.push("DASH_INIT");
            statesArr.push("HEAVY_LAND");
            statesArr.push("STAMINA_KO");
            statesArr.push("ITEM_PICKUP");
            statesArr.push("LOCKED");
        }


        public static function toString(_arg_1:uint):String
        {
            return (((_arg_1 >= 0) && (_arg_1 < statesArr.length)) ? statesArr[_arg_1] : "null");
        }


    }
}//package 

