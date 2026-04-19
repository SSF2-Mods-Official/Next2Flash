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
      
      public static const RIGHT:int = 256;
      
      public static const LEFT:int = 512;
      
      public static const DOWN:int = 1024;
      
      public static const UP:int = 2048;
      
      public static const DT_DASH:int = 4096;
      
      public static const AUTO_DASH:int = 8192;
      
      public static const DASH:int = 16384;
      
      public static const C_RIGHT:int = 32768;
      
      public static const C_LEFT:int = 65536;
      
      public static const C_DOWN:int = 131072;
      
      public static const C_UP:int = 262144;
      
      public static const JUMP2:int = 524288;
      
      public static const SHIELD2:int = 1048576;
      
      public static const JUMP3:int = 2097152;
      
      public var bits:int;
      
      public function ControlBits(param1:int = 0)
      {
         super();
         this.bits = param1;
      }
      
      public static function getControls(param1:int, param2:int) : int
      {
         return (param1 | param2) - param2;
      }
      
      public function get TAP_JUMP() : Boolean
      {
         return this.bits & 1 ? true : false;
      }
      
      public function set TAP_JUMP(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 1 : this.bits & ~1;
      }
      
      public function get SHIELD() : Boolean
      {
         return this.bits & 2 ? true : false;
      }
      
      public function set SHIELD(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 2 : this.bits & ~2;
      }
      
      public function get TAUNT() : Boolean
      {
         return this.bits & 4 ? true : false;
      }
      
      public function set TAUNT(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 4 : this.bits & ~4;
      }
      
      public function get START() : Boolean
      {
         return this.bits & 8 ? true : false;
      }
      
      public function set START(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 8 : this.bits & ~8;
      }
      
      public function get GRAB() : Boolean
      {
         return this.bits & 0x10 ? true : false;
      }
      
      public function set GRAB(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x10 : this.bits & ~0x10;
      }
      
      public function get BUTTON2() : Boolean
      {
         return this.bits & 0x20 ? true : false;
      }
      
      public function set BUTTON2(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x20 : this.bits & ~0x20;
      }
      
      public function get BUTTON1() : Boolean
      {
         return this.bits & 0x40 ? true : false;
      }
      
      public function set BUTTON1(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x40 : this.bits & ~0x40;
      }
      
      public function get JUMP() : Boolean
      {
         return this.bits & 0x80 ? true : false;
      }
      
      public function set JUMP(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x80 : this.bits & ~0x80;
      }
      
      public function get RIGHT() : Boolean
      {
         return this.bits & 0x0100 ? true : false;
      }
      
      public function set RIGHT(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x0100 : this.bits & ~0x0100;
      }
      
      public function get LEFT() : Boolean
      {
         return this.bits & 0x0200 ? true : false;
      }
      
      public function set LEFT(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x0200 : this.bits & ~0x0200;
      }
      
      public function get DOWN() : Boolean
      {
         return this.bits & 0x0400 ? true : false;
      }
      
      public function set DOWN(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x0400 : this.bits & ~0x0400;
      }
      
      public function get UP() : Boolean
      {
         return this.bits & 0x0800 ? true : false;
      }
      
      public function set UP(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x0800 : this.bits & ~0x0800;
      }
      
      public function get DT_DASH() : Boolean
      {
         return this.bits & 0x1000 ? true : false;
      }
      
      public function set DT_DASH(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x1000 : this.bits & ~0x1000;
      }
      
      public function get AUTO_DASH() : Boolean
      {
         return this.bits & 0x2000 ? true : false;
      }
      
      public function set AUTO_DASH(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x2000 : this.bits & ~0x2000;
      }
      
      public function get DASH() : Boolean
      {
         return this.bits & 0x4000 ? true : false;
      }
      
      public function set DASH(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x4000 : this.bits & ~0x4000;
      }
      
      public function get C_RIGHT() : Boolean
      {
         return this.bits & 0x8000 ? true : false;
      }
      
      public function set C_RIGHT(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x8000 : this.bits & ~0x8000;
      }
      
      public function get C_LEFT() : Boolean
      {
         return this.bits & 0x010000 ? true : false;
      }
      
      public function set C_LEFT(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x010000 : this.bits & ~0x010000;
      }
      
      public function get C_DOWN() : Boolean
      {
         return this.bits & 0x020000 ? true : false;
      }
      
      public function set C_DOWN(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x020000 : this.bits & ~0x020000;
      }
      
      public function get C_UP() : Boolean
      {
         return this.bits & 0x040000 ? true : false;
      }
      
      public function set C_UP(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x040000 : this.bits & ~0x040000;
      }
      
      public function get JUMP2() : Boolean
      {
         return this.bits & 0x080000 ? true : false;
      }
      
      public function set JUMP2(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x080000 : this.bits & ~0x080000;
      }
      
      public function get SHIELD2() : Boolean
      {
         return this.bits & 0x100000 ? true : false;
      }
      
      public function set SHIELD2(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x100000 : this.bits & ~0x100000;
      }
      
      public function get JUMP3() : Boolean
      {
         return this.bits & 0x200000 ? true : false;
      }
      
      public function set JUMP3(param1:Boolean) : void
      {
         this.bits = param1 ? this.bits | 0x200000 : this.bits & ~0x200000;
      }
      
      public function reset() : void
      {
         this.bits = 0;
      }
      
      public function clone() : ControlBits
      {
         return new ControlBits(this.bits);
      }
   }
}

