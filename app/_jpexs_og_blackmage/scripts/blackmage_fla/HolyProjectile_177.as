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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol499")]
   public dynamic class HolyProjectile_177 extends MovieClip
   {
      public var attackBox:MovieClip;
      
      public var attackBox2:MovieClip;
      
      public var attackBox3:MovieClip;
      
      public var self:*;
      
      public var character:*;
      
      public var temp:*;
      
      public function HolyProjectile_177()
      {
         super();
         addFrameScript(0,this.frame1,14,this.frame15,44,this.frame45,54,this.frame55);
      }
      
      public function pullInCharacters() : void
      {
         var _loc2_:Number = NaN;
         var _loc3_:Number = NaN;
         this.temp = this.character.getGlobalVariable("fsTargets");
         var _loc1_:int = 0;
         while(_loc1_ < this.temp.length)
         {
            if(!this.temp[_loc1_].isDisposed())
            {
               _loc2_ = (this.self.getX() - this.temp[_loc1_].getX()) / 8;
               _loc3_ = (this.self.getY() - 100 - this.temp[_loc1_].getY()) / 8;
               this.temp[_loc1_].safeMove(_loc2_,0);
               this.temp[_loc1_].safeMove(0,_loc3_);
            }
            _loc1_++;
         }
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getProjectile(this);
         if(SSF2API.isReady() && this.self)
         {
            this.character = this.self.getOwner();
            this.self.addToCamera();
            this.self.updateAttackStats({"refreshRate":1});
            this.self.playSound("magic_screech");
            this.self.createTimer(1,0,this.pullInCharacters);
         }
      }
      
      internal function frame15() : *
      {
         this.self.updateAttackStats({"refreshRate":2});
         this.self.updateAttackBoxStats(1,{
            "damage":2,
            "hitStun":0,
            "direction":140,
            "canDI":false,
            "power":140,
            "kbConstant":40,
            "effectSound":"brawl_magic_s",
            "effect_id":"effect_magichit_light"
         });
      }
      
      internal function frame45() : *
      {
         this.self.destroyTimer(this.pullInCharacters);
      }
      
      internal function frame55() : *
      {
         this.self.removeFromCamera();
         this.self.destroy();
      }
   }
}

