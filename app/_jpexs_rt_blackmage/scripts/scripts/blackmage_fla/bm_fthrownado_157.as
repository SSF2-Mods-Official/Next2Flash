package blackmage_fla
{
   import flash.display.MovieClip;
   
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
         var _loc1_:* = undefined;
         var _loc2_:* = undefined;
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

