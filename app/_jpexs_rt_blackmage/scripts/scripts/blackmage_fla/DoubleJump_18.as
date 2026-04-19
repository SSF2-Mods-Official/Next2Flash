package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1321")]
   public dynamic class DoubleJump_18 extends MovieClip
   {
      public var hand:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var done:Boolean;
      
      public var xframe:*;
      
      public function DoubleJump_18()
      {
         super();
         addFrameScript(0,this.frame1,7,this.frame8,15,this.frame16);
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:MovieClip = null;
         var _loc6_:BlackMageExt = null;
         var _loc7_:Boolean = false;
         var _loc8_:* = undefined;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(SSF2API.isReady() && Boolean(this.self))
         {
            this.done = false;
            this.xframe = "midair";
            if(this.self.getGlobalVariable("screwAttackOn") && this.self.getMidairJumpCount() < 2)
            {
               this.self.forceAttack("item_screw");
            }
            else if(this.self.getGlobalVariable("sonicShieldFiredash") && (Boolean(this.self.getControls().LEFT) || Boolean(this.self.getControls().RIGHT)))
            {
               this.self.forceAttack("item_firedash");
            }
            else if(this.self.getGlobalVariable("sonicShieldBubbleBounce") && Boolean(this.self.getControls().DOWN))
            {
               this.self.forceAttack("item_bubblebounce");
            }
            else if(this.self.isFacingRight() && this.self.getControls().LEFT || !this.self.isFacingRight() && this.self.getControls().RIGHT)
            {
               this.self.stancePlayFrame("backflip");
            }
         }
      }
      
      internal function frame8() : *
      {
         this.self.endAttack();
      }
      
      internal function frame16() : *
      {
         this.self.endAttack();
      }
   }
}

