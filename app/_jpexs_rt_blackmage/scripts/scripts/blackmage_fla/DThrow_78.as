package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1474")]
   public dynamic class DThrow_78 extends MovieClip
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
      
      public function DThrow_78()
      {
         super();
         addFrameScript(0,this.frame1,1,this.frame2,4,this.frame5,7,this.frame8,8,this.frame9,11,this.frame12,25,this.frame26);
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
      
      internal function frame2() : *
      {
         this.self.forceGrabbedHurtFrame("faint");
      }
      
      internal function frame5() : *
      {
         this.self.addEffectToList(this.self.attachEffect("blackmage_dthrow_bubble",{
            "scaleX":1.4,
            "scaleY":1.4,
            "parentLock":true,
            "syncHitStun":true
         }));
         this.self.clearEffectsOnStateChange();
      }
      
      internal function frame8() : *
      {
         this.self.playAttackSound(1);
      }
      
      internal function frame9() : *
      {
         this.xframe = "attack";
      }
      
      internal function frame12() : *
      {
         this.self.forceGrabbedHurtFrame("downed");
      }
      
      internal function frame26() : *
      {
         this.self.endAttack();
      }
   }
}

