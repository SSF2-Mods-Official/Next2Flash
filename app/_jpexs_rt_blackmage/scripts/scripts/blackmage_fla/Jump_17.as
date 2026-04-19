package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1320")]
   public dynamic class Jump_17 extends MovieClip
   {
      public var hand:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var xframe:*;
      
      public var done:*;
      
      public function Jump_17()
      {
         super();
         addFrameScript(0,this.frame1,15,this.frame16,31,this.frame32);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:MovieClip = null;
         var _loc6_:BlackMageExt = null;
         var _loc7_:* = undefined;
         var _loc8_:* = undefined;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         this.xframe = "midair";
         this.done = false;
         if(parent && SSF2API.isReady() && this.self && this.self.getGlobalVariable("screwAttackOn"))
         {
            this.self.endAttack();
            this.self.forceAttack("item_screw");
         }
      }
      
      internal function frame16() : *
      {
         this.self.endAttack();
      }
      
      internal function frame32() : *
      {
         this.self.endAttack();
      }
   }
}

