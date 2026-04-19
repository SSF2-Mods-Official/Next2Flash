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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1487")]
   public dynamic class ItemHome_Run_86 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function ItemHome_Run_86()
      {
         super();
         addFrameScript(0,this.frame1,28,this.frame29,30,this.frame31,32,this.frame33,45,this.frame46);
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
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
         if(Boolean(this.self) && SSF2API.isReady())
         {
            this.self.createTimer(4,-1,this.effects);
         }
      }
      
      internal function frame29() : *
      {
         this.self.destroyTimer(this.effects);
         this.self.updateAttackStats({"superArmor":true});
      }
      
      internal function frame31() : *
      {
         this.self.getItem().activateItem();
         this.self.playAttackSound(1);
         SSF2API.getCamera().shake(6);
         this.self.attachEffect("global_dust_heavy",{
            "x":this.self.flipX(5),
            "y":3,
            "scaleX":-0.75,
            "scaleY":-0.75
         });
      }
      
      internal function frame33() : *
      {
         this.self.getItem().deactivateItem();
         this.self.updateAttackStats({"superArmor":false});
      }
      
      internal function frame46() : *
      {
         this.self.endAttack();
      }
   }
}

