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
   
   [Embed(source="/_assets/assets.swf", symbol="symbol295")]
   public dynamic class WhiteMageProjectile_187 extends MovieClip
   {
      public var self:*;
      
      public var character:*;
      
      public var lowestX:Number;
      
      public var highestX:Number;
      
      public var pos:Array;
      
      public var xCo:*;
      
      public var i:*;
      
      public function WhiteMageProjectile_187()
      {
         super();
         addFrameScript(0,this.frame1,18,this.frame19,64,this.frame65,69,this.frame70);
      }
      
      internal function frame1() : *
      {
         this.self = SSF2API.getProjectile(this);
         if(SSF2API.isReady() && this.self)
         {
            this.character = this.self.getOwner();
         }
      }
      
      internal function frame19() : *
      {
         this.lowestX = 9999999;
         this.highestX = -9999999;
         if(this.character.getGlobalVariable("fsTargets").length > 0)
         {
            this.pos = this.character.getGlobalVariable("fsTargets");
            this.i = 0;
            while(this.i < this.pos.length)
            {
               if(this.pos[this.i].getX() < this.lowestX)
               {
                  this.lowestX = this.pos[this.i].getX();
               }
               if(this.pos[this.i].getX() > this.highestX)
               {
                  this.highestX = this.pos[this.i].getX();
               }
               ++this.i;
            }
         }
         else if(this.self.isFacingRight())
         {
            this.lowestX = this.self.getX() + 200;
            this.highestX = this.self.getX() + 200;
         }
         else
         {
            this.lowestX = this.self.getX() - 200;
            this.highestX = this.self.getX() - 200;
         }
         this.xCo = this.lowestX + (this.highestX - this.lowestX) / 2;
         this.character.fireProjectile("bm_fs_holy",this.xCo,this.self.getY(),true);
      }
      
      internal function frame65() : *
      {
         this.self.attachEffect("bm_fs_warp");
         this.self.playSound("bm_Warp_part2");
      }
      
      internal function frame70() : *
      {
         this.self.destroy();
      }
   }
}

