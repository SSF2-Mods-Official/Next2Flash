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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1334")]
   public dynamic class FSmash_30 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var attackBox2:MovieClip;
      
      public var attackBox3:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var xframe:String;
      
      public var projectile:*;
      
      public function FSmash_30()
      {
         super();
         addFrameScript(0,this.frame1,3,this.frame4,43,this.frame44,44,this.frame45,48,this.frame49,51,this.frame52,58,this.frame59,74,this.frame75,75,this.frame76,86,this.frame87,88,this.frame89,99,this.frame100);
      }
      
      public function effects() : void
      {
         this.self.attachEffect("global_dust_heavy",{
            "x":this.self.flipX(5),
            "y":3,
            "scaleX":-0.5,
            "scaleY":-0.5
         });
      }
      
      internal function frame1() : *
      {
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
         this.xframe = null;
      }
      
      internal function frame4() : *
      {
         this.xframe = "charging";
         this.self.createTimer(4,-1,this.effects);
      }
      
      internal function frame44() : *
      {
         this.self.stancePlayFrame("charging");
      }
      
      internal function frame45() : *
      {
         this.xframe = "attack";
         this.self.destroyTimer(this.effects);
      }
      
      internal function frame49() : *
      {
         this.self.playSound("bmbolt");
         this.self.attachEffect("global_dust_swirl");
      }
      
      internal function frame52() : *
      {
         this.self.attachEffect("global_dust_heavy");
         SSF2API.getCamera().shake(6);
      }
      
      internal function frame59() : *
      {
         this.self.updateAttackBoxStats(1,{
            "damage":10,
            "kbConstant":75,
            "effect_id":"effect_elechit_light",
            "effectSound":"brawl_zap_m"
         });
         this.self.updateAttackBoxStats(2,{
            "damage":10,
            "kbConstant":75,
            "effect_id":"effect_elechit_light",
            "effectSound":"brawl_zap_m"
         });
         this.self.updateAttackBoxStats(3,{
            "damage":10,
            "kbConstant":75,
            "effect_id":"effect_elechit_light",
            "effectSound":"brawl_zap_m"
         });
      }
      
      internal function frame75() : *
      {
         this.self.endAttack();
      }
      
      internal function frame76() : *
      {
         this.xframe = "attack2";
         this.self.playSound("bm_whoosh");
         this.self.destroyTimer(this.effects);
      }
      
      internal function frame87() : *
      {
         this.self.attachEffect("global_dust_swirl");
         this.self.attachEffect("global_sparkle",{
            "x":this.self.flipX(15),
            "y":-30
         });
      }
      
      internal function frame89() : *
      {
         this.projectile = this.self.fireProjectile("fsmashfull");
      }
      
      internal function frame100() : *
      {
         this.self.endAttack();
      }
   }
}

