package blackmage_fla
{
   import flash.display.MovieClip;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1326")]
   public dynamic class Jab_23 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var controls:Object;
      
      public var used:Boolean;
      
      public var time:Number;
      
      public var pressed1:Boolean;
      
      public var pressed2:Boolean;
      
      public function Jab_23()
      {
         super();
         addFrameScript(0,this.frame1,1,this.frame2,2,this.frame3,3,this.frame4,5,this.frame6,9,this.frame10,10,this.frame11,11,this.frame12,12,this.frame13,18,this.frame19);
      }
      
      public function checkControls() : *
      {
         this.controls = this.self.getControls();
         if(!this.controls.BUTTON2)
         {
            this.pressed1 = true;
         }
         if(this.pressed1 && Boolean(this.controls.BUTTON2))
         {
            this.pressed2 = true;
         }
      }
      
      public function checkForGoToJab2() : *
      {
         if(this.pressed2)
         {
            this.pressed1 = false;
            this.pressed2 = false;
            this.self.stancePlayFrame("hit2");
         }
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:MovieClip = null;
         var _loc5_:MovieClip = null;
         var _loc6_:BlackMageExt = null;
         var _loc7_:Object = null;
         var _loc8_:Boolean = false;
         var _loc9_:Number = NaN;
         var _loc10_:Boolean = false;
         var _loc11_:Boolean = false;
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.controls = this.self.getControls();
            this.used = this.self.getGlobalVariable("jab");
            this.time = SSF2API.getElapsedFrames() - this.self.getGlobalVariable("lastUsedJab") || -999;
            if(this.used && this.time <= 15)
            {
               this.self.stancePlayFrame("hit2");
            }
         }
         this.pressed1 = false;
         this.pressed2 = false;
      }
      
      internal function frame2() : *
      {
         this.pressed1 = false;
         this.self.createTimer(1,8,this.checkControls);
      }
      
      internal function frame3() : *
      {
         this.self.addEffectToList(this.self.attachEffect("trail_bmage_jab1",{
            "scaleX":1.4,
            "scaleY":1.4,
            "parentLock":true,
            "syncHitStun":true
         }));
         this.self.clearEffectsOnStateChange();
         this.self.setGlobalVariable("jab",true);
         this.self.playAttackSound(1);
      }
      
      internal function frame4() : *
      {
         this.self.attachEffect("global_dust_blast",{
            "x":this.self.flipX(30),
            "y":-15,
            "parentLock":true
         });
      }
      
      internal function frame6() : *
      {
         this.self.createTimer(1,4,this.checkForGoToJab2);
      }
      
      internal function frame10() : *
      {
         this.self.endAttack();
      }
      
      internal function frame11() : *
      {
         this.self.updateAttackBoxStats(1,{
            "power":45,
            "direction":25,
            "damage":5,
            "hitLag":-1
         });
         this.self.refreshAttackID();
         this.self.setGlobalVariable("jab",false);
         this.self.setGlobalVariable("lastUsedJab",SSF2API.getElapsedFrames());
         this.self.destroyTimer(this.checkControls);
         this.self.destroyTimer(this.checkForGoToJab2);
         this.self.playAttackSound(2);
      }
      
      internal function frame12() : *
      {
         this.self.attachEffect("global_dust_light");
         this.self.addEffectToList(this.self.attachEffect("trail_bmage_jab2",{
            "scaleX":1.4,
            "scaleY":1.4,
            "parentLock":true,
            "syncHitStun":true
         }));
      }
      
      internal function frame13() : *
      {
         this.self.attachEffect("global_dust_blast",{
            "x":this.self.flipX(35),
            "y":-20,
            "parentLock":true
         });
      }
      
      internal function frame19() : *
      {
         this.self.endAttack();
      }
   }
}

