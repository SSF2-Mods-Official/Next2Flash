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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol737")]
   public dynamic class warp_141 extends MovieClip
   {
      public var self:*;
      
      public var xframe:String;
      
      public var character:*;
      
      public function warp_141()
      {
         super();
         addFrameScript(0,this.frame1,32,this.frame33,43,this.frame44);
      }
      
      public function projDestroy(param1:*) : *
      {
         SSF2API.print("activated");
         this.character.removeEventListener(SSF2Event.CHAR_HURT,this.projDestroy);
         this.self.removeFromCamera();
         this.self.destroy();
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getProjectile(this);
         this.xframe = "charging";
         if(SSF2API.isReady() && this.self)
         {
            this.character = this.self.getOwner();
            this.self.addToCamera();
            this.character.addEventListener(SSF2Event.CHAR_HURT,this.projDestroy);
         }
      }
      
      internal function frame33() : *
      {
         this.self.stancePlayFrame("charging");
      }
      
      internal function frame44() : *
      {
         this.self.destroy();
      }
   }
}

