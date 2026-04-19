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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1511")]
   public dynamic class ItemFireDash_100 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var hand:MovieClip;
      
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var hitBox3:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function ItemFireDash_100()
      {
         super();
         addFrameScript(0,this.frame1,6,this.frame7,8,this.frame9,10,this.frame11,16,this.frame17,17,this.frame18,24,this.frame25);
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(SSF2API.isReady() && Boolean(this.self))
         {
            this.self.setLandingLag(true);
            this.self.playSound("sonic_shieldfire_dash");
         }
      }
      
      internal function frame7() : *
      {
         this.self.updateAttackStats({
            "air_ease":-1,
            "allowControl":true,
            "allowFastFall":false
         });
      }
      
      internal function frame9() : *
      {
         this.self.updateAttackStats({"allowFastFall":true});
      }
      
      internal function frame11() : *
      {
         this.self.setLandingLag(false);
      }
      
      internal function frame17() : *
      {
         this.self.endAttack();
      }
      
      internal function frame18() : *
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
      
      internal function frame25() : *
      {
         this.self.endAttack();
      }
   }
}

