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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1465")]
   public dynamic class NAir_69 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var attackBox2:MovieClip;
      
      public var attackBox3:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function NAir_69()
      {
         super();
         addFrameScript(0,this.frame1,2,this.frame3,3,this.frame4,4,this.frame5,6,this.frame7,8,this.frame9,10,this.frame11,12,this.frame13,14,this.frame15,16,this.frame17,22,this.frame23,23,this.frame24,24,this.frame25,31,this.frame32);
      }
      
      public function setAngle(param1:* = null) : *
      {
         var _loc2_:* = this.self.getYSpeed();
         var _loc3_:* = this.self.getXSpeed();
         var _loc4_:* = Math.atan2(_loc2_,_loc3_) * (-180 / Math.PI);
         var _loc5_:* = Math.sqrt(_loc2_ * _loc2_ + _loc3_ * _loc3_) * 4;
         if(!this.self.isFacingRight())
         {
            _loc4_ = 180 - _loc4_;
         }
         if(_loc4_ < 0)
         {
            _loc4_ += 360;
         }
         this.self.updateAttackBoxStats(1,{
            "direction":_loc4_,
            "power":_loc5_
         });
         this.self.updateAttackBoxStats(2,{
            "direction":_loc4_,
            "power":_loc5_
         });
         this.self.updateAttackBoxStats(3,{
            "direction":_loc4_,
            "power":_loc5_
         });
         SSF2API.print(_loc3_.toString() + " | " + _loc2_.toString());
         SSF2API.print(_loc4_.toString() + " | " + _loc5_.toString());
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(Boolean(parent) && SSF2API.isReady())
         {
            this.self.setLandingLag(false);
         }
      }
      
      internal function frame3() : *
      {
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(20),
            "y":-25
         });
         this.self.attachEffect("global_spark",{
            "x":this.self.flipX(-20),
            "y":-35
         });
         this.self.createTimer(1,-1,this.setAngle);
      }
      
      internal function frame4() : *
      {
         this.self.playAttackSound(1);
         this.self.setLandingLag(true);
      }
      
      internal function frame5() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame7() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame9() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame11() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame13() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame15() : *
      {
         this.self.refreshAttackID();
      }
      
      internal function frame17() : *
      {
         this.self.destroyTimer(this.setAngle);
         this.self.updateAttackBoxStats(1,{
            "power":63,
            "weightKB":0,
            "kbConstant":80,
            "direction":45,
            "reversableAngle":true,
            "hitLag":-1,
            "hitStun":-1,
            "selfHitStun":-1
         });
         this.self.updateAttackBoxStats(2,{
            "power":63,
            "weightKB":0,
            "kbConstant":80,
            "direction":45,
            "reversableAngle":true,
            "hitLag":-1,
            "hitStun":-1,
            "selfHitStun":-1
         });
         this.self.updateAttackBoxStats(3,{
            "power":63,
            "weightKB":0,
            "kbConstant":80,
            "direction":45,
            "reversableAngle":true,
            "hitLag":-1,
            "hitStun":-1,
            "selfHitStun":-1
         });
         this.self.refreshAttackID();
         this.self.setLandingLag(false);
      }
      
      internal function frame23() : *
      {
         this.self.endAttack();
      }
      
      internal function frame24() : *
      {
         this.self.destroyTimer(this.setAngle);
         this.self.updateAttackBoxStats(1,{
            "damage":2,
            "power":63,
            "weightKB":0,
            "kbConstant":80,
            "direction":45,
            "reversableAngle":true,
            "hitLag":-1,
            "hitStun":-1,
            "selfHitStun":-1
         });
         this.self.updateAttackBoxStats(2,{
            "damage":2,
            "power":63,
            "weightKB":0,
            "kbConstant":80,
            "direction":45,
            "reversableAngle":true,
            "hitLag":-1,
            "hitStun":-1,
            "selfHitStun":-1
         });
         this.self.updateAttackBoxStats(3,{
            "damage":2,
            "power":63,
            "weightKB":0,
            "kbConstant":80,
            "direction":45,
            "reversableAngle":true,
            "hitLag":-1,
            "hitStun":-1,
            "selfHitStun":-1
         });
         this.self.refreshAttackID();
      }
      
      internal function frame25() : *
      {
         SSF2API.getCamera().shake(3);
         if(this.self.getMetalStatus())
         {
            this.self.playSound("metal_land_m");
         }
         else
         {
            this.self.playSound("blackmage_landHeavy");
         }
      }
      
      internal function frame32() : *
      {
         this.self.endAttack();
      }
   }
}

