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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol1478")]
   public dynamic class ItemDashAttack_82 extends MovieClip
   {
      public var hitBox:MovieClip;
      
      public var hitBox2:MovieClip;
      
      public var itemBox:MovieClip;
      
      public var self:BlackMageExt;
      
      public function ItemDashAttack_82()
      {
         super();
         addFrameScript(0,this.frame1,5,this.frame6,7,this.frame8,23,this.frame24);
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getCharacter(this) as BlackMageExt;
      }
      
      internal function frame6() : *
      {
         this.self.getItem().activateItem();
         this.self.attachEffect("global_dust_light",{"x":this.self.flipX(-7)});
      }
      
      internal function frame8() : *
      {
         this.self.getItem().deactivateItem();
      }
      
      internal function frame24() : *
      {
         this.self.endAttack();
      }
   }
}

