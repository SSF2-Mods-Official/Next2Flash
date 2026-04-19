package blackmage_fla
{
   import adobe.utils.*;
   import flash.accessibility.*;
   import flash.desktop.*;
   import flash.display.*;
   import flash.errors.*;
   import flash.events.*;
   import flash.external.*;
   import flash.filters.*;
   import flash.geom.*;
   import flash.globalization.*;
   import flash.media.*;
   import flash.net.*;
   import flash.net.drm.*;
   import flash.printing.*;
   import flash.profiler.*;
   import flash.sampler.*;
   import flash.sensors.*;
   import flash.system.*;
   import flash.text.*;
   import flash.text.engine.*;
   import flash.text.ime.*;
   import flash.ui.*;
   import flash.utils.*;
   import flash.xml.*;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1462")]
   public dynamic class SSpecial_46 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var grabBox:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var touchBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var continuePlaying:Boolean;
      
      public var ground:Boolean;
      
      public function SSpecial_46()
      {
         super();
         addFrameScript(0,this.frame1,5,this.frame6,7,this.frame8,8,this.frame9,10,this.frame11,20,this.frame21,25,this.frame26,28,this.frame29,34,this.frame35,35,this.frame36,36,this.frame37,37,this.frame38,39,this.frame40,40,this.frame41,41,this.frame42,43,this.frame44,44,this.frame45,45,this.frame46,49,this.frame50,51,this.frame52,52,this.frame53,54,this.frame55,55,this.frame56,57,this.frame58,58,this.frame59,61,this.frame62,62,this.frame63,65,this.frame66,66,this.frame67,69,this.frame70,70,this.frame71,73,this.frame74,74,this.frame75,75,this.frame76,81,this.frame82,87,this.frame88);
      }
      
      public function checkGrabbed() : *
      {
         if(this.self.getGrabbedOpponents()[0])
         {
            this.self.gotoGrabbedCharacter();
            this.self.destroyTimer(this.checkGrabbed);
            this.self.stancePlayFrame("continue");
            this.self.playSound("blackmage_commandGrab");
            this.self.addEffectToList(this.self.attachEffect("cmd_grabbed_gfx",{
               "x":this.self.flipX(10),
               "y":-20,
               "scaleX":-0.4,
               "scaleY":-0.4
            }));
            this.self.clearEffectsOnStateChange();
         }
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.createTimer(1,0,this.checkGrabbed);
            this.continuePlaying = false;
            this.ground = this.self.isOnGround();
            this.self.playSound("haste1");
            this.self.setYSpeed(0);
            this.self.attachEffect("global_sparkle",{
               "x":this.self.flipX(15),
               "y":-30
            });
         }
      }
      
      internal function frame6() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-10),
            "y":-4
         });
      }
      
      internal function frame8() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(100),
            "y":-20
         });
         this.self.setXSpeed(0);
      }
      
      internal function frame9() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(3),
            "y":-8
         });
         this.self.attachEffect("global_dust_heavy");
      }
      
      internal function frame11() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(14),
            "y":-13
         });
      }
      
      internal function frame21() : *
      {
         this.self.destroyTimer(this.checkGrabbed);
      }
      
      internal function frame26() : *
      {
         this.self.attachEffect("global_dust_cloud");
         this.self.updateAttackStats({"air_ease":-0.3});
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_land_s");
         }
      }
      
      internal function frame29() : *
      {
         if(!this.self.isOnGround())
         {
            this.self.setAttackEnabled(false,"b_forward");
            this.self.setAttackEnabled(false,"b_forward_air");
            this.self.endAttack();
         }
      }
      
      internal function frame35() : *
      {
         this.self.setAttackEnabled(false,"b_forward");
         this.self.setAttackEnabled(false,"b_forward_air");
         this.self.endAttack();
      }
      
      internal function frame36() : *
      {
         this.self.playSound("haste2");
         this.self.attachEffect("global_sparkle",{
            "x":this.self.flipX(15),
            "y":-30
         });
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-90),
            "y":-45
         });
      }
      
      internal function frame37() : *
      {
         if(!this.self.isOnGround())
         {
            this.self.setXSpeed(0);
         }
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-60),
            "y":-45
         });
      }
      
      internal function frame38() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-30),
            "y":-45
         });
      }
      
      internal function frame40() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-90),
            "y":-45
         });
      }
      
      internal function frame41() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-60),
            "y":-45
         });
      }
      
      internal function frame42() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-30),
            "y":-45
         });
      }
      
      internal function frame44() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-90),
            "y":-45
         });
      }
      
      internal function frame45() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-60),
            "y":-45
         });
      }
      
      internal function frame46() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-30),
            "y":-45
         });
      }
      
      internal function frame50() : *
      {
         this.self.playSound("bm_sw_m");
      }
      
      internal function frame52() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame53() : *
      {
         this.self.playSound("bm_sw_s");
      }
      
      internal function frame55() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame56() : *
      {
         this.self.playSound("bm_sw_m");
      }
      
      internal function frame58() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame59() : *
      {
         this.self.playSound("bm_sw_s");
      }
      
      internal function frame62() : *
      {
         this.self.updateAttackBoxStats(1,{"damage":1});
         this.self.refreshAttackID();
      }
      
      internal function frame63() : *
      {
         this.self.playSound("bm_sw_m");
      }
      
      internal function frame66() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame67() : *
      {
         this.self.playSound("bm_sw_m");
      }
      
      internal function frame70() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame71() : *
      {
         this.self.playSound("bm_sw_m");
      }
      
      internal function frame74() : *
      {
         this.self.updateAttackBoxStats(1,{
            "selfHitStun":2,
            "damage":7,
            "hasEffect":true
         });
         this.self.updateAttackStats({
            "canFallOff":true,
            "xSpeedDecayAir":-0.15
         });
         this.self.refreshAttackID();
      }
      
      internal function frame75() : *
      {
         this.self.playSound("bm_sw_l");
         this.self.attachEffect("global_dust_heavy");
      }
      
      internal function frame76() : *
      {
         this.self.releaseOpponent();
         this.self.setXSpeed(17.5,false);
      }
      
      internal function frame82() : *
      {
         this.self.setXSpeed(0,false);
      }
      
      internal function frame88() : *
      {
         this.self.endAttack();
      }
   }
}

