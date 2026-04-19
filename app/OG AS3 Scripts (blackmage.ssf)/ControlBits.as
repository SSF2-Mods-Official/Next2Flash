// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//ControlBits

package 
{
    public class ControlBits 
    {

        public static const TAP_JUMP:int = 1;
        public static const SHIELD:int = 2;
        public static const TAUNT:int = 4;
        public static const START:int = 8;
        public static const GRAB:int = 16;
        public static const BUTTON2:int = 32;
        public static const BUTTON1:int = 64;
        public static const JUMP:int = 128;
        public static const RIGHT:int = 0x0100;
        public static const LEFT:int = 0x0200;
        public static const DOWN:int = 0x0400;
        public static const UP:int = 0x0800;
        public static const DT_DASH:int = 0x1000;
        public static const AUTO_DASH:int = 0x2000;
        public static const DASH:int = 0x4000;
        public static const C_RIGHT:int = 0x8000;
        public static const C_LEFT:int = 0x10000;
        public static const C_DOWN:int = 0x20000;
        public static const C_UP:int = 0x40000;
        public static const JUMP2:int = 0x80000;
        public static const SHIELD2:int = 0x100000;
        public static const JUMP3:int = 0x200000;

        public var bits:int;

        public function ControlBits(_arg_1:int=0)
        {
            this.bits = _arg_1;
        }

        public static function getControls(_arg_1:int, _arg_2:int):int
        {
            return ((_arg_1 | _arg_2) - _arg_2);
        }


        public function get TAP_JUMP():Boolean
        {
            return ((bits & 0x01) ? true : false);
        }

        public function set TAP_JUMP(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x01) : (bits & (~(0x01))));
        }

        public function get SHIELD():Boolean
        {
            return ((bits & 0x02) ? true : false);
        }

        public function set SHIELD(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x02) : (bits & (~(0x02))));
        }

        public function get TAUNT():Boolean
        {
            return ((bits & 0x04) ? true : false);
        }

        public function set TAUNT(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x04) : (bits & (~(0x04))));
        }

        public function get START():Boolean
        {
            return ((bits & 0x08) ? true : false);
        }

        public function set START(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x08) : (bits & (~(0x08))));
        }

        public function get GRAB():Boolean
        {
            return ((bits & 0x10) ? true : false);
        }

        public function set GRAB(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x10) : (bits & (~(0x10))));
        }

        public function get BUTTON2():Boolean
        {
            return ((bits & 0x20) ? true : false);
        }

        public function set BUTTON2(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x20) : (bits & (~(0x20))));
        }

        public function get BUTTON1():Boolean
        {
            return ((bits & 0x40) ? true : false);
        }

        public function set BUTTON1(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x40) : (bits & (~(0x40))));
        }

        public function get JUMP():Boolean
        {
            return ((bits & 0x80) ? true : false);
        }

        public function set JUMP(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x80) : (bits & (~(0x80))));
        }

        public function get RIGHT():Boolean
        {
            return ((bits & 0x0100) ? true : false);
        }

        public function set RIGHT(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x0100) : (bits & (~(0x0100))));
        }

        public function get LEFT():Boolean
        {
            return ((bits & 0x0200) ? true : false);
        }

        public function set LEFT(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x0200) : (bits & (~(0x0200))));
        }

        public function get DOWN():Boolean
        {
            return ((bits & 0x0400) ? true : false);
        }

        public function set DOWN(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x0400) : (bits & (~(0x0400))));
        }

        public function get UP():Boolean
        {
            return ((bits & 0x0800) ? true : false);
        }

        public function set UP(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x0800) : (bits & (~(0x0800))));
        }

        public function get DT_DASH():Boolean
        {
            return ((bits & 0x1000) ? true : false);
        }

        public function set DT_DASH(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x1000) : (bits & (~(0x1000))));
        }

        public function get AUTO_DASH():Boolean
        {
            return ((bits & 0x2000) ? true : false);
        }

        public function set AUTO_DASH(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x2000) : (bits & (~(0x2000))));
        }

        public function get DASH():Boolean
        {
            return ((bits & 0x4000) ? true : false);
        }

        public function set DASH(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x4000) : (bits & (~(0x4000))));
        }

        public function get C_RIGHT():Boolean
        {
            return ((bits & 0x8000) ? true : false);
        }

        public function set C_RIGHT(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x8000) : (bits & (~(0x8000))));
        }

        public function get C_LEFT():Boolean
        {
            return ((bits & 0x010000) ? true : false);
        }

        public function set C_LEFT(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x010000) : (bits & (~(0x010000))));
        }

        public function get C_DOWN():Boolean
        {
            return ((bits & 0x020000) ? true : false);
        }

        public function set C_DOWN(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x020000) : (bits & (~(0x020000))));
        }

        public function get C_UP():Boolean
        {
            return ((bits & 0x040000) ? true : false);
        }

        public function set C_UP(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x040000) : (bits & (~(0x040000))));
        }

        public function get JUMP2():Boolean
        {
            return ((bits & 0x080000) ? true : false);
        }

        public function set JUMP2(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x080000) : (bits & (~(0x080000))));
        }

        public function get SHIELD2():Boolean
        {
            return ((bits & 0x100000) ? true : false);
        }

        public function set SHIELD2(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x100000) : (bits & (~(0x100000))));
        }

        public function get JUMP3():Boolean
        {
            return ((bits & 0x200000) ? true : false);
        }

        public function set JUMP3(_arg_1:Boolean):void
        {
            bits = ((_arg_1) ? (bits | 0x200000) : (bits & (~(0x200000))));
        }

        public function reset():void
        {
            bits = 0;
        }

        public function clone():ControlBits
        {
            return (new ControlBits(bits));
        }


    }
}//package 

