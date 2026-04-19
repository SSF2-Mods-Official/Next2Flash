package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1475")]
   public dynamic class BThrow_79 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var attackBox2:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var touchBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var xframe:String;
      
      public function BThrow_79()
      {
         super();
         addFrameScript(0,this.frame1,2,this.frame3,4,this.frame5,5,this.frame6,6,this.frame7,7,this.frame8,8,this.frame9,23,this.frame24);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:MovieClip = null;
         var _loc6_:MovieClip = null;
         var _loc7_:MovieClip = null;
         var _loc8_:BlackMageExt = null;
         var _loc9_:String = null;
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
         this.xframe = null;
      }
      
      internal function frame3() : *
      {
         SSF2API.getCamera().shake(2);
         this.self.playAttackSound(1);
      }
      
      internal function frame5() : *
      {
         this.xframe = "attack";
      }
      
      internal function frame6() : *
      {
         SSF2API.getCamera().shake(2);
      }
      
      internal function frame7() : *
      {
         this.self.playAttackSound(2);
      }
      
      internal function frame8() : *
      {
         SSF2API.getCamera().shake(4);
      }
      
      internal function frame9() : *
      {
         this.self.fireProjectile("bthrowrock");
      }
      
      internal function frame24() : *
      {
         this.self.endAttack();
      }
   }
}

