package blackmage_fla
{
   import flash.display.MovieClip;
   
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
         var _loc1_:* = undefined;
         var _loc2_:String = null;
         var _loc3_:* = undefined;
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

