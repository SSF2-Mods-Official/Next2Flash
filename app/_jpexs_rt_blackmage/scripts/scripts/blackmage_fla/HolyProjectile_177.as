package blackmage_fla
{
   import flash.display.MovieClip;
   
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
         var _loc1_:Number = Number(NaN);
         var _loc2_:Number = Number(NaN);
         this.temp = this.character.getGlobalVariable("fsTargets");
         var _loc3_:int = 0;
         while(_loc3_ < this.temp.length)
         {
            if(!this.temp[_loc3_].isDisposed())
            {
               _loc1_ = (this.self.getX() - this.temp[_loc3_].getX()) / 8;
               _loc2_ = (this.self.getY() - 100 - this.temp[_loc3_].getY()) / 8;
               this.temp[_loc3_].safeMove(_loc1_,0);
               this.temp[_loc3_].safeMove(0,_loc2_);
            }
            _loc3_++;
         }
      }
      
      internal function frame1() : *
      {
         var _loc1_:MovieClip = null;
         var _loc2_:MovieClip = null;
         var _loc3_:MovieClip = null;
         var _loc4_:* = undefined;
         var _loc5_:* = undefined;
         var _loc6_:* = undefined;
         var _loc7_:Number = Number(NaN);
         var _loc8_:Number = Number(NaN);
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

