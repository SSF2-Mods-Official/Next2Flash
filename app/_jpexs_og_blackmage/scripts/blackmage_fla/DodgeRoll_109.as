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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1522")]
   public dynamic class DodgeRoll_109 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public var effect:*;
      
      public function DodgeRoll_109()
      {
         super();
         addFrameScript(0,this.frame1,1,this.frame2,2,this.frame3,8,this.frame9,15,this.frame16);
      }
      
      internal function frame1() : *
      {
         if(SSF2API.isReady())
         {
            this.self = SSF2API.getCharacter(this) as BlackMageExt;
         }
      }
      
      internal function frame2() : *
      {
         this.effect = this.self.attachEffect("global_dust_heavy",{
            "scaleX":0.8,
            "scaleY":0.8
         });
         this.effect.scaleX = -this.effect.scaleX;
      }
      
      internal function frame3() : *
      {
         this.self.setIntangibility(true);
      }
      
      internal function frame9() : *
      {
         this.self.setIntangibility(false);
      }
      
      internal function frame16() : *
      {
         this.self.endAttack();
      }
   }
}

