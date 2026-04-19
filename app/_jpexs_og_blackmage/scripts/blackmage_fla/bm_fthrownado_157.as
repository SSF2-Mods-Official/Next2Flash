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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol609")]
   public dynamic class bm_fthrownado_157 extends MovieClip
   {
      public var self:*;
      
      public var character:*;
      
      public function bm_fthrownado_157()
      {
         super();
         addFrameScript(0,this.frame1,22,this.frame23);
      }
      
      public function remove(param1:*) : void
      {
         this.self.destroy();
         this.character.removeEventListener(SSF2Event.CHAR_HURT,this.remove);
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getProjectile(this);
         if(SSF2API.isReady() && this.self)
         {
            this.character = this.self.getOwner();
            this.character.addEventListener(SSF2Event.CHAR_HURT,this.remove);
         }
      }
      
      internal function frame23() : *
      {
         this.self.destroy();
      }
   }
}

